import base64
from email.message import EmailMessage
from typing import List, Literal, Optional
from googleapiclient.discovery import build
from pydantic import BaseModel, Field

from ..auth import get_credentials
from ..validators import validate_email
from ..errors import with_error_mapping

class EmailSchema(BaseModel):
    to: List[str] = Field(..., description="Recipient email addresses (at least one)")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., description="Email body content")
    cc: Optional[List[str]] = Field(None, description="CC recipients")
    bcc: Optional[List[str]] = Field(None, description="BCC recipients")
    body_type: Literal["plain", "html"] = Field("plain", description="Whether body is plain text or HTML")

def _create_message(params: EmailSchema) -> dict:
    """Helper to create base64url encoded MIME message."""
    all_recipients = []
    
    # Validate emails
    for email_list in [params.to, params.cc or [], params.bcc or []]:
        for email in email_list:
            if not validate_email(email):
                raise ValueError(f"Invalid email address: {email}")
                
    message = EmailMessage()
    message.set_content(params.body, subtype=params.body_type)

    message["To"] = ", ".join(params.to)
    message["Subject"] = params.subject
    
    if params.cc:
        message["Cc"] = ", ".join(params.cc)
    if params.bcc:
        message["Bcc"] = ", ".join(params.bcc)
        
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"raw": encoded_message}

@with_error_mapping
def send_email_impl(params: EmailSchema) -> dict:
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    
    raw_msg = _create_message(params)
    
    # Send the email
    sent_message = service.users().messages().send(
        userId="me",
        body=raw_msg
    ).execute()
    
    return {
        "message_id": sent_message.get("id"),
        "thread_id": sent_message.get("threadId"),
        "confirmation": f"Email sent to {', '.join(params.to)} with subject '{params.subject}'"
    }

@with_error_mapping
def draft_email_impl(params: EmailSchema) -> dict:
    creds = get_credentials()
    service = build("gmail", "v1", credentials=creds)
    
    raw_msg = _create_message(params)
    
    # Create draft
    draft = service.users().drafts().create(
        userId="me",
        body={"message": raw_msg}
    ).execute()
    
    draft_message = draft.get("message", {})
    return {
        "draft_id": draft.get("id"),
        "message_id": draft_message.get("id"),
        "confirmation": f"Draft created for {', '.join(params.to)} with subject '{params.subject}'"
    }
