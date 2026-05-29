# CC_Mini_Agent —— 一个轻量、可读、可扩展的 Python CLI Agent 框架

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square)
![CLI](https://img.shields.io/badge/供应商-无关-2ea44f?style=flat-square)
![Agent Loop](https://img.shields.io/badge/架构-Agent%20Loop-7c3aed?style=flat-square)
![MCP](https://img.shields.io/badge/MCP-supported-orange?style=flat-square)
![Skills](https://img.shields.io/badge/Skills-SKILL.md-0ea5e9?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

</div>

`cc_mini_agent` 是一个轻量、可读、可扩展的 Python CLI Agent 框架。它面向本地开发、代码分析和自动化任务，内置多模型接入、Tool Use、MCP、文件记忆、生命周期 Hook、上下文压缩和基于 `SKILL.md` 的技能系统。

本项目源自对 Claude Code 源代码和工程设计的学习、拆解与 Python 化重构，目标是在保留 Agent Loop、工具调用、上下文管理、Hook、记忆和 Skill 等核心思想的同时，做成一个更轻量、更便于阅读和二次开发的 CLI Agent 学习版。

[English](./README_EN.md)

## 核心能力

- 多模型统一接入：支持 OpenAI-compatible API、Anthropic、Gemini、MiniMax、Kimi/Moonshot、DeepSeek 和 Qwen。
- Agent Loop：支持多轮推理、工具调用、工具结果回填、错误恢复、事件流输出和后台 Worker 通知。
- 内置工具：`bash`、`file_read`、`file_write`、`file_edit`、`glob`、`grep`、`web_search`、`web_fetch`、`ask_user`、`skill_list`、`skill_read`。
- MCP 集成：支持 stdio、SSE 和 streamable HTTP，把外部 MCP Server 的工具桥接到 Agent 工具注册表。
- 上下文管理：包含 snip compact、micro compact、auto compact 和 `prompt_too_long` reactive recovery。
- 长期记忆：默认使用 `~/.cc_mini_agent/memory` 保存 Markdown 记忆，使用 `~/.cc_mini_agent/sessions` 保存会话笔记，并支持 Auto-Dream 后台巩固。
- Hook 系统：支持工具调用前后、LLM 采样后、压缩前后、单轮结束、会话结束等生命周期事件。
- Skill 系统：按照 `skill-name/SKILL.md` 结构发现技能，并通过工具按需读取技能正文和资源。

## 安装

需要 `uv` 和 Python 3.11+。

```bash
git clone https://github.com/TIANXIAZHEXIAN/cc_mini_agent.git
cd cc_mini_agent

uv venv .venv --python 3.11 --prompt cc_mini_agent
source .venv/bin/activate

uv sync --extra all
```

当前文档统一使用 `uv` 完成虚拟环境创建和依赖安装。`prompt_toolkit` 和 `python-dotenv` 已经写入项目依赖，新的虚拟环境执行上面的命令后就可以直接启动 REPL。

## 配置

可以创建 `.env` 文件，也可以直接在 shell 中导出环境变量。

```bash
# 至少设置一个模型供应商的 API Key。
export DEEPSEEK_API_KEY="..."
# export OPENAI_API_KEY="..."
# export MINIMAX_API_KEY="..."
# export ANTHROPIC_API_KEY="..."
# export GEMINI_API_KEY="..."
# export KIMI_API_KEY="..."
# export QWEN_API_KEY="..."

# 可选：网络搜索后端。
export TAVILY_API_KEY="..."
# export BRAVE_API_KEY="..."
# export SERPAPI_API_KEY="..."

# 可选：默认回复语言。
export CC_MINI_AGENT_LANGUAGE="chinese"
```

CLI 自动检测 Provider 的优先级是：

`minimax -> openai -> anthropic -> gemini -> kimi -> deepseek -> qwen`

也可以通过命令行参数显式覆盖 Provider 和模型。

## 运行

```bash
cc                    #直接输入cc即可运行
cc --language chinese
cc --provider deepseek --model deepseek-chat
python -m cc_mini_agent
```

REPL 内置命令：

- `/quit`：退出
- `/tools`：列出已注册工具
- `/reset`：清空当前对话
- `/provider`：查看当前 Provider 和模型
- `/dream`：手动触发记忆巩固
- `/hooks`：查看已注册 Hook

使用 `Alt+Enter` 可以输入换行。

## MCP

CLI 会从当前工作目录加载 `mcp_config.json`。当前配置包含：

- `bocha_search`：项目内置的 Bocha Search MCP Server
- `amap_maps`：通过 `bunx` 启动的高德地图 MCP Server
- `github-mcp`：通过 `bunx` 启动的 GitHub MCP Server

示例：

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

MCP 工具会注册成 `mcp__server_name__tool_name` 形式。MCP 资源可以通过 `list_mcp_resources` 和 `read_mcp_resource` 读取。

## 指令文件

项目级和用户级指令会从 Markdown 文件中发现，并注入系统提示词。

| 路径 | 作用域 |
| --- | --- |
| `~/.cc_mini_agent/CC_MINI_AGENT.md` | 全局用户指令 |
| `~/.cc_mini_agent/rules/*.md` | 全局模块化规则 |
| `CC_MINI_AGENT.md` | 项目级指令 |
| `.cc_mini_agent/CC_MINI_AGENT.md` | 项目级指令 |
| `.cc_mini_agent/rules/*.md` | 项目级模块化规则 |
| `CC_MINI_AGENT.local.md` | 本地私有指令 |

指令文件支持 frontmatter、`@include` 引用和从全局到本地的优先级排序。

## Skill

Skill 使用下面的目录结构：

```text
skill-name/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

默认发现路径包括：

- `~/.cc_mini_agent/skills`
- `skill/`
- `skills/`
- `cc_mini_agent/skill`
- `cc_mini_agent/skills`

默认工具集中包含 `skill_list` 和 `skill_read`，Agent 可以先发现可用 Skill，再按需读取 `SKILL.md` 或 Skill 内部资源。

## 作为库使用

```python
import asyncio

from cc_mini_agent import Config, Engine
from cc_mini_agent.tools import get_default_tools


async def main():
    config = Config(provider="deepseek", language="chinese")
    engine = Engine(config=config, tools=get_default_tools())

    async for event in engine.run("总结一下这个仓库的结构。"):
        if event["type"] == "done":
            print(event["content"])


asyncio.run(main())
```

## 项目结构

```text
cc_mini_agent/
├── cc_mini_agent/
│   ├── agents/          # coordinator 和 sub-agent
│   ├── core/            # engine、messages、tool、permissions、hooks
│   ├── instructions/    # CC_MINI_AGENT.md 发现和 PromptBuilder
│   ├── integrations/    # MCP client
│   ├── memory/          # compact、memory、dream、session persistence
│   ├── providers/       # LLM Provider 抽象和预设
│   ├── skill/           # Skill 发现、校验和工具
│   └── tools/           # 内置工具
├── bocha-search-mcp/    # 内置 Bocha Search MCP Server
├── examples/            # 使用示例
├── mcp_config.json
└── pyproject.toml
```

## 示例

- `examples/simple_agent.py`：最小 Agent Loop 示例
- `examples/multi_provider.py`：多 Provider 切换
- `examples/custom_tool.py`：自定义工具注册
- `examples/memory_example.py`：Memory 和 Dream 巩固
- `examples/mcp_example.py`：MCP 连接和工具发现
- `examples/coordinator_example.py`：多 Agent 协调器

## 说明

- Python 包名是 `cc_mini_agent`。
- CLI 命令是 `cc`。
- console script 在 `pyproject.toml` 中定义为 `cc = "cc_mini_agent.__main__:main"`。
- 项目源自对 Claude Code 源代码和工程设计的学习与重构，不属于 Anthropic 或 Claude Code 官方项目。


## License

MIT
