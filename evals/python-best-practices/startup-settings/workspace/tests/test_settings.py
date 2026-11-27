import contextlib
import io
import os
import unittest
from unittest import mock

from appcfg.cli import main
from appcfg.settings import DEFAULTS, get_setting


class SettingsTest(unittest.TestCase):
    def test_defaults(self):
        with mock.patch.dict(os.environ, clear=True):
            self.assertEqual(get_setting("timeout"), 30)
            self.assertIsNone(get_setting("proxy"))
            self.assertEqual(DEFAULTS["retries"], 3)

    def test_environment_wins(self):
        with mock.patch.dict(os.environ, {"APPCFG_LOG_LEVEL": "DEBUG"}):
            self.assertEqual(get_setting("log_level"), "DEBUG")

    def test_cli(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, clear=True), contextlib.redirect_stdout(out):
            self.assertEqual(main(["get", "retries"]), 0)
            self.assertEqual(main(["report"]), 0)
        self.assertIn("3\n", out.getvalue())
        self.assertIn("log_level", out.getvalue())
