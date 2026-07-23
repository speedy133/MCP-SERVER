import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Minimum scopes required
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/documents"
]

def _write_env_secrets_to_disk():
    """
    If GOOGLE_CREDENTIALS_JSON or GOOGLE_TOKEN_JSON env vars are set,
    write them to disk so the rest of the auth flow can find them.
    This is the recommended pattern for Railway / container deployments
    where you can't commit secret files.
    """
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    token_json = os.environ.get("GOOGLE_TOKEN_JSON")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")

    if creds_json and not os.path.exists(creds_path):
        with open(creds_path, "w") as f:
            f.write(creds_json)

    if token_json and not os.path.exists(token_path):
        with open(token_path, "w") as f:
            f.write(token_json)


def get_credentials() -> Credentials:
    """
    Loads existing tokens or initiates the OAuth flow to get new ones.
    """
    # Materialise env-var secrets to files (Railway / cloud)
    _write_env_secrets_to_disk()

    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "token.json")

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                # If refresh fails, we will fallback to new login
                print(f"Warning: Token refresh failed: {e}")
                creds = None

        if not creds:
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {creds_path}. "
                    "Please download OAuth 2.0 Client IDs from Google Cloud Console "
                    "and set GOOGLE_CREDENTIALS_PATH appropriately."
                )
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            print("\n*** IMPORTANT ***")
            print("Please copy the URL below and paste it into Brave (or any browser of your choice):")
            creds = flow.run_local_server(port=0, open_browser=False)
            
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
            
    return creds
