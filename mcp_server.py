"""Entry point for running MCP server: python mcp_server.py"""

from agent.mcp_server.server import mcp

if __name__ == "__main__":
    mcp.run()