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


async def test_opening_a_toml_config_file_is_logged(client: LanguageClient, example_app: Path) -> None:
    config_file = example_app / "pyproject.toml"

    client.text_document_did_open(
        types.DidOpenTextDocumentParams(
            text_document=types.TextDocumentItem(
                uri=config_file.as_uri(),
                language_id="toml",
                version=1,
                text=config_file.read_text(),
            )
        )
    )
    # The server answers with a log message. Give it a moment to handle the notification.
    await asyncio.sleep(0.5)

    messages = [message.message for message in client.log_messages]
    assert any("Opened toml config file" in message for message in messages)
