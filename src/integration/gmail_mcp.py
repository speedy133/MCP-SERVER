import json
from .mcp_client import MCPClient

class GmailNotifier:
    """Uses the Gmail MCP server to send the notification email."""
    
    def __init__(self, server_url: str):
        self.client = MCPClient(server_url)
        
    def send_email(self, recipient: str, subject: str, email_body: str) -> str:
        """
        Sends an email containing the pulse summary and the doc link.
        
        Args:
            recipient (str): The email address to send to.
            subject (str): The email subject.
            email_body (str): The drafted email body.
            
        Returns:
            str: A confirmation message or message ID returned by Gmail.
        """
        try:
            # MCP server exposes 'draft_email' tool
            raw_result = self.client.call_tool("draft_email", {
                "to": [recipient],
                "subject": subject,
                "body": email_body
            })
            
            try:
                result_dict = json.loads(raw_result)
                return result_dict.get("confirmation", raw_result)
            except json.JSONDecodeError:
                return raw_result
                
        except Exception as e:
            raise RuntimeError(f"Failed to send email via MCP: {e}")


