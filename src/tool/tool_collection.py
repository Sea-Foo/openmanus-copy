
from src.tool.base import BaseTool, ToolFailure, ToolResult

class ToolCollection:

    def __init__(self, *tools: BaseTool):
        self.tools = tools
        self.tool_map = {tool.name: tool for tool in tools}

    