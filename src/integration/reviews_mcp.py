import json
from .mcp_client import MCPClient

class ReviewsFetcher:
    """Uses the ReviewFetcher MCP server to retrieve app reviews."""
    
    def __init__(self, server_url: str):
        self.client = MCPClient(server_url)
        
    def fetch_play_store_reviews(self, app_id: str, count: int = 100) -> list[dict]:
        """Fetch Play Store reviews via MCP."""
        try:
            raw_result = self.client.call_tool("fetch_play_store_reviews", {
                "app_id": app_id,
                "count": count
            })
            
            if isinstance(raw_result, str):
                try:
                    return json.loads(raw_result)
                except json.JSONDecodeError:
                    raise RuntimeError(f"MCP server returned non-JSON response: {raw_result}")
            return raw_result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch Play Store reviews via MCP: {e}")

    def fetch_app_store_reviews(self, app_id: str, count: int = 100) -> list[dict]:
        """Fetch App Store reviews via MCP."""
        try:
            raw_result = self.client.call_tool("fetch_app_store_reviews", {
                "app_id": app_id,
                "count": count
            })
            
            if isinstance(raw_result, str):
                try:
                    return json.loads(raw_result)
                except json.JSONDecodeError:
                    raise RuntimeError(f"MCP server returned non-JSON response: {raw_result}")
            return raw_result
        except Exception as e:
            raise RuntimeError(f"Failed to fetch App Store reviews via MCP: {e}")
