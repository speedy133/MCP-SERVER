# Architecture Design

## 1. System Overview

The system is an automated pipeline that ingests public mobile app reviews, analyzes them using an LLM, polishes the final outputs with Groq LLM, and delivers a weekly pulse report through Google Workspace—all orchestrated via the Model Context Protocol (MCP). The architecture is split into four distinct modules connected by a central orchestrator.

```
┌─────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌─────────────────────┐
│  Data        │   │  Processing &    │   │  Final Drafting  │   │  Integration Module │
│  Ingestion   │──▶│  Analysis Engine  │──▶│  (Groq LLM)      │──▶│  (MCP Gateway)      │
│  Module      │   │  (LLM)           │   │                  │   │                     │
└─────────────┘   └──────────────────┘   └──────────────────┘   │ ┌─────────────────┐ │
      ▲                                                         │ │ Google Docs MCP  │ │
      │                                                         │ └─────────────────┘ │
  Public Reviews                                                │ ┌─────────────────┐ │
  (App Store &                                                  │ │ Gmail MCP        │ │
   Play Store)                                                  │ └─────────────────┘ │
                                                                └─────────────────────┘
```

---

## 2. Core Components

### 2.1. Data Ingestion Module (Review Puller)

| Aspect | Detail |
|---|---|
| **Responsibility** | Fetch and normalize public app reviews from App Store and Play Store for the last 8–12 weeks. |
| **Data Sources** | Public CSV/JSON exports, RSS/Atom feeds, or public-access scraping libraries (e.g., `google-play-scraper`, `app-store-scraper`). |
| **Output Schema** | Normalized review objects with fields: `source`, `date`, `rating`, `title`, `text`. |
| **Constraints** | No scraping behind logins. No ToS-violating automation. |

**Internal Pipeline:**
1. **Fetch** — Pull raw review data from configured sources.
2. **Normalize** — Map source-specific formats into the unified review schema.
3. **Sanitize (PII Scrubbing)** — Strip usernames, emails, device IDs, and any other personally identifiable information using regex patterns and heuristic rules. This happens **before** any data leaves this module.
4. **Deduplicate** — Remove duplicate reviews across sources (e.g., same review text on both stores).
5. **Output** — Emit a clean list of `Review` objects for downstream processing.

---

### 2.2. Processing & Analysis Engine (LLM)

| Aspect | Detail |
|---|---|
| **Responsibility** | Analyze sanitized reviews to produce the structured weekly pulse content. |
| **Input** | Clean `Review` list from the Ingestion Module. |
| **Output** | A structured `PulseReport` object containing themes, quotes, and actions. |

**LLM Pipeline Steps:**

1. **Theme Clustering** — Send the full set of sanitized reviews to the LLM with a prompt instructing it to identify and group reviews into a **maximum of 5 themes** (e.g., Onboarding, KYC, Payments, Statements, Performance). Each review is tagged with its primary theme.
2. **Theme Prioritization** — Rank themes by review volume and sentiment severity. Select the **top 3** themes for the pulse.
3. **Quote Extraction** — For each of the top 3 themes, select **1 verbatim user quote** that best represents the sentiment. Quotes must be real (not invented) and fully anonymized.
4. **Action Generation** — Synthesize **3 concrete, actionable next steps** grounded in the identified themes, aimed at product, support, or growth teams.
5. **Pulse Formatting** — Assemble the output into a scannable, well-structured format (≤ 250 words) ready for document publishing.

**Output Structure (`PulseReport`):**
```json
{
  "generated_date": "2026-07-07",
  "themes": [
    { "name": "Payments", "review_count": 42, "sentiment": "negative" },
    { "name": "Onboarding", "review_count": 35, "sentiment": "mixed" },
    { "name": "Performance", "review_count": 28, "sentiment": "negative" }
  ],
  "quotes": [
    { "theme": "Payments", "text": "..." },
    { "theme": "Onboarding", "text": "..." },
    { "theme": "Performance", "text": "..." }
  ],
  "actions": [
    "...",
    "...",
    "..."
  ],
  "formatted_pulse": "# Weekly Pulse – July 7, 2026\n..."
}
```

---

### 2.3. Final Drafting Module (Groq LLM)

This module sits between the analysis engine and the MCP integration layer. It takes the structured `PulseReport` and uses **Groq LLM** (via the Groq API) to produce polished, publication-ready text for both the Google Doc report and the Gmail draft email.

| Aspect | Detail |
|---|---|
| **Responsibility** | Transform the raw `PulseReport` data into two polished prose outputs: a Google Doc report and an email body. |
| **LLM Provider** | [Groq](https://groq.com/) — chosen for its fast inference speed, making the drafting step near-instant. |
| **Input** | Structured `PulseReport` object from the Processing Engine (themes, quotes, actions). |
| **Output** | `FinalDrafts` object containing `doc_content` (formatted report) and `email_body` (professional email text). |

#### 2.3.1. Report Drafting
- Takes the themes, quotes, and actions from the `PulseReport`.
- Prompts Groq LLM to compose a well-structured, scannable one-page report (≤ 250 words) with clear headings, bullet points, and professional tone.
- Output: `doc_content` — the final text to be written to Google Docs.

#### 2.3.2. Email Drafting
- Takes the same `PulseReport` data plus the report summary.
- Prompts Groq LLM to compose a concise, professional email body that summarizes the key findings and includes a placeholder for the Google Doc link.
- Output: `email_body` — the final email text to be used in the Gmail draft.

**Output Structure (`FinalDrafts`):**
```json
{
  "doc_content": "# Weekly Pulse – July 7, 2026\n\n## Top Themes This Week\n...",
  "email_body": "Hi team,\n\nThis week's app review pulse is ready...\n\nView the full report: {doc_url}"
}
```

---

### 2.4. Integration Module (MCP Gateway)

This module handles all outbound communication with Google Workspace **exclusively via MCP tool calls**. No custom OAuth clients or direct REST API code. It receives the polished drafts from the Groq LLM module.

#### 2.4.1. Google Docs MCP Client
| Aspect | Detail |
|---|---|
| **Responsibility** | Create or update the weekly pulse document in Google Docs. |
| **Input** | `doc_content` from the Final Drafting Module. |
| **MCP Tools Used** | `create_document`, `update_document`, or equivalent tools exposed by the Google Docs MCP server. |
| **Behavior** | Checks if an existing "Weekly Pulse" document exists. If yes, appends/updates it. If no, creates a new one. Returns the document URL. |

#### 2.4.2. Gmail MCP Client
| Aspect | Detail |
|---|---|
| **Responsibility** | Draft a notification email containing or linking to the weekly pulse. |
| **Input** | `email_body` from the Final Drafting Module (with `{doc_url}` replaced by the actual URL). |
| **MCP Tools Used** | `create_draft` or equivalent tool exposed by the Gmail MCP server. |
| **Behavior** | Composes a draft email addressed to the configured recipient (self or alias). |

#### 2.4.3. Authentication & Auth Flow
- **Fully delegated to MCP servers.** The application does not store, manage, or refresh OAuth tokens.
- The MCP server environment handles Google API credentials and token lifecycle.

---

## 3. Orchestrator (Main Pipeline)

The orchestrator is the entry point that wires all modules together and manages execution flow.

```
┌──────────────────────────────────────────────────────────────┐
│                        Orchestrator                          │
│                                                              │
│  1. Load config (app IDs, recipient email, LLM settings)     │
│  2. Call Data Ingestion Module   ──▶  List[Review]           │
│  3. Call Processing Engine       ──▶  PulseReport            │
│  4. Call Groq Final Drafting     ──▶  FinalDrafts            │
│  5. Call Docs MCP Client         ──▶  doc_url                │
│  6. Call Gmail MCP Client        ──▶  draft_id               │
│  7. Log results & exit                                       │
└──────────────────────────────────────────────────────────────┘
```

- **Trigger**: Weekly cron job, scheduled task, or manual invocation.
- **Error Handling**: Each step logs success/failure. If a step fails (e.g., LLM timeout, Groq error, MCP connection error), the pipeline halts gracefully, logs the error, and can be retried.
- **Configuration**: Loaded from a `.env` or config file — app IDs, LLM API key, Groq API key, MCP server addresses, recipient email.

---

## 4. Data Flow Diagram

```
Public App Reviews
       │
       ▼
┌─────────────────┐
│  1. FETCH        │  Raw reviews (CSV/JSON/RSS)
│  2. NORMALIZE    │  Unified schema
│  3. SANITIZE     │  PII stripped
│  4. DEDUPLICATE  │  Clean review list
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  5. CLUSTER      │  ≤ 5 themes
│  6. PRIORITIZE   │  Top 3 themes
│  7. EXTRACT      │  3 verbatim quotes
│  8. GENERATE     │  3 action items
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  9. DRAFT REPORT │  Groq LLM → polished doc content (≤ 250 words)
│ 10. DRAFT EMAIL  │  Groq LLM → professional email body
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 11. PUBLISH DOC  │  Google Docs (via MCP) → doc_url
│ 12. SEND DRAFT   │  Gmail (via MCP) → draft_id
└─────────────────┘
```

---

## 5. Security & Privacy

| Concern | Approach |
|---|---|
| **PII** | Scrubbed at the ingestion layer before any data reaches the LLM or output artifacts. |
| **Authentication** | Delegated entirely to MCP servers. The app never touches OAuth tokens. |
| **Data at Rest** | Raw reviews are processed in-memory and not persisted unless explicitly configured for debugging. |
| **LLM Data** | Only anonymized review text is sent to the LLM. No PII leaves the ingestion boundary. |

---

## 6. Directory Structure (Proposed)

```
MCP Server/
├── docs/
│   ├── ProblemStatement.md
│   ├── context.md
│   ├── architecture.md          ← this file
│   └── implementation-plan.md
├── src/
│   ├── main.py                  # Orchestrator / entry point
│   ├── config.py                # Environment & config loader
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── play_store.py        # Google Play review fetcher
│   │   ├── app_store.py         # App Store review fetcher
│   │   ├── normalizer.py        # Schema normalization & dedup
│   │   └── sanitizer.py         # PII scrubbing
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── llm_client.py        # LLM API connection
│   │   ├── prompts.py           # Prompt templates
│   │   └── pulse_generator.py   # Clustering, quotes, actions
│   ├── drafting/
│   │   ├── __init__.py
│   │   ├── groq_client.py       # Groq LLM API connection
│   │   └── final_drafter.py     # Report & email drafting via Groq
│   └── integration/
│       ├── __init__.py
│       ├── mcp_client.py        # Shared MCP client setup
│       ├── docs_mcp.py          # Google Docs MCP client
│       └── gmail_mcp.py         # Gmail MCP client
├── data/                        # Sample/test review data
├── tests/
├── .env                         # API keys (LLM, Groq, MCP config)
└── requirements.txt
```
