import collections.abc
import contextlib
import io
import os
import subprocess
import sys
import unittest
from unittest import mock

from appcfg.settings import DEFAULTS, get_setting

PROBE = "import sys, appcfg.cli, appcfg.settings; assert 'appcfg.report' not in sys.modules, 'report imported at startup'"


class GraderTest(unittest.TestCase):
    def test_missing_setting(self):
        with mock.patch.dict(os.environ, clear=True):
            with self.assertRaises(KeyError):
                get_setting("colour")
            self.assertIsNone(get_setting("colour", None))
            self.assertIsNone(get_setting("colour", default=None))
            self.assertEqual(get_setting("colour", "blue"), "blue")
            self.assertIsNone(get_setting("proxy"))
            self.assertEqual(get_setting("timeout"), 30)
            self.assertEqual(get_setting("timeout", 5), 30)
        with mock.patch.dict(os.environ, {"APPCFG_COLOUR": "red"}):
            self.assertEqual(get_setting("colour"), "red")

    def test_defaults_read_only(self):
        self.assertIsInstance(DEFAULTS, collections.abc.Mapping)
        self.assertEqual(dict(DEFAULTS), {"log_level": "INFO", "timeout": 30, "retries": 3, "proxy": None})
        with self.assertRaises(TypeError):
            DEFAULTS["timeout"] = 0
        with self.assertRaises((TypeError, AttributeError)):
            DEFAULTS.update(timeout=0)
        self.assertEqual(DEFAULTS["timeout"], 30)

    def test_report_not_loaded_at_startup(self):
        subprocess.run([sys.executable, "-X", "dev", "-W", "error", "-c", PROBE], check=True)

    def test_commands_still_work(self):
        out = io.StringIO()
        with mock.patch.dict(os.environ, clear=True), contextlib.redirect_stdout(out):
            from appcfg.cli import main
            self.assertEqual(main(["get", "retries"]), 0)
            self.assertEqual(main(["report"]), 0)
        self.assertIn("retries", out.getvalue())
        self.assertIn("'INFO'", out.getvalue())
