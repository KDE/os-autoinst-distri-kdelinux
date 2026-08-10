# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2025 Anicaa (Kangwei Zhu) <anicaazhu@gmail.com>
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import requests
import os
from urllib import parse
from dataclasses import dataclass
import re
from lib.common.log import get_logger

_ISO_CHANNEL_URL = os.environ.get("ISO_CHANNEL_URL", "https://storage.kde.org/kde-linux/testing/")
_ISO_PATTERN = re.compile(r"kde-linux_(\d{12})\.iso$")

log = get_logger(__name__)


class DownloadError(Exception):
    """Raised when an error occurs while attempting to download .iso files."""


@dataclass(frozen=True)
class Image:
    version: str
    filename: str


def download_file(download_url: str, filename: str) -> None:
    log.info(f"Started downloading from: {download_url}")
    with requests.get(download_url, stream=True) as req:
        req.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in req.iter_content(chunk_size=8192):
                file.write(chunk)
    log.info("Download completed")
    log.info(f"Downloaded file: {filename}")


def _available_images() -> list[Image]:
    checksums_url = parse.urljoin(
        f"{_ISO_CHANNEL_URL.rstrip('/')}/",
        "SHA256SUMS",
    )
    resp = requests.get(checksums_url)
    resp.raise_for_status()

    images: dict[str, Image] = {}
    for line in resp.text.splitlines():
        match = _ISO_PATTERN.search(line.strip())
        if match is not None:
            filename = match.group(0)
            version = match.group(1)
            images.setdefault(version, Image(version, filename))

    if not images:
        raise DownloadError(".iso files not found on the server")

    return list(images.values())


def _download_image(filename: str) -> str:
    download_file(parse.urljoin(_ISO_CHANNEL_URL, filename), filename)
    return filename


def download_latest() -> str:
    latest_image = max(
        _available_images(),
        key=lambda image: image.version,
    )
    return _download_image(latest_image.filename)


def download_previous(build_version: str) -> str:
    previous_images = [
        image
        for image in _available_images()
        if image.version < build_version
    ]

    if not previous_images:
        raise DownloadError(
            f"No public .iso image exists before build {build_version}"
        )

    previous_image = max(
        previous_images,
        key=lambda image: image.version,
    )
    return _download_image(previous_image.filename)


def download_specific(build_version: str) -> None:
    filename = f"kde-linux_{build_version}.iso"
    download_url = parse.urljoin(_ISO_CHANNEL_URL, filename)
    resp = requests.head(download_url)
    if resp.status_code != 200:
        raise DownloadError(f"Specified build not found: {build_version}")
    download_file(download_url, filename)
