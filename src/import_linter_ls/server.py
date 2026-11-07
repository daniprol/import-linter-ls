"""The language server: connects pygls to our features.

This file only wires things together. The actual logic lives in small modules next to it.
"""

import asyncio
from pathlib import Path

from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path

from import_linter_ls import __version__
from import_linter_ls.config_diagnostics import config_diagnostics
from import_linter_ls.config_files import config_format, find_config_file
from import_linter_ls.violations import Violation, parse_report, run_import_linter

# A language server is a program that an editor starts and talks to with JSON messages (the Language
# Server Protocol, LSP). The editor sends events ("the user opened this file") and we answer or
# send back results ("these lines have problems"). pygls handles the JSON and the protocol for us.
server = LanguageServer("import-linter-ls", __version__)


def log(message: str) -> None:
    """Send a message to the editor's log (VS Code shows it in the extension's output channel)."""
    server.window_log_message(types.LogMessageParams(type=types.MessageType.Info, message=message))


@server.feature(types.INITIALIZED)
def on_initialized(_params: types.InitializedParams) -> None:
    """The editor finished the handshake: from now on it may send us events."""
    log(f"import-linter-ls {__version__} is ready")


# Files that currently show our diagnostics. We must send an empty list for a file once it is fixed.
files_with_diagnostics: set[str] = set()


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
async def on_document_opened(params: types.DidOpenTextDocumentParams) -> None:
    """The user opened a file: check the project, so the editor shows problems right away."""
    await check_project(params.text_document.uri)


@server.feature(types.TEXT_DOCUMENT_DID_SAVE)
async def on_document_saved(params: types.DidSaveTextDocumentParams) -> None:
    """The user saved a file: check the project again."""
    await check_project(params.text_document.uri)


async def check_project(document_uri: str) -> None:
    """Check the config of the project that owns the document, then run import-linter and publish what it finds."""
    file_path = to_fs_path(document_uri)
    if file_path is None:  # not a file on disk, for example an unsaved "untitled:" document
        return
    config_file = find_config_file(Path(file_path))
    if config_file is None:  # no import-linter config nearby, nothing to check
        return

    # A diagnostic is a problem on a range of a file (a squiggly line). We collect them per file, by URI.
    # The config file always gets an entry, even an empty one, so that fixed mistakes disappear.
    config_problems = config_diagnostics(config_file, config_format(config_file) or "ini")
    diagnostics_by_uri = {config_file.as_uri(): config_problems}

    if config_problems:
        # import-linter cannot check contracts that are not configured correctly, so we stop here.
        log(f"{config_file} has {len(config_problems)} problem(s); fix them to check the imports")
    else:
        project_dir = config_file.parent
        log(f"Running import-linter in {project_dir}")
        # import-linter takes a few seconds on big projects. Run it in a thread so the server can keep answering.
        report = await asyncio.to_thread(run_import_linter, project_dir)
        for violation in parse_report(report, project_dir):
            diagnostics_by_uri.setdefault(violation.file.as_uri(), []).append(to_diagnostic(violation))

    publish_diagnostics(diagnostics_by_uri)


def publish_diagnostics(diagnostics_by_uri: dict[str, list[types.Diagnostic]]) -> None:
    """Send the diagnostics to the editor, and clear them in files that had some last time but have none now."""
    for uri in files_with_diagnostics:
        diagnostics_by_uri.setdefault(uri, [])

    for uri, diagnostics in diagnostics_by_uri.items():
        server.text_document_publish_diagnostics(types.PublishDiagnosticsParams(uri=uri, diagnostics=diagnostics))
    files_with_diagnostics.clear()
    files_with_diagnostics.update(uri for uri, diagnostics in diagnostics_by_uri.items() if diagnostics)


def to_diagnostic(violation: Violation) -> types.Diagnostic:
    """Underline the whole line of the import."""
    # LSP positions start at 0 for both line and character, while import-linter's line numbers start at 1.
    line_index = violation.line - 1
    line_text = violation.file.read_text(errors="replace").splitlines()[line_index]
    return types.Diagnostic(
        range=types.Range(
            start=types.Position(line=line_index, character=0),
            end=types.Position(line=line_index, character=len(line_text)),
        ),
        message=f"{violation.importer} imports {violation.imported}, which breaks an import-linter contract",
        severity=types.DiagnosticSeverity.Error,
        source="import-linter",
    )
