#!/usr/bin/env bash

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

for var in OPENQA_HOST_ADDR CASEDIR WORKER_CLASS; do
    if [[ -z "${!var}" ]]; then
        echo "[ERROR] $var is not set in environment" >&2
        exit 1
    fi
done

echo "[INFO] Running test job $TEST..."

if [[ -n "$LIVE" ]]; then
    FLAVOR=live-system
    HDD_1="$(basename "$LIVE")"
    HDD_2="$(basename "$SYSEXT")"
    PUBLISH_HDD_3="$(basename "$HDD")"
    NUMDISKS=3
else
    FLAVOR=full-system
    HDD_1="$(basename "$HDD")"
    HDD_2="$(basename "$SYSEXT")"
    NUMDISKS=2
fi

WORKER_CACHE=/var/lib/openqa/cache/${OPENQA_HOST_ADDR}:${OPENQA_HOST_PORT}/factory/hdd
mkdir -p "$WORKER_CACHE"

upload_asset() {
    local path="$1"
    local name
    name=$(basename "$path")
    echo "[INFO] Uploading $name to server..."
    openqa-cli api -X POST assets \
        --host "https://${OPENQA_HOST_ADDR}:${OPENQA_PORT}" \
        --param-file asset="$path" \
        type=hdd
}

if [[ -n "$LIVE" ]]; then
    upload_asset "$LIVE"
else
    upload_asset "$HDD"
fi
[[ -n "$SYSEXT" ]] && upload_asset "$SYSEXT"

poll_openqa_job() {
    local job_id="$1"
    local host="$2"
    local result

    echo "[INFO] Job ${job_id} submitted. Polling for result..."

    while true; do
        result=$(openqa-cli api --host "https://${host}" jobs/${job_id} \
                 | jq -r '.job.result // empty')
        echo "[INFO] Job result: ${result}"

        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi
        sleep 5
    done

    if [[ "${result}" != "passed" && "${result}" != "softfailed" ]]; then
        echo "[ERROR] Job ${job_id} failed with result: ${result}"
        echo "[INFO] Job URL: https://${host}/tests/${job_id}"
        exit 1
    fi

    echo "[INFO] Job ${job_id} completed with result: ${result}"
    echo "[INFO] Job URL: https://${host}/tests/${job_id}"
}

JOB_ID=$(openqa-cli api -X POST jobs \
    --host https://${OPENQA_HOST_ADDR}:${OPENQA_HOST_PORT} \
    DISTRI=KDE-Linux \
    VERSION="$BUILD" \
    FLAVOR="$FLAVOR" \
    ARCH=x86_64 \
    BUILD="$BUILD" \
    TEST="$TEST" \
    MACHINE=general_64bit \
    HDD_1="$HDD_1" \
    HDD_2="$HDD_2" \
    $( [[ -n "$LIVE" ]] && echo PUBLISH_HDD_3="$PUBLISH_HDD_3" ) \
    $( [[ -n "$LIVE" ]] && echo DO_INSTALL=1 ) \
    $( [[ -n "$LIVE" ]] && echo HDDSIZEGB=50 ) \
    $( [[ "$UPGRADE" -eq 1 ]] && echo DO_UPGRADE=1 ) \
    BOOTFROM=c \
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
    _GROUP="KDE Linux" \
    WORKER_CLASS=$WORKER_CLASS | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR:$OPENQA_HOST_PORT"
