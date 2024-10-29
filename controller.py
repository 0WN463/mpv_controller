import socket
import sys
import json
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
        self.path = 'page.html' 

        with open('page.html', 'r') as f:
            self.wfile.write(f.buffer.read())

    def do_POST(self) -> None:
        parsed_url = urlparse(self.path)
        route = parsed_url.path
        query_params = parse_qs(parsed_url.query)

        if route == '/playpause':
            send_to_socket('cycle pause')
            self.send_response(204)
            self.end_headers()
            return
        
httpd = HTTPServer(('', PORT), SimpleHTTPRequestHandler)
httpd.serve_forever()
