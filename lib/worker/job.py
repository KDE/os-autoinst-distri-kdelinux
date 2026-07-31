# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import os
from lib.common.log import get_logger


logger = get_logger(__name__)

_OPENQA_SHARE_PATH = Path("/var/lib/openqa/share/factory/hdd")
_OPENQA_POOL_PATH = Path("/var/lib/openqa/pool")
_PFLASH_PATH = Path("/usr/share/qemu/ovmf-x86_64-4m-vars.bin")
_PFLASH_OVERLAY_PATH = (
    _OPENQA_POOL_PATH / "1" / "raid" / "pflash-vars-overlay0"
)
_PFLASH_TEMP_PATH = Path("/tmp/pflash-vars-overlay0")

_POLL_SECONDS = 5
_SCHEDULED_TIMEOUT = 30

_TERMINAL_RESULTS = {
    "passed",
    "softfailed",
    "failed",
    "incomplete",
    "timeout",
    "user_cancelled",
    "obsoleted",
    "cancelled",
    "skipped",
}


class InvalidJobError(Exception):
    """Raised when an openQA job is invalid."""


@dataclass(frozen=True)
class JobSuccess:
    result: str


@dataclass(frozen=True)
class JobNonFatalFailure:
    reason: str


@dataclass(frozen=True)
class JobFatalFailure:
    reason: str


type JobResult = JobSuccess | JobNonFatalFailure | JobFatalFailure


@dataclass(frozen=True)
class JobConfig:
    hdd: Path
    sysext: Path
    build: str
    name: str
    flavor: str
    casedir: Path
    live: Path | None = None
    group: str | None = None
    after: int | None = None
    worker_class: str | None = None
    upgrade: bool = False
    encrypt: bool = False

    def __post_init__(self) -> None:
        if self.live is not None and self.upgrade:
            raise InvalidJobError(
                "Live installation and upgrade are mutually exclusive"
            )


class OpenQAClient:
    def __init__(self, host: str, scheme: str = "https") -> None:
        self.host = host
        self.scheme = scheme

    def request(self, *args: str) -> dict[str, Any]:
        logger.debug("Running openQA API request: %s", " ".join(args))

        result = subprocess.run(
            [
                "openqa-cli",
                "api",
                "--host",
                f"{self.scheme}://{self.host}",
                *args,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        response = json.loads(result.stdout)

        if not isinstance(response, dict):
            raise InvalidJobError("openQA returned an invalid response")

        return response


class Job:
    def __init__(self, client: OpenQAClient, config: JobConfig) -> None:
        self.client = client
        self.config = config
        self._job_id: int | None = None

    @property
    def job_id(self) -> int:
        if self._job_id is None:
            raise InvalidJobError("Job has not been submitted")

        return self._job_id

    @property
    def web_url(self) -> str:
        host = self.client.host

        if host == "localhost":
            host = "localhost:1080"

        return f"{self.client.scheme}://{host}/tests/{self.job_id}"

    def run(self) -> JobResult:
        logger.info("Running test job %s", self.config.name)

        if self.config.live is not None:
            self._stage_asset(self.config.live)
            self._stage_asset(_PFLASH_PATH)
        else:
            self._stage_asset(self.config.hdd)

        self._stage_asset(self.config.sysext)

        self.submit()
        result = self.poll_until_finished()

        if not isinstance(result, JobFatalFailure):
            if self.config.live is not None or self.config.upgrade:
                self._produce_installed_hdd()
                self._produce_pflash_vars()

            clean_pool()

        return result

    def submit(self) -> int:
        response = self.client.request(
            "-X",
            "POST",
            "jobs",
            *(
                f"{key}={value}"
                for key, value in self._submission_settings().items()
            ),
        )

        logger.debug("Job creation response: %s", response)

        job_id = response.get("id")

        if not isinstance(job_id, int):
            raise InvalidJobError(
                f"Job creation returned an invalid ID: {job_id!r}"
            )

        self._job_id = job_id
        logger.info("Submitted job %s", job_id)

        return job_id

    def poll_until_finished(self) -> JobResult:
        logger.info("Polling job %s for its result", self.job_id)
        logger.message(
            "View the running %s job at %s",
            self.config.name,
            self.web_url,
        )

        previous_state: str | None = None
        previous_result: str | None = None
        scheduled_since: float | None = None

        while True:
            response = self.client.request(f"jobs/{self.job_id}")
            job_data = response.get("job")

            if not isinstance(job_data, dict):
                raise InvalidJobError(
                    "openQA job response contains no job object"
                )

            state = job_data.get("state")
            result = job_data.get("result")

            if not isinstance(state, str) or not isinstance(result, str):
                raise InvalidJobError(
                    "openQA returned an invalid job state or result"
                )

            if state != previous_state or result != previous_result:
                logger.info(
                    "Job state changed to %s; result changed to %s",
                    state,
                    result,
                )
                previous_state = state
                previous_result = result

            if result in _TERMINAL_RESULTS:
                break

            if state == "scheduled":
                if scheduled_since is None:
                    scheduled_since = time.monotonic()
                elif time.monotonic() - scheduled_since > _SCHEDULED_TIMEOUT:
                    return JobFatalFailure(
                        f"job {self.job_id} stayed scheduled for over "
                        f"{_SCHEDULED_TIMEOUT} seconds"
                    )
            else:
                scheduled_since = None

            time.sleep(_POLL_SECONDS)

        if result in {"passed", "softfailed"}:
            logger.success(
                "Job %s completed with result %s",
                self.job_id,
                result,
            )
            return JobSuccess(result)

        if result != "failed":
            return JobFatalFailure(
                f"job {self.job_id} ended with unexpected result {result}"
            )

        return self._classify_failed_job()

    def _classify_failed_job(self) -> JobResult:
        response = self.client.request(f"jobs/{self.job_id}/details")
        job_data = response.get("job")

        if not isinstance(job_data, dict):
            raise InvalidJobError(
                "openQA details response contains no job object"
            )

        test_results = job_data.get("testresults")

        if not isinstance(test_results, list):
            raise InvalidJobError(
                "openQA details response contains no test results"
            )

        fatal_modules = [
            result["name"]
            for result in test_results
            if isinstance(result, dict)
            and result.get("result") == "failed"
            and result.get("fatal") == 1
            and isinstance(result.get("name"), str)
        ]

        if fatal_modules:
            reason = (
                f"Job {self.job_id} aborted; fatal modules failed: "
                + ", ".join(fatal_modules)
            )
            logger.error(reason)
            return JobFatalFailure(reason)

        reason = (
            f"job {self.job_id} failed; no fatal modules were involved"
        )
        logger.warning(reason)

        return JobNonFatalFailure(reason)

    def _submission_settings(self) -> dict[str, str]:
        config = self.config

        settings = {
            "DISTRI": "KDE-Linux",
            "VERSION": config.build,
            "FLAVOR": config.flavor,
            "ARCH": "x86_64",
            "BUILD": config.build,
            "TEST": config.name,
            "MACHINE": "general_64bit",
            "HDD_2": config.sysext.name,
            "BOOT_HDD_IMAGE": "1",
            "BACKEND": "qemu",
            "UEFI": "1",
            "UEFI_PFLASH_CODE": (
                "/usr/share/qemu/ovmf-x86_64-4m-code.bin"
            ),
            "UEFI_PFLASH_VARS": (
                _PFLASH_PATH.name
            ),
            "QEMUCPUS": "4",
            "QEMURAM": "4096",
            "QEMUCPU": "host",
            "CASEDIR": str(config.casedir),
            "NEEDLES_DIR": "%%CASEDIR%%/needles",
            "TIMEOUT_SCALE": "3",
            "VIRTIO_CONSOLE": "1",
            "NICTYPE_USER_OPTIONS": "hostfwd=tcp::2222-:22",
        }

        if config.live is not None:
            settings.update(
                {
                    "HDD_3": config.live.name,
                    "DO_INSTALL": "1",
                    "HDDSIZEGB": "30",
                    "NUMDISKS": "3",
                }
            )
        else:
            settings.update(
                {
                    "HDD_1": config.hdd.name,
                    "NUMDISKS": "2",
                }
            )

        if config.upgrade:
            settings["DO_UPGRADE"] = "1"

        if config.encrypt:
            settings["FDE_INSTALL"] = "1"

        if config.after is not None:
            settings["_START_AFTER_JOBS"] = str(config.after)

        if config.group is not None:
            settings["_GROUP"] = config.group

        if not os.environ.get("MOCK_MODE") and config.worker_class is not None:
            # No point setting a worker class in mock mode - just schedule
            # to the only worker there is.
            settings["WORKER_CLASS"] = config.worker_class

        return settings

    def _stage_asset(self, path: Path) -> None:
        if not path.is_file():
            logger.info(
                "%s is already in the worker share, skipping staging",
                path.name,
            )
            return

        _OPENQA_SHARE_PATH.mkdir(parents=True, exist_ok=True)
        shutil.copy(path, _OPENQA_SHARE_PATH / path.name)

        logger.info("Staged %s into the worker share", path.name)

    def _produce_installed_hdd(self) -> None:
        pool_disk = next(
            _OPENQA_POOL_PATH.glob("*/raid/hd0*"),
            None,
        )

        if pool_disk is None:
            raise InvalidJobError(
                "Install target disk was not found in the worker pool"
            )

        destination = _OPENQA_SHARE_PATH / self.config.hdd.name
        _OPENQA_SHARE_PATH.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Flattening installed disk %s into %s",
            pool_disk,
            destination,
        )

        if pool_disk.name == "hd0-overlay0":
            subprocess.run(
                ["qemu-img", "commit", pool_disk],
                check=True,
            )
        else:
            subprocess.run(
                [
                    "qemu-img",
                    "convert",
                    "-O",
                    "qcow2",
                    pool_disk,
                    destination,
                ],
                check=True,
            )

    def _produce_pflash_vars(self) -> None:
        pflash_factory = _OPENQA_SHARE_PATH / _PFLASH_PATH.name

        logger.info(
            "Updating %s for the next job",
            pflash_factory,
        )

        subprocess.run(
            [
                "qemu-img",
                "convert",
                "-f",
                "qcow2",
                "-O",
                "raw",
                _PFLASH_OVERLAY_PATH,
                _PFLASH_TEMP_PATH,
            ],
            check=True,
        )
        _PFLASH_TEMP_PATH.replace(pflash_factory)


def clean_pool() -> None:
    logger.info("Cleaning openQA worker pool")

    if not _OPENQA_POOL_PATH.is_dir():
        logger.info("openQA worker pool does not exist")
        return

    removed = 0

    try:
        for worker_pool in _OPENQA_POOL_PATH.iterdir():
            if not worker_pool.is_dir() or worker_pool.is_symlink():
                continue

            for entry in worker_pool.iterdir():
                if entry.is_dir() and not entry.is_symlink():
                    shutil.rmtree(entry)
                else:
                    entry.unlink()

                removed += 1
    except OSError as error:
        raise OSError(
            f"Could not clean openQA worker pool: {error}"
        ) from error

    logger.info("Removed %d entries from the openQA worker pool", removed)
