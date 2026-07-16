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
FDE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upgrade) UPGRADE=1; shift ;;
        --encrypt) FDE=1; shift ;;
        *) echo "[ERROR] Unknown argument: $1" >&2; exit 1 ;;
    esac
done

SYSEXT_IMG="${SYSEXT_IMG:-openqa-sysext.img}"

find_local_iso() {
    find "$CASEDIR" -maxdepth 1 -name '*.iso' -print -quit
}

download_public_image() {
    local image_arg="$1"
    local image_name

    image_name=$(cd "$CASEDIR" && python3 "$CASEDIR/utils/download_image.py" "$image_arg")
    printf '%s/%s\n' "$CASEDIR" "$image_name"
}

download_image_url() {
    local image_url="$1"
    local image_name
    local image_path

    image_name=$(basename "$image_url")
    image_path="$CASEDIR/$image_name"

    echo "[INFO] Downloading image from $image_url..." >&2
    curl -L -o "$image_path" "$image_url"
    printf '%s\n' "$image_path"
}

set_build_from_image_name() {
    local image_name="$1"

    OUTPUT=${image_name%.iso}
    VERSION=${OUTPUT##*_}
}

latest_public_version() {
    local version

    version=$(curl -fsSL "https://storage.kde.org/kde-linux/testing/sysupdate/v2/SHA256SUMS" | sed -nE 's/.*kde-linux_([0-9]{12}).*/\1/p' | head -n1)
    if [[ -z "$version" ]]; then
        echo "[ERROR] Could not determine public version from upstream SHA256SUMS." >&2
        exit 1
    fi

    printf '%s\n' "$version"
}

resolve_build_under_test() {
    IMG_PATH=$(find_local_iso)

    if [[ -z "$IMG_PATH" && "$UPGRADE" -ne 1 ]]; then
        if [[ -n "${IMAGE_URL:-}" ]]; then
            IMG_PATH=$(download_image_url "$IMAGE_URL")
        else
            echo "[INFO] No .iso image found, downloading latest..."
            IMG_PATH=$(download_public_image --latest)
        fi
    fi

    if [[ -n "$IMG_PATH" ]]; then
        set_build_from_image_name "$(basename "$IMG_PATH")"
    elif [[ -n "${IMAGE_URL:-}" ]]; then
        set_build_from_image_name "$(basename "$IMAGE_URL")"
    else
        VERSION=$(latest_public_version)
        OUTPUT="kde-linux_$VERSION"
    fi
}

resolve_install_live() {
    if [[ "$UPGRADE" -ne 1 ]]; then
        INSTALL_LIVE="$IMG_PATH"
        return
    fi

    # The upgrade flow installs an older base, then upgrades it to the build under test.
    # Staged builds should start from the latest published image; published builds should start
    # from the previous one.
    if [[ -n "${STAGING_CHANNEL_URL:-}" ]]; then
        # The build under test is an unpublished staged image so install the latest published image.
        echo "[INFO] Downloading latest published image as the upgrade base..."
        INSTALL_LIVE=$(download_public_image --latest)
    else
        # The build under test is the latest published image, so install the previous one.
        echo "[INFO] Downloading previous image for upgrade test..."
        INSTALL_LIVE=$(download_public_image --previous-image)
    fi
}

resolve_build_under_test
resolve_install_live
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

# The upgrade flow uses install-system and sanity-test as well, so these jobs get their own flavor.
if [[ "$UPGRADE" -eq 1 ]]; then
    LIVE_FLAVOR=live-upgrade
    INSTALLED_FLAVOR=installed-upgrade
else
    LIVE_FLAVOR=live
    INSTALLED_FLAVOR=installed
fi

if [[ "$FDE" -eq 1 ]]; then
    LIVE_FLAVOR+="-encrypted"
    INSTALLED_FLAVOR+="-encrypted"
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
    --build "$VERSION" \
    $( [[ "$FDE" -eq 1 ]] && echo "--encrypt" )

if [[ "$UPGRADE" -eq 1 ]]; then
    run_job \
        --name upgrade-system \
        --flavor "$INSTALLED_FLAVOR" \
        --hdd "$DISK" \
        --sysext "$SYSEXT_IMG" \
        --build "$VERSION" \
        --upgrade \
        $( [[ "$FDE" -eq 1 ]] && echo "--encrypt" )
fi

run_job \
    --name sanity-test \
    --flavor "$INSTALLED_FLAVOR" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION" \
    $( [[ "$FDE" -eq 1 ]] && echo "--encrypt" )

if [[ "$TESTS_FAILED" -ne 0 ]]; then
    echo "[ERROR] One or more jobs had failing tests." >&2
    exit 1
fi
