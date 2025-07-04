#!/bin/bash

for i in {1..10}; do
  if curl -s http://localhost/api/v1/jobs >/dev/null; then
    echo "[INFO] openQA is ready"
    break
  fi
  echo "[INFO] Waiting for openQA..."
  sleep 3
done