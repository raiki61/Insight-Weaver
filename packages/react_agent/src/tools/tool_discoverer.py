from typing import Coroutine, Any, Optional

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from config.config import MCPServers
from tools.tool_registry import ToolRegistry
import logging

class ToolDiscoverer:
    """様々なソースからツールを発見し、レジストリに登録する。"""
    def __init__(self, mcp_servers: MCPServers):
        self.mcp_servers = mcp_servers

    async def discover_from_mcp(self, group: Optional[str] = None) -> list[BaseTool]:
        logging.debug("Discovering tools from MCP...")
        client = MultiServerMCPClient(self.mcp_servers.to_multiserver_dict(group))
        tools = await client.get_tools()
        return tools


