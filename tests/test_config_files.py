"""Unit tests for finding config files: plain functions, so no server is needed."""

from pathlib import Path

import pytest

from import_linter_ls.config_files import config_format, find_config_file

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


def test_find_config_file_walks_up_to_the_config_file(example_app: Path) -> None:
    storage_file = example_app / "src" / "layered_app" / "low" / "storage.py"

    assert find_config_file(storage_file) == example_app / "pyproject.toml"


def test_find_config_file_prefers_the_nearest_folder(example_app: Path) -> None:
    # The example app has a second, INI copy of its config in `ini/`.
    assert find_config_file(example_app / "ini" / ".importlinter") == example_app / "ini" / ".importlinter"
