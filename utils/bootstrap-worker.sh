#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>
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

# Start the worker with --no-cleanup so it preserves the pool after each job instead of
# wiping it. install-system's published qcow2 then stays in the pool, and we don't have to
# re-download it from the server. This isn't great, but the upstream script hardcodes the
# OpenQA worker's arguments, and we shouldn't be reimplementing their code.
# Also strip the launcher's hardcoded --verbose so we don't spam CI.
sed -i -e 's#/usr/share/openqa/script/worker #&--no-cleanup #' -e 's# --verbose##' /run_openqa_worker.sh
grep -q -- '--no-cleanup' /run_openqa_worker.sh \
    || { echo "[ERROR] Could not enable --no-cleanup on the openQA worker launcher" >&2; exit 1; }

/run_openqa_worker.sh &
