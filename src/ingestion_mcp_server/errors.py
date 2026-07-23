from googleapiclient.errors import HttpError
from typing import Callable, Any

def map_google_error(e: HttpError) -> str:
    """
    Maps Google API HttpErrors to human-readable/MCP tool error strings.
    """
    status_code = e.resp.status
    error_details = str(e)
    
    if status_code == 401:
        return "Authentication expired or invalid. Please re-run the OAuth flow."
    elif status_code == 403:
        return f"Permission denied (403). The account may lack required scopes or access rights. Details: {error_details}"
    elif status_code == 404:
        return f"Resource not found (404). Check the document ID or email identifiers. Details: {error_details}"
    elif status_code == 429:
        return "Rate limited (429). Please wait before trying again."
    elif status_code >= 500:
        return f"Google API server error ({status_code}). Please try again later."
    
    return f"Google API error ({status_code}): {error_details}"

def with_error_mapping(func: Callable) -> Callable:
    """
    Decorator to map Google API errors to standard exceptions with clean messages.
    (Optional helper if using standard functions, though MCP handles exceptions automatically).
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            raise RuntimeError(map_google_error(e))
    return wrapper
