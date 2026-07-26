# SPDX-FileCopyrightText: 2026 Blender Authors
#
# SPDX-License-Identifier: GPL-3.0-or-later

import importlib.util
import os
import unittest
from types import SimpleNamespace
from unittest import mock

_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "chat_client",
    "chat_client.py",
)
_SPEC = importlib.util.spec_from_file_location("blender_chat_client", _PATH)
assert _SPEC is not None and _SPEC.loader is not None
chat_client = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(chat_client)


class TestChatClientHelpers(unittest.IsolatedAsyncioTestCase):
    def test_openai_malformed_tool_arguments_are_reported(self) -> None:
        response = {
            "choices": [{
                "finish_reason": "tool_calls",
                "message": {
                    "tool_calls": [{
                        "id": "call-1",
                        "function": {"name": "test", "arguments": "{"},
                    }],
                },
            }],
        }
        _message, calls, _text, _done = chat_client._process_openai_response(response)
        self.assertEqual(calls[0][0:2], ("call-1", "test"))
        self.assertIsNone(calls[0][2])
        self.assertIsNotNone(calls[0][3])

    async def test_call_tool_preserves_error_state(self) -> None:
        result = SimpleNamespace(
            content=[SimpleNamespace(type="text", text="failed")],
            isError=True,
        )
        session = mock.AsyncMock()
        session.call_tool.return_value = result
        text, is_error = await chat_client._call_tool(session, "test", {})
        self.assertEqual(text, "ERROR: failed")
        self.assertTrue(is_error)

    def test_http_helpers_apply_timeout(self) -> None:
        response = mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'{"choices": []}'
        with mock.patch.object(chat_client.urllib.request, "urlopen", return_value=response) as urlopen:
            chat_client._api_chat_completions("http://localhost", [], [], None)
        self.assertEqual(urlopen.call_args.kwargs["timeout"], chat_client._HTTP_TIMEOUT)

    def test_shlex_preserves_quoted_command_parts(self) -> None:
        self.assertEqual(
            chat_client.shlex.split('"/tmp/My Server/mcp" --flag "value with spaces"'),
            ["/tmp/My Server/mcp", "--flag", "value with spaces"],
        )


if __name__ == "__main__":
    unittest.main()
