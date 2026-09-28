import sys
import unittest
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from health_check import check
from log_report import summarize


class TestScripts(unittest.TestCase):
    def test_access_log(self):
        rows = [
            '192.0.2.1 - - [28/Sep/2026:10:00:00 +0530] "GET / HTTP/1.1" 200 10\n',
            '192.0.2.1 - - [28/Sep/2026:10:01:00 +0530] "GET /lost HTTP/1.1" 404 10\n',
            'bad row\n',
        ]
        total, missing, skipped, paths, ips = summarize(rows)
        self.assertEqual((total, missing, skipped), (2, 1, 1))
        self.assertEqual(paths['/lost'], 1)
        self.assertEqual(ips['192.0.2.1'], 2)

    def test_http_status(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200 if self.path == '/ok' else 503)
                self.end_headers()
            def log_message(self, *args):
                pass
        server = HTTPServer(('127.0.0.1', 0), Handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            base = f'http://127.0.0.1:{server.server_port}'
            self.assertEqual(check(base + '/ok', 1), (True, 'HTTP 200'))
            self.assertEqual(check(base + '/bad', 1), (False, 'HTTP 503'))
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == '__main__':
    unittest.main()
