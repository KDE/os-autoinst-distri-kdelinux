#!/usr/bin/env bash
set -euo pipefail

# Configures and starts the openQA worker daemon for CI and local worker runs.
# Sets a unique WORKER_CLASS so submitted jobs are pinned to this worker instance.

export WORKER_CLASS="kde-linux-worker-$(cat /proc/sys/kernel/random/uuid)"

cat > /etc/openqa/workers.ini <<EOF
[global]
HOST = ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}
BACKEND = qemu
WORKER_CLASS = ${WORKER_CLASS}
EOF

cat > /etc/openqa/client.conf <<EOF
[${OPENQA_HOST_ADDR}]
key = ${OPENQA_API_KEY}
secret = ${OPENQA_API_SECRET}
EOF

for i in {1..10}; do
    if curl -sk ${OPENQA_SCHEME:-https}://${OPENQA_HOST_ADDR}/api/v1/jobs >/dev/null; then
        echo "[INFO] openQA is ready"
        break
    fi
    echo "[INFO] Waiting for openQA..."
    sleep 3
done

rm -f /var/lib/openqa/cache/cache.sqlite

/run_openqa_worker.sh &
