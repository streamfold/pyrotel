# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import threading
from email.message import Message
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class Request:
    path: str
    headers: Message

    def __init__(self, path: str, headers : Message):
        self.path = path
        self.headers = headers

class RequestTracker:
    _requests: list[Request]

    def __init__(self):
        self._requests = []

    def add(self, req : Request):
        self._requests.append(req)

    def get_count(self):
        return len(self._requests)

    def get_requests(self):
        return self._requests

    def reset(self):
        self._requests = []

class MockServer(BaseHTTPRequestHandler):
    tracker = RequestTracker()

    @classmethod
    def reset_count(cls):
        cls.tracker.reset()

    def do_POST(self):
        if self.path == '/v1/traces':
            req = Request(self.path, self.headers)
            self.tracker.add(req)
            self.send_response(200)
        elif self.path == '/api/v0.2/traces': # datadog
            req = Request(self.path, self.headers)
            self.tracker.add(req)
            self.send_response(200)
        elif self.path.startswith('/?database='): # clickhouse
            req = Request(self.path, self.headers)
            self.tracker.add(req)
            self.send_response(200)
        else:
            self.send_response(404)
        self.end_headers()

class MockServerHandle:
    def __init__(self, server: HTTPServer):
        self.thr = None
        self.server = server

    def with_thr(self, thr: threading.Thread):
        self.thr = thr

    def address(self):
        return self.server.server_address

    def stop(self):
        if self.server is not None:
            self.server.shutdown()
            self.server = None
        self.thr.join(1)

@pytest.fixture
def mock_server():
    httpd = HTTPServer(('localhost', 0), MockServer)
    handle = MockServerHandle(httpd)
    thr = threading.Thread(target=run_server, args=(handle,))
    thr.start()
    handle.with_thr(thr)

    yield handle

    handle.stop()

def run_server(hnd: MockServerHandle):
    hnd.server.serve_forever()
    # if we exit early we may end up blocking on shutdown
    hnd.server = None

