import contextlib
import importlib.util
import io
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class TelegramSecurityTests(unittest.TestCase):
    def load_notifier(self, credentials=True):
        requests = types.ModuleType("requests")
        requests.post = Mock()
        pandas = types.ModuleType("pandas")
        environment = {"TELEGRAM_BOT_TOKEN": "123456789:" + "A" * 35, "TELEGRAM_CHAT_ID": "42"} if credentials else {}
        with patch.dict(sys.modules, {"requests": requests, "pandas": pandas}), patch.dict(os.environ, environment, clear=True):
            path = Path(__file__).resolve().parents[1] / "scripts/telegram_notifier.py"
            spec = importlib.util.spec_from_file_location("security_test_notifier", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        return module, requests

    def test_missing_credentials_never_send(self):
        module, requests = self.load_notifier(False)
        with contextlib.redirect_stdout(io.StringIO()):
            module.send_telegram_message("test")
        requests.post.assert_not_called()

    def test_request_has_timeout_and_redacts_message(self):
        module, requests = self.load_notifier()
        module.send_telegram_message("exception URL contains " + module.BOT_TOKEN)
        kwargs = requests.post.call_args.kwargs
        self.assertEqual(kwargs["timeout"], 15)
        self.assertNotIn(module.BOT_TOKEN, kwargs["data"]["text"])
        requests.post.return_value.raise_for_status.assert_called_once()

    def test_network_exception_does_not_print_token(self):
        module, requests = self.load_notifier()
        requests.post.side_effect = RuntimeError("https://api.telegram.org/bot" + module.BOT_TOKEN)
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            module.send_telegram_message("test")
        self.assertNotIn(module.BOT_TOKEN, stream.getvalue())
        self.assertIn("RuntimeError", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
