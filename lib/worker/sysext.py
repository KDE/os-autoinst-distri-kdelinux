# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import base64
import os
import pwd
import shutil
import subprocess
from pathlib import Path

from lib.common.log import get_logger
from lib.common.paths import OPENQA_SSH_PRIVATE_KEY

logger = get_logger(__name__)

_OPENQA_ROOT_AUTHORIZED_KEY = Path(
    "usr/lib/kde-linux-openqa/openqa-root-authorized-key"
)


def _compile_requirements(casedir: Path, sysext_root: Path) -> None:
    requirements = (
        sysext_root
        / "usr"
        / "lib"
        / "kde-linux-openqa"
        / "requirements.txt"
    )

    requirements.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "uv",
            "export",
            "--quiet",
            "--only-group",
            "sut",
            "--format",
            "requirements.txt",
            "--no-emit-project",
            "--output-file",
            requirements,
        ],
        cwd=casedir,
        check=True,
    )


def _generate_ssh_keypair(sysext_root: Path) -> None:
    """Create the host key and stage the public key in the SUT sysext."""
    private_key = Path(OPENQA_SSH_PRIVATE_KEY)
    public_key = private_key.with_suffix(".pub")
    staged_public_key = sysext_root / _OPENQA_ROOT_AUTHORIZED_KEY

    # Remove a stale key before generating its replacement.
    private_key.unlink(missing_ok=True)
    public_key.unlink(missing_ok=True)
    staged_public_key.unlink(missing_ok=True)

    try:
        subprocess.run(
            [
                "ssh-keygen",
                "-q",
                "-t",
                "ed25519",
                "-N",
                "",
                "-C",
                "kde-linux-openqa",
                "-f",
                str(private_key),
            ],
            check=True,
        )
        staged_public_key.parent.mkdir(parents=True, exist_ok=True)
        staged_public_key.write_bytes(public_key.read_bytes())
        staged_public_key.chmod(0o644)
        private_key.chmod(0o600)
        # Ensure the worker can actually use the key.
        if os.geteuid() == 0:
            try:
                worker = pwd.getpwnam("_openqa-worker")
            except KeyError:
                pass
            else:
                os.chown(private_key, worker.pw_uid, worker.pw_gid)
    finally:
        # The public key is copied into the sysext, so no need to keep this around.
        public_key.unlink(missing_ok=True)


def _configure_sysupdate(
    sysext_root: Path,
    channel_url: str | None,
    public_key_b64: str | None,
    disable_caibx: bool,
    verify_updates: bool,
) -> None:
    sysupdate_dir = sysext_root / "usr" / "lib" / "sysupdate.d"
    pubring = (
        sysext_root
        / "usr"
        / "lib"
        / "systemd"
        / "import-pubring.pgp"
    )

    # Dropins and masks in this directory are generated for one specific run,
    # so never retain them when rebuilding the sysext.
    if sysupdate_dir.is_dir():
        shutil.rmtree(sysupdate_dir)

    pubring.unlink(missing_ok=True)

    if not channel_url:
        return

    # Redirect updates to a staged CI tree or a temporary local source.
    override = ""
    if not verify_updates:
        override += "[Transfer]\nVerify=no\n\n"
    override += f"[Source]\nPath={channel_url}\n"

    dropins = [
        sysupdate_dir / "50-root-x86-64-caibx.transfer.d",
        sysupdate_dir / "50-root-x86-64-erofs.transfer.d",
        sysupdate_dir / "60-esp.transfer.d",
    ]

    for dropin in dropins:
        dropin.mkdir(parents=True, exist_ok=True)
        (dropin / "99-openqa-override.conf").write_text(override)

    if disable_caibx:
        # CAIBX is produced after the root and UKI, so permit testing a build
        # as soon as those two essential artifacts are ready.
        caibx_transfer = sysupdate_dir / "50-root-x86-64-caibx.transfer"
        caibx_transfer.symlink_to("/dev/null")

    # Give it an ephemeral signing key so the SUT can verify non-production
    # update metadata.
    if public_key_b64:
        pubring.parent.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            ["gpg", "--dearmor"],
            input=base64.b64decode(public_key_b64),
            capture_output=True,
            check=True,
        )
        pubring.write_bytes(result.stdout)


def build_sysext(
    *,
    channel_url: str | None = None,
    public_key_b64: str | None = None,
    disable_caibx: bool = False,
    verify_updates: bool = True,
) -> Path:
    casedir = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    sysext_root = casedir / "extensions" / "openqa"

    # Build the openQA sysext for the SUT.
    # The top-level files in ./lib are shared between the host and the SUT, so copy them in at sysext build time.
    # These are in .gitignore.
    sysext_lib = sysext_root / "usr" / "lib" / "kde-linux-openqa" / "lib"

    shutil.copytree(
        casedir / "lib",
        sysext_lib,
        dirs_exist_ok=True,
    )

    _generate_ssh_keypair(sysext_root)

    # Build the requirements declared in pyproject.toml into the sysext.
    _compile_requirements(casedir, sysext_root)

    channel_url = channel_url or os.environ.get("STAGING_CHANNEL_URL")
    public_key_b64 = public_key_b64 or os.environ.get("SYSUPDATE_PUBKEY_B64")
    _configure_sysupdate(
        sysext_root,
        channel_url,
        public_key_b64,
        disable_caibx,
        verify_updates,
    )

    sysext_image = Path("openqa-sysext.img")
    os.environ["SYSEXT_IMG"] = str(sysext_image)

    subprocess.run(
        [
            "mkfs.erofs",
            "--quiet",
            "-L",
            "kde-openqa-ext",
            sysext_image,
            sysext_root,
        ],
        check=True,
    )

    logger.info("Built openQA sysext at %s", sysext_image)
    return sysext_image
