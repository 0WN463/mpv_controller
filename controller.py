#!/usr/bin/env python3

import json
import socket
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 8000
socket_path = sys.argv[1]

def send_to_socket(cmd: str) -> None:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(socket_path)
            sock.sendall((cmd + '\n').encode())
        except socket.error as e:
            print(f"Socket error: {e}")

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.end_headers()

        if self.path == '/':
            with open('page.html', 'r') as f:
                self.wfile.write(f.buffer.read())
                return
        elif self.path == '/style.css':
            with open('style.css', 'r') as f:
                self.wfile.write(f.buffer.read())
                return

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        route = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        match route:
            case '/playpause':
                send_to_socket('cycle pause')
            case '/seek':
                amt, *_ = query_params['amt']
                send_to_socket(f'seek {amt}')
            case '/volume':
                amt, *_ = query_params['amt']
                send_to_socket(f'set volume {amt}')
            case '/info':
                send_to_socket('{"command": ["expand-properties", "osd-msg-bar", "show-text", "${media-title}\\n${time-pos}/${duration}"]}')

        self.send_response(204)
        self.end_headers()
        
httpd = HTTPServer(('', PORT), SimpleHTTPRequestHandler)
httpd.serve_forever()
