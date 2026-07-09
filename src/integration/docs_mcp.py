from datetime import datetime
import json
from .mcp_client import MCPClient

class DocsPublisher:
    """Uses the Google Docs MCP server to publish the Weekly Pulse Report."""
    
    def __init__(self, server_url: str):
        self.client = MCPClient(server_url)
        
    def publish_pulse(self, doc_content: str) -> str:
        """
        Creates a new Google Doc with the pulse report content.
        
        Args:
            doc_content (str): The polished markdown/text content from Groq.
            
        Returns:
            str: The URL of the newly created Google Doc.
        """
        title = f"Weekly Pulse – {datetime.now().strftime('%B %d, %Y')}"
        
        try:
            # We assume the Docs MCP Server has a tool called 'create_document'
            # which takes 'title' and 'content' and returns a JSON string with 'url'.
            # (Note: In a real MCP, you'd check the available tools first, but this is the contracted API)
            raw_result = self.client.call_tool("create_document", {
                "title": title,
                "content": doc_content
            })
            
            # The MCP SDK usually returns a stringified JSON in the TextContent
            try:
                result_dict = json.loads(raw_result)
                return result_dict.get("url", raw_result)
            except json.JSONDecodeError:
                # Fallback if the tool returns a raw URL string instead of JSON
                return raw_result
                
        except Exception as e:
            raise RuntimeError(f"Failed to publish to Google Docs via MCP: {e}")
