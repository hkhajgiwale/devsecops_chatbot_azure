from typing import Dict, List
from agents.tools._core.base_tool import BaseTool


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name()] = tool

    def get_tool(self, name: str) -> BaseTool:
        return self._tools.get(name)

    def list_tools(self) -> List[str]:
        return list(self._tools.keys())

    def get_all(self) -> List[BaseTool]:
        return list(self._tools.values())
