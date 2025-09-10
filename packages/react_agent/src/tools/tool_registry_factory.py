
from tool_discoverer import ToolDiscoverer

class ToolRegistryFactory:
    def __init__(self, tool_discoverer: ToolDiscoverer):

        self.tool_discoverer = tool_discoverer

    def create(self):

        self.tool_discoverer.discover_from_mcp()

