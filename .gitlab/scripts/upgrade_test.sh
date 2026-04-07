#!/bin/bash
IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

# Move the image to openqa dir
mv "$CI_PROJECT_DIR/$IMG" /var/lib/openqa/factory/hdd/

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
        return 1
    fi
    echo "[INFO] Job ${job_id} completed with result: ${result}"
    echo "[INFO] Job URL: http://${host}/tests/${job_id}"
    return 0
}

run_with_retry() {
    local test_name="$1"
    local max_retries=2
    local attempt=1

    while [[ $attempt -le $((max_retries + 1)) ]]; do
        echo "[INFO] $test_name - Attempt $attempt"

        if [[ $attempt -eq 1 ]]; then
            shift
            "$@"
            local exit_code=$?
        else
            shift
            "$@"
            local exit_code=$?
        fi

        if [[ $exit_code -eq 0 ]]; then
            echo "[INFO] $test_name succeeded on attempt $attempt"
            return 0
        else
            echo "[WARNING] $test_name failed on attempt $attempt"
            if [[ $attempt -le $max_retries ]]; then
                echo "[INFO] Retrying $test_name (attempt $((attempt + 1)) of $((max_retries + 1)))..."
                sleep 10
            fi
        fi
        ((attempt++))
    done

    echo "[ERROR] $test_name failed after $max_retries retries"
    exit 1
}


echo "[INFO] Start installation tests(Previously success build)..."
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
TIMEOUT_SCALE=3

# Test Configuration
TEST=install_full_system
#CASEDIR=https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git#refs/heads/brute-force-debug
CASEDIR=https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git
NEEDLES_DIR=%%CASEDIR%%/needles
DO_INSTALL=1
HDDSIZEGB=50

# Assign it with a pre-configured group name.
_GROUP="KDE Linux"

run_installation_test() {
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
        TIMEOUT_SCALE="$TIMEOUT_SCALE" \
        _GROUP="$_GROUP" | jq -r .id)

    poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
}

run_with_retry "Installation test" run_installation_test
echo "[INFO] Successfully installed full system fcrom live image(Previous success build)..."

# Start testing the installed system
echo "[INFO] Start testing the installed system (Upgrade only)"
FLAVOR="full-system"
NUMDISKS=1
DO_UPGRADE=1
TEST="upgrade_system"

run_upgrade_test() {
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
        DO_UPGRADE="$DO_UPGRADE" \
        QEMUCPUS="$QEMUCPUS" \
        QEMURAM="$QEMURAM" \
        HDDSIZEGB="$HDDSIZEGB" \
        NUMDISKS="$NUMDISKS" \
        CASEDIR="$CASEDIR" \
        NEEDLES_DIR="$NEEDLES_DIR" \
        TIMEOUT_SCALE="$TIMEOUT_SCALE" \
        _GROUP="$_GROUP" | jq -r .id)

    poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
}

run_with_retry "Upgrade test" run_upgrade_test
echo "[INFO] Upgrade success!"

exit 0
