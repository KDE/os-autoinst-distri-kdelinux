#!/bin/bash
set -euo pipefail
# Only run this locally, for CI tests, we will use opensuse/tumbleweed + bootstrap scripts.
#podman run --rm -it \
#    -v "$PWD":/builds/1/project \
#    -w /builds/1/project \
#    -p 5991:5991 -p 1443:443 -p 5990:5990 -p 1080:80 -p 9526:9526 \
#    --device /dev/kvm  \
#    --name openqa-server \
#    registry.opensuse.org/devel/openqa/containers/openqa-single-instance

# Start Another terminal instance, and run
# podman exec -it openqa-server bash
# ./utils/mocks/job_live+fullsystem/mock.sh --CASEDIR=https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git

# default CASEDIR
rm -rf /var/lib/openqa/tests/kde-linux
cp -r /builds/1/project /var/lib/openqa/tests/kde-linux
chown -R geekotest:geekotest /var/lib/openqa/tests/kde-linux
CASEDIR=/var/lib/openqa/tests/kde-linux

# Parse arguments
for arg in "$@"; do
    case $arg in
        --CASEDIR=*)
            CASEDIR="${arg#*=}"
            shift
            ;;
        *)
            echo "[ERROR] Unknown argument: $arg"
            echo "[USAGE] $0 --CASEDIR=your_case_repo_url"
            exit 1
            ;;
    esac
done

if [[ -z "$CASEDIR" ]]; then
    echo "[ERROR] --CASEDIR not provided"
    exit 1
fi

zypper --non-interactive install perl-Inline-Python python3-requests python3-beautifulsoup4 dos2unix vim erofs-utils python3-fabric

# Bootstrap OpenQA Environment
#/usr/share/openqa/script/openqa-bootstrap &
#./utils/wait_openqa_ready.sh

# Download the latest image
python3 utils/download_image.py --latest

export CI_PROJECT_DIR=$(pwd)
IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

# Create a mountable image with the bootstrapping sysext
SYSEXT_IMG="openqa-sysext.img"
mkfs.erofs -L "kde-openqa-ext" "$SYSEXT_IMG" "$CI_PROJECT_DIR/extensions/openqa"

# Move the images to openqa dir
mv "$CI_PROJECT_DIR/$IMG" /var/lib/openqa/factory/hdd/
mv "$CI_PROJECT_DIR/$SYSEXT_IMG" /var/lib/openqa/factory/hdd/

poll_openqa_job() {
    # OpenQA will keep result of the test running as 'none', before the test running finish. Another approach is jq -r '.job.status'.
    local job_id="$1"
    local host="$2"
    local result

    echo "[INFO] Job ${job_id} submitted. Polling job result..."
    local status_json="/var/lib/openqa/pool/1/autoinst-status.json"

    while true; do
        result=$(openqa-cli api --host "http://${host}" jobs/${job_id} \
                 | jq -r '.job.result // empty')
        echo "[INFO] Job result: ${result}"
        if [[ -f "$status_json" ]]; then
            local current_test
            local status
            current_test=$(jq -r '.current_test // empty' "$status_json")
            status=$(jq -r '.status // empty' "$status_json")
            if [[ -n "$current_test" && "$status" == "running" ]]; then
                echo "[STATUS] Currently running: $current_test"
            fi
        fi

        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi
        sleep 5
    done

    if [[ "${result}" != "passed" && "${result}" != "softfailed" ]]; then
        echo "[ERROR] Job ${job_id} failed with result: ${result}"
        echo "[INFO] Job URL: http://${host}/tests/${job_id}"
        exit 1
    fi
    echo "[INFO] Job ${job_id} completed with result: ${result}"
    echo "[INFO] Job URL: http://${host}/tests/${job_id}"
}


echo "[INFO] Start installation tests..."
# Distri Configuration
DISTRI=KDE-Linux
FLAVOR=live-system
ARCH=x86_64
BUILD="${VERSION}"

# Machine configuration
MACHINE=general_64bit
BACKEND=qemu
QEMUCPUS=4
QEMURAM=4096
QEMUCPU=host
NUMDISKS=3
BOOT_HDD_IMAGE=1
UEFI=1
UEFI_PFLASH_CODE=/usr/share/qemu/ovmf-x86_64-4m-code.bin
UEFI_PFLASH_VARS=/usr/share/qemu/ovmf-x86_64-4m-vars.bin

# Test Configuration
TEST=install_full_system
NEEDLES_DIR=%%CASEDIR%%/needles
DO_INSTALL=1
HDDSIZEGB=50

# Assign it with a pre-configured group name.
_GROUP="KDE Linux"

JOB_ID=$(openqa-cli api -X POST jobs \
    --host http://${OPENQA_HOST_ADDR} \
    DISTRI="$DISTRI" \
    VERSION="$VERSION" \
    FLAVOR="$FLAVOR" \
    ARCH="$ARCH" \
    BUILD="$BUILD" \
    TEST="$TEST" \
    MACHINE="$MACHINE" \
    PUBLISH_HDD_1="$DISK" \
    HDD_2="$SYSEXT_IMG" \
    HDD_3="$IMG" \
    BOOT_HDD_IMAGE="$BOOT_HDD_IMAGE" \
    BACKEND="$BACKEND" \
    UEFI="$UEFI" \
    UEFI_PFLASH_CODE="$UEFI_PFLASH_CODE" \
    UEFI_PFLASH_VARS="$UEFI_PFLASH_VARS" \
    DO_INSTALL="$DO_INSTALL" \
    QEMUCPUS="$QEMUCPUS" \
    QEMURAM="$QEMURAM" \
    QEMUCPU="$QEMUCPU" \
    HDDSIZEGB="$HDDSIZEGB" \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="$NEEDLES_DIR" \
    TIMEOUT_SCALE=3 \
    VIRTIO_CONSOLE=1 \
    NICTYPE_USER_OPTIONS="hostfwd=tcp::2222-:22" \
    _GROUP="$_GROUP" | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] Successfully installed full system from live image..."

# Start testing the installed system
echo "[INFO] Start testing the installed system"
FLAVOR="full-system"
NUMDISKS=2
DO_INSTALL=0
TEST="installed_system_sanity_check"

JOB_ID=$(openqa-cli api -X POST jobs \
    --host http://${OPENQA_HOST_ADDR} \
    DISTRI="$DISTRI" \
    VERSION="$VERSION" \
    FLAVOR="$FLAVOR" \
    ARCH="$ARCH" \
    BUILD="$BUILD" \
    TEST="$TEST" \
    MACHINE="$MACHINE" \
    HDD_1="$DISK" \
    HDD_2="$SYSEXT_IMG" \
    BACKEND="$BACKEND" \
    UEFI="$UEFI" \
    UEFI_PFLASH_CODE="$UEFI_PFLASH_CODE" \
    UEFI_PFLASH_VARS="$UEFI_PFLASH_VARS" \
    DO_INSTALL="$DO_INSTALL" \
    QEMUCPUS="$QEMUCPUS" \
    QEMURAM="$QEMURAM" \
    QEMUCPU="$QEMUCPU" \
    HDDSIZEGB="$HDDSIZEGB" \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="$NEEDLES_DIR" \
    TIMEOUT_SCALE=3 \
    VIRTIO_CONSOLE=1 \
    NICTYPE_USER_OPTIONS="hostfwd=tcp::2222-:22" \
    _GROUP="$_GROUP" | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] All passed!"

exit 0
