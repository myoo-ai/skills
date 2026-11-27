"""Command line: `appcfg get NAME` and `appcfg report`."""

import sys

from appcfg import report
from appcfg.settings import get_setting


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    match args:
        case ["get", name]:
            print(get_setting(name))
            return 0
        case ["report"]:
            print(report.render())
            return 0
    print("usage: appcfg get NAME | appcfg report", file=sys.stderr)
    return 2
