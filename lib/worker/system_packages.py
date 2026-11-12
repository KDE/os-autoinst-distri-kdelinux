# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import subprocess

from lib.common.log import get_logger

logger = get_logger(__name__)

_PACKAGES = (
    "python3-asyncio",
    "python3-requests",
    "python3-beautifulsoup4",
    "python3-colorlog",
    "python3-websockets",
    "dos2unix",
    "vim",
    "openssh-clients",
    "erofs-utils",
    "gpg2",
    "python3-fabric",
    "perl-Inline-Python",
)


def install() -> None:
    """Configure package repositories and install missing worker dependencies (mock mode)."""

    if not os.environ.get("MOCK_MODE"):
        return

    logger.info("Installing worker system packages…")

    subprocess.run(
        ["zypper", "removerepo", "devel-languages-perl"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    missing = [
        package
        for package in _PACKAGES
        if subprocess.run(
            ["rpm", "-q", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        ).returncode
        != 0
    ]

    if not missing:
        logger.info("Worker system packages are already installed")
        return

    result = subprocess.run(
        [
            "zypper",
            "--non-interactive",
            "--gpg-auto-import-keys",
            "install",
            *missing,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    if result.returncode not in (0, 106):
        raise subprocess.CalledProcessError(result.returncode, result.args)

    logger.info("Installed worker system packages")
