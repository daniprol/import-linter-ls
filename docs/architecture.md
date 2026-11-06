# Architecture

```text
VS Code  <-- stdin/stdout, LSP JSON messages -->  python -m import_linter_ls
(vscode-extension/, TypeScript)                   (src/import_linter_ls/, pygls)
                                                          |
                                                          v
                                                   import-linter (checks contracts)
```

- The **server** (`src/import_linter_ls/`) holds all features. `server.py` only wires [pygls](https://pygls.readthedocs.io/)
  to small modules, one job each.
- The **extension** (`vscode-extension/`) finds the Python interpreter and starts the server. Nothing else.
- **import-linter** does the real checking. Its internals are not a public API, so only one adapter module will
  import them, with the version pinned.
- Config positions (which line a contract or option is on) are found by our own small INI and TOML scanners,
  because import-linter drops line numbers when it parses config.
