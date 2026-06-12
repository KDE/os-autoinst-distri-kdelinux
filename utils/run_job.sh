#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
set -euo pipefail

# Run an OpenQA job from within a worker.

HDD=
LIVE=
SYSEXT=
BUILD=
TEST=
UPGRADE=0

while [[ $# -gt 0 ]]; do
    case "$1" in
        --live)
            LIVE="$2"
            shift 2
            ;;
        --hdd)
            HDD="$2"
            shift 2
            ;;
        --sysext)
            SYSEXT="$2"
            shift 2
            ;;
        --build)
            BUILD="$2"
            shift 2
            ;;
        --name)
            TEST="$2"
            shift 2
            ;;
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

if [[ -z "$HDD" ]]; then
    echo "[ERROR] --hdd is required" >&2
    exit 1
fi

if [[ -z "$BUILD" ]]; then
    echo "[ERROR] --build is required" >&2
    exit 1
fi

if [[ -z "$TEST" ]]; then
    echo "[ERROR] --name is required" >&2
    exit 1
fi

if [[ -z "$SYSEXT" ]]; then
    echo "[ERROR] --sysext is required" >&2
    exit 1
fi

if [[ -n "$LIVE" && "$UPGRADE" -eq 1 ]]; then
    echo "[ERROR] --live and --upgrade are mutually exclusive" >&2
    exit 1
fi

required_vars=(OPENQA_HOST_ADDR CASEDIR)
[[ -z "${MOCK_MODE:-}" ]] && required_vars+=(WORKER_CLASS)
for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in environment" >&2
        exit 1
    fi
done

echo "[INFO] Running test job $TEST..."

if [[ -n "$LIVE" ]]; then
    FLAVOR=live-system
    # HDD_1 is the blank install target, HDD_2 the sysext, and HDD_3 the live boot medium..
    HDD_2="$(basename "$SYSEXT")"
    HDD_3="$(basename "$LIVE")"
    NUMDISKS=3
else
    FLAVOR=full-system
    HDD_1="$(basename "$HDD")"
    HDD_2="$(basename "$SYSEXT")"
    NUMDISKS=2
fi

openqa() {
    openqa-cli api --host "${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}" "$@"
}

stage_asset() {
    local path="$1"
    local name
    name=$(basename "$path")

    # This will be the system disk, which has already been placed into the share.
    if [[ ! -f "$path" ]]; then
        echo "[INFO] $name is the installed disk, already in the worker share; skipping."
        return 0
    fi

    # Actually stage the asset by dropping it in the local share.
    # No assets are required to be uploaded to the server.
    local share=/var/lib/openqa/share/factory/hdd
    mkdir -p "$share"
    cp "$path" "$share/$name"
    echo "[INFO] Staged $name into the worker share."
}

if [[ -n "$LIVE" ]]; then
    stage_asset "$LIVE"
else
    stage_asset "$HDD"
fi
stage_asset "$SYSEXT"

# Since we purposefully don't PUBLISH_HDD_1, flatten the install disk straight into the share.
# This would otherwise have been done by PUBLISH_HDD_1, but then we have a wasteful upload rigamarole
# to the server, even while all assets are completely self-contained within the worker.
produce_installed_hdd() {
    local name="$1"
    local share=/var/lib/openqa/share/factory/hdd
    [[ -e "$share/$name" ]] && return 0

    local pool_disk
    pool_disk=$(find /var/lib/openqa/pool -path '*/raid/hd0' -print -quit 2>/dev/null || true)
    if [[ -z "$pool_disk" ]]; then
        echo "[ERROR] Install target disk not found in the worker pool. Pool contents:" >&2
        find /var/lib/openqa/pool -maxdepth 3 >&2 || true
        exit 1
    fi

    mkdir -p "$share"
    qemu-img convert -O qcow2 "$pool_disk" "$share/$name"
    echo "[INFO] Flattened the installed disk ($pool_disk) into $share/$name, for the next job."
}

# Clean up the pool ourselves, because we set `--no-cleanup` in the worker so we're able to
# pre-seed the qcow2 image.
clean_pool() {
    rm -rf /var/lib/openqa/pool/*/* 2>/dev/null || true
}

poll_openqa_job() {
    local job_id="$1"
    local result

    echo "[INFO] Job ${job_id} submitted. Polling for result..."

    # Jobs should immediately schedule as the worker basically submits its own job.
    local scheduled_timeout=30
    local scheduled_since=

    while true; do
        local job_data state
        job_data=$(openqa jobs/${job_id})
        result=$(echo "$job_data" | jq -r '.job.result // empty')
        state=$(echo "$job_data" | jq -r '.job.state // empty')
        echo -e "[INFO] Job state: ${state}\t Job result: ${result}"

        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi

        if [[ "${state}" == "scheduled" ]]; then
            [[ -z "$scheduled_since" ]] && scheduled_since=$SECONDS
            if (( SECONDS - scheduled_since > scheduled_timeout )); then
                echo "[ERROR] Job ${job_id} stayed in the scheduled state for over ${scheduled_timeout}s." >&2
                exit 1
            fi
        else
            scheduled_since=
        fi

        sleep 5
    done

    echo "[INFO] Job URL: ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}/tests/${job_id}"

    if [[ "${result}" == "passed" || "${result}" == "softfailed" ]]; then
        echo "[INFO] Job ${job_id} completed with result: ${result}"
        return
    fi

    if [[ "${result}" != "failed" ]]; then
        echo "[ERROR] Job ${job_id} ended with unexpected result: ${result}" >&2
        exit 1
    fi

    # Job failed; check whether a fatal-flagged module caused the failure.
    # If so, the test suite was aborted early and subsequent jobs should not run.
    local details fatal_failures
    details=$(openqa jobs/${job_id}/details)
    fatal_failures=$(echo "$details" | jq -r '
        .job.testresults[]
        | select(.result == "failed" and .fatal == 1)
        | .name
    ')

    if [[ -n "$fatal_failures" ]]; then
        echo "[ERROR] Job ${job_id} aborted; fatal module(s) failed: $(echo "$fatal_failures" | tr '\n' ' ')" >&2
        exit 1
    fi

    echo "[WARN] Job ${job_id} failed; no fatal modules involved, continuing to next job."
}

GROUP_ARG=()
[[ -z "${MOCK_MODE:-}" ]] && GROUP_ARG=("_GROUP=KDE Linux")

JOB_RESPONSE=$(openqa -X POST jobs \
    DISTRI=KDE-Linux \
    VERSION="$BUILD" \
    FLAVOR="$FLAVOR" \
    ARCH=x86_64 \
    BUILD="$BUILD" \
    TEST="$TEST" \
    MACHINE=general_64bit \
    $( [[ -z "$LIVE" ]] && echo HDD_1="$HDD_1" ) \
    HDD_2="$HDD_2" \
    $( [[ -n "$LIVE" ]] && echo HDD_3="$HDD_3" ) \
    $( [[ -n "$LIVE" ]] && echo DO_INSTALL=1 ) \
    $( [[ -n "$LIVE" ]] && echo HDDSIZEGB=20 ) \
    $( [[ "$UPGRADE" -eq 1 ]] && echo DO_UPGRADE=1 ) \
    BOOT_HDD_IMAGE=1 \
    BACKEND=qemu \
    UEFI=1 \
    UEFI_PFLASH_CODE=/usr/share/qemu/ovmf-x86_64-4m-code.bin \
    UEFI_PFLASH_VARS=/usr/share/qemu/ovmf-x86_64-4m-vars.bin \
    QEMUCPUS=4 \
    QEMURAM=4096 \
    QEMUCPU=host \
    NUMDISKS="$NUMDISKS" \
    CASEDIR="$CASEDIR" \
    NEEDLES_DIR="%%CASEDIR%%/needles" \
    TIMEOUT_SCALE=3 \
    VIRTIO_CONSOLE=1 \
    NICTYPE_USER_OPTIONS="hostfwd=tcp::2222-:22" \
    "${GROUP_ARG[@]}" \
    $( [[ -z "${MOCK_MODE:-}" ]] && echo WORKER_CLASS="$WORKER_CLASS" ) )

echo "[INFO] Job creation response: $JOB_RESPONSE"
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r .id)
if [[ -z "$JOB_ID" || "$JOB_ID" == "null" ]]; then
    echo "[ERROR] Job creation failed" >&2
    exit 1
fi

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"

# Move installed disk out of the pool into the share so the next job resolves
# it, then clear the pool now that the job is done - since this isn't done automatically.
if [[ -n "$LIVE" ]]; then
    produce_installed_hdd "$(basename "$HDD")"
fi
clean_pool
