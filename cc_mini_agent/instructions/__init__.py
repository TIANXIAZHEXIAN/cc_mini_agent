"""
Instructions — 指令 + 系统提示词

Discovers CC_MINI_AGENT.md instruction files and builds the system prompt.
发现 CC_MINI_AGENT.md 指令文件并构建系统提示词。
"""
from cc_mini_agent.instructions.cc_mini_agentmd import (
    InstructionFile,
    discover_instruction_files,
    format_instructions_prompt,
    get_user_cc_mini_agent_dir,
    get_large_files,
)
from cc_mini_agent.instructions.prompts import PromptBuilder

__all__ = [
    "InstructionFile",
    "discover_instruction_files",
    "format_instructions_prompt",
    "get_user_cc_mini_agent_dir",
    "get_large_files",
    "PromptBuilder",
]
