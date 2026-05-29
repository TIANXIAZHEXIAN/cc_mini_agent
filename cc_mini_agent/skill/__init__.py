"""Skill discovery and loading support for cc_mini_agent."""

from cc_mini_agent.skill.loader import (
    Skill,
    SkillError,
    discover_skills,
    format_skills_prompt,
    get_default_skill_roots,
    load_skill,
    parse_skill_file,
    validate_skill_directory,
)

__all__ = [
    "Skill",
    "SkillError",
    "discover_skills",
    "format_skills_prompt",
    "get_default_skill_roots",
    "load_skill",
    "parse_skill_file",
    "validate_skill_directory",
]
