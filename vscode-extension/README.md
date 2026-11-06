# Import Linter for VS Code

Shows [import-linter](https://import-linter.readthedocs.io/) contract errors and import violations in VS Code.

1. Install the language server in your project's environment: `uv add --dev import-linter-ls` (or `pip install import-linter-ls`).
2. Select that environment with **Python: Select Interpreter**.
3. Open a project with an import-linter config (`.importlinter`, `setup.cfg` or `pyproject.toml`).

The extension uses the interpreter selected in the Python extension. To use another one, set `importLinterLs.interpreter`.
Logs are in **Output > Import Linter**.

Full docs: <https://daniprol.github.io/import-linter-ls/>
