#!/bin/bash

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

IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
# Move the downloaded raw file into the test directory
mkdir -p /installation-tests
mv $CI_PROJECT_DIR/$IMG /installation-tests
cd /installation-tests
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

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
TIMEOUT_SCALE=3

# Test Configuration
TEST=install_full_system
#CASEDIR=https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git#refs/heads/brute-force-debug
CASEDIR=https://invent.kde.org/tduck/os-autoinst-distri-kdelinux.git
NEEDLES_DIR=needles
DO_INSTALL=1
HDDSIZEGB=50

# Assign it with a pre-configured group name.
_GROUP="KDE Linux"

run_installation_test() {
    isotovideo \
        --exit-status-from-test-results \
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
        _GROUP="$_GROUP"
}

run_with_retry "Installation test" run_installation_test

echo "[INFO] Successfully installed full system from live image..."

# Start testing the installed system
echo "[INFO] Start testing the installed system"

# Move the created qcow2 into fullsystem directory
mkdir -p /fullsystem-test
mv /installation-tests/assets_public/$DISK /fullsystem-test
cd /fullsystem-test

FLAVOR="full-system"
NUMDISKS=1
DO_INSTALL=0
TEST="installed_system_sanity_check"

run_sanity_test() {
    isotovideo \
        --exit-status-from-test-results \
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
        TIMEOUT_SCALE="$TIMEOUT_SCALE" \
        _GROUP="$_GROUP"
}

run_with_retry "Sanity check test" run_sanity_test

echo "[INFO] Latest build passed successfully."

exit 0
