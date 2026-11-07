# VS Code

1. Install `import-linter-ls`, in your project's environment (`uv add --dev import-linter-ls`) or once for your
   user (`uv tool install import-linter-ls`).
2. Install the **Import Linter** extension. Until it is on the Marketplace, download the `.vsix` from the
   [latest release](https://github.com/daniprol/import-linter-ls/releases/latest) and run
   **Extensions: Install from VSIX...**.
3. If you installed it in the project, select the project's environment with **Python: Select Interpreter**.

The extension starts when the workspace has a `.importlinter`, `setup.cfg` or `pyproject.toml`.

## What it does

When you open or save a file, the extension runs import-linter on the project and underlines every import that
breaks a contract. The project is the nearest folder above the file with an import-linter config.

## How the server is found

In order, the first one that works:

1. the `importLinterLs.interpreter` setting;
2. the project's environment, if `import-linter-ls` is installed there. It comes from the **Python Environments**
   extension when `python.useEnvironmentsExtension` is on, otherwise from the **Python** extension. Neither is
   required;
3. the `import-linter-ls` command on the PATH, as installed by `uv tool install` or `pipx`.

If none works, you get an error that says how to install it. The server restarts when you select another
environment or change a setting.

With `uv tool install` the server runs outside your project's environment. That is fine: import-linter does not
import your code, it only needs to find your package, and the server tells it to look in the project folder and in
`src/`. Custom contract types from another installed package are not available there.

## Settings

| Setting | Purpose |
|---|---|
| `importLinterLs.interpreter` | Python that has `import-linter-ls`. Empty: find it as described above. |
| `importLinterLs.trace.server` | `off`, `messages` or `verbose`: log the messages between VS Code and the server. |

## Commands

- **Import Linter: Restart Language Server**

## Troubleshooting

Open **Output > Import Linter**. It says which Python or command started the server, and why the others were skipped.
