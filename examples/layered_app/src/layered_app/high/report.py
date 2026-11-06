"""High level code: builds a report using the low level storage. This direction is allowed."""

from layered_app.low import storage


def build_report() -> str:
    return f"{len(storage.load_items())} items"
