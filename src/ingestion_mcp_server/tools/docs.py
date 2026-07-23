import datetime
from googleapiclient.discovery import build
from pydantic import BaseModel, Field

from ..auth import get_credentials
from ..validators import extract_doc_id
from ..errors import with_error_mapping


class DocsAppendSchema(BaseModel):
    document_id: str = Field(..., description="The Google Doc ID or full Docs URL")
    content: str = Field(..., description="Text content to append")
    add_timestamp_heading: bool = Field(False, description="If true, prepend a heading line with the current date/time")
    leading_newline: bool = Field(True, description="Insert a newline before the content")


class DocsCreateSchema(BaseModel):
    title: str = Field(..., description="Title for the new Google Doc")
    content: str = Field(..., description="Text content to populate the document with")


@with_error_mapping
def create_document_impl(params: DocsCreateSchema) -> dict:
    """Create a brand-new Google Doc with the given title and body content."""
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)

    # Step 1: Create an empty doc with the title
    doc = service.documents().create(body={"title": params.title}).execute()
    doc_id = doc["documentId"]

    # Step 2: Insert the body content (index 1 = right after the implicit newline)
    if params.content.strip():
        service.documents().batchUpdate(
            documentId=doc_id,
            body={
                "requests": [
                    {
                        "insertText": {
                            "location": {"index": 1},
                            "text": params.content,
                        }
                    }
                ]
            },
        ).execute()

    url = f"https://docs.google.com/document/d/{doc_id}/edit"
    return {
        "document_id": doc_id,
        "url": url,
        "title": params.title,
        "characters_written": len(params.content),
    }


@with_error_mapping
def append_to_google_doc_impl(params: DocsAppendSchema) -> dict:
    creds = get_credentials()
    service = build("docs", "v1", credentials=creds)
    
    doc_id = extract_doc_id(params.document_id)
    if not doc_id:
        raise ValueError("Could not extract a valid Document ID from the provided input.")
        
    # Fetch the document to find the end index
    document = service.documents().get(documentId=doc_id).execute()
    
    # Calculate end index: body's content list's last element's endIndex - 1
    content_elements = document.get("body", {}).get("content", [])
    if not content_elements:
        raise RuntimeError("Document body is empty or malformed.")
        
    last_element = content_elements[-1]
    end_index = last_element.get("endIndex", 1) - 1
    
    # Prepare text to insert
    text_to_insert = ""
    if params.leading_newline:
        text_to_insert += "\n"
        
    if params.add_timestamp_heading:
        now_str = datetime.datetime.now().isoformat(timespec='seconds')
        text_to_insert += f"--- Entry: {now_str} ---\n"
        
    text_to_insert += params.content
    
    # We must insert at least something
    if not text_to_insert:
        raise ValueError("Content to append is empty.")

    requests = [
        {
            "insertText": {
                "location": {
                    "index": end_index,
                },
                "text": text_to_insert
            }
        }
    ]
    
    # Execute the batch update
    service.documents().batchUpdate(
        documentId=doc_id, body={"requests": requests}
    ).execute()
    
    return {
        "document_id": doc_id,
        "characters_appended": len(text_to_insert),
        "link": f"https://docs.google.com/document/d/{doc_id}/edit"
    }

