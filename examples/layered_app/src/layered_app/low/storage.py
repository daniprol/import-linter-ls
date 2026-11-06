"""Low level code: loads items from storage."""

# BROKEN ON PURPOSE: `low` must not import from `high`. import-linter reports this line.
from layered_app.high import report  # noqa: F401


def load_items() -> list[str]:
    return ["apple", "pear"]
