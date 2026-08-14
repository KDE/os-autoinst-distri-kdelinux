# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import ssl
import subprocess
import time
import urllib.request
import uuid
from functools import cache
from pathlib import Path
from lib.common.log import get_logger


logger = get_logger(__name__)

_WORKERS_CONFIG = Path("/etc/openqa/workers.ini")
_CLIENT_CONFIG = Path("/etc/openqa/client.conf")
_CACHE_DATABASE = Path("/var/lib/openqa/cache/cache.sqlite")
_WORKER_LAUNCHER = Path("/run_openqa_worker.sh")


class WorkerConfigurationError(Exception):
    """Raised when the openQA worker cannot be configured."""


# Sets a unique WORKER_CLASS so submitted jobs are pinned to this worker instance.
# Lazily-evaluated global constant.
@cache
def get_worker_class() -> str:
    return f"kde-linux-worker-{uuid.uuid4()}"


def start_worker() -> subprocess.Popen[bytes]:
    """Configures and starts the openQA worker daemon for CI and local worker runs."""

    host = os.environ["OPENQA_HOST_ADDR"]
    api_key = os.environ["OPENQA_API_KEY"]
    api_secret = os.environ["OPENQA_API_SECRET"]
    scheme = os.environ.get("OPENQA_SCHEME", "https")

    # Setting CRITICAL_LOAD_AVG_THRESHOLD might prevent jobs getting stuck in the scheduled
    # state, see https://gitlab.gnome.org/GNOME/openqa-tests/-/work_items/126
    _WORKERS_CONFIG.write_text(
        "[global]\n"
        f"HOST = {scheme}://{host}\n"
        "BACKEND = qemu\n"
        f"WORKER_CLASS = {get_worker_class()}\n"
        "CRITICAL_LOAD_AVG_THRESHOLD = 100\n"
    )

    _CLIENT_CONFIG.write_text(
        f"[{host}]\n"
        f"key = {api_key}\n"
        f"secret = {api_secret}\n"
    )

    context = ssl._create_unverified_context()

    for _ in range(10):
        try:
            with urllib.request.urlopen(
                f"{scheme}://{host}/api/v1/jobs",
                context=context,
            ):
                logger.info("openQA is ready")
                break
        except OSError:
            logger.info("Waiting for openQA… (polling every 2 seconds)")
            time.sleep(2)

    _CACHE_DATABASE.unlink(missing_ok=True)

    # Start the worker with --no-cleanup so it preserves the pool after each job instead of
    # wiping it. install-system's published qcow2 then stays in the pool, and we don't have to
    # re-download it from the server. This isn't great, but the upstream script hardcodes the
    # OpenQA worker's arguments, and we shouldn't be reimplementing their code.
    # Also strip the launcher's hardcoded --verbose so we don't spam CI.
    launcher = _WORKER_LAUNCHER.read_text()
    launcher = launcher.replace(
        "/usr/share/openqa/script/worker ",
        "/usr/share/openqa/script/worker --no-cleanup ",
    )
    launcher = launcher.replace(" --verbose", "")
    _WORKER_LAUNCHER.write_text(launcher)

    if "--no-cleanup" not in launcher:
        raise WorkerConfigurationError(
            "Could not enable --no-cleanup on the openQA worker launcher"
        )

    if os.environ.get("CI") == "true":
        log_path = Path("gitlab-artifacts/worker.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with log_path.open("a") as log:
            return subprocess.Popen(
                [_WORKER_LAUNCHER],
                stdout=log,
                stderr=subprocess.STDOUT,
            )

    return subprocess.Popen([_WORKER_LAUNCHER])
