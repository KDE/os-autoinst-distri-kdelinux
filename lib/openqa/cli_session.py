# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from fabric import Connection
from fabric import config
import testapi

_SSH_HOST = '127.0.0.1'
_SSH_PORT = 2222

def _get_connection() -> Connection:
    return Connection(
        host=_SSH_HOST,
        port=_SSH_PORT,
        user='root',
        connect_kwargs={
            'password': '',
            'look_for_keys': False,
            'allow_agent': False,
        },
    )


class CliSession:
    def __init__(self):
        self._conn: Connection | None = None

    def _ensure_connected(self):
        if self._conn is None or not self._conn.is_connected:
            self._conn = _get_connection()

    def reset(self):
        if self._conn:
            try:
                self._conn.close()
            except EOFError:
                # We can't handshake if the system is shut down!
                # Doesn't matter anyway.
                pass
        self._conn = None

    def run(self, cmdline: str, timeout: int = 90, wait_result: bool = True) -> str | None:
        self._ensure_connected()
        result = self._conn.run(cmdline, timeout=timeout, warn=True, hide=True)
        if result.failed:
            raise RuntimeError(f'Command failed: {cmdline}\n{result.stderr}')
        return result.stdout if wait_result else None

    def get(self, remote: str, local: str):
        self._ensure_connected()
        self._conn.get(remote, local=local)


session = CliSession()
