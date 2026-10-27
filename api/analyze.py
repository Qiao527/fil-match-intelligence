"""Explicit Vercel Python entrypoint; implementation shared with local runtime."""

from api.index import handler as PublicHandler


class handler(PublicHandler):
    """Vercel discovers a top-level handler class, including inherited methods."""
