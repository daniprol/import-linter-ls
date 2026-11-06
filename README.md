# import-linter-ls

A language server for [import-linter](https://import-linter.readthedocs.io/), with a VS Code extension.
See your architecture contract errors and import violations in the editor, not only in CI.

> **Status: early.** The server starts and recognises import-linter config files. Diagnostics, hover and completion
> are coming. See the [roadmap](docs/roadmap.md).

## Use it in VS Code

1. Install the server in your project:

   ```bash
   uv add --dev import-linter-ls     # or: pip install import-linter-ls
   ```

2. Install the **Import Linter** extension. Until it is on the Marketplace, download the `.vsix` from the
   [latest release](https://github.com/daniprol/import-linter-ls/releases/latest) and run
   **Extensions: Install from VSIX...**.
3. Select your project's Python environment (**Python: Select Interpreter**) and open your project.

It works with `.importlinter`, `setup.cfg` and `pyproject.toml` configs. Check **Output > Import Linter** for logs.

| Setting | Purpose |
|---|---|
| `importLinterLs.interpreter` | Python that has `import-linter-ls`. Empty: use the one selected in VS Code. |
| `importLinterLs.trace.server` | `off`, `messages` or `verbose`: log the editor/server messages. |

Command: **Import Linter: Restart Language Server**.

## Use it in another editor

Any editor with an LSP client can run the server over stdio with `import-linter-ls`
(or `python -m import_linter_ls`).

## Develop

```bash
uv sync && pnpm install
uv run prek install       # git hooks
uv run pytest             # unit + integration tests
```

To try the extension, open this folder in VS Code and press `F5`, then open `examples/layered_app`.
More in [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md).

## Layout

| Path | What |
|---|---|
| `src/import_linter_ls/` | The language server (Python, [pygls](https://pygls.readthedocs.io/)). |
| `vscode-extension/` | The VS Code extension (TypeScript), a thin client. |
| `examples/layered_app/` | Example app with one broken contract, in TOML and INI. |
| `tests/` | Unit and integration tests. |
| `docs/` | Documentation site ([zensical](https://zensical.org/)). |
