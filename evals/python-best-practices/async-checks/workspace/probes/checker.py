"""Run health probes against hosts."""

from collections.abc import Awaitable, Callable

type Probe = Callable[[str], Awaitable[bool]]
"""An async function that reports whether a host is healthy."""


def normalize_host(host: str) -> str:
    """Return host lowercased, without scheme, port or trailing dot."""
    host = host.strip().lower()
    _, sep, rest = host.partition("://")
    if sep:
        host = rest
    host = host.split("/", 1)[0].rsplit(":", 1)[0]
    return host.removesuffix(".")
