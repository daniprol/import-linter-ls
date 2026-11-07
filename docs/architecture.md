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
- **import-linter** does the real checking. Its internals are not a public API, so only one module,
  `import_linter_adapter.py`, imports them, and the version is pinned.
- Config positions (which line a contract or option is on) are found by our own small INI and TOML scanners,
  because import-linter drops line numbers when it parses config. The scanners never parse values: import-linter's
  own readers do that. They only look for `[section]` headers and `name =` at the start of a line
  (`config_positions.py`). `config_diagnostics.py` joins the problems and the positions.

## Config diagnostics

On open and on save, the server finds the nearest config file and checks it without building the import graph:

| Problem | Where it is underlined |
|---|---|
| INI or TOML syntax error | the line the parser reports |
| missing `root_package`, contract `name`, `type` or a required option | the section header |
| unknown contract type (with "did you mean") | the `type` option |
| unrecognized option (with "did you mean"), invalid value | the option |

Unlike `lint-imports`, every broken contract is reported, not just the first one. While the config has problems,
import-linter is not run, because it cannot check contracts that are not configured correctly.
