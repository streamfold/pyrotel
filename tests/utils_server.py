from __future__ import annotations

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest


class RequestTracker:
    def __init__(self):
        self.trace_count = 0

    def increment(self):
        self.trace_count += 1

    def get_count(self):
        return self.trace_count

    def reset(self):
        self.trace_count = 0

class MockServer(BaseHTTPRequestHandler):
    tracker = RequestTracker()

    @classmethod
    def reset_count(cls):
        cls.tracker.reset()

    def do_POST(self):
        if self.path == '/v1/traces':
            self.tracker.increment()
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

