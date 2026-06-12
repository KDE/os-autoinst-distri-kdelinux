#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Start the OpenQA stack using the image's own entrypoint
skip_suse_tests=1 skip_suse_specifics=1 /usr/share/openqa/script/openqa-bootstrap &

echo "[INFO] Waiting for OpenQA bootstrap to complete..."
until [[ -s /etc/openqa/client.conf ]]; do sleep 2; done

cat > /etc/openqa/client.conf <<EOF
[auth]
# method name is case sensitive!
method = Fake

[localhost]
key = 1234567890ABCDEF
secret = 1234567890ABCDEF
EOF

echo "[INFO] Waiting for worker to start..."
until ps -ef | grep -q "[o]penqa/script/worker"; do sleep 2; done

# The bundled worker wipes its pool after each job. produce_installed_hdd takes the installed disk
# from the pool to give to the next job, so the pool must survive the first job.
# openqa-bootstrap starts the worker without --no-cleanup, so swap it for a --no-cleanup launched one.
echo "[INFO] Restarting the worker with --no-cleanup so its pool survives between jobs..."
worker_user=$(ps -o user= -p "$(pgrep -f 'openqa/script/worker' | head -n1)" 2>/dev/null | tr -d ' ')
pkill -f 'openqa/script/worker' || true
for _ in $(seq 1 10); do pgrep -f 'openqa/script/worker' >/dev/null || break; sleep 1; done
su -s /bin/bash "${worker_user:-root}" -c '/usr/share/openqa/script/worker --no-cleanup --instance 1 --verbose' &
until ps -ef | grep -q "[o]penqa/script/worker"; do sleep 2; done

echo "[INFO] Cancelling stale scheduled jobs..."
openqa-cli api jobs state=scheduled \
    | jq -r '.jobs[].id' \
    | while read -r id; do
        openqa-cli api -X POST "jobs/$id/cancel" || true
    done

export MOCK_MODE=1
export CASEDIR=/casedir

cat > /root/.bashrc <<EOF
export MOCK_MODE=1
export CASEDIR=/casedir
EOF

/casedir/worker.sh || true

echo "[INFO] Jobs complete. To inspect results, run:"
echo "    podman exec -it openqa-single-instance bash"
sleep infinity
