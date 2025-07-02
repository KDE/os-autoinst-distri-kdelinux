#!/bin/bash

# Install dependencies
zypper --non-interactive install perl-Inline-Python python3-requests python3-beautifulsoup4

# Download the lastest live image
IMG=$(python3 scripts/download_image.py | grep "Found the lastest file" | cut -d ':' -f 2 | xargs)
OUTPUT=${IMG_NAME%.raw}
DISK=${OUTPUT}.qcow2

OPENQA_API_KEY=
OPENQA_API_SECRET=