#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import re
import os

url = "https://files.kde.org/kde-linux/?C=M;O=D"
base_url = "https://files.kde.org/kde-linux/"

# request and parse the image downloading site
resp = requests.get(url)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

# Exclude the .test.raw file
pattern = re.compile(r'kde-linux_\d+\.raw$')

# Find all links
links = soup.find_all("a", href=pattern)

# If found, pick the first one as it is ordered by desc.
if links:
    latest_href = links[0]["href"]
    download_url = base_url + latest_href
    print(f"Start downloading from: {download_url}")

    with requests.get(download_url, stream=True) as req:
        req.raise_for_status()
        with open(latest_href, 'wb') as file:
            for chunk in req.iter_content(chunk_size=8192):
                file.write(chunk)
    print("Download completed")
    print(f"Found the lastest file: {latest_href}")
else:
    print("Raw files not found")
    sys.exit(1)
