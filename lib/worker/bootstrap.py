# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import os
import subprocess
import time
from functools import cache
from pathlib import Path

from openqa_client.client import OpenQA_Client
from openqa_client.exceptions import OpenQAClientError

from lib.common.log import get_logger

logger = get_logger(__name__)

_WORKERS_CONFIG = Path("/etc/openqa/workers.ini")
_CLIENT_CONFIG = Path("/etc/openqa/client.conf")
_CACHE_DATABASE = Path("/var/lib/openqa/cache/cache.sqlite")


class WorkerConfigurationError(Exception):
    """Raised when the openQA worker cannot be configured."""


# Sets a unique WORKER_CLASS so submitted jobs are pinned to this worker instance.
# Lazily-evaluated global constant.
@cache
def get_worker_class() -> str:
    return f"kde-linux-worker-{os.environ['CI_RUNNER_SHORT_TOKEN']}"


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

    client = OpenQA_Client(
        server=host,
        scheme=scheme,
        retries=0,
    )
    client.session.verify = False

    for _ in range(10):
        try:
            client.openqa_request("GET", "jobs")
            logger.debug("openQA is ready")
            break
        except OpenQAClientError:
            logger.info("Waiting for openQA… (polling every 2 seconds)")
            time.sleep(2)

    _CACHE_DATABASE.unlink(missing_ok=True)

    # Start the worker with --no-cleanup so it preserves the pool after each job instead of
    # wiping it. install-system's published qcow2 then stays in the pool, and we don't have to
    # re-download it from the server.
    launcher = [
        "/usr/share/openqa/script/worker",
        "--no-cleanup",
        "--instance",
        "1",
    ]

    # Manually strip out virtualenv path before starting worker
    runner_env = os.environ.copy()
    runner_env.pop("VIRTUAL_ENV", None)
    runner_env.pop("VIRTUAL_ENV_PROMPT", None)
    runner_env.pop("PYTHONHOME", None)

    path_parts = runner_env.get("PATH", "").split(os.pathsep)
    clean_path = [p for p in path_parts if "worker-venv" not in p]
    runner_env["PATH"] = os.pathsep.join(clean_path)

    log_path = Path("gitlab-artifacts/worker.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    openqa_dir = Path("/var/lib/openqa")

    with log_path.open("a") as log:
        return subprocess.Popen(
            launcher,
            stdout=log,
            stderr=subprocess.STDOUT,
            env=runner_env,
            cwd=openqa_dir,
        )
