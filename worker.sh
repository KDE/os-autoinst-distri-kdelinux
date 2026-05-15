#!/usr/bin/env bash
set -euo pipefail

# Bootstraps and runs the test suite within an OpenQA server.

# Installs dependencies for running tests
DEPS=(
    python3-requests
    python3-beautifulsoup4
    dos2unix
    vim
    erofs-utils
    python3-fabric
    perl-Inline-Python
)

OS_VERSION=$(. /etc/os-release && echo "$VERSION_ID")
zypper --non-interactive addrepo --refresh \
    "https://download.opensuse.org/repositories/devel:/languages:/perl/openSUSE_Leap_${OS_VERSION}/" \
    devel-languages-perl || true

MISSING=()
for pkg in "${DEPS[@]}"; do
    rpm -q "$pkg" &>/dev/null || MISSING+=("$pkg")
done
[[ ${#MISSING[@]} -gt 0 ]] && zypper --non-interactive --gpg-auto-import-keys install "${MISSING[@]}" || true

export CASEDIR="$(git rev-parse --show-toplevel)"

# Create a mountable image with the bootstrapping sysext
SYSEXT_IMG="openqa-sysext.img"
mkfs.erofs -L "kde-openqa-ext" "$SYSEXT_IMG" "$CASEDIR/extensions/openqa"

# Find and use the .raw live image, move it to local cache dir so we don't pull it from the server
# This needs to be provided from somewhere. In CI, pull it from the previous stage and in mock just
# download it or get it from the base of the directory.
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
# This will be the name of the disk published to OpenQA
DISK=${OUTPUT}.qcow2

# Get the .env file - won't be in CI. The variables will be secrets instead.
if [[ -f .env ]]; then
    set -a
    source .env
    set +a
fi

for var in OPENQA_HOST_ADDR OPENQA_API_KEY OPENQA_API_SECRET OPENQA_SSH_USER; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in environment" >&2
        exit 1
    fi
done

# Put a private key in a Gitlab secret - this is for Gitlab CI
if [[ -n "${OPENQA_SSH_PRIVATE_KEY:-}" ]]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
    echo "$OPENQA_SSH_PRIVATE_KEY" > ~/.ssh/id_ed25519
    chmod 600 ~/.ssh/id_ed25519
fi

# Give ourselves a unique UUID so the called job always runs on the calling worker
export WORKER_CLASS="kde-linux-worker-$(cat /proc/sys/kernel/random/uuid)"

# Autogenerate required files
cat > /etc/openqa/workers.ini <<EOF
[global]
HOST = https://${OPENQA_HOST_ADDR}
BACKEND = qemu
WORKER_CLASS = ${WORKER_CLASS}
EOF

cat > /etc/openqa/client.conf <<EOF
[${OPENQA_HOST_ADDR}]
key = ${OPENQA_API_KEY}
secret = ${OPENQA_API_SECRET}
EOF

# Wait for OpenQA to be ready
for i in {1..10}; do
  if curl -s https://${OPENQA_HOST_ADDR}/api/v1/jobs >/dev/null; then
    echo "[INFO] openQA is ready"
    break
  fi
  echo "[INFO] Waiting for openQA..."
  sleep 3
done

# Clear stale pending entries from previous runs
rm -f /var/lib/openqa/cache/cache.sqlite

# Spin up the worker
/run_openqa_worker.sh &

# Parse arguments
UPGRADE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --upgrade)
            UPGRADE=1
            shift
            ;;
        *)
            echo "[ERROR] Unknown argument: $1" >&2
            exit 1
            ;;
    esac
done

RUN_JOB="$CASEDIR/utils/run_job.sh"

# In upgrade mode, download the previous image to use for install
if [[ "$UPGRADE" -eq 1 ]]; then
    echo "[INFO] Downloading previous image for upgrade test..."
    PREV_IMG_PATH=$(python3 "$CASEDIR/utils/download_image.py" --previous-image)
    INSTALL_LIVE="$PREV_IMG_PATH"
else
    INSTALL_LIVE="$IMG_PATH"
fi

# Job 1: Install the system from live image
bash "$RUN_JOB" \
    --name install-system \
    --live "$INSTALL_LIVE" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"

# Job 2 (optional): Upgrade the installed system
if [[ "$UPGRADE" -eq 1 ]]; then
    bash "$RUN_JOB" \
        --name upgrade-system \
        --hdd "$DISK" \
        --sysext "$SYSEXT_IMG" \
        --build "$VERSION" \
        --upgrade
fi

# Job 2/3: Sanity test the final system
bash "$RUN_JOB" \
    --name sanity-test \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$BUILD"
