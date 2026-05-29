#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

# Submits and polls all test jobs for a build.

if [[ -z "${CASEDIR:-}" ]]; then
    echo "[ERROR] CASEDIR is not set; run from a worker shell or source worker.sh first" >&2
    exit 1
fi

UPGRADE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upgrade) UPGRADE=1; shift ;;
        *) echo "[ERROR] Unknown argument: $1" >&2; exit 1 ;;
    esac
done

SYSEXT_IMG="openqa-sysext.img"
IMG_PATH=$(find "$CASEDIR" -maxdepth 1 -name '*.raw' | head -n1)
if [[ -z "$IMG_PATH" ]]; then
    echo "[ERROR] No .raw image found in $CASEDIR" >&2
    exit 1
fi
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2

RUN_JOB="$CASEDIR/utils/run_job.sh"

if [[ "$UPGRADE" -eq 1 ]]; then
    echo "[INFO] Downloading previous image for upgrade test..."
    PREV_IMG_PATH=$(python3 "$CASEDIR/utils/download_image.py" --previous-image)
    INSTALL_LIVE="$PREV_IMG_PATH"
else
    INSTALL_LIVE="$IMG_PATH"
fi

# In a mock single-instance container, comment out any of the below test jobs you don't want to run if you aim to test a specific one.
# Then you'll be able to run utils/jobs.sh in the shell that you get dropped into after the single-instance test suites are done.
# The install job will at least have to have run before you're able to do this. This will happen on first mock container run.
bash "$RUN_JOB" \
    --name install-system \
    --live "$INSTALL_LIVE" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"

if [[ "$UPGRADE" -eq 1 ]]; then
    bash "$RUN_JOB" \
        --name upgrade-system \
        --hdd "$DISK" \
        --sysext "$SYSEXT_IMG" \
        --build "$VERSION" \
        --upgrade
fi

bash "$RUN_JOB" \
    --name sanity-test \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"
