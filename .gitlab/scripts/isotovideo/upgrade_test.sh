#!/bin/bash
IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

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
TIMEOUT_SCALE=10

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

echo "[INFO] Successfully installed full system fcrom live image(Previous success build)..."

# Start testing the installed system
echo "[INFO] Start testing the installed system (Upgrade only)"

# Move the created qcow2 into test directory
mv assets_public/* $CI_PROJECT_DIR

FLAVOR="full-system"
NUMDISKS=1
DO_UPGRADE=1
TEST="upgrade_system"

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
    DO_UPGRADE="$DO_UPGRADE" \
    QEMUCPUS="$QEMUCPUS" \
    QEMURAM="$QEMURAM" \
    HDDSIZEGB="$HDDSIZEGB" \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="$NEEDLES_DIR" \
    TIMEOUT_SCALE="$TIMEOUT_SCALE" \
    _GROUP="$_GROUP"

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] Upgrade success!"

exit 0
