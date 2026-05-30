# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib.openqa.cli_session import session
from lib.paths import VENV_DIR, LIB_DIR, RESULTS_DIR
from lib import user_manager
import shlex
import os
import uuid
import functools
import shutil
from pathlib import Path
from testapi import perl

def _cli_command(method):
    @functools.wraps(method)
    def wrapper(self, *args, user: user_manager.User | None = None, **kwargs) -> str:
        cmdline = method(self, *args, **kwargs)
        try:
            output = self._run_transient(cmdline, user=user)
        finally:
            # Collect results even when the test failed; the SUT writes the JUnit XML
            # before exiting non-zero, so we still want to pull it back for reporting.
            self._collect()
        return output
    return wrapper

class CliTest:
    def __init__(self, name: str, artifacts: list[str] | None = None, timeout: int = 90):
        self.name            = name
        self._remote_results = f'{RESULTS_DIR}/{name}/junit.xml'
        self._artifacts      = artifacts or []
        self.timeout         = timeout

    def _run_transient(self, cmdline: str, user: user_manager.User | None = None) -> str:
        unit = f'kde-linux-openqa-{self.name}-{uuid.uuid4().hex[:8]}'
        effective_user = user or user_manager.root()
        safe_cmd = shlex.quote(cmdline)
        base_run = f'systemd-run --unit={unit} --wait --collect '

        if effective_user.name == 'root':
            systemd_run = f'{base_run} bash -lc {safe_cmd}'
        else:
            systemd_run = (
                f'{base_run} --machine=$(id -u {effective_user.name})@.host '
                f'--uid={effective_user.name} --user bash -lc {safe_cmd}'
            )

        try:
            session.run(systemd_run, timeout=self.timeout)
        finally:
            if effective_user.name == 'root':
                journal_cmd = f'journalctl -u {unit} --no-pager -o cat'
            else:
                journal_cmd = f'journalctl _SYSTEMD_USER_UNIT={unit}.service --no-pager -o cat'
            output = session.run(journal_cmd, wait_result=True)
            diag(f'{unit} outputted:\n{output}')

        return output or ''

    @_cli_command
    def run_cmdline(self, cmdline: str) -> str:
        return cmdline

    @_cli_command
    def run_script(self, script_name: str = None, directory: str = None) -> str:
        script_name = script_name or f"{self.name}.sh"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f"{script_path}"

    @_cli_command
    def run_python(self, script_name: str = None, directory: str = None) -> str:
        script_name = script_name or f"{self.name}.py"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f'source {VENV_DIR}/bin/activate && python3 {script_path}'

    @_cli_command
    def run_selenium(self, script_name: str = None, directory: str = None) -> str:
        script_name = script_name or f"{self.name}.py"
        script_path = Path(directory or LIB_DIR) / "tests" / script_name
        return f'source {VENV_DIR}/bin/activate && {LIB_DIR}/openqa-selenium-webdriver-at-spi-run {script_path}'

    def _collect(self):
        try:
            session.run(f'test -f {self._remote_results}', wait_result=False)
            diag(f'JUnit XML exists for {self.name}, collecting...')
            local_results = f'/tmp/junit-{self.name}.xml'
            session.get(self._remote_results, local_results)

            upname = f'{self.name}-results.xml'
            Path('ulogs').mkdir(exist_ok=True)
            shutil.copy(local_results, f'ulogs/{upname}')

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
            diag(f'No JUnit XML for {self.name}, not collecting.')

        for artifact_path in self._artifacts:
            local_artifact = f'/tmp/{self.name}-{os.path.basename(artifact_path)}'
            session.get(artifact_path, local_artifact)
            shutil.copy(local_artifact, f'ulogs/{os.path.basename(local_artifact)}')
