# Changelog

## Unreleased

- Project scaffold: language server that starts and recognises import-linter config files, VS Code extension that
  launches it, example app, docs, CI and release workflows.
- Config diagnostics: on open and save, show syntax errors, unknown contract types and missing, unknown or invalid
  options in `.importlinter`, `setup.cfg` and `pyproject.toml`, on the line where they are.
- Throwaway first feature: on open and on save, run import-linter and show each broken import as an error.
