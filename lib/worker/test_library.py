# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

import shutil
from pathlib import Path

from lib.worker.test_manifest import Manifest


def stage_libraries(
    destination: Path, manifest: Manifest, *, repo_root: Path
) -> None:
    """Merge lib/ in this repo with extensions added downstream."""
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(repo_root / "lib", destination, dirs_exist_ok=True, ignore=ignore)

    project = manifest.test_root / "lib"
    if project.is_dir():
        shutil.copytree(project, destination, dirs_exist_ok=True, ignore=ignore)
