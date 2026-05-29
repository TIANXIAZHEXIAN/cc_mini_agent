#!/usr/bin/env python3
"""Rename the project from claw_agent/claw-agent to cc_mini_agent.

Default mode is a dry run. Use --apply to actually modify files.
This script is intentionally self-contained and skips itself, .env files,
virtual environments, caches, git metadata, and binary assets.
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

OLD_PACKAGE = "claw_agent"
NEW_PACKAGE = "cc_mini_agent"
OLD_DISTRIBUTION = "claw-agent"
NEW_DISTRIBUTION = "cc_mini_agent"
OLD_ROOT_NAMES = {"cc-mini-agent", "claw-agent", "claw_agent"}
NEW_ROOT_NAME = "cc_mini_agent"
OLD_INSTRUCTION_FILE = "CLAW.md"
NEW_INSTRUCTION_FILE = "CC_MINI_AGENT.md"
OLD_LOCAL_INSTRUCTION_FILE = "CLAW.local.md"
NEW_LOCAL_INSTRUCTION_FILE = "CC_MINI_AGENT.local.md"
OLD_LANGUAGE_ENV = "CLAW_LANGUAGE"
NEW_LANGUAGE_ENV = "CC_MINI_AGENT_LANGUAGE"
OLD_INSTRUCTION_MODULE = "clawmd.py"
NEW_INSTRUCTION_MODULE = "cc_mini_agent_md.py"

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    "node_modules",
    "dist",
    "build",
}

SKIP_FILE_NAMES = {".env"}

TEXT_EXTENSIONS = {
    ".py",
    ".pyi",
    ".md",
    ".rst",
    ".txt",
    ".toml",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
    ".cfg",
    ".conf",
    ".lock",
    ".sh",
    ".bash",
    ".ps1",
}

TEXT_FILE_NAMES = {
    ".gitignore",
    ".env.example",
    "PKG-INFO",
    "SOURCES.txt",
    "entry_points.txt",
    "requires.txt",
    "top_level.txt",
    "dependency_links.txt",
}

OLD_NAME_PATTERNS = [
    "claw_agent",
    "claw-agent",
    "CLAW.md",
    "CLAW.local.md",
    "CLAW_LANGUAGE",
    "~/.claw",
    ".claw",
    "clawmd",
]


@dataclass(frozen=True)
class RenameAction:
    source: Path
    target: Path
    kind: str


@dataclass(frozen=True)
class TextChange:
    path: Path
    replacements: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename claw_agent project files to cc_mini_agent. Defaults to dry-run."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually modify files and rename directories. Without this flag, only print planned changes.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Repository root to rename. Defaults to the directory containing this script.",
    )
    return parser.parse_args()


def is_repo_like(root: Path) -> bool:
    return (root / "pyproject.toml").is_file() and (
        (root / OLD_PACKAGE).is_dir() or (root / NEW_PACKAGE).is_dir()
    )


def is_text_file(path: Path) -> bool:
    if path.name in SKIP_FILE_NAMES:
        return False
    if path.name in TEXT_FILE_NAMES:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def iter_text_files(root: Path, script_path: Path) -> Iterable[Path]:
    for current_root, dir_names, file_names in os.walk(root):
        dir_names[:] = [name for name in dir_names if name not in SKIP_DIR_NAMES]
        for file_name in file_names:
            path = Path(current_root) / file_name
            if path.resolve() == script_path:
                continue
            if is_text_file(path):
                yield path


def apply_text_replacements(text: str) -> tuple[str, int]:
    replacements = 0
    literal_replacements = [
        (OLD_LOCAL_INSTRUCTION_FILE, NEW_LOCAL_INSTRUCTION_FILE),
        (OLD_INSTRUCTION_FILE, NEW_INSTRUCTION_FILE),
        (OLD_LANGUAGE_ENV, NEW_LANGUAGE_ENV),
        ("~/.claw", "~/.cc_mini_agent"),
        (".claw_memory", ".cc_mini_agent_memory"),
        (".claw/", ".cc_mini_agent/"),
        (".claw", ".cc_mini_agent"),
        ("claw.md", "cc_mini_agent.md"),
        ("clawmd.py", "cc_mini_agent_md.py"),
        ("instructions.clawmd", "instructions.cc_mini_agent_md"),
        ("instructions/clawmd.py", "instructions/cc_mini_agent_md.py"),
        ("get_user_claw_dir", "get_user_cc_mini_agent_dir"),
        ("user_claw_md", "user_cc_mini_agent_md"),
        ("dot_claw_path", "dot_cc_mini_agent_path"),
        ("dot_claw", "dot_cc_mini_agent"),
        (OLD_PACKAGE, NEW_PACKAGE),
        (OLD_DISTRIBUTION, NEW_DISTRIBUTION),
        ("Claw Agent", NEW_PACKAGE),
        ("claw-agent", NEW_DISTRIBUTION),
        ("cc-mini-agent", NEW_ROOT_NAME),
        ("/home/yuan/cc-mini-agent", "/home/yuan/cc_mini_agent"),
        ("/home/yuan/claw-agent", "/home/yuan/cc_mini_agent"),
        ('prog="claw"', 'prog="cc"'),
        ("prog='claw'", "prog='cc'"),
        ("claw --", "cc --"),
        ("python -m claw_agent", "python -m cc_mini_agent"),
        ("python3 -m claw_agent", "python3 -m cc_mini_agent"),
    ]

    for old, new in literal_replacements:
        count = text.count(old)
        if count:
            text = text.replace(old, new)
            replacements += count

    regex_replacements = [
        (
            re.compile(r"(?m)^\s*(?:agent|claw)\s*=\s*['\"]cc_mini_agent\.__main__:main['\"]\s*$"),
            'cc = "cc_mini_agent.__main__:main"',
        ),
        (
            re.compile(r"(?m)^\s*name\s*=\s*['\"]claw-agent['\"]\s*$"),
            'name = "cc_mini_agent"',
        ),
        (
            re.compile(r"(?m)^\s*name\s*=\s*['\"]claw_agent['\"]\s*$"),
            'name = "cc_mini_agent"',
        ),
    ]

    for pattern, replacement in regex_replacements:
        text, count = pattern.subn(replacement, text)
        replacements += count

    return text, replacements


def collect_rename_actions(root: Path) -> list[RenameAction]:
    actions: list[RenameAction] = []
    package_dir = root / OLD_PACKAGE
    if package_dir.exists():
        actions.append(RenameAction(package_dir, root / NEW_PACKAGE, "package directory"))

    egg_info_dir = root / f"{OLD_PACKAGE}.egg-info"
    if egg_info_dir.exists():
        actions.append(
            RenameAction(egg_info_dir, root / f"{NEW_PACKAGE}.egg-info", "egg-info directory")
        )

    for source in [
        root / OLD_PACKAGE / "instructions" / OLD_INSTRUCTION_MODULE,
        root / NEW_PACKAGE / "instructions" / OLD_INSTRUCTION_MODULE,
    ]:
        if source.exists():
            actions.append(
                RenameAction(source, source.with_name(NEW_INSTRUCTION_MODULE), "instruction module")
            )
    return actions


def collect_text_changes(root: Path, script_path: Path) -> list[TextChange]:
    changes: list[TextChange] = []
    for path in iter_text_files(root, script_path):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        _, replacements = apply_text_replacements(text)
        if replacements:
            changes.append(TextChange(path, replacements))
    return changes


def execute_text_changes(root: Path, script_path: Path) -> list[TextChange]:
    changed: list[TextChange] = []
    for path in iter_text_files(root, script_path):
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated, replacements = apply_text_replacements(original)
        if replacements and updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(TextChange(path, replacements))
    return changed


def execute_renames(actions: list[RenameAction]) -> list[RenameAction]:
    completed: list[RenameAction] = []
    for action in actions:
        if not action.source.exists():
            continue
        if action.target.exists():
            raise FileExistsError(f"Cannot rename {action.source} to {action.target}: target exists")
        action.source.rename(action.target)
        completed.append(action)
    return completed


def rename_root_if_needed(root: Path, apply: bool) -> tuple[Path, str | None]:
    if root.name == NEW_ROOT_NAME or root.name not in OLD_ROOT_NAMES:
        return root, None
    target = root.with_name(NEW_ROOT_NAME)
    message = f"root directory: {root} -> {target}"
    if not apply:
        return target, message
    if target.exists():
        raise FileExistsError(f"Cannot rename root {root} to {target}: target exists")
    os.chdir(root.parent)
    root.rename(target)
    return target, message


def scan_residuals(root: Path, script_path: Path) -> list[str]:
    residuals: list[str] = []
    for path in iter_text_files(root, script_path):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        hits = [pattern for pattern in OLD_NAME_PATTERNS if pattern in text]
        if hits:
            residuals.append(f"{path}: {', '.join(sorted(set(hits)))}")
    for old_path in [root / OLD_PACKAGE, root / f"{OLD_PACKAGE}.egg-info"]:
        if old_path.exists():
            residuals.append(f"{old_path}: old path still exists")
    return residuals


def parse_python_files(root: Path, script_path: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*.py"):
        if any(part in SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.resolve() == script_path:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except Exception as exc:
            errors.append(f"{path}: {exc}")
    return errors


def print_plan(root: Path, script_path: Path) -> int:
    renames = collect_rename_actions(root)
    text_changes = collect_text_changes(root, script_path)
    planned_root, root_message = rename_root_if_needed(root, apply=False)

    print("DRY RUN: no files were modified.")
    print(f"Repository root: {root}")
    print()

    print("Planned renames:")
    if renames:
        for action in renames:
            print(f"  - {action.kind}: {action.source} -> {action.target}")
    else:
        print("  - none")
    if root_message:
        print(f"  - {root_message}")
    print()

    print("Planned text updates:")
    if text_changes:
        for change in text_changes:
            print(f"  - {change.path} ({change.replacements} replacement(s))")
    else:
        print("  - none")

    print()
    print("Run with --apply to perform these changes.")
    if planned_root != root:
        print(f"After --apply, the project directory will be: {planned_root}")
    return 0


def apply_changes(root: Path, script_path: Path) -> int:
    print(f"Applying rename in: {root}")
    completed_renames = execute_renames(collect_rename_actions(root))
    changed_files = execute_text_changes(root, script_path)
    final_root, root_message = rename_root_if_needed(root, apply=True)
    final_script_path = final_root / script_path.name
    residuals = scan_residuals(final_root, final_script_path)
    syntax_errors = parse_python_files(final_root, final_script_path)

    print()
    print("Completed renames:")
    if completed_renames:
        for action in completed_renames:
            print(f"  - {action.kind}: {action.source} -> {action.target}")
    else:
        print("  - none")
    if root_message:
        print(f"  - {root_message}")

    print()
    print("Updated text files:")
    if changed_files:
        for change in changed_files:
            print(f"  - {change.path} ({change.replacements} replacement(s))")
    else:
        print("  - none")

    print()
    if residuals:
        print("Residual old-name references to review:")
        for item in residuals:
            print(f"  - {item}")
    else:
        print("Residual old-name references: none found")

    if syntax_errors:
        print()
        print("Python syntax errors:")
        for item in syntax_errors:
            print(f"  - {item}")
        return 1

    print()
    print("Python syntax check: passed")
    print(f"Final project root: {final_root}")
    return 0


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    script_path = Path(__file__).resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    if not is_repo_like(root):
        print(
            "Error: this does not look like the target repository. "
            "Expected pyproject.toml plus claw_agent/ or cc_mini_agent/.",
            file=sys.stderr,
        )
        return 2

    if args.apply:
        return apply_changes(root, script_path)
    return print_plan(root, script_path)


if __name__ == "__main__":
    raise SystemExit(main())
