# Contributing

Read [AGENTS.md](AGENTS.md) first: it explains the style (simple, clear, commented for beginners).

## Setup

```bash
uv sync && pnpm install
uv run prek install
```

## Checks

```bash
uv run pytest                              # unit and integration tests
uv run pytest -m unit                      # only the fast ones
uv run ruff check . && uv run ty check     # Python lint and types
pnpm --dir vscode-extension lint           # extension lint (oxlint)
pnpm --dir vscode-extension typecheck      # extension types (tsc)
uv run --only-group docs zensical serve    # preview the docs on http://localhost:8000
```

## Try the extension

Open the repo in VS Code and press `F5` (**Run Extension**). In the new window, open `examples/layered_app`.

## Release

1. Set the same new version in `pyproject.toml` and `vscode-extension/package.json`, and update `CHANGELOG.md`.
2. Merge to `main`, then push a tag: `git tag v0.1.0 && git push origin v0.1.0`.
3. The **Release** workflow runs the CI checks, builds the wheel, sdist and `.vsix`, and checks that the tag matches both
   versions and is on `main`. After you approve the `pypi` environment it publishes to PyPI, then creates the GitHub
   release with the `.vsix` attached.
4. To rehearse, run **Release** by hand (Actions > Release > Run workflow): it publishes to TestPyPI.

One-time setup:

- PyPI and TestPyPI: add a [trusted publisher](https://docs.pypi.org/trusted-publishers/) for this repo, workflow
  `release.yml`, environment `pypi` (and `testpypi`).
- GitHub: create the `pypi` and `testpypi` environments (require your approval on `pypi`) and set Pages > Source to
  "GitHub Actions" for the docs.
