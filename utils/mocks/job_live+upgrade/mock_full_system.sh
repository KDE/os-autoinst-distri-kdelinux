# default CASEDIR
CASEDIR=https://invent.kde.org/anicaazhu/os-autoinst-distri-kdelinux.git
for arg in "$@"; do
    case $arg in
        --CASEDIR=*)
            CASEDIR="${arg#*=}"
            shift
            ;;
        *)
            echo "[ERROR] Unknown argument: $arg"
            echo "[USAGE] $0 --CASEDIR=your_case_repo_url"
            exit 1
            ;;
    esac
done

if [[ -z "$CASEDIR" ]]; then
    echo "[ERROR] --CASEDIR not provided"
    exit 1
fi

cd /var/lib/openqa/factory/hdd
export CI_PROJECT_DIR=$(pwd)
IMG_PATH=$(find "$CI_PROJECT_DIR" -maxdepth 1 -name '*.raw' | head -n1)
IMG=$(basename "$IMG_PATH")
OUTPUT=${IMG%.raw}
VERSION=${OUTPUT##*_}
DISK=${OUTPUT}.qcow2
OPENQA_HOST_ADDR=localhost

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
        exit 1
    fi
    echo "[INFO] Job ${job_id} completed with result: ${result}"
    echo "[INFO] Job URL: http://${host}/tests/${job_id}"
}

echo "[INFO] Start installation tests..."

# Distri Configuration
DISTRI=KDE-Linux
FLAVOR="full-system"
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
NEEDLES_DIR=%%CASEDIR%%/needles
HDDSIZEGB=50

# Start testing the installed system
echo "[INFO] Start testing the installed system (Upgrade only)"
FLAVOR="full-system"
NUMDISKS=1
DO_UPGRADE=1
TEST="upgrade_system"

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
    TIMEOUT_SCALE=3 \
    _GROUP="$_GROUP" | jq -r .id)

poll_openqa_job "$JOB_ID" "$OPENQA_HOST_ADDR"
echo "[INFO] Upgrade success!"

exit 0
