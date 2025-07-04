# This script should only be used when mock.sh have been run.
cd /var/lib/openqa/factory/hdd
export CI_PROJECT_DIR=$(pwd)
IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${IMG##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

poll_openqa_job() {
    # OpenQA will keep result of the test running as 'none', before the test running finish. Another approach is jq -r '.job.status'.
    local job_id="$1"
    local host="$2"
    local result

    echo "[INFO] Job ${job_id} submitted. Polling job result..."
    while true; do
        result=$(openqa-cli api --host "http://${host}" jobs/${job_id} \
                 | jq -r '.job.result // empty')
        echo "[INFO] Job result: ${result}"
        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi
        sleep 30
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
NUMDISKS=2
BOOTFROM=c
UEFI=1
UEFI_PFLASH_CODE=/usr/share/qemu/ovmf-x86_64-4m-code.bin
UEFI_PFLASH_VARS=/usr/share/qemu/ovmf-x86_64-4m-vars.bin

# Test Configuration
TEST=install_full_system
CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git#refs/heads/brute-force-debug
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
    HDD_1="$IMG" \
    PUBLISH_HDD_2="$DISK" \
    BOOTFROM="$BOOTFROM" \
    BACKEND="$BACKEND" \
    UEFI="$UEFI" \
    UEFI_PFLASH_CODE="$UEFI_PFLASH_CODE" \
    UEFI_PFLASH_VARS="$UEFI_PFLASH_VARS" \
    DO_INSTALL="$DO_INSTALL" \
    QEMUCPUS="$QEMUCPUS" \
    QEMURAM="$QEMURAM" \
    HDDSIZEGB="$HDDSIZEGB" \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="$NEEDLES_DIR" \
    TIMEOUT_SCALE=3 \
    _GROUP="$_GROUP" | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] Successfully installed full system from live image..."

# Start testing the installed system
echo "[INFO] Start testing the installed system"
FLAVOR="full-system"
NUMDISKS=1
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
    BOOTFROM="$BOOTFROM" \
    BACKEND="$BACKEND" \
    UEFI="$UEFI" \
    UEFI_PFLASH_CODE="$UEFI_PFLASH_CODE" \
    UEFI_PFLASH_VARS="$UEFI_PFLASH_VARS" \
    DO_INSTALL="$DO_INSTALL" \
    QEMUCPUS="$QEMUCPUS" \
    QEMURAM="$QEMURAM" \
    HDDSIZEGB="$HDDSIZEGB" \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="$NEEDLES_DIR" \
    TIMEOUT_SCALE=3 \
    _GROUP="$_GROUP" | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] All passed!"

exit 0