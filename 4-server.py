"""Small HTTP wrapper around Wisecow's fortune and cowsay commands."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from html import escape
import os
import subprocess

PORT = int(os.environ.get("PORT", "4499"))


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self._respond(200, "ok\n", "text/plain; charset=utf-8")
            return
        if self.path != "/":
            self._respond(404, "not found\n", "text/plain; charset=utf-8")
            return
        try:
            fortune = subprocess.run(["fortune", "-s"], check=True, capture_output=True,
                                     text=True, timeout=5).stdout
            cow = subprocess.run(["cowsay"], input=fortune, check=True,
                                 capture_output=True, text=True, timeout=5).stdout
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            self._respond(503, "wisdom unavailable\n", "text/plain; charset=utf-8")
            return
        self._respond(200, f"<!doctype html><meta charset='utf-8'><title>Wisecow</title><pre>{escape(cow)}</pre>\n",
                      "text/html; charset=utf-8")

    def _respond(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
