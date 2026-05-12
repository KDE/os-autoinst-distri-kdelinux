#!/usr/bin/env bash
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

required_vars=(OPENQA_HOST_ADDR OPENQA_SSH_USER CASEDIR)
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

stage_asset() {
    local path="$1"
    local name
    name=$(basename "$path")

    # If the file doesn't exist in the current execution workspace,
    # it's an existing openQA asset. Skip staging entirely.
    if [[ ! -f "$path" ]]; then
        echo "[INFO] $name not found locally. Assuming it is already an asset on the openQA server; skipping upload."
        return 0
    fi

    # Move the asset into the worker share so we don't download something we already have.
    echo "[INFO] Staging $name into worker share..."
    local share=/var/lib/openqa/share/factory/hdd
    mkdir -p "$share"
    cp "$path" "$share/$name"
    if [[ -n "${MOCK_MODE:-}" ]]; then
        # If we're in a single-instance mock container, this is all we need to do.
        return
    fi

    # Ensure the required factory directory on the WebUI exists
    ssh -o StrictHostKeyChecking=accept-new \
        "${OPENQA_SSH_USER}@${OPENQA_HOST_ADDR}" \
        "mkdir -p /var/lib/openqa/factory/hdd && chmod 777 /var/lib/openqa/factory/hdd"

    # Compare the hash of the asset on the worker to the asset on the server, upload if they're different
    local local_hash remote_hash
    local_hash=$(sha256sum "$path" | awk '{print $1}')
    remote_hash=$(ssh -o StrictHostKeyChecking=accept-new \
        "${OPENQA_SSH_USER}@${OPENQA_HOST_ADDR}" \
        "sha256sum /var/lib/openqa/factory/hdd/$name 2>/dev/null | awk '{print \$1}'" || true)

    if [[ "$local_hash" == "$remote_hash" ]]; then
        echo "[INFO] $name is unchanged on server, skipping upload."
    else
        echo "[INFO] Uploading $name to server via sftp..."
        printf 'put "%s" /var/lib/openqa/factory/hdd/\n' "$path" \
            | sftp -o StrictHostKeyChecking=accept-new \
                   "${OPENQA_SSH_USER}@${OPENQA_HOST_ADDR}"

        ssh -o StrictHostKeyChecking=accept-new \
            "${OPENQA_SSH_USER}@${OPENQA_HOST_ADDR}" \
            "ls -lh /var/lib/openqa/factory/hdd/$name" \
            || { echo "[ERROR] $name not found on server after upload" >&2; exit 1; }

        ssh -o StrictHostKeyChecking=accept-new \
            "${OPENQA_SSH_USER}@${OPENQA_HOST_ADDR}" \
            "chmod 644 /var/lib/openqa/factory/hdd/$name"
    fi

    # Explicitly register the asset on the WebUI
    local reg_response
    reg_response=$(openqa-cli api -X POST assets \
        --host "${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}" \
        name="$name" \
        type="hdd")
    echo "[INFO] Asset registration response for $name: $reg_response"
}

if [[ -n "$LIVE" ]]; then
    stage_asset "$LIVE"
else
    stage_asset "$HDD"
fi
stage_asset "$SYSEXT"

poll_openqa_job() {
    local job_id="$1"
    local result

    echo "[INFO] Job ${job_id} submitted. Polling for result..."

    while true; do
        local job_data state
        job_data=$(openqa-cli api --host "${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}" jobs/${job_id})
        result=$(echo "$job_data" | jq -r '.job.result // empty')
        state=$(echo "$job_data" | jq -r '.job.state // empty')
        echo -e "[INFO] Job state: ${state}\t Job result: ${result}"

        if [[ "${result}" =~ ^(passed|softfailed|failed|incomplete|timeout|user_cancelled|obsoleted|cancelled|skipped)$ ]]; then
            break
        fi
        sleep 5
    done

    if [[ "${result}" != "passed" && "${result}" != "softfailed" ]]; then
        echo "[ERROR] Job ${job_id} failed with result: ${result}"
        echo "[INFO] Job URL: ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}/tests/${job_id}"
        exit 1
    fi

    echo "[INFO] Job ${job_id} completed with result: ${result}"
    echo "[INFO] Job URL: ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}/tests/${job_id}"
}

GROUP_ARG=()
[[ -z "${MOCK_MODE:-}" ]] && GROUP_ARG=("_GROUP=KDE Linux")

JOB_RESPONSE=$(openqa-cli api -X POST jobs \
    --host ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR} \
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
    "${GROUP_ARG[@]}" \
    $( [[ -z "${MOCK_MODE:-}" ]] && echo WORKER_CLASS="$WORKER_CLASS" ) )

echo "[INFO] Job creation response: $JOB_RESPONSE"
JOB_ID=$(echo "$JOB_RESPONSE" | jq -r .id)
if [[ -z "$JOB_ID" || "$JOB_ID" == "null" ]]; then
    echo "[ERROR] Job creation failed" >&2
    exit 1
fi

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
