"""Skill discovery, parsing, validation, and prompt formatting.

The skill layout follows the common agent skill convention:

skill-name/
    SKILL.md
    scripts/
    references/
    assets/
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Optional


_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
_SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$|^[a-z0-9]$")


class SkillError(ValueError):
    """Raised when a skill folder or SKILL.md file is invalid."""


@dataclass(frozen=True)
class Skill:
    """Parsed skill metadata and body."""

    name: str
    description: str
    path: str
    skill_file: str
    body: str
    license: Optional[str] = None
    compatibility: Optional[str] = None
    allowed_tools: Optional[str] = None
    metadata: dict[str, str] = field(default_factory=dict)


def get_default_skill_roots(cwd: Optional[str] = None) -> list[str]:
    """Return skill roots in low-to-high priority order.

    Later roots override earlier roots when they contain a skill with the same
    name. This lets project skills override user-level skills.
    """

    roots: list[Path] = [Path.home() / ".claw" / "skills"]
    if cwd:
        base = Path(cwd)
        roots.extend(
            [
                base / "skill",
                base / "skills",
                base / "claw_agent" / "skill",
                base / "claw_agent" / "skills",
            ]
        )

    result: list[str] = []
    seen: set[str] = set()
    for root in roots:
        normalized = str(root.expanduser().resolve())
        if normalized in seen or not root.is_dir():
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def discover_skills(
    roots: Optional[Iterable[str]] = None,
    *,
    cwd: Optional[str] = None,
) -> list[Skill]:
    """Discover valid skills from one or more skill roots.

    Invalid skill folders are skipped so a single broken skill does not prevent
    the agent from starting. Use validate_skill_directory() for strict checks.
    """

    skill_roots = list(roots) if roots is not None else get_default_skill_roots(cwd)
    discovered: dict[str, Skill] = {}

    for root in skill_roots:
        root_path = Path(root).expanduser()
        if not root_path.is_dir():
            continue

        for child in sorted(root_path.iterdir(), key=lambda p: p.name):
            if not child.is_dir():
                continue
            skill_file = child / "SKILL.md"
            if not skill_file.is_file():
                continue
            try:
                skill = parse_skill_file(skill_file)
            except SkillError:
                continue
            discovered[skill.name] = skill

    return [discovered[name] for name in sorted(discovered)]


def load_skill(
    name: str,
    roots: Optional[Iterable[str]] = None,
    *,
    cwd: Optional[str] = None,
) -> Skill:
    """Load a skill by name from the discovered skill roots."""

    for skill in discover_skills(roots, cwd=cwd):
        if skill.name == name:
            return skill
    raise SkillError(f"Skill not found: {name}")


def validate_skill_directory(skill_dir: str) -> Skill:
    """Strictly validate one skill directory and return the parsed skill."""

    directory = Path(skill_dir).expanduser()
    if not directory.is_dir():
        raise SkillError(f"Skill directory not found: {skill_dir}")
    return parse_skill_file(directory / "SKILL.md")


def parse_skill_file(skill_file: str | Path) -> Skill:
    """Parse and validate a SKILL.md file."""

    path = Path(skill_file).expanduser()
    if path.name != "SKILL.md":
        raise SkillError(f"Expected SKILL.md, got: {path.name}")
    if not path.is_file():
        raise SkillError(f"Missing required SKILL.md: {path}")

    raw = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(raw)
    if not match:
        raise SkillError(f"{path} must start with YAML frontmatter")

    metadata = _parse_frontmatter(match.group(1))
    body = raw[match.end() :].strip()
    skill_dir = path.parent

    name = _required_str(metadata, "name", path)
    description = _required_str(metadata, "description", path)

    _validate_name(name, skill_dir.name, path)
    _validate_length(description, "description", path, 1, 1024)

    license_name = _optional_str(metadata, "license", path)
    compatibility = _optional_str(metadata, "compatibility", path)
    if compatibility is not None:
        _validate_length(compatibility, "compatibility", path, 1, 500)

    allowed_tools = _optional_str(metadata, "allowed-tools", path)
    extra_metadata = metadata.get("metadata") or {}
    if not isinstance(extra_metadata, dict):
        raise SkillError(f"{path}: metadata must be a key-value mapping")
    normalized_metadata = {
        str(key): str(value) for key, value in extra_metadata.items()
    }

    return Skill(
        name=name,
        description=description,
        path=str(skill_dir.resolve()),
        skill_file=str(path.resolve()),
        body=body,
        license=license_name,
        compatibility=compatibility,
        allowed_tools=allowed_tools,
        metadata=normalized_metadata,
    )


def format_skills_prompt(skills: Iterable[Skill]) -> str:
    """Format discovered skills as lightweight system prompt metadata."""

    skill_list = list(skills)
    if not skill_list:
        return ""

    lines = [
        "# Skills",
        "The following skills are available. A skill is a folder with a SKILL.md file and optional scripts, references, and assets.",
        "Use a skill when the user's request matches its description. Before using a matched skill, read its SKILL.md file and follow its instructions. Load scripts, references, or assets only when needed.",
        "",
        "Available skills:",
    ]
    for skill in skill_list:
        lines.extend(
            [
                f"- {skill.name}: {skill.description}",
                f"  SKILL.md: {skill.skill_file}",
            ]
        )
    return "\n".join(lines)


def _parse_frontmatter(header: str) -> dict[str, Any]:
    """Parse the small YAML subset required for skill frontmatter."""

    result: dict[str, Any] = {}
    current_map_key: Optional[str] = None

    for raw_line in header.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent > 0 and current_map_key:
            key, value = _split_key_value(line)
            nested = result.setdefault(current_map_key, {})
            if not isinstance(nested, dict):
                raise SkillError(f"{current_map_key} must be a key-value mapping")
            nested[key] = _unquote(value)
            continue

        key, value = _split_key_value(line)
        if value == "":
            result[key] = {}
            current_map_key = key
        else:
            result[key] = _unquote(value)
            current_map_key = None

    return result


def _split_key_value(line: str) -> tuple[str, str]:
    if ":" not in line:
        raise SkillError(f"Invalid frontmatter line: {line}")
    key, _, value = line.partition(":")
    key = key.strip()
    if not key:
        raise SkillError(f"Invalid frontmatter key in line: {line}")
    return key, value.strip()


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def _required_str(metadata: dict[str, Any], key: str, path: Path) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SkillError(f"{path}: required field '{key}' must be a non-empty string")
    return value.strip()


def _optional_str(metadata: dict[str, Any], key: str, path: Path) -> Optional[str]:
    value = metadata.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise SkillError(f"{path}: optional field '{key}' must be a non-empty string")
    return value.strip()


def _validate_name(name: str, parent_name: str, path: Path) -> None:
    if not _SKILL_NAME_RE.match(name):
        raise SkillError(
            f"{path}: name must be 1-64 chars of lowercase letters, digits, and hyphens"
        )
    if "--" in name:
        raise SkillError(f"{path}: name must not contain consecutive hyphens")
    if name != parent_name:
        raise SkillError(
            f"{path}: name '{name}' must match parent directory '{parent_name}'"
        )


def _validate_length(
    value: str,
    field_name: str,
    path: Path,
    min_length: int,
    max_length: int,
) -> None:
    length = len(value)
    if length < min_length or length > max_length:
        raise SkillError(
            f"{path}: {field_name} must be {min_length}-{max_length} characters"
        )
