"""
Configuration loader for the Weekly Pulse Pipeline.

Loads environment variables from .env and exposes them as a validated
config dictionary. All required keys are checked at import time so
missing values are caught early.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from the project root ────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_dotenv_path = _PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=_dotenv_path)

# ── Required environment variable keys ─────────────────────────
_REQUIRED_KEYS = [
    "LLM_API_KEY",
    "GROQ_API_KEY",
    "MCP_DOCS_SERVER_URL",
    "MCP_GMAIL_SERVER_URL",
    "RECIPIENT_EMAIL",
]


def _load_config() -> dict:
    """
    Read all required keys from the environment and return them as a dict.
    Raises SystemExit with a clear message if any key is missing.
    """
    missing = [key for key in _REQUIRED_KEYS if not os.getenv(key)]
    if missing:
        print(
            f"[CONFIG ERROR] Missing required environment variables:\n"
            f"  {', '.join(missing)}\n"
            f"Please set them in {_dotenv_path} or your environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    config_dict = {key: os.getenv(key) for key in _REQUIRED_KEYS}
    
    # Add optional keys
    config_dict["DEFAULT_PLAY_STORE_ID"] = os.getenv("DEFAULT_PLAY_STORE_ID")
    config_dict["DEFAULT_APP_STORE_ID"] = os.getenv("DEFAULT_APP_STORE_ID")
    
    return config_dict


# ── Expose config at module level ──────────────────────────────
config = _load_config()


if __name__ == "__main__":
    # Quick sanity check: python src/config.py
    print("✅ Config loaded successfully:")
    for key, value in config.items():
        # Mask sensitive keys
        if "KEY" in key or "SECRET" in key:
            display = value[:4] + "****" if len(value) > 4 else "****"
        else:
            display = value
        print(f"  {key} = {display}")
