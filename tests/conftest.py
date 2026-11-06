"""Shared fixtures."""

import sys
from pathlib import Path

import pytest
import pytest_lsp
from lsprotocol import types
from pytest_lsp import ClientServerConfig, LanguageClient

EXAMPLE_APP = Path(__file__).parent.parent / "examples" / "layered_app"


@pytest.fixture
def example_app() -> Path:
    """The example app, which has an import-linter contract that is broken on purpose."""
    return EXAMPLE_APP


@pytest_lsp.fixture(
    config=ClientServerConfig(server_command=[sys.executable, "-m", "import_linter_ls"]),
)
async def client(lsp_client: LanguageClient):
    """A fake editor connected to a real server process, already past the handshake."""
    await lsp_client.initialize_session(
        types.InitializeParams(
            capabilities=types.ClientCapabilities(),
            root_uri=EXAMPLE_APP.as_uri(),
        )
    )
    yield lsp_client
    await lsp_client.shutdown_session()
