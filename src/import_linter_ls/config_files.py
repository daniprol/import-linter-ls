"""Finding out which files are import-linter config files."""

from pathlib import Path

# import-linter reads its config from these files (see its docs, "Usage").
# `.importlinter` and `setup.cfg` use the INI format, `pyproject.toml` uses TOML.
INI_CONFIG_FILE_NAMES = frozenset({".importlinter", "setup.cfg"})
TOML_CONFIG_FILE_NAMES = frozenset({"pyproject.toml"})

# Some projects pass their own file with `lint-imports --config my_file`. We cannot know those names,
# so we only recognise the three default ones for now.


def config_format(path: Path) -> str | None:
    """Return "ini" or "toml" if `path` can hold import-linter config, otherwise None.

    Only the file name is checked. A `pyproject.toml` or `setup.cfg` is only a *candidate*: it
    holds import-linter config only if it has an `importlinter` section.
    """
    if path.name in INI_CONFIG_FILE_NAMES:
        return "ini"
    if path.name in TOML_CONFIG_FILE_NAMES:
        return "toml"
    return None
