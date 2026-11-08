import json
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/health'):
            body = json.dumps({
                "status": "ok",
                "app": "nanocloud-demo",
                "hostname": socket.gethostname(),
            }).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path == '/' or self.path == '/index.html':
            try:
                with open('/demo/index.html', 'rb') as fh:
                    body = fh.read()
            except Exception:
                body = b'index.html not found'
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        body = b'Not found'
        self.send_response(404)
        self.send_header('Content-Type', 'text/plain')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
