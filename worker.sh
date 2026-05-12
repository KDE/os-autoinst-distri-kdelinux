#!/usr/bin/env bash
set -euo pipefail

# Bootstraps and runs the test suite within an OpenQA server.

# Installs dependencies for running tests
DEPS=(
#    perl-inline-Python
    python3-requests
    python3-beautifulsoup4
    dos2unix
    vim
    erofs-utils
    python3-fabric
)
zypper --non-interactive install "${DEPS[@]}" || true

export CASEDIR="$(git rev-parse --show-toplevel)"

# Create a mountable image with the bootstrapping sysext
SYSEXT_IMG="openqa-sysext.img"
mkfs.erofs -L "kde-openqa-ext" "$SYSEXT_IMG" "$CASEDIR/extensions/openqa"

# Find and use the .raw live image, move it to local cache dir so we don't pull it from the server
# This needs to be provided from somewhere. In CI, pull it from the previous stage and in mock just
# download it or get it from the base of the directory.
IMG_PATH=$(find "$CASEDIR" -maxdepth 1 -name '*.raw' | head -n1)
if [[ -z "$IMG_PATH" ]]; then
    echo "[INFO] No .raw image found, downloading latest..."
    IMG_PATH=$(python3 "$CASEDIR/utils/download_image.py" --latest)
fi
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
# This will be the name of the disk published to OpenQA
DISK=${OUTPUT}.qcow2

# Get the .env file
set -a
source .env
set +a

for var in OPENQA_HOST_ADDR OPENQA_API_KEY OPENQA_API_SECRET; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in .env" >&2
        exit 1
    fi
done

# Give ourselves a unique UUID so the called job always runs on the calling worker
export WORKER_CLASS="kde-linux-worker-$(cat /proc/sys/kernel/random/uuid)"

# Autogenerate required files
cat > /etc/openqa/workers.ini <<EOF
[global]
HOST = https://${OPENQA_HOST_ADDR}:${OPENQA_HOST_PORT}
BACKEND = qemu
WORKER_CLASS = ${WORKER_CLASS}
EOF

cat > /etc/openqa/client.conf <<EOF
[${OPENQA_HOST_ADDR}:${OPENQA_HOST_PORT}]
key = ${OPENQA_API_KEY}
secret = ${OPENQA_API_SECRET}
EOF

# Wait for OpenQA to be ready
for i in {1..10}; do
  if curl -s https://${OPENQA_HOST_ADDR}:${OPENQA_HOST_PORT}/api/v1/jobs >/dev/null; then
    echo "[INFO] openQA is ready"
    break
  fi
  echo "[INFO] Waiting for openQA..."
  sleep 3
done


# Spin up the actual worker instance
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
echo "[INFO] Running install-system job..."
bash "$RUN_JOB" \
    --name install-system \
    --live "$INSTALL_LIVE" \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$VERSION"

# Job 2 (optional): Upgrade the installed system
if [[ "$UPGRADE" -eq 1 ]]; then
    echo "[INFO] Running upgrade-system job..."
    bash "$RUN_JOB" \
        --name upgrade-system \
        --hdd "$DISK" \
        --sysext "$SYSEXT_IMG" \
        --build "$VERSION" \
        --upgrade
fi

# Job 2/3: Sanity test the final system
echo "[INFO] Running sanity-test job..."
bash "$RUN_JOB" \
    --name sanity-test \
    --hdd "$DISK" \
    --sysext "$SYSEXT_IMG" \
    --build "$BUILD"
