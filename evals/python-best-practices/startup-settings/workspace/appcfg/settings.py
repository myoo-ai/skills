"""Worker settings: environment variables override the defaults."""

import os

DEFAULTS = {
    "log_level": "INFO",
    "timeout": 30,
    "retries": 3,
    "proxy": None,
}


def get_setting(name, default=None):
    """Return setting `name` from APPCFG_<NAME>, else the defaults, else `default`."""
    value = os.environ.get("APPCFG_" + name.upper())
    if value is not None:
        return value
    if name in DEFAULTS:
        return DEFAULTS[name]
    return default
