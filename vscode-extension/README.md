# Import Linter for VS Code

Shows [import-linter](https://import-linter.readthedocs.io/) contract errors and import violations in VS Code.

1. Install the language server, in your project (`uv add --dev import-linter-ls`) or once for your user
   (`uv tool install import-linter-ls`).
2. Open a project with an import-linter config (`.importlinter`, `setup.cfg` or `pyproject.toml`).

The extension uses, in order: the `importLinterLs.interpreter` setting, the project's environment selected in the
Python or Python Environments extension, then the `import-linter-ls` command on the PATH.
Logs are in **Output > Import Linter**.

Full docs: <https://daniprol.github.io/import-linter-ls/>
