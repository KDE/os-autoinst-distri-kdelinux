# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *
from lib import user_manager
import base64

_SHELL_INIT = 'export TERM=dumb; unset PROMPT_COMMAND; unsetopt zle 2>/dev/null; set +o emacs +o vi 2>/dev/null; export PS1="# "\n'
_PROMPT     = r'# '

class SerialSession:
    """Manages a single virtio-terminal session, tracking the logged-in user"""

    def __init__(self):
        self._user:  user_manager.User | None = None
        self._ready: bool = False

    def _ensure_ready(self):
        select_console('virtio-terminal')
        if not self._ready:
            type_string(_SHELL_INIT)
            wait_serial(_PROMPT, timeout=30)
            self._ready = True

    def reset(self):
        """Resets state to logged out - call after machine power actions"""
        self._ready = False
        self._user  = None

    def login(self, target: user_manager.User):
        """Log in or switch to another user"""
        if self._user is not None and target.name == self._user.name:
            return

        select_console('virtio-terminal')

        if self._user is None:
            type_string('\n')
            wait_serial(r'login: ', timeout=30)
            type_string(target.name + '\n')
            if target.pw:
                wait_serial(r'[Pp]assword: ', timeout=10)
                type_string(target.pw + '\n')
        elif target.name == 'root':
            self._ensure_ready()
            type_string('sudo -i\n')
        elif self._user.name == 'root':
            self._ensure_ready()
            type_string(f'su - {target.name}\n')
        else:
            self._ensure_ready()
            type_string('sudo -i\n')
            wait_serial(_PROMPT, timeout=15)
            type_string(f'su - {target.name}\n')

        wait_serial(r'[~$#]', timeout=30)
        self._user  = target
        self._ready = False
        type_string('\n')   # confirm shell is responding
        wait_serial(r'[~$#]', timeout=10)
        self._ensure_ready()

    def run(self, cmdline: str, user: user_manager.User | None = None) -> str:
        """Run a command in a transient systemd unit, optionally as a specific user"""
        if self._user is None:
            raise RuntimeError("No user logged in - call login() first")

        effective_user = user if user is not None else self._user
        self._ensure_ready()
        try:
            if effective_user.name == 'root':
                full_cmd = f'systemd-run --pipe --wait --collect bash -c {cmdline!r}'
            else:
                uid_expr = f'$(id -u {effective_user.name})'
                full_cmd = (
                    f'systemd-run --machine={uid_expr}@.host '
                    f'--uid={effective_user.name} --user '
                    f'--pipe --wait --collect bash -lc {cmdline!r}'
                )
            type_string(full_cmd + '\n')

            if effective_user.pw:
                wait_serial(r'Password: ', timeout=10)
                type_string(effective_user.pw + '\n')
            return wait_serial(_PROMPT, timeout=30)

        finally:
            select_console('desktop')
            self._ready = False

session = SerialSession()

class SerialTest:
    """Runs tests inside the SUT and collects JUnit XML and optional artifacts for OpenQA"""

    RESULTS_DIR = '/tests/sut/openqa-junit-results'
    SENTINEL    = 'JUNIT_BEGIN'

    def __init__(self, name: str, artifacts: list[str] | None = None):
        self.name            = name
        self._remote_results = f'{self.RESULTS_DIR}/{name}-results.xml'
        self._artifacts      = artifacts or []

    def run_cmd(self, cmdline: str, user: user_manager.User | None = None):
        """Run an arbitrary command."""
        session.run(cmdline, user=user)
        self._collect()

    def run_selenium(self, script_path: str, user: user_manager.User | None = None):
        """Run a selenium-webdriver-at-spi unittest file with xmlrunner"""
        session.run(f'/tests/sut/openqa-selenium-webdriver-at-spi-run {script_path}', user=user)
        self._collect()

    def _collect_file(self, remote_path: str, host_path: str):
        """Pull a file from SUT over serial via base64"""
        raw = session.run(
            f'echo {self.SENTINEL} && base64 -w0 {remote_path} && echo JUNIT_END'
        )
        lines = raw.splitlines()
        start = next(i for i, l in enumerate(lines) if 'JUNIT_BEGIN' in l)
        end   = next(i for i, l in enumerate(lines) if 'JUNIT_END' in l)
        b64   = ''.join(l.strip() for l in lines[start+1:end])
        data  = base64.b64decode(b64)
        with open(host_path, 'wb') as f:
            f.write(data)

    def _collect(self):
        """Pull JUnit XML and artifacts from SUT and report to OpenQA"""
        host_path = f'/tmp/{self.name}-results.xml'

        # junit XML is optional, some tests don't need it
        result = session.run(f'test -f {self._remote_results} && echo exists || echo missing')
        if 'exists' in result:
            self._collect_file(self._remote_results, host_path)
            parse_junit_log(host_path)
            upload_logs(host_path)

        # artifacts are explicitly listed so failure to collect them is an error
        for artifact_path in self._artifacts:
            artifact_name = artifact_path.split('/')[-1]
            host_artifact = f'/tmp/{artifact_name}'
            self._collect_file(artifact_path, host_artifact)
            upload_logs(host_artifact)
