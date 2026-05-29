"""
cc_mini_agent — Provider-agnostic Python agent framework.
cc_mini_agent — 供应商无关的 Python 智能体框架。

Core concepts / 核心概念:
  - Engine: The agent loop (provider-agnostic)
  - Provider: Unified LLM interface (OpenAI, Claude, Gemini, MiniMax, Kimi, DeepSeek)
  - Tool: Schema-driven, permission-gated tools
  - Hooks: Lifecycle event system (pre/post tool, stop, session, compact)
  - Memory: File-based persistent memory with dream consolidation
  - Instructions: CC_MINI_AGENT.md project-level instruction files
  - MCP: Model Context Protocol for external tool servers
"""
from cc_mini_agent.core.engine import Engine
from cc_mini_agent.core.tool import Tool, tool, ToolRegistry
from cc_mini_agent.core.hooks import HookManager, HookEvent, HookContext, HookResult
from cc_mini_agent.core.messages import UserMessage, AssistantMessage, ToolCall, ToolResult
from cc_mini_agent.providers import (
    LLMProvider, LLMResponse, LLMToolCall,
    OpenAICompatibleProvider, AnthropicProvider, GeminiProvider,
    create_provider, PROVIDER_PRESETS,
)
from cc_mini_agent.config import Config

__all__ = [
    "Engine", "Tool", "tool", "ToolRegistry", "Config",
    "HookManager", "HookEvent", "HookContext", "HookResult",
    "UserMessage", "AssistantMessage", "ToolCall", "ToolResult",
    "LLMProvider", "LLMResponse", "LLMToolCall",
    "OpenAICompatibleProvider", "AnthropicProvider", "GeminiProvider",
    "create_provider", "PROVIDER_PRESETS",
]
