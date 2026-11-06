"""Unit tests: `config_format` is a plain function, so no server is needed."""

from pathlib import Path

import pytest

from import_linter_ls.config_files import config_format

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("file_name", "expected_format"),
    [
        (".importlinter", "ini"),
        ("setup.cfg", "ini"),
        ("pyproject.toml", "toml"),
        ("settings.py", None),
        ("importlinter.toml", None),
    ],
)
def test_config_format_is_found_from_the_file_name(file_name: str, expected_format: str | None) -> None:
    assert config_format(Path("/some/project") / file_name) == expected_format
