from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Sample")

@mcp.tool()
def get_server_status() -> dict[str, str]:
    """return server status"""
    return {"status": "ok"}

@mcp.tool()
def start_server() -> dict[str, str]:
    """start server"""
    return {"status": "Server start"}

if __name__ == "__main__":
    mcp.run(transport = "streamable-http")
