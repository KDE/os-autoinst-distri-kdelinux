# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import re
import subprocess
from contextlib import chdir, nullcontext
from dataclasses import dataclass, replace
from pathlib import Path
from urllib.parse import urlsplit

import requests

import lib.worker.job
import lib.worker.sysext
from lib.common.log import get_logger
from lib.common.paths import git_root
from lib.worker.download_image import (
    channel_url,
    download_file,
    download_latest,
    download_previous,
)
from lib.worker.local_update import (
    LocalUpdateError,
    inspect_build_output,
    serve_local_update,
)

logger = get_logger(__name__)

_ISO_VERSION_PATTERN = re.compile(r"kde-linux_(\d{12})\.iso$")


class JobFlowError(Exception):
    """Raised when an openQA job flow cannot continue."""


@dataclass(frozen=True)
class BuildUnderTest:
    image: Path | None
    output: str
    build: str


class JobFlow:
    def __init__(
        self,
        client: lib.worker.job.OpenQAClient,
        group: str | None,
        worker_class: str | None,
    ) -> None:
        self.client = client
        self.group = group
        self.worker_class = worker_class
        self.parent: int | None = None
        self.tests_failed = False

    def run_job(self, config: lib.worker.job.JobConfig) -> None:
        config = replace(
            config,
            group=self.group,
            after=self.parent,
            worker_class=self.worker_class,
        )

        current_job = lib.worker.job.Job(self.client, config)
        result = current_job.run()
        self.parent = current_job.job_id

        match result:
            case lib.worker.job.JobSuccess():
                pass
            case lib.worker.job.JobNonFatalFailure():
                self.tests_failed = True
            case lib.worker.job.JobFatalFailure(reason=reason):
                raise JobFlowError(reason)


def _find_local_iso(
    casedir: Path,
    older_than: str | None = None,
) -> Path | None:
    images: dict[str, Path] = {}

    for image in casedir.glob("*.iso"):
        match = _ISO_VERSION_PATTERN.fullmatch(image.name)
        if match is None:
            continue

        version = match.group(1)
        if older_than is None or version < older_than:
            images[version] = image

    if not images:
        return None

    return images[max(images)]


def _download_image_url(casedir: Path, image_url: str) -> Path:
    image_name = Path(urlsplit(image_url).path).name

    if not image_name:
        raise JobFlowError(f"Invalid image URL: {image_url}")

    image_path = casedir / image_name

    download_file(
        image_url,
        str(image_path),
    )

    return image_path


def _build_from_image(
    image_name: str,
    image: Path | None,
) -> BuildUnderTest:
    output = Path(image_name).stem

    return BuildUnderTest(
        image=image,
        output=output,
        build=output.rsplit("_", 1)[-1],
    )


def _version_from_image(image: Path) -> str:
    match = _ISO_VERSION_PATTERN.fullmatch(image.name)
    if match is None:
        raise JobFlowError(
            f"Could not determine build version from image {image.name}"
        )

    return match.group(1)


def _validate_upgrade_base(
    image: Path,
    target: BuildUnderTest,
) -> Path:
    if _version_from_image(image) >= target.build:
        raise JobFlowError(
            f"Upgrade base {image.name} is not older than target "
            f"{target.build}"
        )

    return image


def _latest_public_version() -> str:
    response = requests.get(
        channel_url().rstrip("/") + "/sysupdate/v2/SHA256SUMS"
    )
    response.raise_for_status()

    versions = re.findall(
        r"kde-linux_([0-9]{12})",
        response.text,
    )

    if not versions:
        raise JobFlowError(
            "Could not determine public version from upstream SHA256SUMS"
        )

    return max(versions)


def _resolve_build_under_test(
    casedir: Path,
    upgrade: bool,
) -> BuildUnderTest:
    image_url = os.environ.get("IMAGE_URL")

    if upgrade:
        if image_url:
            image_name = Path(urlsplit(image_url).path).name
            logger.info("Using %s as the upgrade target", image_name)
            return _build_from_image(image_name, None)

        version = _latest_public_version()
        logger.info("Using latest public build %s as the upgrade target", version)
        return BuildUnderTest(
            image=None,
            output=f"kde-linux_{version}",
            build=version,
        )

    image = _find_local_iso(casedir)

    if image is None:
        if image_url:
            image = _download_image_url(casedir, image_url)
        else:
            logger.info("No .iso image found, downloading latest")
            with chdir(casedir):
                image = casedir / download_latest()

    return _build_from_image(image.name, image)


def _resolve_install_image(
    casedir: Path,
    build: BuildUnderTest,
    upgrade: bool,
    upgrade_from: Path | None = None,
) -> Path:
    if not upgrade:
        if build.image is None:
            raise JobFlowError(
                "Non-upgrade flow has no installation image"
            )

        return build.image

    if upgrade_from is not None:
        image = upgrade_from.expanduser()
        if not image.is_absolute():
            image = casedir / image

        image = image.resolve()
        if not image.is_file():
            raise JobFlowError(f"Upgrade base does not exist: {image}")

        logger.info(
            "Using local image %s as the explicit upgrade base",
            image,
        )
        return _validate_upgrade_base(image, build)

    # The upgrade flow installs an older base, then upgrades it to the build
    # under test. Staged builds should start from the latest published image;
    # published builds should start from the previous one.
    if os.environ.get("STAGING_CHANNEL_URL"):
        # The build under test is an unpublished staged image, so install the
        # latest published image.
        logger.info(
            "Downloading latest published image as the upgrade base"
        )
        with chdir(casedir):
            image = casedir / download_latest()
        return _validate_upgrade_base(image, build)

    # The build under test is a published image, so use the newest local image
    # that is still older than the target when one is available.
    local_image = _find_local_iso(casedir, older_than=build.build)
    if local_image is not None:
        logger.info(
            "Using existing older image %s as the upgrade base",
            local_image.name,
        )
        return _validate_upgrade_base(local_image, build)

    logger.info("Downloading previous image for upgrade test")
    with chdir(casedir):
        image = casedir / download_previous(build.build)
    return _validate_upgrade_base(image, build)


def _stage_mock_tests(casedir: Path) -> None:
    # Copy test cases to the directory where openQA expects so that the needle
    # editor works.
    destination = Path("/var/lib/openqa/tests/kde-linux")
    destination.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "rsync",
            "-a",
            "--delete",
            "--exclude",
            "*.iso",
            "--exclude",
            "*.img",
            "--exclude",
            "/.*",
            f"{casedir}/",
            destination,
        ],
        check=True,
    )

    subprocess.run(
        [
            "chown",
            "-R",
            "geekotest:geekotest",
            destination,
        ],
        check=True,
    )


def _flavors(
    upgrade: bool,
    encrypt: bool,
) -> tuple[str, str]:
    if upgrade:
        live = "live-upgrade"
        installed = "installed-upgrade"
    else:
        live = "live"
        installed = "installed"

    if encrypt:
        live += "-encrypted"
        installed += "-encrypted"

    return live, installed


def _job_group(upgrade: bool) -> str | None:
    # Mock doesn't have any groups.
    if os.environ.get("MOCK_MODE"):
        return None

    if upgrade:
        return "KDE Linux Upgrade"

    return "KDE Linux Installation"


def run_jobs(
    *,
    worker_class: str | None = None,
    upgrade: bool = False,
    encrypt: bool = False,
    upgrade_from: Path | None = None,
    upgrade_to: Path | None = None,
) -> None:
    """Submit and poll all test jobs for a build."""

    casedir = git_root()
    mock_mode = bool(os.environ.get("MOCK_MODE"))

    if (upgrade_from is None) != (upgrade_to is None):
        raise JobFlowError(
            "--upgrade-from and --upgrade-to must be specified together"
        )

    if upgrade_from is not None and not upgrade:
        raise JobFlowError(
            "--upgrade-from and --upgrade-to require --upgrade"
        )

    if not mock_mode and worker_class is None:
        raise JobFlowError(
            "worker_class is required outside mock mode"
        )

    try:
        target_output = None
        if upgrade_to is not None and upgrade_from is not None:
            target = upgrade_to.expanduser()
            base = upgrade_from.expanduser()
            if not target.is_absolute():
                target = casedir / target
            if not base.is_absolute():
                base = casedir / base

            target_output = inspect_build_output(target)
            target_build = BuildUnderTest(
                image=None,
                output=f"kde-linux_{target_output.version}",
                build=target_output.version,
            )
            upgrade_from = base.resolve()
            if not upgrade_from.is_file():
                raise JobFlowError(
                    f"Upgrade base does not exist: {upgrade_from}"
                )
            _validate_upgrade_base(upgrade_from, target_build)

        update_context = (
            serve_local_update(target_output, casedir)
            if target_output is not None
            else nullcontext(None)
        )

        with update_context as local_update:
            if local_update is not None:
                build = BuildUnderTest(
                    image=None,
                    output=f"kde-linux_{local_update.version}",
                    build=local_update.version,
                )
                sysext_image = lib.worker.sysext.build_sysext(
                    channel_url=local_update.url,
                    disable_caibx=local_update.disable_caibx,
                    verify_updates=False,
                )
            else:
                build = _resolve_build_under_test(casedir, upgrade)
                sysext_image = lib.worker.sysext.build_sysext()

            _run_resolved_jobs(
                casedir=casedir,
                build=build,
                sysext_image=sysext_image,
                worker_class=worker_class,
                upgrade=upgrade,
                encrypt=encrypt,
                upgrade_from=upgrade_from,
                mock_mode=mock_mode,
            )
    except LocalUpdateError as error:
        raise JobFlowError(str(error)) from error


def _run_resolved_jobs(
    *,
    casedir: Path,
    build: BuildUnderTest,
    sysext_image: Path,
    worker_class: str | None,
    upgrade: bool,
    encrypt: bool,
    upgrade_from: Path | None,
    mock_mode: bool,
) -> None:
    install_image = _resolve_install_image(
        casedir,
        build,
        upgrade,
        upgrade_from,
    )
    disk = Path(f"{build.output}.qcow2")

    if mock_mode:
        _stage_mock_tests(casedir)

    live_flavor, installed_flavor = _flavors(
        upgrade,
        encrypt,
    )

    flow = JobFlow(
        client=lib.worker.job.OpenQAClient(
            host=os.environ["OPENQA_HOST_ADDR"],
            scheme=os.environ.get("OPENQA_SCHEME", "https"),
        ),
        group=_job_group(upgrade),
        worker_class=worker_class,
    )

    # Chain each job onto the previous one, so we get a nice dependency graph.
    # A successful job continues normally, while a non-fatal test failure is
    # recorded and the remaining jobs continue. Everything else is a fatal
    # failure, so fail fast.
    flow.run_job(
        lib.worker.job.JobConfig(
            name="install-system",
            variant=os.environ.get("VARIANT"),
            flavor=live_flavor,
            live=install_image,
            hdd=disk,
            sysext=sysext_image,
            build=build.build,
            casedir=casedir,
            encrypt=encrypt,
        )
    )

    if upgrade:
        flow.run_job(
            lib.worker.job.JobConfig(
                name="upgrade-system",
                variant=os.environ.get("VARIANT"),
                flavor=installed_flavor,
                hdd=disk,
                sysext=sysext_image,
                build=build.build,
                casedir=casedir,
                upgrade=True,
                encrypt=encrypt,
            )
        )

    flow.run_job(
        lib.worker.job.JobConfig(
            name="sanity-test",
            variant=os.environ.get("VARIANT"),
            flavor=installed_flavor,
            hdd=disk,
            sysext=sysext_image,
            build=build.build,
            casedir=casedir,
            encrypt=encrypt,
        )
    )

    if flow.tests_failed:
        raise JobFlowError(
            "one or more jobs had failing tests"
        )
