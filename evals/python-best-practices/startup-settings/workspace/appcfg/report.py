"""The `appcfg report` command."""

import time

from appcfg.settings import DEFAULTS, get_setting

# Stands in for compiling our report templates, which takes a while.
time.sleep(0.5)


def render() -> str:
    """Return a table of every setting and its current value."""
    width = max(len(name) for name in DEFAULTS)
    return "\n".join(f"{name:<{width}}  {get_setting(name)!r}" for name in DEFAULTS)
