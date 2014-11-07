# -*- coding: utf-8 -*-

"""
This module contains configuration tests for the Relayr restful HTTP API client.

Attention: The configuration mechanism is likely to change.
"""

import os
import json
import socket
from threading import Thread
try:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
except ImportError:
    from http.server import HTTPServer, BaseHTTPRequestHandler

import pytest

from relayr.compat import PY3


def get_free_port():
    "Return a free port number."

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    port = sock.getsockname()[1]
    return port


class GetHandler(BaseHTTPRequestHandler):
    "A handler that returns the received HTTP header as serialized JSON body."

    def do_GET(self):
        message = json.dumps(dict(self.headers.items()), indent=4)
        self.send_response(200)
        self.end_headers()
        if PY3:
            self.wfile.write(bytes(message, 'UTF-8'))
        else:
            self.wfile.write(message)


class MyThread(Thread):
    "A tiny HTTP server running in a thread."

    def __init__(self, port):
        Thread.__init__(self)
        self.port = port

    def run(self):
        self.server = HTTPServer(('localhost', self.port), GetHandler)
        self.server.serve_forever()

    def stop(self):
        self.server.shutdown()


class TestConfig(object):
    "Test configuration aspects."

    def test_change_useragent(self):
        "Test changing the HTTP useragent string."

        from relayr import config
        from relayr.api import Api
        port = get_free_port()
        t = MyThread(port)
        t.start()

        previous = config.relayrAPI[:]

        url = 'http://localhost:%d' % port
        config.relayrAPI = url

        if PY3:
            user_agent_key = 'User-Agent'
        else:
            user_agent_key = 'user-agent'

        # default config user-agent
        headers = Api().get_server_status()
        assert headers[user_agent_key] == config.userAgent

        # modified config user-agent
        config.userAgent = 'Python Relayr API Super Special Testing Agent'
        headers = Api().get_server_status()
        assert headers[user_agent_key] == config.userAgent

        t.stop()

        config.relayrAPI = previous
