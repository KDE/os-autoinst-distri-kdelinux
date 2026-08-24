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


def build_sysext() -> Path:
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

    sysupdate_dir = sysext_root / "usr" / "lib" / "sysupdate.d"
    pubring = (
        sysext_root
        / "usr"
        / "lib"
        / "systemd"
        / "import-pubring.pgp"
    )

    staging_channel_url = os.environ.get("STAGING_CHANNEL_URL")
    pubkey_b64 = os.environ.get("SYSUPDATE_PUBKEY_B64")

    # Clean up before creating the sysext.
    if not staging_channel_url and sysupdate_dir.is_dir():
        # If we haven't been passed a URL, clean up any dropins that may point to one from a previous run.
        shutil.rmtree(sysupdate_dir)

    if not pubkey_b64 and pubring.is_file():
        # If we haven't been passed a signing key, clean up any that exist from a previous run.
        pubring.unlink()

    if staging_channel_url:
        # Create sysupdate.d dropins to redirect updates to our staged S3 image in CI.
        override = f"[Source]\nPath={staging_channel_url}\n"

        dropins = [
            sysupdate_dir / "50-root-x86-64-caibx.transfer.d",
            sysupdate_dir / "50-root-x86-64-erofs.transfer.d",
            sysupdate_dir / "60-esp.transfer.d",
        ]

        for dropin in dropins:
            dropin.mkdir(parents=True, exist_ok=True)
            (dropin / "99-openqa-override.conf").write_text(override)

        # Give it an ephemeral signing key, generated in CI, so it can verify updates from a staging channel outside of master upstream.
        if pubkey_b64:
            pubring.parent.mkdir(parents=True, exist_ok=True)

            result = subprocess.run(
                ["gpg", "--dearmor"],
                input=base64.b64decode(pubkey_b64),
                capture_output=True,
                check=True,
            )
            pubring.write_bytes(result.stdout)

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
