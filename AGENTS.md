# Notes for coding agents

import-linter-ls is a language server for [import-linter](https://import-linter.readthedocs.io/), plus a VS Code
extension that uses it. It is also a place to learn how language servers and editor extensions work, so the code
must teach. Keep it small, clean and readable. Do not overengineer.

## The main rule: a junior engineer can read any file and understand it, without help

- Use clear, plain names (`contract_options`, `config_file_path`), not abbreviations (`opts`, `cfg`).
- Prefer simple, straight-line code and small functions. No clever tricks, and no abstractions before they are needed.
- Comments explain *why*, and briefly *what* for anything non-obvious: LSP concepts (a "feature", a "diagnostic", a
  "position"), pygls handlers, VS Code APIs and import-linter internals. Assume the reader has never used them.
- Be concise and direct in code, comments, docs and the README. No filler, no repeating the code in words.

## Design

- `src/import_linter_ls/server.py` only wires pygls to our features. Each feature lives in its own small module
  (one job per file) and is a plain function that can be tested without a server.
- Only one module, `import_linter_ls/import_linter_adapter.py` (not written yet), may import import-linter internals.
  They are not a public API, so everything else goes through that adapter. The import-linter version is pinned in
  `pyproject.toml`.
- Never print to stdout in the server: editors use it for the protocol. Send messages to the editor with `log`.
- `vscode-extension/` is a thin client. It finds the Python interpreter and starts `python -m import_linter_ls`.
  Features belong in the server, so every editor gets them.
- `examples/layered_app` is a small app with a contract that is broken on purpose. Tests and manual tries use it.

## Workflow

- Python: uv, ruff, ty, pytest, prek. TypeScript: pnpm, oxfmt, oxlint, tsc, esbuild. Docs: zensical.
- `uv sync && pnpm install`, then `uv run prek install` once. Hooks (`prek.toml`) run on commit and on push, and CI
  runs the same ones.
- `uv run pytest` runs everything. Tests marked `unit` need no server. Tests marked `integration` start the real
  server and talk LSP to it (pytest-lsp).
- Avoid mocking or patching unless there is no other way. Prefer the real server and the example app.
- Update `docs/` and `CHANGELOG.md` with every user-visible change. Releases are described in `CONTRIBUTING.md`.
