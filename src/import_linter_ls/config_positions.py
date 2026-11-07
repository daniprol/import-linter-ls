"""Find where the import-linter sections and options are in a config file.

import-linter parses config with `configparser` (INI) and `tomllib` (TOML). Both give back plain values
and forget which line each one came from, but a diagnostic needs a line. So we scan the text ourselves.

The scanner does not parse values: the real parsers already do that. It only looks for two kinds of lines:
- section headers: `[importlinter:contract:layers]` (INI) or `[[tool.importlinter.contracts]]` (TOML)
- option names at the start of a line: `layers = ...` (INI) or `layers = [` (TOML)
Lines inside a multi-line value (the INI continuation lines, the items of a TOML array) never look like
`name =` at the start of a line, so they are skipped.
"""

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Span:
    """A piece of one line. Lines and characters are counted from 0, as LSP does."""

    line: int
    start: int
    end: int


@dataclass
class Section:
    """An import-linter section: where its header is, and where each of its options is."""

    header: Span
    options: dict[str, Span] = field(default_factory=dict)


@dataclass
class ConfigPositions:
    """The positions of the general `importlinter` section and of each contract, in file order."""

    session: Section | None = None
    contracts: list[Section] = field(default_factory=list)


# `[name]` or `[[name]]`, with optional spaces inside the brackets.
SECTION_HEADER = re.compile(r"^\s*\[\[?\s*(?P<name>[^\]]+?)\s*\]\]?")
# An option name at the very start of the line, followed by `=` (or `:` in INI).
INI_OPTION = re.compile(r"^(?P<name>[\w.-]+)\s*[=:]")
TOML_OPTION = re.compile(r"^\s*(?P<name>[\w-]+)\s*=")


def find_positions(text: str, file_format: str) -> ConfigPositions:
    """Scan `text` (in "ini" or "toml" format) for the import-linter sections and their options."""
    option_pattern = INI_OPTION if file_format == "ini" else TOML_OPTION
    positions = ConfigPositions()
    current_section: Section | None = None  # None while we are outside any import-linter section

    for line_number, line in enumerate(text.splitlines()):
        header = SECTION_HEADER.match(line)
        if header:
            section_kind = import_linter_section_kind(header["name"], file_format)
            current_section = None
            if section_kind is not None:
                current_section = Section(Span(line_number, header.start("name"), header.end("name")))
                if section_kind == "session":
                    positions.session = current_section
                else:
                    positions.contracts.append(current_section)
            continue

        option = option_pattern.match(line)
        if option and current_section is not None:
            # configparser makes option names lowercase, so we do too. TOML keeps them as they are.
            name = option["name"].lower() if file_format == "ini" else option["name"]
            current_section.options.setdefault(name, Span(line_number, option.start("name"), option.end("name")))

    return positions


def import_linter_section_kind(section_name: str, file_format: str) -> str | None:
    """Say whether a section holds the general options ("session"), a contract ("contract"), or neither (None).

    The names are the ones import-linter's own readers look for.
    """
    if file_format == "ini":
        if section_name == "importlinter":
            return "session"
        if section_name.startswith("importlinter:"):  # importlinter:contract:<id>
            return "contract"
    else:
        if section_name == "tool.importlinter":
            return "session"
        if section_name == "tool.importlinter.contracts":
            return "contract"
    return None
