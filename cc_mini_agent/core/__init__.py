"""
Core — 核心引擎 + 基础类型
The minimal core: engine loop, messages, tools, hooks, permissions.
"""
from cc_mini_agent.core.engine import Engine
from cc_mini_agent.core.tool import Tool, tool, ToolRegistry, ToolContext, RiskLevel
from cc_mini_agent.core.hooks import HookManager, HookEvent, HookContext, HookResult
from cc_mini_agent.core.messages import UserMessage, AssistantMessage, ToolCall, ToolResult
from cc_mini_agent.core.permissions import PermissionContext, PermissionMode, check_permission
