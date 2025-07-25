#!/bin/bash
# Test Base Directories
TEST_BASE_DIRS=("/installation-tests" "/fullsystem-test")

# Results Directory
RESULT_DIR="$CI_PROJECT_DIR/reports"

# Create destination directory
mkdir -p "$RESULT_DIR"

# Correct file names
FILES_TO_COPY=("video.ogv" "worker-log.txt" "serial_terminal.txt" "serial_terminal_user.txt" "autoinst-log.txt" \
               "virtio_console.log" "virtio_console_user.log" "virtio_console_user.out" "video_time.vtt")

for base_dir in "${TEST_BASE_DIRS[@]}"; do
    if [ -d "$base_dir" ]; then
        for filename in "${FILES_TO_COPY[@]}"; do
            src_file="$base_dir/$filename"
            if [ -f "$src_file" ]; then
                cp "$src_file" "$RESULT_DIR/$(basename "$base_dir")-$filename"
            fi
        done

        for job_dir in "$base_dir"/*; do
            if [ -d "$job_dir" ]; then
                for filename in "${FILES_TO_COPY[@]}"; do
                    src_file="$job_dir/$filename"
                    if [ -f "$src_file" ]; then
                        cp "$src_file" "$RESULT_DIR/$(basename "$job_dir")-$filename"
                    fi
                done
            fi
        done
    fi
done
