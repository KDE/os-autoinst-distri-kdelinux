#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Thomas Duckworth <tduck@filotimoproject.org>

# Start the OpenQA stack using the image's own entrypoint
# The bundled worker wipes its pool after each job. produce_installed_hdd takes the installed disk
# from the pool to give to the next job, so the pool must survive the first job.
# openqa-bootstrap starts the worker without --no-cleanup, so swap it for a --no-cleanup launched one.
sed -i 's#OPENQA_DIR/script/worker #&--no-cleanup #' /usr/share/openqa/script/openqa-bootstrap
grep -q -- '--no-cleanup' /usr/share/openqa/script/openqa-bootstrap \
    || { echo "[ERROR] Could not enable --no-cleanup on the openQA worker launcher" >&2; exit 1; }

mkdir -p /var/log/apache2
mkdir -p /srv/www/htdocs

skip_suse_tests=1 skip_suse_specifics=1 /usr/share/openqa/script/openqa-bootstrap &

echo "[INFO] Waiting for OpenQA WebUI to start..."
while ! curl -o /dev/null -w "%{http_code}" -sIL http://localhost/ | grep 200; do
    sleep 3
done

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

cat > /root/.bashrc <<EOF
export MOCK_MODE=1
export CASEDIR=/casedir
EOF

# Don't auto submit jobs in the mock. Let the user choose what jobs to run.
/casedir/worker.sh || true

echo "[INFO] Open a shell in the container to run jobs:"
echo "    podman exec -it openqa-single-instance bash"
echo "[INFO] Refer to README.md for instructions."
sleep infinity
