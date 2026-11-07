"""Unit tests for the scanner that finds where sections and options are in a config file."""

import pytest

from import_linter_ls.config_positions import Span, find_positions

pytestmark = pytest.mark.unit

INI_CONFIG = """\
[metadata]
name = not-ours

[importlinter]
root_package = my_app

[importlinter:contract:layers]
name = Layers
type = layers
layers =
    my_app.high
    my_app.low
"""

TOML_CONFIG = """\
[project]
name = "not-ours"

[tool.importlinter]
root_package = "my_app"

[[tool.importlinter.contracts]]
name = "Layers"
type = "layers"
layers = [
    "my_app.high",
    "my_app.low",
]

[[tool.importlinter.contracts]]
name = "Independent"
"""


def test_ini_sections_and_options_are_found() -> None:
    positions = find_positions(INI_CONFIG, "ini")

    assert positions.session is not None
    assert positions.session.header == Span(line=3, start=1, end=13)
    assert positions.session.options == {"root_package": Span(line=4, start=0, end=12)}
    assert len(positions.contracts) == 1
    assert list(positions.contracts[0].options) == ["name", "type", "layers"]


def test_other_sections_are_ignored() -> None:
    positions = find_positions(INI_CONFIG, "ini")

    assert positions.session is not None
    assert "name" not in positions.session.options  # `name` of [metadata] is not ours


def test_ini_option_names_are_lowercase_like_configparser_makes_them() -> None:
    positions = find_positions("[importlinter]\nRoot_Package = my_app\n", "ini")

    assert positions.session is not None
    assert list(positions.session.options) == ["root_package"]


def test_toml_contracts_are_found_in_file_order() -> None:
    positions = find_positions(TOML_CONFIG, "toml")

    assert positions.session is not None
    assert positions.session.header.line == 3
    assert [contract.header.line for contract in positions.contracts] == [6, 14]
    assert list(positions.contracts[0].options) == ["name", "type", "layers"]
    assert list(positions.contracts[1].options) == ["name"]


def test_lines_inside_a_toml_array_are_not_options() -> None:
    text = '[[tool.importlinter.contracts]]\nignore_imports = [\n    "a.b -> c.d",\n]\n'

    assert list(find_positions(text, "toml").contracts[0].options) == ["ignore_imports"]
