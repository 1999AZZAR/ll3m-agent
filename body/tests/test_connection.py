# SPDX-FileCopyrightText: 2026 Blender Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib
import os
import sys
import unittest
from unittest import mock

_MCP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mcp")
if _MCP_DIR not in sys.path:
    sys.path.insert(0, _MCP_DIR)

connection = importlib.import_module("blmcp.tools_helpers.connection")


class _FakeSocket:
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = iter(chunks)

    def __enter__(self):
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def settimeout(self, _timeout: float) -> None:
        pass

    def connect(self, _address: tuple[str, int]) -> None:
        pass

    def sendall(self, _data: bytes) -> None:
        pass

    def recv(self, _size: int) -> bytes:
        return next(self.chunks, b"")


class TestConnectionResponseValidation(unittest.TestCase):
    def _send(self, chunks: list[bytes]):
        with mock.patch.object(connection.socket, "socket", return_value=_FakeSocket(chunks)):
            return connection.send_code("result = {}", strict_json=True)

    def test_accepts_fragmented_object_response(self) -> None:
        self.assertEqual(self._send([b'{"status":', b'"ok"}\0']), {"status": "ok"})

    def test_rejects_non_object_json_response(self) -> None:
        for payload in (b"[]\0", b"null\0", b'"ok"\0'):
            with self.subTest(payload=payload):
                with self.assertRaises(ConnectionError):
                    self._send([payload])


if __name__ == "__main__":
    unittest.main()
