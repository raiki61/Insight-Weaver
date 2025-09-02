from typing import Dict, List

from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_function

from config.config import Config


class ToolRegistry:
    """ツールの登録、発見、管理を行うクラス"""
    def __init__(self, config: Config):
        self.tools : Dict[str, BaseTool] = {}
        self.config = config

    def register_tool(self, tool: BaseTool):
        """ツールの登録"""
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' already exists.")
        self.tools[tool.name] = tool
        print(f"Tool '{tool.name}' registered.")

    def find_tool(self, tool_name: str) -> BaseTool:
        """ツールの発見"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool with name '{tool_name}' not found.")
        return self.tools[tool_name]

    def get_all_tools(self) -> List[BaseTool]:
        """登録されている全てのツールを取得"""
        return list(self.tools.values())

    def get_function_declarations(self) -> List[Dict]:
        """
        全てのツールをLLM（特にOpenAI）が要求するFunction Callingのスキーマ形式に変換して取得します。
        """
        return [convert_to_openai_function(tool) for tool in self.tools.values()]

