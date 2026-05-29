# CC_Mini_Agent —— A lightweight, readable, and extensible Python CLI Agent framework.

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)
![CLI](https://img.shields.io/badge/Provider-Agnostic-2ea44f?style=flat-square)
![Agent Loop](https://img.shields.io/badge/Architecture-Agent%20Loop-7c3aed?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-supported-orange?style=flat-square)
![Skills](https://img.shields.io/badge/Skills-SKILL.md-0ea5e9?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

`cc_mini_agent` is a small, readable Python CLI agent framework inspired by modern coding agents. It includes a provider-agnostic agent loop, local tool use, MCP integration, file-based memory, lifecycle hooks, context compression, and SKILL.md-based skills.

This project originated from studying, dissecting, and rebuilding Claude Code's source code and engineering design in Python. The goal is to preserve core ideas such as the agent loop, tool use, context management, hooks, memory, and skills while keeping the implementation lightweight, readable, and easy to extend.

[中文](./README.md)

## Highlights

- Provider-agnostic LLM layer: OpenAI-compatible APIs, Anthropic, Gemini, MiniMax, Kimi/Moonshot, DeepSeek, and Qwen.
- Agent loop: multi-turn reasoning, tool calling, tool-result feedback, retry/recovery, streaming-style events, and background worker notifications.
- Built-in tools: `bash`, `file_read`, `file_write`, `file_edit`, `glob`, `grep`, `web_search`, `web_fetch`, `ask_user`, `skill_list`, and `skill_read`.
- MCP support: stdio, SSE, and streamable HTTP transports; external MCP tools are bridged into the agent registry.
- Context management: snip compact, micro compact, auto compact, and reactive `prompt_too_long` recovery.
- Memory: local markdown memory under `~/.cc_mini_agent/memory`, session notes under `~/.cc_mini_agent/sessions`, and Auto-Dream consolidation.
- Hooks: Python lifecycle callbacks for tool use, sampling, compact, turn stop, and session end.
- Skills: discover and read local skills following the `skill-name/SKILL.md` convention.

## Install

`uv` and Python 3.11+ are required.

```bash
git clone https://github.com/TIANXIAZHEXIAN/cc_mini_agent.git
cd cc_mini_agent

uv venv .venv --python 3.11 --prompt cc_mini_agent
source .venv/bin/activate

uv sync --extra all
```

The documentation now uses `uv` for both virtual environment creation and dependency installation. `prompt_toolkit` and `python-dotenv` are now declared in the project dependencies, so a fresh virtual environment can start the REPL directly after the command above.

## Configure

Create a `.env` file or export environment variables in your shell.

```bash
# Set at least one provider key.
export DEEPSEEK_API_KEY="..."
# export OPENAI_API_KEY="..."
# export MINIMAX_API_KEY="..."
# export ANTHROPIC_API_KEY="..."
# export GEMINI_API_KEY="..."
# export KIMI_API_KEY="..."
# export QWEN_API_KEY="..."

# Optional web search backends.
export TAVILY_API_KEY="..."
# export BRAVE_API_KEY="..."
# export SERPAPI_API_KEY="..."

# Optional response language.
export CC_MINI_AGENT_LANGUAGE="chinese"
```

Provider detection priority in the CLI is:

`minimax -> openai -> anthropic -> gemini -> kimi -> deepseek -> qwen`

You can override the detected provider and model from the command line.

## Run

```bash
cc
cc --language chinese
cc --provider deepseek --model deepseek-chat
python -m cc_mini_agent
```

Inside the REPL:

- `/quit`: exit
- `/tools`: list registered tools
- `/reset`: clear the conversation
- `/provider`: show the active provider and model
- `/dream`: manually run memory consolidation
- `/hooks`: inspect registered hooks

Use `Alt+Enter` to insert a newline.

## MCP

The CLI loads `mcp_config.json` from the current working directory. The bundled config starts:

- `bocha_search`: local Bocha Search MCP server from `bocha-search-mcp`
- `amap_maps`: Amap MCP server through `bunx`
- `github-mcp`: GitHub MCP server through `bunx`

Example:

```json
{
  "mcpServers": {
    "bocha_search": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/yuan/cc_mini_agent/bocha-search-mcp",
        "run",
        "bocha-search-mcp"
      ]
    }
  }
}
```

MCP tools are registered with names like `mcp__server_name__tool_name`. MCP resources can be accessed through `list_mcp_resources` and `read_mcp_resource`.

## Instructions

Project and user instructions are loaded from markdown files and injected into the system prompt.

| Location | Scope |
| --- | --- |
| `~/.cc_mini_agent/CC_MINI_AGENT.md` | global user instructions |
| `~/.cc_mini_agent/rules/*.md` | global modular rules |
| `CC_MINI_AGENT.md` | project instructions |
| `.cc_mini_agent/CC_MINI_AGENT.md` | project instructions |
| `.cc_mini_agent/rules/*.md` | project modular rules |
| `CC_MINI_AGENT.local.md` | local private instructions |

Instruction files support frontmatter, `@include` references, and priority ordering from global to local.

## Skills

Skills are folders with this layout:

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

Default skill roots include:

- `~/.cc_mini_agent/skills`
- `skill/`
- `skills/`
- `cc_mini_agent/skill`
- `cc_mini_agent/skills`

The default tool set includes `skill_list` and `skill_read`, so the agent can discover available skills and load `SKILL.md` or bundled text resources only when needed.

## Use As A Library

```python
import asyncio

from cc_mini_agent import Config, Engine
from cc_mini_agent.tools import get_default_tools


async def main():
    config = Config(provider="deepseek", language="chinese")
    engine = Engine(config=config, tools=get_default_tools())

    async for event in engine.run("Summarize this repository."):
        if event["type"] == "done":
            print(event["content"])


asyncio.run(main())
```

## Project Layout

```text
cc_mini_agent/
├── cc_mini_agent/
│   ├── agents/          # coordinator and sub-agent helpers
│   ├── core/            # engine, messages, tools, permissions, hooks
│   ├── instructions/    # CC_MINI_AGENT.md discovery and prompt builder
│   ├── integrations/    # MCP client
│   ├── memory/          # compact, memory, dream, session persistence
│   ├── providers/       # LLM provider abstraction and presets
│   ├── skill/           # skill discovery, validation, skill tools
│   └── tools/           # built-in tools
├── bocha-search-mcp/    # bundled Bocha Search MCP server
├── examples/            # usage examples
├── mcp_config.json
└── pyproject.toml
```

## Examples

- `examples/simple_agent.py`: minimal agent loop
- `examples/multi_provider.py`: provider switching
- `examples/custom_tool.py`: custom tool registration
- `examples/memory_example.py`: memory and dream consolidation
- `examples/mcp_example.py`: MCP connection and tool discovery
- `examples/coordinator_example.py`: multi-agent coordinator

## Notes

- The package name is `cc_mini_agent`.
- The CLI command is `cc`.
- The console script is defined in `pyproject.toml` as `cc = "cc_mini_agent.__main__:main"`.
- This project originated from studying and rebuilding Claude Code's source code and engineering design in Python; it is not an official Anthropic or Claude Code project.


## License

MIT
