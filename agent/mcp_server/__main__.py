"""Entry point for running MCP server as a module: python -m agent.mcp_server"""

from agent.mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run()