"""Integration tests: start the real server process and talk LSP to it, like an editor does."""

import asyncio
from pathlib import Path

import pytest
from lsprotocol import types
from pytest_lsp import LanguageClient

pytestmark = pytest.mark.integration


async def test_server_says_it_is_ready_after_the_handshake(client: LanguageClient) -> None:
    await asyncio.sleep(0.5)  # the server handles the notification in the background

    assert any("is ready" in message.message for message in client.log_messages)


async def test_saving_a_file_shows_the_broken_import_as_a_diagnostic(client: LanguageClient, example_app: Path) -> None:
    storage_file = example_app / "src" / "layered_app" / "low" / "storage.py"

    client.text_document_did_save(
        types.DidSaveTextDocumentParams(text_document=types.TextDocumentIdentifier(uri=storage_file.as_uri()))
    )
    # import-linter takes a moment to run, so wait until the server publishes the diagnostics.
    for _ in range(100):
        diagnostics = client.diagnostics.get(storage_file.as_uri(), [])
        if diagnostics:
            break
        await asyncio.sleep(0.1)

    assert len(diagnostics) == 1
    assert diagnostics[0].range.start.line == 3  # "l.4" in import-linter's report, counted from 1
    assert "layered_app.high.report" in diagnostics[0].message
