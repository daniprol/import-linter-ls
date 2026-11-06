"""Entry point: `python -m import_linter_ls` or the `import-linter-ls` command."""

from import_linter_ls.server import server


def main() -> None:
    # Editors start the server as a child process and talk to it over stdin and stdout,
    # so never print to stdout: it would corrupt the protocol messages. Use `log` from server.py instead.
    server.start_io()


if __name__ == "__main__":
    main()
