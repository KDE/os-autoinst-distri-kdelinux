# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import hashlib
import http.server
import re
import tempfile
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from functools import partial
from pathlib import Path

from lib.common.log import get_logger

logger = get_logger(__name__)

_ROOT_PATTERN = re.compile(
    r"kde-linux_([0-9]{12})_root-x86-64\.erofs"
)
_QEMU_HOST_ADDRESS = "10.0.2.2"


class LocalUpdateError(Exception):
    """Raised when a build output cannot be used as an update source."""


@dataclass(frozen=True)
class BuildOutput:
    version: str
    root: Path
    uki: Path
    caibx: Path | None


@dataclass(frozen=True)
class LocalUpdateSource:
    version: str
    url: str
    disable_caibx: bool


class _RequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:
        logger.debug("Local update server: " + format, *args)

    def copyfile(self, source, outputfile) -> None:
        try:
            super().copyfile(source, outputfile)
        except (BrokenPipeError, ConnectionResetError):
            logger.debug("Local update client closed its connection")


def inspect_build_output(directory: Path) -> BuildOutput:
    directory = directory.expanduser().resolve()
    if not directory.is_dir():
        raise LocalUpdateError(
            f"Local build output does not exist: {directory}"
        )

    roots: dict[str, Path] = {}
    for root in directory.glob("kde-linux_*_root-x86-64.erofs"):
        match = _ROOT_PATTERN.fullmatch(root.name)
        if match:
            roots[match.group(1)] = root

    if not roots:
        raise LocalUpdateError(
            f"No KDE Linux root image found in {directory}"
        )

    version = max(roots)
    uki = directory / f"kde-linux_{version}.efi"
    if not uki.is_file():
        raise LocalUpdateError(
            f"The {version} build in {directory} has no matching UKI"
        )

    caibx = directory / f"kde-linux_{version}_root-x86-64.caibx"

    return BuildOutput(
        version=version,
        root=roots[version],
        uki=uki,
        caibx=caibx if caibx.is_file() else None,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(16 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _link_artifacts(
    build: BuildOutput,
    repository: Path,
) -> list[Path]:
    artifacts = [build.root, build.uki]
    if build.caibx is not None:
        artifacts.append(build.caibx)

    for artifact in artifacts:
        (repository / artifact.name).symlink_to(artifact)

    return artifacts


def _create_manifest(repository: Path, artifacts: list[Path]) -> None:
    manifest = repository / "SHA256SUMS"
    manifest.write_text(
        "".join(
            f"{_sha256(artifact)}  {artifact.name}\n"
            for artifact in artifacts
        )
    )


def _prepare_repository(build: BuildOutput, repository: Path) -> None:
    repository.mkdir()
    artifacts = _link_artifacts(build, repository)
    _create_manifest(repository, artifacts)


@contextmanager
def serve_local_update(
    build: BuildOutput,
    temporary_parent: Path,
) -> Iterator[LocalUpdateSource]:
    with tempfile.TemporaryDirectory(
        prefix=".openqa-local-update-",
        dir=temporary_parent,
    ) as temporary_directory:
        temporary_path = Path(temporary_directory)
        repository = temporary_path / "sysupdate"
        _prepare_repository(build, repository)

        handler = partial(_RequestHandler, directory=str(repository))
        server = http.server.ThreadingHTTPServer(("0.0.0.0", 0), handler)
        server_thread = threading.Thread(
            target=server.serve_forever,
            name="openqa-local-update-server",
            daemon=True,
        )
        server_thread.start()

        port = server.server_address[1]
        url = f"http://{_QEMU_HOST_ADDRESS}:{port}/"
        logger.info("Serving local update %s at %s", build.version, url)

        try:
            yield LocalUpdateSource(
                version=build.version,
                url=url,
                disable_caibx=build.caibx is None,
            )
        finally:
            server.shutdown()
            server.server_close()
            server_thread.join()
