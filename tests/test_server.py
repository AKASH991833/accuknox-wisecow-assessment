import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from io import BytesIO
from http.server import HTTPServer
from threading import Thread
from urllib.error import HTTPError
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import Handler


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_health(self):
        with urlopen(self.base + '/healthz') as resp:
            self.assertEqual((resp.status, resp.read()), (200, b'ok\n'))

    def test_unknown_path(self):
        with self.assertRaises(HTTPError) as raised:
            urlopen(self.base + '/missing')
        self.assertEqual(raised.exception.code, 404)

    def test_fortune_error(self):
        with patch('server.subprocess.run', side_effect=FileNotFoundError('fortune missing')):
            with self.assertRaises(HTTPError) as raised:
                urlopen(self.base + '/')
        self.assertEqual(raised.exception.code, 503)

    def test_cow_escaping(self):
        class Result:
            def __init__(self, stdout): self.stdout = stdout
        with patch('server.subprocess.run', side_effect=[Result('hello'), Result('<cow>')]):
            with urlopen(self.base + '/') as resp:
                self.assertIn(b'&lt;cow&gt;', resp.read())


if __name__ == '__main__':
    unittest.main()
