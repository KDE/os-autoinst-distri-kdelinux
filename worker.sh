#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -eo pipefail

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
    gpg2
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

# Build the openqa sysext for the SUT.
# The top-level files in ./lib are shared between the host and the SUT, so copy them in at sysext build time.
# These are in .gitignore.
SYSEXT_LIB="$CASEDIR/extensions/openqa/usr/lib/kde-linux-openqa/lib"
mkdir -p "$SYSEXT_LIB"
find -L "$CASEDIR/lib" -maxdepth 1 -type f -exec cp -f {} "$SYSEXT_LIB/" \;

# Clean up before creating the sysext.
if [[ -z "${STAGING_CHANNEL_URL:-}" && -d "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/" ]]; then
    # If we haven't been passed a URL, clean up any dropins that may point to one from a previous run.
    rm -rf "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/"
fi
if [[ -z "${SYSUPDATE_PUBKEY_B64:-}" && -f "$CASEDIR/extensions/openqa/usr/lib/systemd/import-pubring.pgp" ]]; then
    # If we haven't been passed a signing key, clean up any that exist from a previous run.
    rm -f "$CASEDIR/extensions/openqa/usr/lib/systemd/import-pubring.pgp"
fi

if [[ -n "${STAGING_CHANNEL_URL:-}" ]]; then
    # Create sysupdate.d dropins to redirect updates to our staged S3 image in CI.
    mkdir -p "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/50-root-x86-64-caibx.transfer.d/"
    mkdir -p "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/50-root-x86-64-erofs.transfer.d/"
    mkdir -p "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/60-esp.transfer.d/"

    tee "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/50-root-x86-64-caibx.transfer.d/99-openqa-override.conf" \
        "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/50-root-x86-64-erofs.transfer.d/99-openqa-override.conf" \
        "$CASEDIR/extensions/openqa/usr/lib/sysupdate.d/60-esp.transfer.d/99-openqa-override.conf" > /dev/null <<EOF
[Source]
Path=${STAGING_CHANNEL_URL}
EOF
    # Give it an ephemeral signing key, generated in CI, so it can verify updates from a staging channel outside of master upstream.
    if [[ -n "${SYSUPDATE_PUBKEY_B64:-}" ]]; then
        mkdir -p "$CASEDIR/extensions/openqa/usr/lib/systemd"
        echo "$SYSUPDATE_PUBKEY_B64" | base64 -d | gpg --dearmor > "$CASEDIR/extensions/openqa/usr/lib/systemd/import-pubring.pgp"
    fi
fi

export SYSEXT_IMG="openqa-sysext.img"
mkfs.erofs --quiet -L "kde-openqa-ext" "$SYSEXT_IMG" "$CASEDIR/extensions/openqa"

# Check if all the required environment variables exist outside of a single-instance mock, where they aren't required
required_vars=(OPENQA_HOST_ADDR)
[[ -z "${MOCK_MODE:-}" ]] && required_vars+=(OPENQA_API_KEY OPENQA_API_SECRET)
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in environment" >&2
        exit 1
    fi
done

# In the single-instance mock users should submit jobs themselves.
if [[ -n "${MOCK_MODE:-}" ]]; then
    exit 0
fi

# Run test jobs
if [[ "$UPGRADE" -eq 1 ]]; then
    bash "$CASEDIR/utils/jobs.sh" --upgrade
else
    bash "$CASEDIR/utils/jobs.sh"
fi
