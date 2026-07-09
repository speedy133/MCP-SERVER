# Implementation Plan

## Overview
This plan breaks the project into **7 sequential phases**, each with clear inputs, outputs, files to create/modify, and acceptance criteria. Phases are ordered by dependency—each builds on the previous one.

---

## Phase 1: Project Scaffolding & Configuration

**Goal**: Set up the repository structure, dependencies, and environment configuration so all subsequent phases have a stable foundation.

### Tasks
| # | Task | Files | Details |
|---|---|---|---|
| 1.1 | Create directory structure | `src/`, `src/ingestion/`, `src/processing/`, `src/integration/`, `data/`, `tests/` | Match the layout from `architecture.md` |
| 1.2 | Initialize Python package files | `src/ingestion/__init__.py`, `src/processing/__init__.py`, `src/integration/__init__.py` | Empty init files to make packages importable |
| 1.3 | Create `requirements.txt` | `requirements.txt` | Include: `google-play-scraper`, `app-store-scraper`, `python-dotenv`, `google-generativeai` (or chosen LLM SDK), `groq` (Groq Python SDK), `mcp` (MCP client SDK) |
| 1.4 | Create environment config | `.env.example`, `.env` | Keys: `LLM_API_KEY`, `GROQ_API_KEY`, `MCP_DOCS_SERVER_URL`, `MCP_GMAIL_SERVER_URL`, `APP_ID_PLAY_STORE`, `APP_ID_APP_STORE`, `RECIPIENT_EMAIL` |
| 1.5 | Create config loader | `src/config.py` | Load `.env` values and expose them as a config object/dict used by all modules |
| 1.6 | Set up `.gitignore` | `.gitignore` | Ignore `.env`, `__pycache__/`, `data/*.json`, `venv/` |

### Acceptance Criteria
- [ ] Running `python -c "from src.config import config; print(config)"` loads env values without error.
- [ ] All directories and init files exist.

---

## Phase 2: Data Ingestion — Review Fetching

**Goal**: Build the module that pulls public reviews from both app stores and normalizes them into a unified schema.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 2.1 | Implement Play Store fetcher | `src/ingestion/play_store.py` | Function `fetch_play_store_reviews(app_id: str, count: int) -> list[dict]`. Uses `google-play-scraper` library. Returns raw reviews. |
| 2.2 | Implement App Store fetcher | `src/ingestion/app_store.py` | Function `fetch_app_store_reviews(app_id: str, count: int) -> list[dict]`. Uses `app-store-scraper` library. Returns raw reviews. |
| 2.3 | Implement normalizer | `src/ingestion/normalizer.py` | Function `normalize(raw_reviews: list[dict], source: str) -> list[Review]`. Maps source-specific fields to unified schema: `{ source, date, rating, title, text }`. |
| 2.4 | Implement deduplicator | `src/ingestion/normalizer.py` | Function `deduplicate(reviews: list[Review]) -> list[Review]`. Removes duplicate reviews based on text similarity or exact match. |
| 2.5 | Write sample test data | `data/sample_reviews.json` | A static JSON file with ~20 sample reviews for offline development and testing. |
| 2.6 | Unit tests | `tests/test_ingestion.py` | Test normalization, deduplication, and verify schema compliance. |

### Unified Review Schema
```python
@dataclass
class Review:
    source: str      # "play_store" | "app_store"
    date: str        # ISO 8601 date string
    rating: int      # 1–5
    title: str       # Review title (may be empty)
    text: str        # Review body
```

### Acceptance Criteria
- [ ] Fetchers return review lists from both stores for a given app ID.
- [ ] Normalizer produces `Review` objects matching the schema.
- [ ] Deduplication removes exact-match duplicate reviews.
- [ ] All unit tests pass.

---

## Phase 3: Data Ingestion — PII Sanitization

**Goal**: Ensure no personally identifiable information passes beyond the ingestion boundary.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 3.1 | Implement PII scrubber | `src/ingestion/sanitizer.py` | Function `sanitize(reviews: list[Review]) -> list[Review]`. Uses regex to detect and redact: emails (`\S+@\S+`), phone numbers, @-handles, device IDs, and names (basic heuristics). Replaces matches with `[REDACTED]`. |
| 3.2 | Build regex pattern registry | `src/ingestion/sanitizer.py` | A `PII_PATTERNS` dict mapping pattern names to compiled regex objects for maintainability. |
| 3.3 | Unit tests | `tests/test_sanitizer.py` | Test with deliberately seeded PII data. Assert that output contains zero PII matches. |

### Acceptance Criteria
- [ ] Running `sanitize()` on reviews containing emails, handles, and phone numbers returns text with `[REDACTED]` replacements.
- [ ] No PII survives in the output list.
- [ ] All unit tests pass.

---

## Phase 4: Processing & Analysis Engine (LLM)

**Goal**: Build the LLM-powered pipeline that clusters reviews into themes, extracts quotes, generates actions, and formats the weekly pulse.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 4.1 | Implement LLM client | `src/processing/llm_client.py` | Class `LLMClient` wrapping the chosen LLM API. Methods: `generate(prompt: str, expect_json: bool)`. Handles API auth, JSON parsing, retries, and backoff. |
| 4.2 | Design prompt templates | `src/processing/prompts.py` | Store string constants: `LOCAL_ANALYSIS_PROMPT` (for map chunks) and `SYNTHESIS_PROMPT` (for global reduction). Enforces JSON schema. |
| 4.3 | Implement pulse generator | `src/processing/pulse_generator.py` | Class `PulseGenerator` that buckets reviews by sentiment (Detractor, Passive, Promoter) and chunks them. Runs Map-Reduce if volume > 50. |
| 4.4 | Define `PulseReport` model | `src/processing/pulse_generator.py` | Dataclasses: `Theme`, `Quote`, and `PulseReport` (generated_date, themes, quotes, actions). |
| 4.5 | Implement response parser | `src/processing/pulse_generator.py` | Parse LLM JSON responses into structured `PulseReport` fields. |
| 4.6 | Unit tests | `tests/test_processing.py` | Test with sample reviews using a mocked LLM client. Verify parsing and bucketing logic. |

### LLM Call Sequence (Map-Reduce)
```
[Detractors] ──▶ chunk(50) ──▶ [LOCAL_ANALYSIS_PROMPT] ──▶ Local Themes
[Passives]   ──▶ chunk(50) ──▶ [LOCAL_ANALYSIS_PROMPT] ──▶ Local Themes
[Promoters]  ──▶ chunk(50) ──▶ [LOCAL_ANALYSIS_PROMPT] ──▶ Local Themes
                                                               │
                                                               ▼
All Local Themes ──▶ [SYNTHESIS_PROMPT] ──▶ Final Top 5 Themes, 3 Quotes, 3 Actions (JSON)
```

### Acceptance Criteria
- [ ] `PulseGenerator` groups reviews by rating before analysis.
- [ ] Large review volumes are successfully batched (Map phase) and synthesized (Reduce phase).
- [ ] Themes ≤ 5, quotes = 3 (verbatim, not invented), actions = 3.
- [ ] All unit tests pass.

---

## Phase 5: Final Drafting Module (Groq LLM)

**Goal**: Use Groq LLM to transform the raw `PulseReport` into a polished, publication-ready Google Doc report and a professional email body before handing off to MCP.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 5.1 | Implement Groq client | `src/drafting/groq_client.py` | Class `GroqClient` wrapping the Groq Python SDK. Method: `generate(prompt: str, model: str = "llama-3.3-70b-versatile") -> str`. Handles API key auth and retries. |
| 5.2 | Design report drafting prompt | `src/drafting/prompts.py` | `REPORT_DRAFT_PROMPT` — instructs Groq to compose a scannable one-page report (≤ 250 words) with headings, bullet points, and professional tone from the `PulseReport` data. |
| 5.3 | Design email drafting prompt | `src/drafting/prompts.py` | `EMAIL_DRAFT_PROMPT` — instructs Groq to compose a concise, professional email body summarizing the pulse and including a `{doc_url}` placeholder. |
| 5.4 | Implement final drafter | `src/drafting/final_drafter.py` | Class `FinalDrafter` with method `draft(pulse_report: PulseReport) -> FinalDrafts`. Calls Groq twice: once for the report, once for the email. Returns a `FinalDrafts` object. |
| 5.5 | Define `FinalDrafts` model | `src/drafting/final_drafter.py` | Dataclass: `{ doc_content: str, email_body: str }`. |
| 5.6 | Unit tests | `tests/test_drafting.py` | Test with a mock `PulseReport`. Verify `doc_content` is ≤ 250 words and `email_body` contains `{doc_url}` placeholder. |

### Groq Call Sequence
```
PulseReport
    │
    ├──▶ [REPORT_DRAFT_PROMPT + themes/quotes/actions] ──▶ Groq ──▶ doc_content (polished report)
    │
    └──▶ [EMAIL_DRAFT_PROMPT + themes/summary]          ──▶ Groq ──▶ email_body (professional email)
```

### Acceptance Criteria
- [ ] `FinalDrafter.draft()` produces a `FinalDrafts` object with both `doc_content` and `email_body`.
- [ ] `doc_content` is well-structured, scannable, and ≤ 250 words.
- [ ] `email_body` is professional and includes the `{doc_url}` placeholder.
- [ ] All unit tests pass.

---

## Phase 6: Integration Module — MCP Gateway

**Goal**: Connect to Google Docs and Gmail MCP servers to publish the pulse and draft the notification email.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 6.1 | Implement MCP base client | `src/integration/mcp_client.py` | Shared MCP client setup: connect to an MCP server URL, call tools, handle responses. Wraps the MCP Python SDK. |
| 6.2 | Implement Google Docs MCP client | `src/integration/docs_mcp.py` | Function `publish_pulse(doc_content: str) -> str`. Receives polished `doc_content` from the Groq drafting module. Calls the Docs MCP server to create or update a document. Returns the Google Doc URL. |
| 6.3 | Implement Gmail MCP client | `src/integration/gmail_mcp.py` | Function `draft_email(recipient: str, subject: str, email_body: str) -> str`. Receives polished `email_body` from the Groq drafting module (with `{doc_url}` replaced). Calls the Gmail MCP server to create a draft email. Returns the draft ID. |
| 6.4 | Integration tests | `tests/test_integration.py` | Test MCP client connectivity. Verify that `publish_pulse` returns a valid URL and `draft_email` returns a draft ID. (Requires MCP servers to be running.) |

### MCP Tool Call Examples

**Google Docs — Create Document:**
```python
result = mcp_client.call_tool("create_document", {
    "title": "Weekly Pulse – July 7, 2026",
    "content": final_drafts.doc_content
})
doc_url = result["url"]
```

**Gmail — Create Draft:**
```python
email_body = final_drafts.email_body.replace("{doc_url}", doc_url)
result = mcp_client.call_tool("create_draft", {
    "to": "team@example.com",
    "subject": "Weekly App Review Pulse – July 7, 2026",
    "body": email_body
})
draft_id = result["draft_id"]
```

### Acceptance Criteria
- [ ] `publish_pulse()` successfully creates a Google Doc and returns a URL.
- [ ] `draft_email()` successfully creates a Gmail draft and returns a draft ID.
- [ ] No custom OAuth or REST API code exists in the codebase.
- [ ] Integration tests pass with live MCP servers.

---

## Phase 7: Orchestrator & End-to-End Pipeline

**Goal**: Wire all modules together into a single executable pipeline with proper error handling and logging.

### Tasks
| # | Task | File | Details |
|---|---|---|---|
| 7.1 | Implement main orchestrator | `src/main.py` | Sequential execution: load config → fetch reviews → sanitize → generate pulse → Groq draft → publish doc → draft email → log summary. |
| 7.2 | Add logging | `src/main.py` | Use Python `logging` module. Log start/end of each phase, review counts, theme names, doc URL, draft ID, and any errors. |
| 7.3 | Add error handling | `src/main.py` | Wrap each phase in try/except. If a phase fails, log the error with traceback and halt gracefully (do not proceed to downstream phases). |
| 7.4 | End-to-end test | `tests/test_e2e.py` | Run the full pipeline with sample data. Verify that a Google Doc is created and a Gmail draft exists. |

### Orchestrator Pseudocode
```python
def main():
    config = load_config()

    # Step 1: Ingest
    play_reviews = fetch_play_store_reviews(config.play_app_id)
    app_reviews  = fetch_app_store_reviews(config.app_store_id)
    all_reviews  = normalize(play_reviews + app_reviews)
    all_reviews  = deduplicate(all_reviews)
    all_reviews  = sanitize(all_reviews)
    log.info(f"Ingested {len(all_reviews)} clean reviews")

    # Step 2: Analyze
    pulse = PulseGenerator(config.llm_api_key).generate_pulse(all_reviews)
    log.info(f"Pulse generated: {len(pulse.themes)} themes")

    # Step 3: Draft with Groq
    drafts = FinalDrafter(config.groq_api_key).draft(pulse)
    log.info("Final report and email drafted via Groq")

    # Step 4: Publish & Notify
    doc_url  = publish_pulse(drafts.doc_content)
    email_body = drafts.email_body.replace("{doc_url}", doc_url)
    draft_id = draft_email(config.recipient, subject, email_body)
    log.info(f"Doc: {doc_url} | Draft: {draft_id}")
```

### Acceptance Criteria
- [ ] `python src/main.py` executes the full pipeline end-to-end.
- [ ] A Google Doc is created with the Groq-polished report.
- [ ] A Gmail draft is created with the Groq-polished email body and a link to the Doc.
- [ ] Errors in any phase are caught, logged, and prevent downstream execution.
- [ ] End-to-end test passes.

---

## Phase 8: Scheduling & Deployment

**Goal**: Automate weekly execution so the pulse is generated and delivered without manual intervention.

### Tasks
| # | Task | File/Tool | Details |
|---|---|---|---|
| 8.1 | Create run script | `run.sh` / `run.ps1` | Activate virtual environment and execute `python src/main.py`. |
| 8.2 | Configure weekly schedule | OS Scheduler | **Linux**: cron entry `0 9 * * 1 /path/to/run.sh` (every Monday 9 AM). **Windows**: Task Scheduler pointing to `run.ps1`. |
| 8.3 | (Optional) Dockerize | `Dockerfile` | Containerize the app for cloud deployment (e.g., Google Cloud Run + Cloud Scheduler, AWS Lambda + EventBridge). |
| 8.4 | Documentation | `README.md` | Setup instructions, environment variable reference, how to run manually, how to configure scheduling. |

### Acceptance Criteria
- [ ] The pipeline runs automatically on the configured schedule.
- [ ] `README.md` documents full setup and usage.

---

## Phase Summary & Dependencies

```
Phase 1 ──▶ Phase 2 ──▶ Phase 3 ──▶ Phase 4 ──▶ Phase 5 ──▶ Phase 6 ──▶ Phase 7 ──▶ Phase 8
Setup       Fetch       Sanitize    LLM/Pulse   Groq        MCP Docs    Orchestrate  Schedule
            Reviews     PII         Analysis    Drafting    & Gmail     & Wire       & Deploy
```

| Phase | Depends On | Key Output |
|---|---|---|
| 1. Scaffolding | — | Project structure, config loader |
| 2. Review Fetching | Phase 1 | `play_store.py`, `app_store.py`, `normalizer.py` |
| 3. PII Sanitization | Phase 2 | `sanitizer.py` |
| 4. LLM Processing | Phase 1, 3 | `llm_client.py`, `pulse_generator.py`, `prompts.py` |
| 5. Groq Drafting | Phase 1, 4 | `groq_client.py`, `final_drafter.py`, `drafting/prompts.py` |
| 6. MCP Integration | Phase 1 | `docs_mcp.py`, `gmail_mcp.py`, `mcp_client.py` |
| 7. Orchestrator | Phase 2–6 | `main.py` (end-to-end pipeline) |
| 8. Scheduling | Phase 7 | Automated weekly execution |
