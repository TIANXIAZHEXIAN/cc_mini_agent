"""Optional tools for listing and reading Claw Agent skills."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from claw_agent.core.tool import RiskLevel, Tool, ToolContext
from claw_agent.skill.loader import SkillError, discover_skills, load_skill


class SkillListTool(Tool):
    name = "skill_list"
    description = (
        "List available agent skills from configured skill folders. Use this "
        "when you need to see which SKILL.md-based skills are available."
    )
    risk_level = RiskLevel.LOW
    is_read_only = True

    def get_parameters(self) -> dict:
        return {"type": "object", "properties": {}}

    async def call(self, arguments: dict[str, Any], context: ToolContext) -> str:
        skills = discover_skills(cwd=context.cwd)
        if not skills:
            return "No skills found."

        return "\n".join(
            f"- {skill.name}: {skill.description}\n  SKILL.md: {skill.skill_file}"
            for skill in skills
        )


class SkillReadTool(Tool):
    name = "skill_read"
    description = (
        "Read a skill's SKILL.md file or one bundled resource inside that "
        "skill folder. Use this before applying a skill."
    )
    risk_level = RiskLevel.LOW
    is_read_only = True

    def get_parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill folder to read.",
                },
                "resource_path": {
                    "type": "string",
                    "description": "Relative path inside the skill folder. Defaults to SKILL.md.",
                    "default": "SKILL.md",
                },
            },
            "required": ["skill_name"],
        }

    async def call(self, arguments: dict[str, Any], context: ToolContext) -> str:
        skill_name = arguments["skill_name"]
        resource_path = arguments.get("resource_path") or "SKILL.md"

        try:
            skill = load_skill(skill_name, cwd=context.cwd)
        except SkillError as exc:
            return f"Error: {exc}"

        base = Path(skill.path).resolve()
        target = (base / resource_path).resolve()
        try:
            target.relative_to(base)
        except ValueError:
            return "Error: resource_path must stay inside the skill folder."

        if not target.is_file():
            return f"Error: resource not found: {resource_path}"

        try:
            return target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"Error: resource is not a UTF-8 text file: {resource_path}"
