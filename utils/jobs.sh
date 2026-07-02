#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

# Submits and polls all test jobs for a build.

if [[ -z "${CASEDIR:-}" ]]; then
    echo "[ERROR] CASEDIR is not set. Wait until the worker has fully initialised itself before entering this shell." >&2
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
IMG_PATH=$(find "$CASEDIR" -maxdepth 1 -name '*.iso' | head -n1)
if [[ -z "$IMG_PATH" && "$UPGRADE" -ne 1 ]]; then
    echo "[ERROR] No .iso image found in $CASEDIR" >&2
    exit 1
fi

if [[ -n "$IMG_PATH" ]]; then
    IMG=$(basename "$IMG_PATH")
    OUTPUT=${IMG%.iso}
    VERSION=${OUTPUT##*_}
else
    if [[ -z "${IMAGE_URL:-}" ]]; then
        echo "[ERROR] Upgrade jobs without a local .iso require IMAGE_URL for the build label." >&2
        exit 1
    fi
    IMG=$(basename "$IMAGE_URL")
    OUTPUT=${IMG%.iso}
    VERSION=${OUTPUT##*_}
fi
DISK=${OUTPUT}.qcow2

# Copy test cases to the directory where openQA expects so that needle editor works
if [[ -n "${MOCK_MODE:-}" ]]; then
    mkdir -p /var/lib/openqa/tests/kde-linux
    rsync -a --delete --exclude '*.iso' --exclude '*.img' "$CASEDIR"/* /var/lib/openqa/tests/kde-linux
    chown -R geekotest:geekotest /var/lib/openqa/tests/kde-linux
fi

# Chain each job onto the previous one, so we get a nice dependency graph.
# retcode 0 = passed, retcode 2 = non-fatal tests failed
# Everything else is a fatal failure, so fail fast.
# Created job id is emitted through fd 3 and stdout goes into fd 4 so PARENT doesn't
# eat the logs. A bit of weird plumbing.
TESTS_FAILED=0
PARENT=
exec 4>&1
run_job() {
    local retcode=0
    PARENT=$(bash "$CASEDIR"/utils/run_job.sh "$@" --group "$GROUP" --after "$PARENT" 3>&1 1>&4) || retcode=$?
    case "$retcode" in
        0) ;;
        2) TESTS_FAILED=1 ;;
        *) exit "$retcode" ;;
    esac
}

if [[ "$UPGRADE" -eq 1 ]]; then
    # The upgrade flow installs an older base, then upgrades it to the build under test.
    # Hence, if we have an image staged, we CANNOT be using that same one as the installed image
    # which will be upgraded from our staging repo.
    # We also shouldn't be using some older image, we should be using the latest publicly available
    # image as the upgrade base, since we're testing incremental upgrades.
    if [[ "${USE_LATEST_IMAGE_UPGRADE:-0}" -eq 1 ]]; then
        # The build under test is an unpublished staged image so install the latest published image.
        echo "[INFO] Downloading latest published image as the upgrade base..."
        INSTALL_LIVE=$(python3 "$CASEDIR/utils/download_image.py" --latest)
    else
        # The build under test is the latest published image, so install the previous one.
        echo "[INFO] Downloading previous image for upgrade test..."
        INSTALL_LIVE=$(python3 "$CASEDIR/utils/download_image.py" --previous-image)
    fi
else
    INSTALL_LIVE="$IMG_PATH"
fi

# The upgrade flow uses install-system and sanity-test as well, so these jobs get their own flavor.
if [[ "$UPGRADE" -eq 1 ]]; then
    LIVE_FLAVOR=live-upgrade
    INSTALLED_FLAVOR=installed-upgrade
else
    LIVE_FLAVOR=live
    INSTALLED_FLAVOR=installed
fi

# Put the whole flow in its own job group so each flow gets its own build overview,
# and the dependency chain stays within one group. Mock doesn't have any groups, so don't set it here.
GROUP=
if [[ -z "${MOCK_MODE:-}" ]]; then
    if [[ "$UPGRADE" -eq 1 ]]; then
        GROUP="KDE Linux Upgrade"
    else
        GROUP="KDE Linux Installation"
    fi
fi

# In a mock single-instance container, comment out any of the below test jobs you don't want to run if you aim to test a specific one.
# Then you'll be able to run utils/jobs.sh in the shell that you get dropped into after the single-instance test suites are done.
# The install job will at least have to have run before you're able to do this. This will happen on first mock container run.
run_job \
    --name install-system \
    --flavor "$LIVE_FLAVOR" \
    --live "$INSTALL_LIVE" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"

if [[ "$UPGRADE" -eq 1 ]]; then
    run_job \
        --name upgrade-system \
        --flavor "$INSTALLED_FLAVOR" \
        --hdd "$DISK" \
        --sysext "$SYSEXT_IMG" \
        --build "$VERSION" \
        --upgrade
fi

run_job \
    --name sanity-test \
    --flavor "$INSTALLED_FLAVOR" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"

if [[ "$TESTS_FAILED" -ne 0 ]]; then
    echo "[ERROR] One or more jobs had failing tests." >&2
    exit 1
fi
