# VS Code

1. Install `import-linter-ls` in your project's environment (see [Get started](index.md)).
2. Install the **Import Linter** extension. Until it is on the Marketplace, download the `.vsix` from the
   [latest release](https://github.com/daniprol/import-linter-ls/releases/latest) and run
   **Extensions: Install from VSIX...**.
3. Select the project's environment with **Python: Select Interpreter**.

The extension starts when the workspace has a `.importlinter`, `setup.cfg` or `pyproject.toml`.

## What it does

When you open or save a file, the extension runs import-linter on the project and underlines every import that
breaks a contract. The project is the nearest folder above the file with an import-linter config.

## Settings

| Setting | Purpose |
|---|---|
| `importLinterLs.interpreter` | Python that has `import-linter-ls`. Empty: use the one selected in VS Code. |
| `importLinterLs.trace.server` | `off`, `messages` or `verbose`: log the messages between VS Code and the server. |

## Commands

- **Import Linter: Restart Language Server**

## Troubleshooting

Open **Output > Import Linter**. If it says `No module named import_linter_ls`, the selected interpreter does not have
the package: install it there, or set `importLinterLs.interpreter`.
