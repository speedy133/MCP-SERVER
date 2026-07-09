import asyncio
from typing import Any, Dict
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

class MCPClient:
    """Base client for connecting to an MCP SSE Server and calling tools."""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        
    async def _call_tool_async(self, tool_name: str, arguments: dict) -> Any:
        """Connects to the SSE server, calls the tool, and returns the result."""
        # Using context managers to handle connection lifecycle automatically
        async with sse_client(self.server_url) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                # Initialize connection
                await session.initialize()
                
                # Call the specific tool
                result = await session.call_tool(tool_name, arguments)
                
                # The result usually has a content list, typically containing TextContent
                if result and hasattr(result, 'content') and len(result.content) > 0:
                    # In a robust implementation, you might parse this more deeply
                    return result.content[0].text
                return str(result)

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Synchronous wrapper to call an MCP tool."""
        return asyncio.run(self._call_tool_async(tool_name, arguments))
