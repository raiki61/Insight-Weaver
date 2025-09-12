
from tools.tool_discoverer import ToolDiscoverer
from tools.tool_registry import ToolRegistry


class ToolRegistryFactory:
    def __init__(self, tool_discoverer: ToolDiscoverer):

        self.tool_registry = None
        self.tool_discoverer = tool_discoverer

    async def create(self)-> ToolRegistry:

        tools = await self.tool_discoverer.discover_from_mcp()
        self.tool_registry: ToolRegistry = ToolRegistry()
        for tool in tools:
            self.tool_registry.register_tool(tool)
        return self.tool_registry


