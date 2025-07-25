#!/bin/bash

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
#CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git#refs/heads/brute-force-debug
CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git
NEEDLES_DIR=needles
DO_INSTALL=1
HDDSIZEGB=50

# Assign it with a pre-configured group name.
_GROUP="KDE Linux"

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

INSTALL_EXIT_CODE=$?
if [[ $INSTALL_EXIT_CODE -ne 0 ]]; then
  echo "[ERROR] Installation test failed with exit code $INSTALL_EXIT_CODE"
  exit $INSTALL_EXIT_CODE
fi

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

EXIT_CODE=$?
if [[ $EXIT_CODE -ne 0 ]]; then
  echo "[ERROR] Full System test failed with exit code $EXIT_CODE"
  exit $EXIT_CODE
fi

echo "[INFO] Latest build passed successfully."

exit 0