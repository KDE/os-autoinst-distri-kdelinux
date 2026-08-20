# SPDX-License-Identifier: LGPL-2.0-only OR LGPL-3.0-only OR LicenseRef-KDE-Accepted-LGPL
# SPDX-FileCopyrightText: 2026 Bhushan Shah <bhushan.shah@machinesoul.in>

import asyncio
import json

from testapi import *
from websockets.asyncio.server import serve

from lib.common.log import get_logger

_WS_HOST = "0.0.0.0"
_WS_PORT = 8765

log = get_logger(__name__)


class QueueError(Exception):
    """Exception raised when tried to start commands in parallel"""


class AutoinstProxy:
    """Proxy server for autoinst testapi from the SUT"""

    def __init__(self):
        self.background_loop = None
        self.background_task = None
        self.server = None
        self.request: str = None
        self.api = {
            "assert_and_click": assert_and_click,
            "assert_screen": assert_screen,
            "assert_screen_change": assert_screen_change,
            "check_screen": check_screen,
            "record_info": record_info,
            "record_soft_failure": record_soft_failure,
            "wait_screen_change": wait_screen_change,
            "wait_still_screen": wait_still_screen,
        }

    def handle_queue(self):
        if self.request:
            payload: dict = json.loads(self.request)
            command: str = payload[0]
            args = payload[1]
            if command not in self.api:
                raise ValueError(f"Unknown command {command}")
            self.api[command](*args)
            self.request = None

    async def _handler(self, websocket):
        async for message in websocket:
            log.info(f"Message from SUT {message}")
            if self.request:
                raise QueueError(
                    f"Request {message} recieved when {self.request} was processing."
                )
            self.request = message
            while self.request:
                await asyncio.sleep(1)
            await websocket.send("pass")

    async def _apitest_proxy(self):
        try:
            self.server = await serve(self._handler, _WS_HOST, _WS_PORT)
            await self.server.serve_forever()
        except asyncio.CancelledError:
            self.server.close()
            await server.wait_closed()
            raise ()

    def start_ws(self):
        self.background_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.background_loop)
        self.background_task = self.background_loop.create_task(self._apitest_proxy())
        self.background_loop.run_forever()

    def stop(self):
        if self.background_loop and self.background_task:
            self.background_loop.call_soon_threadsafe(self.background_task.cancel)
