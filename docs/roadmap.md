# Roadmap

Features are added one at a time. Both INI and TOML configs are supported from the first feature on.

1. **Skeleton** (done): the server starts, recognises config files and logs to the editor. The VS Code extension launches it.
2. **Config diagnostics**: syntax errors, unknown contract types, missing required fields, unknown options with "did you mean".
3. **Violation diagnostics**: run the contracts on save and mark the offending `import` lines.
4. **Hover**: explain contract types and options.
5. **Completion**: contract types, option names and module names.
6. **Go to definition** on module names in the config.
7. **Quick fixes**: add an import to `ignore_imports`.
