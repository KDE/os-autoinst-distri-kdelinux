# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

from testapi import *

def run(cmdline, root=False):
    # Ensure we're in the terminal
    select_console('virtio-terminal')

    try:
        # TODO don't run this every time
        type_string('export TERM=dumb; unset PROMPT_COMMAND; export PS1="# "; set +o emacs +o vi\n')
        wait_serial(r'#', timeout=30)

        if root:
            # TODO store and use password
            type_string('sudo -i\n')
            wait_serial(r'#', timeout=30)
            type_string('export TERM=dumb; unset PROMPT_COMMAND; export PS1="# "; set +o emacs +o vi\n')
            wait_serial(r'#', timeout=30)

        assert_script_run(cmdline)

    finally:
        if root:
            assert_script_run('exit')

        # Then switch back to the GUI to avoid breaking needle tests
        select_console('desktop')
