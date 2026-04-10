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
        if root:
            assert_script_run(f'sudo bash -c {cmdline!r}')
        else:
            assert_script_run(cmdline)
    finally:
        select_console('desktop')
