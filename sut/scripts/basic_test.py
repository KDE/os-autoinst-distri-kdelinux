# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2025 Harald Sitter <sitter@kde.org>
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Checks if the boot has been blessed without any failed units, and returns 1 if not.

import json
import subprocess
import sys
import time
from pathlib import Path

# 1000 is the uid of the live user. always.
BLESS_FILE = Path('/run/user/1000/kde-linux-bless-session')
POLL_INTERVAL = 5
TIMEOUT = 120

elapsed = 0
while elapsed < TIMEOUT:
    if BLESS_FILE.is_file():
        failed = json.loads(subprocess.check_output(['systemctl', '--failed', '--output=json']))
        if failed:
            print('Boot blessed but failed units detected:')
            for unit in failed:
                print(json.dumps(unit))
                try:
                    journal = subprocess.check_output(
                        ['journalctl', '--no-pager', f'_SYSTEMD_UNIT={unit["unit"]}']
                    ).decode()
                    print(journal)
                except Exception as e:
                    print(f'Failed to get journal for {unit["unit"]}: {e}')
            sys.exit(1)
        else:
            print('Boot blessed, no failed units.')
            sys.exit(0)

    time.sleep(POLL_INTERVAL)
    elapsed += POLL_INTERVAL

print(f'Timed out after {TIMEOUT}s waiting for bless file.')
sys.exit(1)
