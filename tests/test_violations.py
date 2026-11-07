"""Unit tests for reading import-linter's report."""

import os
from pathlib import Path

import pytest

from import_linter_ls.violations import Violation, environment_that_finds_the_project, parse_report, run_import_linter

pytestmark = pytest.mark.unit

STORAGE_FILE_PARTS = ("src", "layered_app", "low", "storage.py")


def test_the_report_of_the_example_app_has_one_violation(example_app: Path) -> None:
    report = run_import_linter(example_app)

    assert parse_report(report, example_app) == [
        Violation(
            file=example_app.joinpath(*STORAGE_FILE_PARTS),
            line=4,
            importer="layered_app.low.storage",
            imported="layered_app.high.report",
        )
    ]


def test_an_import_repeated_on_several_lines_gives_one_violation_per_line(example_app: Path) -> None:
    report = "- layered_app.low.storage -> layered_app.high.report (l.4, l.9)"

    assert [violation.line for violation in parse_report(report, example_app)] == [4, 9]


def test_import_linter_looks_for_the_package_in_the_project_and_its_src_folder(example_app: Path) -> None:
    python_path = environment_that_finds_the_project(example_app)["PYTHONPATH"].split(os.pathsep)

    assert python_path[:2] == [str(example_app), str(example_app / "src")]
