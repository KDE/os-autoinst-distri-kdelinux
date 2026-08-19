# SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

import json

from websockets.sync.client import connect

_AUTOINST_URL = "ws://10.0.2.2:8765"

_WS_HOST = "0.0.0.0"
_WS_PORT = 8765


class OpenQAAutoinst:
    """Wrapper for autoinst testapi from the SUT"""

    def __init__(self):
        pass

    def call_testapi(self, funcname: str, *args) -> str:
        """This can be used to call the testapi functions on os-autoinst testapi"""
        payload = [funcname, args]
        try:
            with connect(_AUTOINST_URL) as websocket:
                websocket.send(json.dumps(payload))
                response = websocket.recv()
                return response
        except Exception as e:
            print(f"Failed to connect to openQA server {e}")
