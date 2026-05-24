#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

# Parse cmdline to see if we're doing an upgrade job
UPGRADE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upgrade) UPGRADE=1; shift ;;
        *) echo "[ERROR] Unknown argument: $1" >&2; exit 1 ;;
    esac
done

# Set the casedir to the git repo
export CASEDIR="$(git rev-parse --show-toplevel)"

# Get environment variables
if [[ -z "${MOCK_MODE:-}" && -f "$CASEDIR/.env" ]]; then
    set -a
    source "$CASEDIR/.env"
    set +a
fi

# Bootstrap the worker's configuration if we aren't in a mock environment where this is already done
if [[ -z "${MOCK_MODE:-}" ]]; then
    source "$CASEDIR/utils/bootstrap-worker.sh"
fi

# Install dependencies for the worker to run jobs
DEPS=(
    python3-requests
    python3-beautifulsoup4
    dos2unix
    vim
    erofs-utils
    python3-fabric
    perl-Inline-Python
)

if [[ -z "${MOCK_MODE:-}" ]]; then
    OS_VERSION=$(. /etc/os-release && echo "$VERSION_ID")
    zypper --non-interactive addrepo --refresh \
        "https://download.opensuse.org/repositories/devel:/languages:/perl/openSUSE_Leap_${OS_VERSION}/" \
        devel-languages-perl || true
else
    # The single-instance bootstrap installs os-autoinst-distri-opensuse-deps which adds this Leap repo
    zypper removerepo devel-languages-perl 2>/dev/null || true
fi

MISSING=()
for pkg in "${DEPS[@]}"; do
    rpm -q "$pkg" &>/dev/null || MISSING+=("$pkg")
done
[[ ${#MISSING[@]} -gt 0 ]] && zypper --non-interactive --gpg-auto-import-keys install "${MISSING[@]}" || true

# Build the openqa sysext for the SUT
SYSEXT_IMG="openqa-sysext.img"
mkfs.erofs -L "kde-openqa-ext" "$SYSEXT_IMG" "$CASEDIR/extensions/openqa"

# Download and set up .raw live image
IMG_PATH=$(find "$CASEDIR" -maxdepth 1 -name '*.raw' | head -n1)
if [[ -z "$IMG_PATH" ]]; then
    if [[ -n "${IMAGE_URL:-}" ]]; then
        echo "[INFO] Downloading image from $IMAGE_URL..."
        IMG_PATH="$CASEDIR/$(basename "$IMAGE_URL")"
        curl -L -o "$IMG_PATH" "$IMAGE_URL"
    else
        echo "[INFO] No .raw image found, downloading latest..."
        IMG_PATH=$(python3 "$CASEDIR/utils/download_image.py" --latest)
    fi
fi
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2

# Check if all the required environment variables exist outside of a single-instance mock, where they aren't required
required_vars=(OPENQA_HOST_ADDR OPENQA_SSH_USER)
[[ -z "${MOCK_MODE:-}" ]] && required_vars+=(OPENQA_API_KEY OPENQA_API_SECRET OPENQA_SSH_PRIVATE_KEY)
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in environment" >&2
        exit 1
    fi
done

# Register the SSH private key for sftp
if [[ -n "${OPENQA_SSH_PRIVATE_KEY:-}" ]]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "$OPENQA_SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
    chmod 600 ~/.ssh/id_ed25519
fi

# Run test jobs
RUN_JOB="$CASEDIR/utils/run_job.sh"

if [[ "$UPGRADE" -eq 1 ]]; then
    # If we're doing an upgrade job, download the previously-published image
    echo "[INFO] Downloading previous image for upgrade test..."
    PREV_IMG_PATH=$(python3 "$CASEDIR/utils/download_image.py" --previous-image)
    INSTALL_LIVE="$PREV_IMG_PATH"
else
    INSTALL_LIVE="$IMG_PATH"
fi

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
