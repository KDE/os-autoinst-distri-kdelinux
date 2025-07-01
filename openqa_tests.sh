#!/bin/bash
set -euo pipefail

EPOCH=$(date --utc +%s)
VERSION=$(date --utc --date="@$EPOCH" +%Y%m%d)

# All the openqa resources are in the /var/lib/openqa directory
# imaging artifacts are in the /srv/kde-raw directory.
# RAW="/srv/kde-raw/$CI_PIPELINE_ID/kde.raw"
RAW="/srv/kde-raw/$CI_PIPELINE_ID/kde.raw"

# Make a hdd directory for the openqa disk images
mkdir -p /var/lib/openqa/factory/hdd

# Copy the kde-linux image to the hdd directory
cp "$RAW" /var/lib/openqa/factory/hdd/kde.raw

# Allocate a 50G qcow2 image that kdelinux will be installed to
qemu-img create -f qcow2 /var/lib/openqa/factory/hdd/install.qcow2 50G

# Install the inline python module for openqa
zypper --non-interactive install perl-Inline-Python

cd /var/lib/openqa/share/tests

# Put this file inside /var/lib/openqa/tests to obey the openqa conventions.
# However, this vars.json could be created at anywhere. Running an `isotovideo` command at the same directory as vars.json will trigger OpenQA backend to clone the git repo that contains test cases, which specified in the CASEDIR datafiled , into that directory. OpenQA will then looking for CASEDIR and NEEDLES_DIR to locate test cases.
# OpenQA will read varaibles from this file to start running tests. During test running, it will override some data fields in this file. So it is a good idea to perserve a original copy to trigger the wanted test behavior.

# "INCLUDE_MODULES" : "boot_to_desktop"
# "SCEDULE" : "", # check https://open.qa/docs/#_schedule_asset_nr_url

cat > vars.json << EOF
{
   "ARCH" : "x86_64",
   "BACKEND" : "qemu",
   "DISTRI" : "kdelinux",
   "BIOS" : null,
   "BOOTFROM" : "c",
   "CASEDIR" : "https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git",
   "NEEDLES_DIR": "needles",
   "CDMODEL" : "scsi-cd",
   "DO_INSTALL" : "1",
   "FLAVOR" : "live",
   "HDDMODEL" : "virtio-blk",
   "HDDSIZEGB" : "50",
   "HDD_1" : "/var/lib/openqa/share/factory/hdd/kde.raw",
   "HDD_2" : "/var/lib/openqa/share/factory/hdd/install.qcow2",
   "QEMU_DISABLE_COPY_ON_WRITE" : "1",
   "JOBTOKEN" : "",
   "MACHINE" : "64bit_kdeos",
   "NEEDLES_GIT_HASH" : "UNKNOWN",
   "NEEDLES_GIT_URL" : "UNKNOWN (no .git found)",
   "NICMAC" : "",
   "NICMODEL" : "virtio-net",
   "NICTYPE" : "user",
   "NICVLAN" : "0",
   "NUMDISKS" : "2",
   "PRODUCTDIR" : "",
   "QEMUCPUS" : "4",
   "QEMUPORT" : 15222,
   "QEMURAM" : "4096",
   "TEST" : "",
   "TEST_GIT_HASH" : "UNKNOWN",
   "TEST_GIT_URL" : "UNKNOWN (no .git found)",
   "UEFI" : "1",
   "UEFI_PFLASH_CODE" : "/usr/share/qemu/ovmf-x86_64-4m-code.bin",
   "UEFI_PFLASH_VARS" : "/usr/share/qemu/ovmf-x86_64-4m-vars.bin",
   "VERSION" : "$VERSION",
   "VIRTIO_CONSOLE" : 1
}
EOF

isotovideo

echo "Waiting for tests to finish..."
sleep 30 

cd testresults
output_file="output"
fail_count=0

# clean output
> "$output_file"

# For every test module result, check if it success or not.
for f in result-*.json; do
    [ -f "$f" ] || continue

    module=$(echo "$f" | sed 's/^result-//; s/\.json$//')
    result=$(jq -r '.result' "$f")

    echo "Module: $module - Result: $result" >> "$output_file"

    if [ "$result" != "ok" ]; then
        fail_count=$((fail_count + 1))
    fi
done

if [ "$fail_count" -gt 0 ]; then
    echo "Modules failed to pass tests: $fail_count" >> "$output_file"
    exit 1
else
    echo "All modules pass tests!" >> "$output_file"
    exit 0
fi


## The following should work once we have a OpenQA server. Current isotovideo is most suitable for docker executor runners.
# # OpenQA Job.
# # Todo, Parametrize the each attribute.
# job_info=$(openqa-cli api -X POST jobs --host http://localhost:1080 \
#     DISTRI=kdelinux_ \
#     VERSION=$(date +%Y%m%d) \
#     FLAVOR=live \
#     ARCH=x86_64 \
#     TEST=boot_to_desktop \
#     MACHINE=64bit_kdeos \
#     HDD_1=kde.raw \
#     HDD_2=install.qcow2 \
#     BOOTFROM=disk \
#     BACKEND=qemu \
#     UEFI=1 \
#     UEFI_PFLASH_CODE=/usr/share/qemu/ovmf-x86_64-4m-code.bin \
#     UEFI_PFLASH_VARS=/usr/share/qemu/ovmf-x86_64-4m-vars.bin \
#     DO_INSTALL=1 \
#     QEMUCPUS=4 \
#     QEMURAM=4096 \
#     HDDSIZEGB=50 \
#     NUMDISKS=2 \
#     CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git \
#     NEEDLES_DIR=%%CASEDIR%%/needles \
#  )

# # Extract jobid
# job_id=$(echo "$job_info" | grep -oP '"id":\K[0-9]+')

# echo "Submitted job ID: $job_id"


