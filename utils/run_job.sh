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
FLAVOR=
AFTER=
GROUP=

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
        --flavor)
            FLAVOR="$2"
            shift 2
            ;;
        --group)
            GROUP="$2"
            shift 2
            ;;
        # Have a chained dependency on an already-submitted job so webui links them
        # in its dependency graph.
        --after)
            AFTER="$2"
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

if [[ -z "$FLAVOR" ]]; then
    echo "[ERROR] --flavor is required" >&2
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
    # HDD_1 is the blank install target, HDD_2 the sysext, and HDD_3 the live boot medium..
    HDD_2="$(basename "$SYSEXT")"
    HDD_3="$(basename "$LIVE")"
    NUMDISKS=3
else
    HDD_1="$(basename "$HDD")"
    HDD_2="$(basename "$SYSEXT")"
    NUMDISKS=2
fi

openqa() {
    openqa-cli api --host "${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}" "$@"
}

banner() {
    local level="$1" message="$2"
    local rule color out=1
    case "$level" in
        ERROR) rule='\e[1;91m'; color='\e[1;91m'; out=2 ;;  # red
        WARN)  rule='\e[1;93m'; color='\e[1;93m'; out=2 ;;  # yellow
        *)     rule='\e[1;95m'; color='\e[1;96m'         ;;  # magenta rule, cyan text
    esac
    local line='━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    {
        printf '\n%b%s\e[0m\n' "$rule" "$line"
        printf '%-9s %b%s\e[0m\n' "[$level]" "$color" "$message"
        printf '%b%s\e[0m\n\n' "$rule" "$line"
    } >&"$out"
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

    echo "[INFO] Job ${job_id} submitted. Polling for result..."

    # Jobs should immediately schedule as the worker basically submits its own job.
    local scheduled_timeout=30
    local scheduled_since=

    banner INFO "View the running job here:  ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}/tests/${job_id}"

    local result=
    local state=

    while true; do
        local job_data new_state new_result
        job_data=$(openqa jobs/${job_id})

        new_state="$(echo "$job_data" | jq -r '.job.state // empty')"
        new_result="$(echo "$job_data" | jq -r '.job.result // empty')"

        if [[ "${state}" != "${new_state}" \
        || "${result}" != "${new_result}" ]]; then
            state="$new_state"
            result="$new_result"
            echo -e "[INFO] Job state changed to: ${state}\t Job result changed to: ${result}"
        fi


        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi

        if [[ "${state}" == "scheduled" ]]; then
            [[ -z "$scheduled_since" ]] && scheduled_since=$SECONDS
            if (( SECONDS - scheduled_since > scheduled_timeout )); then
                banner ERROR "Job ${job_id} stayed in the scheduled state for over ${scheduled_timeout}s."
                return 1
            fi
        else
            scheduled_since=
        fi

        sleep 5
    done

    if [[ "${result}" == "passed" || "${result}" == "softfailed" ]]; then
        banner INFO "Job ${job_id} completed with result: ${result}"
        return 0
    fi

    if [[ "${result}" != "failed" ]]; then
        banner ERROR "Job ${job_id} ended with unexpected result: ${result}"
        return 1
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
        banner ERROR "Job ${job_id} aborted; fatal module(s) failed: $(echo "$fatal_failures" | tr '\n' ' ')"
        return 1
    fi

    banner WARN "Job ${job_id} failed; no fatal modules involved."
    return 2
}

GROUP_ARG=()
[[ -n "$GROUP" ]] && GROUP_ARG=("_GROUP=$GROUP")

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
    $( [[ -n "$AFTER" ]] && echo _START_AFTER_JOBS="$AFTER" ) \
    "${GROUP_ARG[@]}" \
    $( [[ -z "${MOCK_MODE:-}" ]] && echo WORKER_CLASS="$WORKER_CLASS" ) )

echo "[INFO] Job creation response: $JOB_RESPONSE"
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r .id)
if [[ -z "$JOB_ID" || "$JOB_ID" == "null" ]]; then
    banner ERROR "Job creation failed"
    exit 1
fi

# Emit the job id on fd 3 so jobs.sh can chain the next job, only if fd 3 was created.
if { true >&3; } 2>/dev/null; then
    echo "$JOB_ID" >&3
fi

poll_retcode=0
poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR" || poll_retcode=$?

# Move installed disk out of the pool into the share so the next job resolves
# it, then clear the pool now that the job is done - since this isn't done automatically.
# A fatal failure is marked by retcode 1. In this case fail fast.
if [[ "$poll_retcode" -ne 1 ]]; then
    if [[ -n "$LIVE" || "$UPGRADE" -eq 1 ]]; then
        produce_installed_hdd "$(basename "$HDD")"
    fi
    clean_pool
fi

exit "$poll_retcode"
