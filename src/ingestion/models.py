from dataclasses import dataclass

@dataclass
class Review:
    source: str      # "play_store" | "app_store"
    date: str        # ISO 8601 date string
    rating: int      # 1–5
    title: str       # Review title (may be empty)
    text: str        # Review body
