from __future__ import annotations

import threading

from http.server import HTTPServer, BaseHTTPRequestHandler, ThreadingHTTPServer

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
    def __init__(self, server: HTTPServer, thr: threading.Thread):
        self.server = server
        self.thr = thr

    def address(self):
        return self.server.server_address

    def stop(self):
        self.server.shutdown()
        self.thr.join(1)

def new_server() -> MockServerHandle:
    httpd = HTTPServer(('localhost', 0), MockServer)
    thr = threading.Thread(target=run_server, args=(httpd,))
    thr.start()

    return MockServerHandle(httpd, thr)

def run_server(srv: HTTPServer):
    srv.serve_forever()

