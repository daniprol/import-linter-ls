# Changelog

## Unreleased

- Project scaffold: language server that starts and recognises import-linter config files, VS Code extension that
  launches it, example app, docs, CI and release workflows.
- Config diagnostics: on open and save, show syntax errors, unknown contract types and missing, unknown or invalid
  options in `.importlinter`, `setup.cfg` and `pyproject.toml`, on the line where they are.
- VS Code: find the server in the project's environment (Python or Python Environments extension, neither required),
  or else the `import-linter-ls` command on the PATH, for example from `uv tool install import-linter-ls`. Show a
  clear error when it is not installed.
- import-linter finds `src/` layout packages even when the server is installed apart from the project.
- Throwaway first feature: on open and on save, run import-linter and show each broken import as an error.
