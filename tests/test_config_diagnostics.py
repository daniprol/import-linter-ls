"""Unit tests for config diagnostics: write a config file, check it, and look at what is underlined."""

from pathlib import Path

import pytest

from import_linter_ls.config_diagnostics import config_diagnostics

pytestmark = pytest.mark.unit


def check(folder: Path, file_name: str, text: str) -> list[tuple[int, str]]:
    """Write a config file and return its diagnostics as (line, message) pairs, to keep the asserts short."""
    config_file = folder / file_name
    config_file.write_text(text)
    file_format = "toml" if file_name.endswith(".toml") else "ini"
    return [
        (diagnostic.range.start.line, diagnostic.message) for diagnostic in config_diagnostics(config_file, file_format)
    ]


@pytest.mark.parametrize("config_file", ["pyproject.toml", "ini/.importlinter"])
def test_the_example_app_config_has_no_problems(example_app: Path, config_file: str) -> None:
    file_format = "toml" if config_file.endswith(".toml") else "ini"

    assert config_diagnostics(example_app / config_file, file_format) == []


def test_a_pyproject_without_import_linter_config_has_no_problems(tmp_path: Path) -> None:
    assert check(tmp_path, "pyproject.toml", '[project]\nname = "app"\n') == []


def test_an_ini_syntax_error_is_shown_on_its_line(tmp_path: Path) -> None:
    text = "[importlinter]\nroot_package = my_app\n= no name\n"

    assert check(tmp_path, ".importlinter", text) == [
        (2, "Invalid INI: this line is not a section, an option or a continuation"),
    ]


def test_a_toml_syntax_error_is_shown_on_its_line(tmp_path: Path) -> None:
    text = '[tool.importlinter]\nroot_package = "my_app\n'

    [(line, message)] = check(tmp_path, "pyproject.toml", text)
    assert line == 1
    assert message.startswith("Invalid TOML")


def test_every_broken_contract_is_reported_on_the_right_line(tmp_path: Path) -> None:
    text = """\
[importlinter]
root_package = my_app

[importlinter:contract:one]
name = One
type = layer
layers = my_app.a

[importlinter:contract:two]
name = Two
type = forbidden
source_modules = my_app.a
forbiden_modules = my_app.b
"""

    assert check(tmp_path, ".importlinter", text) == [
        (5, "Unknown contract type 'layer'. Did you mean 'layers'?"),
        (8, "Missing required option 'forbidden_modules'."),  # missing: shown on the section header
        (12, "'forbiden_modules': Unrecognized option. Did you mean 'forbidden_modules'?"),
    ]


def test_missing_general_options_and_names_are_reported_in_toml(tmp_path: Path) -> None:
    text = """\
[tool.importlinter]

[[tool.importlinter.contracts]]
type = "independence"
modules = ["my_app.a", "my_app.b"]
"""

    assert check(tmp_path, "pyproject.toml", text) == [
        (0, "Missing required option 'root_package' (or 'root_packages')."),
        (2, "Missing required option 'name'."),
    ]


def test_custom_contract_types_are_not_checked(tmp_path: Path) -> None:
    text = """\
[importlinter]
root_package = my_app
contract_types = my_type: my_app.contracts.MyContract

[importlinter:contract:one]
name = One
type = my_type
anything = goes
"""

    assert check(tmp_path, ".importlinter", text) == []
