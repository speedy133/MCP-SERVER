import json
from .mcp_client import MCPClient

class GmailNotifier:
    """Uses the Gmail MCP server to draft the notification email."""
    
    def __init__(self, server_url: str):
        self.client = MCPClient(server_url)
        
    def draft_email(self, recipient: str, subject: str, email_body: str) -> str:
        """
        Creates a draft email containing the pulse summary and the doc link.
        
        Args:
            recipient (str): The email address to send to.
            subject (str): The email subject.
            email_body (str): The drafted email body.
            
        Returns:
            str: The Draft ID returned by Gmail.
        """
        try:
            # We assume the Gmail MCP Server has a tool called 'create_draft'
            raw_result = self.client.call_tool("create_draft", {
                "to": recipient,
                "subject": subject,
                "body": email_body
            })
            
            try:
                result_dict = json.loads(raw_result)
                return result_dict.get("draft_id", raw_result)
            except json.JSONDecodeError:
                return raw_result
                
        except Exception as e:
            raise RuntimeError(f"Failed to create draft in Gmail via MCP: {e}")
