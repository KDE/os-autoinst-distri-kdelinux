#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Start the OpenQA stack using the image's own entrypoint
skip_suse_tests=1 skip_suse_specifics=1 /usr/share/openqa/script/openqa-bootstrap &

echo "[INFO] Waiting for OpenQA bootstrap to complete..."
until [[ -s /etc/openqa/client.conf ]]; do sleep 2; done

echo "[INFO] Waiting for worker to start..."
until ps -ef | grep -q "[o]penqa/script/worker"; do sleep 2; done

echo "[INFO] Cancelling stale scheduled jobs..."
openqa-cli api jobs state=scheduled \
    | jq -r '.jobs[].id' \
    | while read -r id; do
        openqa-cli api -X POST "jobs/$id/cancel" || true
    done

export MOCK_MODE=1
export CASEDIR=/casedir
/casedir/worker.sh || true

echo "[INFO] Jobs complete. To inspect results, run:"
echo "    podman exec -it openqa-single-instance bash"
sleep infinity
