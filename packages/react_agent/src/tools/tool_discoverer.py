from config.config import Config
from tools.tool_registry import ToolRegistry
import logging

class ToolDiscoverer:
    """様々なソースからツールを発見し、レジストリに登録する。"""
    def __init__(self, registry: ToolRegistry, config: Config):
        self.registry = registry
        self.config = config

    async def discover_from_mcp(self):
        logging.debug("Discovering tools from MCP...")
