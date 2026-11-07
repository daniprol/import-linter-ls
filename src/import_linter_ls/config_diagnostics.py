"""Check an import-linter config file and say where each mistake is.

The adapter finds the mistakes (import-linter knows which options are valid), and the scanner in
`config_positions` finds the lines. This module joins the two into LSP diagnostics.
"""

from pathlib import Path

from lsprotocol import types

from import_linter_ls.config_positions import ConfigPositions, Section, Span, find_positions
from import_linter_ls.import_linter_adapter import ConfigProblem, check_config


def config_diagnostics(config_file: Path, file_format: str) -> list[types.Diagnostic]:
    """Return one diagnostic (a squiggly line with a message) for each mistake in `config_file`."""
    text = config_file.read_text(encoding="utf-8")
    positions = find_positions(text, file_format)
    lines = text.splitlines()
    return [
        types.Diagnostic(
            range=to_range(span_of(problem, positions, lines)),
            message=problem.message,
            severity=types.DiagnosticSeverity.Error,
            source="import-linter",
        )
        for problem in check_config(config_file, file_format)
    ]


def span_of(problem: ConfigProblem, positions: ConfigPositions, lines: list[str]) -> Span:
    """Pick the best place to underline: the option, else its section header, else the start of the file."""
    if problem.line is not None:  # a syntax error: underline the whole line the parser reported
        # The parser counts lines from 1. It can also point one line past the end, for example at an
        # unclosed bracket, so we stay inside the file.
        line_index = max(0, min(problem.line - 1, len(lines) - 1))
        return Span(line_index, 0, len(lines[line_index]) if lines else 0)

    section = positions.session if problem.contract_index is None else contract_at(positions, problem.contract_index)
    if section is None:
        return Span(0, 0, 0)
    # A missing option has no line of its own, so we underline the section header instead.
    return section.options.get(problem.option or "", section.header)


def contract_at(positions: ConfigPositions, contract_index: int) -> Section | None:
    """The contract section at `contract_index`, or None if the scanner did not find that many."""
    if contract_index < len(positions.contracts):
        return positions.contracts[contract_index]
    return None


def to_range(span: Span) -> types.Range:
    return types.Range(
        start=types.Position(line=span.line, character=span.start),
        end=types.Position(line=span.line, character=span.end),
    )
