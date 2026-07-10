"""
Weekly Pulse Pipeline — Main Orchestrator

Usage:
    # Manual run (any app):
    python src/main.py com.whatsapp 310633997
    python src/main.py com.spotify.music 324684580 --count 200

    # Automated run (uses DEFAULT_PLAY_STORE_ID / DEFAULT_APP_STORE_ID env vars):
    python src/main.py
"""

import argparse
import logging
import os
import sys
import traceback
from datetime import datetime

# ── Logging setup ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("WeeklyPulse")


def parse_args():
    """Parse command-line arguments for app IDs and review count.
    
    Falls back to DEFAULT_PLAY_STORE_ID / DEFAULT_APP_STORE_ID env vars
    when no CLI args are provided (for Railway cron deployment).
    """
    parser = argparse.ArgumentParser(
        description="Generate a Weekly Pulse Report for any mobile app.",
        epilog="Example: python src/main.py com.whatsapp 310633997 --count 150",
    )
    parser.add_argument(
        "play_store_id",
        nargs="?",
        default=os.getenv("DEFAULT_PLAY_STORE_ID"),
        help="Google Play Store package ID (e.g., com.whatsapp). "
             "Falls back to DEFAULT_PLAY_STORE_ID env var.",
    )
    parser.add_argument(
        "app_store_id",
        nargs="?",
        default=os.getenv("DEFAULT_APP_STORE_ID"),
        help="Apple App Store numeric ID (e.g., 310633997). "
             "Falls back to DEFAULT_APP_STORE_ID env var.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=int(os.getenv("REVIEW_COUNT", "100")),
        help="Number of reviews to fetch per store (default: 100)",
    )
    args = parser.parse_args()

    if not args.play_store_id or not args.app_store_id:
        parser.error(
            "App IDs required. Provide them as arguments or set "
            "DEFAULT_PLAY_STORE_ID and DEFAULT_APP_STORE_ID env vars."
        )

    return args


def run_pipeline(play_store_id: str, app_store_id: str, count: int) -> dict:
    """Run the end-to-end pulse pipeline and return the results."""
    from src.config import config
    
    log.info("=" * 60)
    log.info("  Weekly Pulse Pipeline")
    log.info("  Play Store: %s | App Store: %s", play_store_id, app_store_id)
    log.info("  Reviews per store: %d", count)
    log.info("=" * 60)

    # ── Phase 1: Ingest Reviews ────────────────────────────────
    log.info("-" * 40)
    log.info("PHASE 1: Fetching reviews...")

    from src.ingestion.play_store import fetch_play_store_reviews
    from src.ingestion.app_store import fetch_app_store_reviews
    from src.ingestion.normalizer import normalize, deduplicate
    from src.ingestion.sanitizer import sanitize

    log.info("  Fetching Play Store reviews for '%s'...", play_store_id)
    play_raw = fetch_play_store_reviews(play_store_id, count=count)
    log.info("  Fetched %d raw Play Store reviews.", len(play_raw))

    log.info("  Fetching App Store reviews for '%s'...", app_store_id)
    app_raw = fetch_app_store_reviews(app_store_id, count=count)
    log.info("  Fetched %d raw App Store reviews.", len(app_raw))

    # Normalize
    play_reviews = normalize(play_raw, "play_store")
    app_reviews = normalize(app_raw, "app_store")
    all_reviews = play_reviews + app_reviews
    log.info("  Normalized: %d reviews (%d Play + %d App).",
                len(all_reviews), len(play_reviews), len(app_reviews))

    # Deduplicate
    all_reviews = deduplicate(all_reviews)
    log.info("  After deduplication: %d reviews.", len(all_reviews))

    # Sanitize PII
    all_reviews = sanitize(all_reviews)
    log.info("  After PII sanitization: %d clean reviews.", len(all_reviews))

    if not all_reviews:
        raise ValueError("No reviews survived filtering. Try a different app or increase count.")

    # ── Phase 2: LLM Analysis (Groq) ─────────────────────────
    log.info("-" * 40)
    log.info("PHASE 2: Generating pulse analysis via Groq...")

    from src.drafting.groq_client import GroqClient
    from src.processing.pulse_generator import PulseGenerator

    llm = GroqClient(api_key=config["GROQ_API_KEY"])
    generator = PulseGenerator(llm_client=llm)
    pulse_report = generator.generate_pulse(all_reviews)

    log.info("  Pulse generated: %d themes, %d quotes, %d actions.",
                len(pulse_report.themes), len(pulse_report.quotes), len(pulse_report.actions))

    for i, theme in enumerate(pulse_report.themes, 1):
        log.info("    Theme %d: %s (%s)", i, theme.name, theme.sentiment)

    # ── Phase 3: Groq Drafting ─────────────────────────────────
    log.info("-" * 40)
    log.info("PHASE 3: Drafting polished report via Groq...")

    from src.drafting.drafter import ReportDrafter

    drafter = ReportDrafter(groq_client=llm)
    drafts = drafter.draft_report(pulse_report)

    log.info("  Draft complete (Doc: %d words, Email: %d words).", 
                len(drafts.doc_content.split()), len(drafts.email_body.split()))

    # ── Phase 4: Publish to Google Docs via MCP ────────────────
    log.info("-" * 40)
    log.info("PHASE 4: Publishing to Google Docs via MCP...")

    doc_url = None
    try:
        from src.integration.docs_mcp import DocsPublisher

        publisher = DocsPublisher(server_url=config["MCP_DOCS_SERVER_URL"])
        doc_url = publisher.publish_pulse(drafts.doc_content)

        log.info("  Google Doc published: %s", doc_url)

    except Exception as e:
        log.error("PHASE 4 FAILED: %s", e)
        log.debug(traceback.format_exc())
        log.warning("  Continuing without Doc URL — email will not contain a link.")

    # ── Phase 5: Send Email via Gmail MCP ─────────────────────
    log.info("-" * 40)
    log.info("PHASE 5: Sending email via MCP...")

    confirmation = None
    try:
        from src.integration.gmail_mcp import GmailNotifier

        # Replace the {doc_url} placeholder with the actual doc URL
        email_body = drafts.email_body.replace("{doc_url}", doc_url or "[Doc creation failed]")

        subject = f"Weekly App Review Pulse - {datetime.now().strftime('%B %d, %Y')}"
        recipient = config["RECIPIENT_EMAIL"]

        notifier = GmailNotifier(server_url=config["MCP_GMAIL_SERVER_URL"])
        confirmation = notifier.send_email(
            recipient=recipient,
            subject=subject,
            email_body=email_body,
        )

        log.info("  Gmail sent! %s", confirmation)
        log.info("  Recipient: %s", recipient)

    except Exception as e:
        log.error("PHASE 5 FAILED: %s", e)
        log.debug(traceback.format_exc())

    # ── Summary ────────────────────────────────────────────────
    log.info("=" * 60)
    log.info("  PIPELINE COMPLETE")
    log.info("  App: %s / %s", play_store_id, app_store_id)
    log.info("  Reviews analyzed: %d", len(all_reviews))
    log.info("  Themes found: %d", len(pulse_report.themes))
    if doc_url:
        log.info("  Google Doc: %s", doc_url)
    log.info("=" * 60)
    
    return {
        "play_store_id": play_store_id,
        "app_store_id": app_store_id,
        "reviews_analyzed": len(all_reviews),
        "themes_found": len(pulse_report.themes),
        "doc_url": doc_url,
        "doc_content": drafts.doc_content,
        "email_body": drafts.email_body,
        "email_confirmation": confirmation
    }


def main():
    try:
        from src.config import config
    except SystemExit:
        log.error("Missing environment variables. Check your .env file.")
        return
    except Exception as e:
        log.error("Failed to load config: %s", e)
        return

    args = parse_args()
    
    try:
        run_pipeline(
            play_store_id=args.play_store_id,
            app_store_id=args.app_store_id,
            count=args.count
        )
    except Exception as e:
        log.error("PIPELINE FAILED: %s", e)
        log.debug(traceback.format_exc())


if __name__ == "__main__":
    main()
