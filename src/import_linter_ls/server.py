"""The language server: connects pygls to our features.

This file only wires things together. The actual logic lives in small modules next to it.
"""

from pathlib import Path

from lsprotocol import types
from pygls.lsp.server import LanguageServer
from pygls.uris import to_fs_path

from import_linter_ls import __version__
from import_linter_ls.config_files import config_format

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


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def on_document_opened(params: types.DidOpenTextDocumentParams) -> None:
    """The user opened a file. For now we only log whether it can hold import-linter config."""
    file_path = to_fs_path(params.text_document.uri)
    if file_path is None:  # not a file on disk, for example an unsaved "untitled:" document
        return
    path = Path(file_path)
    file_format = config_format(path)
    if file_format:
        log(f"Opened {file_format} config file: {path}")
