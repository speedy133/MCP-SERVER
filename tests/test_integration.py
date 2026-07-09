import pytest
from unittest.mock import MagicMock, patch
from src.integration.docs_mcp import DocsPublisher
from src.integration.gmail_mcp import GmailNotifier
from src.integration.mcp_client import MCPClient

@patch('src.integration.docs_mcp.MCPClient')
def test_publish_pulse(MockMCPClient):
    # Setup mock
    mock_instance = MockMCPClient.return_value
    # Simulate the MCP tool returning a JSON string containing the URL
    mock_instance.call_tool.return_value = '{"url": "https://docs.google.com/document/d/12345/edit"}'
    
    # Execute
    publisher = DocsPublisher("http://localhost:3000/docs")
    url = publisher.publish_pulse("Test Document Content")
    
    # Assert
    assert url == "https://docs.google.com/document/d/12345/edit"
    mock_instance.call_tool.assert_called_once()
    args, kwargs = mock_instance.call_tool.call_args
    assert args[0] == "create_document"
    assert "Test Document Content" in args[1]["content"]

@patch('src.integration.gmail_mcp.MCPClient')
def test_draft_email(MockMCPClient):
    # Setup mock
    mock_instance = MockMCPClient.return_value
    # Simulate the MCP tool returning a JSON string containing the draft ID
    mock_instance.call_tool.return_value = '{"draft_id": "r123456789"}'
    
    # Execute
    notifier = GmailNotifier("http://localhost:3000/gmail")
    draft_id = notifier.draft_email("test@example.com", "Subject", "Body Content")
    
    # Assert
    assert draft_id == "r123456789"
    mock_instance.call_tool.assert_called_once()
    args, kwargs = mock_instance.call_tool.call_args
    assert args[0] == "create_draft"
    assert args[1]["to"] == "test@example.com"
    assert args[1]["body"] == "Body Content"
