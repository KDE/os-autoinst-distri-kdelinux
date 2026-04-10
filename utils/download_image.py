#!/usr/bin/python3
import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import glob

base_url = "https://files.kde.org/kde-linux/"

def find_local_file(filename):
    """Check if a matching .raw file already exists in the current directory."""
    if os.path.isfile(filename):
        print(f"Found existing file: {filename}")
        return filename
    return None

def download_file(download_url, filename):
    print(f"Start downloading from: {download_url}")
    with requests.get(download_url, stream=True) as req:
        req.raise_for_status()
        with open(filename, 'wb') as file:
            for chunk in req.iter_content(chunk_size=8192):
                file.write(chunk)
    print("Download completed")
    print(f"Downloaded file: {filename}")

def download(build_index):
    url = base_url + "?C=M;O=D"
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    pattern = re.compile(r'kde-linux_\d+\.raw$')
    links = soup.find_all("a", href=pattern)
    print(links)
    if links:
        latest_href = links[build_index]["href"]
        if find_local_file(latest_href):
            return
        download_url = base_url + latest_href
        download_file(download_url, latest_href)
    else:
        print("Raw files not found")
        sys.exit(1)

def download_specific(build_version):
    filename = f"kde-linux_{build_version}.raw"
    if find_local_file(filename):
        return
    download_url = base_url + filename
    try:
        resp = requests.head(download_url)
        if resp.status_code != 200:
            print(f"Specified build not found: {build_version}")
            sys.exit(1)
    except Exception as e:
        print(f"Error checking build: {e}")
        sys.exit(1)
    download_file(download_url, filename)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: script.py [--latest | --build=VERSION | --previously_success]")
        sys.exit(1)
    arg = sys.argv[1]
    if arg == "--latest":
        download(build_index=0)
    elif arg.startswith("--build="):
        build_version = arg.split("=", 1)[1]
        if not re.fullmatch(r"\d{12}", build_version):
            print("Invalid version format. Expected format: YYYYMMDDHHMM")
            sys.exit(1)
        download_specific(build_version)
    elif arg == "--previously-success":
        """
            Each build appears twice in the list: one icon link and one text link.
            To get the previous successful build, we skip the latest (index 0 and 1) and pick index 2.
        """
        download(build_index=2)
    else:
        print("Unknown argument")
        sys.exit(1)
