"""
Tools — 工具集入口

Registry of all built-in tools.
"""
from cc_mini_agent.tools.bash_tool import BashTool
from cc_mini_agent.tools.file_tools import FileReadTool, FileWriteTool, FileEditTool
from cc_mini_agent.tools.glob_tool import GlobTool
from cc_mini_agent.tools.grep_tool import GrepTool
from cc_mini_agent.tools.web_fetch_tool import WebFetchTool
from cc_mini_agent.tools.web_search_tool import WebSearchTool
from cc_mini_agent.tools.ask_user_tool import AskUserQuestionTool
from cc_mini_agent.skill.tools import SkillListTool, SkillReadTool

def get_default_tools():
    """Get all built-in tools / 获取所有内置工具
    """
    return [
        BashTool(),
        FileReadTool(),
        FileWriteTool(),
        FileEditTool(),
        GlobTool(),
        GrepTool(),
        WebFetchTool(),
        WebSearchTool(),
        AskUserQuestionTool(),
        SkillListTool(),
        SkillReadTool(),
    ]
