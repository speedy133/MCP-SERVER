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
        async def _do_call():
            # Using context managers to handle connection lifecycle automatically
            async with sse_client(self.server_url) as streams:
                async with ClientSession(streams[0], streams[1]) as session:
                    # Initialize connection
                    await session.initialize()
                    
                    # Call the specific tool
                    result = await session.call_tool(tool_name, arguments)
                    
                    if result and hasattr(result, 'content') and len(result.content) > 0:
                        texts = [c.text for c in result.content if c.type == "text"]
                        if len(texts) == 1:
                            return texts[0]
                        else:
                            # Reconstruct a JSON array if there are multiple JSON objects
                            return "[" + ",".join(texts) + "]"
                        
                    return str(result)
                    
        # Wrap with a 15 second timeout so the backend doesn't hang indefinitely
        return await asyncio.wait_for(_do_call(), timeout=15.0)

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Synchronous wrapper to call an MCP tool."""
        return asyncio.run(self._call_tool_async(tool_name, arguments))
