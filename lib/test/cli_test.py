# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

import functools
import os
import shlex
import shutil
import threading
import time
import uuid
from pathlib import Path

from testapi import *
from testapi import perl

from lib.common import user_manager
from lib.common.log import get_logger
from lib.common.paths import LIB_DIR, RESULTS_DIR, VENV_DIR
from lib.test import autoinst_proxy
from lib.test.cli_session import session

log = get_logger(__name__)


def _cli_command(method):
    @functools.wraps(method)
    def wrapper(self, *args, user: user_manager.User | None = None, **kwargs) -> str:
        cmdline = method(self, *args, **kwargs)
        log.info(f"Running {cmdline} on SUT")
        try:
            output = self._run_transient(cmdline, user=user)
        finally:
            # Collect results even when the test failed; the SUT writes the JUnit XML
            # before exiting non-zero, so we still want to pull it back for reporting.
            self._collect()
        return output

    return wrapper


class CliTest:
    def __init__(
        self, name: str, artifacts: list[str] | None = None, timeout: int = 90
    ):
        self.name = name
        self._remote_results = f"{RESULTS_DIR}/{name}/junit.xml"
        self._artifacts = artifacts or []
        self.timeout = timeout
        self.autoinst_proxy = autoinst_proxy.AutoinstProxy()

    def _run_transient(
        self, cmdline: str, user: user_manager.User | None = None
    ) -> str:
        unit = f"kde-linux-openqa-{self.name}-{uuid.uuid4().hex[:8]}"
        effective_user = user or user_manager.root()
        safe_cmd = shlex.quote(cmdline)
        inhibit_cmd = "systemd-inhibit --why=openQA --who=openQA --what=idle "
        base_run = f"systemd-run --unit={unit} --wait --collect "

        if effective_user.name == "root":
            systemd_run = f"{base_run} {inhibit_cmd} bash -lc {safe_cmd}"
        else:
            systemd_run = (
                f"{base_run} --machine=$(id -u {effective_user.name})@.host "
                f"--uid={effective_user.name} --user {inhibit_cmd} bash -lc {safe_cmd}"
            )

        session_exception: RuntimeError | None = None

        def _session_wrapper():
            nonlocal session_exception
            try:
                session.run(systemd_run, self.timeout)
            except RuntimeError as e:
                session_exception = e

        try:
            proxy_thread = threading.Thread(target=self.autoinst_proxy.start_ws)
            proxy_thread.start()
            session_thread = threading.Thread(target=_session_wrapper)
            session_thread.start()
            while session_thread.is_alive():
                self.autoinst_proxy.handle_queue()
                time.sleep(1)

            if session_exception:
                raise session_exception

        finally:
            self.autoinst_proxy.stop()
            proxy_thread.join(1)
            session_thread.join(1)
            if effective_user.name == "root":
                journal_cmd = f"journalctl -u {unit} --no-pager -o cat"
            else:
                journal_cmd = (
                    f"journalctl _SYSTEMD_USER_UNIT={unit}.service --no-pager -o cat"
                )
            output = session.run(journal_cmd, wait_result=True)
            log.info(f"{unit} outputted:\n{output}")

        return output or ""

    @_cli_command
    def run_cmdline(self, cmdline: str) -> str:
        return cmdline

    @_cli_command
    def run_script(
        self, script_name: str | None = None, directory: str | None = None
    ) -> str:
        script_name = script_name or f"{self.name}.sh"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f"{script_path}"

    @_cli_command
    def run_python(
        self, script_name: str | None = None, directory: str | None = None
    ) -> str:
        script_name = script_name or f"{self.name}.py"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f"source {VENV_DIR}/bin/activate && python3 {script_path}"

    @_cli_command
    def run_selenium(
        self,
        script_name: str | None = None,
        directory: str | None = None,
        args: str | None = None,
    ) -> str:
        script_name = script_name or f"{self.name}.py"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f"source {VENV_DIR}/bin/activate && {LIB_DIR}/openqa-selenium-webdriver-at-spi-run {script_path} {args}"

    def _collect(self):
        try:
            session.run(f"test -f {self._remote_results}", wait_result=False)
            log.info(f"JUnit XML exists for {self.name}, collecting...")
            local_results = f"/tmp/junit-{self.name}.xml"
            session.get(self._remote_results, local_results)

            upname = f"{self.name}-results.xml"

            Path("ulogs").mkdir(exist_ok=True)
            shutil.copy2(local_results, Path("ulogs") / upname)

            ci_project_dir = os.environ.get("CI_PROJECT_DIR")
            if ci_project_dir:
                gitlab_artifact_dir = Path(ci_project_dir) / "gitlab-artifacts"
                gitlab_artifact_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(local_results, gitlab_artifact_dir / upname)

            # There's no nice testapi function to do this in python, so we have to call the underlying perl
            perl.eval(f"""
                local @INC = ($ENV{{OPENQA_LIBPATH}} // '/usr/share/openqa/lib', @INC);
                require OpenQA::Parser;
                OpenQA::Parser->import('parser');
                my $parser = parser(JUnit => 'ulogs/{upname}');
                $parser->write_output(bmwqemu::result_dir());
                $parser->write_test_result(bmwqemu::result_dir());
            """)

        except RuntimeError:
            log.info(f"No JUnit XML for {self.name}, not collecting.")

        for artifact_path in self._artifacts:
            local_artifact = f"/tmp/{self.name}-{os.path.basename(artifact_path)}"
            try:
                session.get(artifact_path, local_artifact)
            except FileNotFoundError:
                log.warning(
                    "Artifact %s was not produced by %s",
                    artifact_path,
                    self.name,
                )
                continue
            shutil.copy(local_artifact, f"ulogs/{os.path.basename(local_artifact)}")
