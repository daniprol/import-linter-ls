"""Run import-linter on a project and turn its report into a list of violations.

This is a throwaway first version: it runs `lint-imports` and reads its text output. It will be
replaced by a module that talks to import-linter directly (see docs/roadmap.md).
"""

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Violation:
    """One import that breaks a contract. `line` starts at 1, like in an editor's status bar."""

    file: Path
    line: int
    importer: str
    imported: str


def run_import_linter(project_dir: Path) -> str:
    """Run `lint-imports` in `project_dir` and return its report (the output is the same for pass and fail)."""
    # Start the `lint-imports` command through Python so that it uses the same environment as the
    # server, on every operating system. `--no-cache` makes sure that a saved file is analysed again.
    code = "from importlinter.cli import lint_imports_command; lint_imports_command()"
    result = subprocess.run(
        [sys.executable, "-c", code, "--no-cache"],
        cwd=project_dir,
        capture_output=True,
        text=True,
        check=False,  # exit code 1 only means "there are broken contracts"
    )
    return result.stdout


# A broken import is reported like this: `- layered_app.low.storage -> layered_app.high.report (l.4)`.
# When one module imports the same thing twice there are several line numbers: `(l.4, l.9)`.
VIOLATION_LINE = re.compile(r"(?P<importer>[\w.]+) -> (?P<imported>[\w.]+) \((?P<lines>l\.\d+(?:, l\.\d+)*)\)")


def parse_report(report: str, project_dir: Path) -> list[Violation]:
    """Find the broken imports in the text printed by `lint-imports`."""
    violations = []
    for match in VIOLATION_LINE.finditer(report):
        file = module_to_file(match["importer"], project_dir)
        if file is None:
            continue
        for line_number in re.findall(r"\d+", match["lines"]):
            violations.append(Violation(file, int(line_number), match["importer"], match["imported"]))
    return violations


def module_to_file(module: str, project_dir: Path) -> Path | None:
    """Find the source file of a module like `layered_app.low.storage`, in the project or in its `src` folder."""
    relative = Path(*module.split("."))
    for source_root in (project_dir, project_dir / "src"):
        for candidate in (source_root / relative.with_suffix(".py"), source_root / relative / "__init__.py"):
            if candidate.is_file():
                return candidate
    return None
