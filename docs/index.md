# import-linter-ls

A language server for [import-linter](https://import-linter.readthedocs.io/): see contract errors and import
violations in your editor, as you type, instead of waiting for `lint-imports` in CI.

## Install

```bash
uv add --dev import-linter-ls     # or: pip install import-linter-ls
```

Then install the [VS Code extension](vscode.md), or [connect another editor](other-editors.md).

It reads the same config files as import-linter: `.importlinter`, `setup.cfg` and `pyproject.toml`.

!!! note "Early stage"
    Today the server shows config mistakes and broken imports when you open or save a file. See the [roadmap](roadmap.md) for what comes next.
