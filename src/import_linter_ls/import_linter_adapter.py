"""The only module that imports import-linter's internals.

import-linter has no public API for checking a config, so we call its internal classes. They may change
in any release, which is why the version is pinned in `pyproject.toml` and why every call lives here:
when import-linter changes, this is the only file to fix.
"""

import configparser
import difflib
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from importlinter import configuration
from importlinter.adapters.user_options import IniFileUserOptionReader, TomlFileUserOptionReader
from importlinter.application import use_cases
from importlinter.domain.contract import Contract, InvalidContractOptions

# import-linter's readers open files through a "settings" object that its command line fills in at start.
# We do the same, once.
configuration.configure()

# The contract types that ship with import-linter, as {"layers": LayersContract, ...}.
BUILT_IN_CONTRACT_TYPES: dict[str, type[Contract]] = dict(use_cases._get_built_in_contract_types())


@dataclass(frozen=True)
class ConfigProblem:
    """One mistake in a config file.

    import-linter does not know line numbers, so a problem says *where* in import-linter's terms:
    - `contract_index`: which contract (0 for the first one in the file), or None for the `importlinter`
      section that holds the general options (`root_package`, ...).
    - `option`: the option that is wrong, or None when the problem is about the whole section.
    - `line`: only set for syntax errors, where the parser does know the line (counted from 1).
    """

    message: str
    contract_index: int | None = None
    option: str | None = None
    line: int | None = None


def check_config(config_file: Path, file_format: str) -> list[ConfigProblem]:
    """Read `config_file` like import-linter does and return every mistake in it.

    Unlike `lint-imports`, this does not stop at the first broken contract, and it does not need to
    build the import graph, so it is fast.
    """
    reader = IniFileUserOptionReader() if file_format == "ini" else TomlFileUserOptionReader()
    try:
        user_options = reader._read_config_filename(str(config_file))
    except (configparser.Error, tomllib.TOMLDecodeError) as error:
        return [syntax_problem(error)]
    if user_options is None:  # for example a pyproject.toml without a [tool.importlinter] table
        return []

    problems = check_session_options(user_options.session_options)
    if not user_options.contracts_options:
        problems.append(ConfigProblem("No contracts found. Add at least one contract."))
    for contract_index, contract_options in enumerate(user_options.contracts_options):
        problems += check_contract(contract_index, contract_options, user_options.session_options)
    return problems


def syntax_problem(error: configparser.Error | tomllib.TOMLDecodeError) -> ConfigProblem:
    """Turn a parser error into a problem on the line the parser reports."""
    if isinstance(error, tomllib.TOMLDecodeError):
        # Python 3.11 only has the line in the message: "Invalid value (at line 2, column 20)".
        match = re.search(r"at line (\d+)", str(error))
        return ConfigProblem(f"Invalid TOML: {error}", line=int(match[1]) if match else None)
    if isinstance(error, configparser.MissingSectionHeaderError):
        return ConfigProblem("Invalid INI: the file must start with a [section] header", line=error.lineno)
    if isinstance(error, configparser.ParsingError):  # it can list several bad lines: we show the first one
        return ConfigProblem(
            "Invalid INI: this line is not a section, an option or a continuation", line=error.errors[0][0]
        )
    # Other errors, such as a duplicate section, have a one-line message and sometimes a line number.
    first_line_of_message = str(error).splitlines()[0]
    return ConfigProblem(f"Invalid INI: {first_line_of_message}", line=getattr(error, "lineno", None))


def check_session_options(session_options: dict[str, Any]) -> list[ConfigProblem]:
    """The general options. Only `root_package` (or `root_packages`) is required."""
    if "root_package" not in session_options and "root_packages" not in session_options:
        return [ConfigProblem("Missing required option 'root_package' (or 'root_packages').")]
    return []


def check_contract(
    contract_index: int, contract_options: dict[str, Any], session_options: dict[str, Any]
) -> list[ConfigProblem]:
    """Check one contract: its `name` and `type`, then the options that its type expects."""
    problems = [
        ConfigProblem(f"Missing required option '{required_option}'.", contract_index)
        for required_option in ("name", "type")
        if required_option not in contract_options
    ]
    contract_type = contract_options.get("type")
    if contract_type is None:
        return problems

    # Projects can add their own contract types with the `contract_types` option. Their classes are
    # imported from the project, which runs project code, so we trust them without checking.
    # Each entry looks like "my_type: my_project.contracts.MyContract". An INI value on a single line is a string.
    contract_type_entries = session_options.get("contract_types", [])
    if isinstance(contract_type_entries, str):
        contract_type_entries = [contract_type_entries]
    custom_contract_types = {entry.split(":")[0].strip() for entry in contract_type_entries}
    if contract_type in custom_contract_types:
        return problems

    contract_class = BUILT_IN_CONTRACT_TYPES.get(contract_type)
    if contract_class is None:
        message = f"Unknown contract type '{contract_type}'."
        close_matches = difflib.get_close_matches(contract_type, BUILT_IN_CONTRACT_TYPES, n=1)
        if close_matches:
            message += f" Did you mean '{close_matches[0]}'?"
        return [*problems, ConfigProblem(message, contract_index, option="type")]

    # Building a contract checks its options against the fields its class declares. It raises
    # InvalidContractOptions with one message per bad option, for example
    # {"forbiden_modules": "Unrecognized option. Did you mean 'forbidden_modules'?"}.
    try:
        contract_class(
            name=contract_options.get("name", ""), session_options=session_options, contract_options=contract_options
        )
    except InvalidContractOptions as error:
        problems += [
            ConfigProblem(option_message(option, message), contract_index, option)
            for option, message in error.errors.items()
        ]
    return problems


def option_message(option: str, message: str) -> str:
    """Name the option in the message. A missing option is underlined on its section header, so the name matters."""
    if message == "This is a required field.":
        return f"Missing required option '{option}'."
    return f"'{option}': {message}"
