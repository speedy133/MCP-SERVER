# Edge Cases & Corner Scenarios

This document catalogs edge cases and corner scenarios across all pipeline modules, along with recommended handling strategies.

---

## 1. Data Ingestion Module

### 1.1. No Reviews Found
- **Scenario**: The app has zero public reviews in the 8–12 week window (e.g., brand-new app, delisted app, or wrong app ID).
- **Impact**: The entire pipeline has no data to process.
- **Handling**: Log a warning and exit gracefully. Do **not** create an empty Google Doc or draft email. Optionally send a notification: _"No reviews found for the configured app IDs."_

### 1.2. Only One Store Returns Reviews
- **Scenario**: Play Store returns reviews but App Store returns zero (or vice versa), due to regional availability, API issues, or the app being single-platform.
- **Impact**: Pipeline proceeds with partial data; themes may be skewed toward one platform.
- **Handling**: Log which store returned empty results. Proceed with available reviews. Include a note in the pulse: _"Data sourced from Play Store only this week."_

### 1.3. Very Few Reviews (< 10)
- **Scenario**: The app receives too few reviews to produce meaningful themes.
- **Impact**: Clustering into 5 themes becomes unreliable; quotes may be repetitive.
- **Handling**: Set a minimum review threshold (e.g., 10). If below threshold, generate a simplified pulse noting limited data, or skip the pulse with a log message.

### 1.4. Extremely Long Review Text
- **Scenario**: A single review contains thousands of characters (rants, pasted logs, etc.).
- **Impact**: May blow up LLM token limits or skew analysis.
- **Handling**: Truncate individual review text to a configurable max length (e.g., 1000 characters) during normalization. Log truncation.

### 1.5. Non-English / Mixed-Language Reviews
- **Scenario**: Reviews are in multiple languages, or entirely in a non-English language.
- **Impact**: LLM clustering and quote extraction may produce inconsistent results.
- **Handling**: Optionally filter to a target language during ingestion. If multilingual support is needed, pass language hints to the LLM prompt. Document the supported language(s) in config.

### 1.6. Duplicate Reviews Across Stores
- **Scenario**: A user posts identical or near-identical reviews on both App Store and Play Store.
- **Impact**: Inflates theme counts and may surface the same quote twice.
- **Handling**: Deduplicate using exact text match and fuzzy matching (e.g., >90% similarity). Prefer the more recent copy.

### 1.7. Fetcher API Rate Limiting / Downtime
- **Scenario**: The public scraping library or RSS feed is rate-limited, blocked, or temporarily down.
- **Impact**: Ingestion fails partway or returns incomplete data.
- **Handling**: Implement retry with exponential backoff (max 3 retries). If all retries fail, log the error and halt. Do not proceed with partial, unreliable data.

### 1.8. Malformed or Missing Review Fields
- **Scenario**: A review is missing a `title`, `rating`, or `date` field.
- **Impact**: Downstream processing may fail on `None` values.
- **Handling**: Set sensible defaults during normalization (e.g., empty string for missing title, `0` for missing rating). Log any reviews with missing critical fields (`text`). Discard reviews with no `text` content.

---

## 2. PII Sanitization

### 2.1. PII Embedded in Non-Obvious Formats
- **Scenario**: An email is written as `john [at] gmail [dot] com`, or a phone number uses spaces: `+1 555 123 4567`.
- **Impact**: Regex-based scrubber misses the PII.
- **Handling**: Maintain a broad set of regex patterns covering common obfuscation styles. Periodically audit sample outputs for PII leakage. Consider a secondary LLM-based PII check for high-sensitivity deployments.

### 2.2. Over-Redaction
- **Scenario**: The scrubber redacts legitimate product names, feature names, or version numbers that resemble PII patterns (e.g., `v2.3.1@release`).
- **Impact**: Quotes become unreadable or lose context.
- **Handling**: Maintain an allowlist of known safe terms (product names, versions). Test the scrubber against a curated set of false-positive examples.

### 2.3. Review Text is Entirely PII
- **Scenario**: A review is nothing but a username and email asking for support.
- **Impact**: After sanitization, the review text is just `[REDACTED] [REDACTED]`.
- **Handling**: Discard reviews where the post-sanitization text is below a minimum meaningful length (e.g., < 10 characters).

---

## 3. Processing & Analysis Engine (LLM)

### 3.1. LLM API Timeout or Failure
- **Scenario**: The LLM API (e.g., Gemini) is down, returns a 5xx error, or times out.
- **Impact**: No `PulseReport` is generated; pipeline stalls.
- **Handling**: Retry up to 3 times with exponential backoff. If all retries fail, log the error and halt. Do not fall back to a "best guess" pulse.

### 3.2. LLM Returns Malformed / Unparseable Output
- **Scenario**: The LLM ignores the structured output instructions and returns freeform text, or JSON with unexpected keys.
- **Impact**: `PulseReport` parsing fails.
- **Handling**: Validate LLM output against the expected schema. If parsing fails, retry the prompt (up to 2 times) with a stricter instruction. If still invalid, log the raw response and halt.

### 3.3. LLM Invents Quotes
- **Scenario**: The LLM fabricates a quote instead of selecting a verbatim one from the input reviews.
- **Impact**: Violates the "no invented wording" requirement.
- **Handling**: After quote extraction, verify each returned quote exists (exact or near-exact match) in the original sanitized review list. Reject and re-prompt for any unmatched quotes.

### 3.4. All Reviews Have the Same Theme
- **Scenario**: Every review is about the same issue (e.g., a major outage).
- **Impact**: Clustering produces only 1 theme instead of 3–5.
- **Handling**: Allow the pulse to report fewer than 3 themes if the data genuinely supports only 1–2. Adjust the pulse template to handle `1 ≤ themes ≤ 5` gracefully.

### 3.5. LLM Token Limit Exceeded
- **Scenario**: The total review text exceeds the LLM's context window.
- **Impact**: API returns a token-limit error, or silently truncates input.
- **Handling**: Before calling the LLM, count tokens and truncate/sample the review list if it exceeds the model's limit. Prefer a representative sample (stratified by rating) over simple truncation.

### 3.6. Conflicting Sentiment Across Stores
- **Scenario**: Play Store reviews are overwhelmingly negative, but App Store reviews are positive (or vice versa).
- **Impact**: Themes may mask platform-specific issues.
- **Handling**: Include the `source` field in the data sent to the LLM. Optionally annotate themes with platform breakdown in the pulse.

---

## 4. Final Drafting Module (Groq LLM)

### 4.1. Groq API Timeout or Failure
- **Scenario**: Groq API is unreachable, rate-limited, or returns an error.
- **Impact**: No polished report or email is generated.
- **Handling**: Retry up to 3 times with exponential backoff. If Groq is unavailable, fall back to using the raw `PulseReport.formatted_pulse` from Phase 4 as the doc content, and a simple template for the email body. Log the fallback clearly.

### 4.2. Groq Output Exceeds Word Limit
- **Scenario**: Groq generates a report that is over 250 words despite the prompt constraint.
- **Impact**: The pulse is no longer "scannable" per the requirements.
- **Handling**: Count words in the returned `doc_content`. If > 250, re-prompt Groq with an explicit instruction to shorten. If still over after 2 retries, truncate to 250 words at a sentence boundary and append `...`.

### 4.3. Groq Alters Verbatim Quotes
- **Scenario**: During polishing, Groq paraphrases a quote instead of keeping it verbatim.
- **Impact**: Violates the "no invented wording" constraint.
- **Handling**: After drafting, verify that each quote in `doc_content` still matches a quote from the original `PulseReport`. If not, replace the altered quote with the original verbatim version.

### 4.4. `{doc_url}` Placeholder Missing from Email Body
- **Scenario**: Groq generates an email body that omits the `{doc_url}` placeholder.
- **Impact**: The final email will not contain a link to the Google Doc.
- **Handling**: After drafting, check that `{doc_url}` exists in `email_body`. If missing, append a line: `\nView the full report: {doc_url}`.

---

## 5. Integration Module (MCP Gateway)

### 5.1. MCP Server Unreachable
- **Scenario**: The Google Docs or Gmail MCP server is down or misconfigured.
- **Impact**: Cannot publish the doc or create the draft.
- **Handling**: Retry connection up to 3 times. If all fail, log the error with the MCP server URL. Save the generated report and email body locally as fallback files (`data/pulse_fallback.md`, `data/email_fallback.txt`) so the user can manually publish.

### 5.2. MCP Authentication Failure
- **Scenario**: The MCP server's OAuth tokens have expired or are revoked.
- **Impact**: Tool calls return 401/403 errors.
- **Handling**: Log the auth error clearly with instructions for the user to re-authenticate with the MCP server. Halt the pipeline. Save drafts locally as fallback.

### 5.3. Google Doc Already Exists (Duplicate Creation)
- **Scenario**: The pipeline runs twice in the same week, creating duplicate "Weekly Pulse" documents.
- **Impact**: Stakeholders see two conflicting versions.
- **Handling**: Before creating a new doc, search for an existing doc with the same title and date. If found, update it instead of creating a duplicate. Use a naming convention like `Weekly Pulse – YYYY-MM-DD` to identify.

### 5.4. Gmail Draft Quota / Size Limits
- **Scenario**: The pulse content is too large for a Gmail draft, or the account has hit API quotas.
- **Impact**: Draft creation fails.
- **Handling**: If the body is too large, include only a summary in the email and link to the full Google Doc. Log quota errors and retry after a delay.

### 5.5. Recipient Email is Invalid
- **Scenario**: The configured `RECIPIENT_EMAIL` is malformed or doesn't exist.
- **Impact**: Draft creation may fail, or the draft is unusable.
- **Handling**: Validate the email format at startup (config loader phase). Reject obviously invalid formats. Note that Gmail draft creation may still succeed even for invalid addresses—the error surfaces at send time.

---

## 6. Orchestrator / Pipeline-Level

### 6.1. Partial Pipeline Failure (Mid-Run Crash)
- **Scenario**: The pipeline succeeds through analysis but crashes during MCP integration.
- **Impact**: A `PulseReport` was generated but never published.
- **Handling**: Implement checkpointing. Save intermediate outputs (`PulseReport`, `FinalDrafts`) to disk after each phase. On restart, detect checkpoints and resume from the last successful phase.

### 6.2. Concurrent Executions
- **Scenario**: A cron job triggers while a previous run is still in progress.
- **Impact**: Duplicate docs, race conditions, or garbled output.
- **Handling**: Use a lock file (`data/.pipeline.lock`). At startup, check if the lock exists. If it does, log a warning and exit. Remove the lock on completion or error.

### 6.3. Missing or Invalid Environment Variables
- **Scenario**: `.env` is missing `GROQ_API_KEY`, `LLM_API_KEY`, or MCP server URLs.
- **Impact**: Pipeline crashes with an unhelpful `KeyError`.
- **Handling**: Validate all required env vars at startup in `config.py`. If any are missing, print a clear error listing the missing keys and exit immediately.

### 6.4. Clock / Timezone Issues
- **Scenario**: The server's clock is wrong, or timezones cause the "last 8–12 weeks" window to be miscalculated.
- **Impact**: Reviews from the wrong date range are fetched.
- **Handling**: Use UTC internally for all date calculations. Log the computed date range at the start of ingestion for auditability.

---

## Summary Table

| Module | Edge Case | Severity | Strategy |
|---|---|---|---|
| Ingestion | No reviews found | High | Halt gracefully, notify |
| Ingestion | Single store returns data | Medium | Proceed, annotate pulse |
| Ingestion | Very few reviews | Medium | Minimum threshold check |
| Ingestion | Extremely long review | Low | Truncate at max length |
| Ingestion | Non-English reviews | Medium | Language filter or hint |
| Ingestion | API rate limiting | High | Retry with backoff |
| Sanitizer | Obfuscated PII | High | Broad regex + audit |
| Sanitizer | Over-redaction | Medium | Allowlist safe terms |
| LLM | API timeout/failure | High | Retry, then halt |
| LLM | Malformed output | High | Schema validation + retry |
| LLM | Invented quotes | High | Post-verification against source |
| LLM | Token limit exceeded | Medium | Pre-call token counting + sampling |
| Groq | API failure | High | Retry, fallback to raw pulse |
| Groq | Output exceeds 250 words | Medium | Re-prompt or truncate |
| Groq | Altered quotes | High | Post-verification |
| Groq | Missing `{doc_url}` | Medium | Auto-append placeholder |
| MCP | Server unreachable | High | Retry, save local fallback |
| MCP | Auth failure | High | Log, halt, save fallback |
| MCP | Duplicate doc creation | Medium | Check-before-create |
| Pipeline | Partial failure | High | Checkpoint & resume |
| Pipeline | Concurrent execution | Medium | Lock file |
| Pipeline | Missing env vars | High | Validate at startup |
