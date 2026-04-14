# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

_SHELL_INIT = 'export TERM=dumb; unset PROMPT_COMMAND; unsetopt zle 2>/dev/null; set +o emacs +o vi 2>/dev/null; export PS1="# "\n'
_PROMPT = r'# '

_console_ready = False

def _ensure_console_ready():
    global _console_ready
    select_console('virtio-terminal')
    if not _console_ready:
        type_string(_SHELL_INIT)
        wait_serial(_PROMPT, timeout=30)
        _console_ready = True

def run(cmdline, root=False):
    _ensure_console_ready()
    try:
        # Run a transient service in the user's current session
        if root:
            full_cmd = f'systemd-run --pipe --wait --collect bash -c {cmdline!r}'
        else:
            # Then get all their desktop vars to pass into it
            full_cmd = (
                f'eval $(systemctl --user show-environment | '
                f'grep -E "^(DISPLAY|WAYLAND_DISPLAY|DBUS_SESSION_BUS_ADDRESS|XDG_RUNTIME_DIR)=" | '
                f'sed \'s/^/export /\') && '
                f'systemd-run --pipe --user --wait --collect '
                f'--setenv=DISPLAY=$DISPLAY '
                f'--setenv=WAYLAND_DISPLAY=$WAYLAND_DISPLAY '
                f'--setenv=DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS '
                f'--setenv=XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR '
                f'bash -c {cmdline!r}'
            )

        assert_script_run(full_cmd)
    finally:
        select_console('desktop')
