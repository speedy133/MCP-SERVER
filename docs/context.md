# Project Context

## Goal
Turn raw mobile app store feedback (App Store & Play Store) into a weekly pulse that a team can scan in minutes—covering what users care about, what they actually said, and what to do next. Deliver the pulse through Google Docs and Gmail using MCP servers, without building custom OAuth or REST integrations.

## End-to-End Flow
1. **Pull Reviews** — Import recent public App Store and Play Store reviews (last 8–12 weeks). Fields include rating, title, text, and date.
2. **Cluster into Themes** — Group reviews into at most 5 themes (e.g., onboarding, KYC, payments, statements, withdrawals).
3. **Generate Weekly Pulse** — Distill a one-page note (≤ 250 words) containing:
   - Top 3 themes
   - 3 verbatim user quotes (anonymized, no invented wording)
   - 3 concrete action ideas
4. **Publish to Google Docs** — Create or update the pulse document via the Google Docs MCP server.
5. **Draft Email via Gmail** — Create a draft email (to self or alias) containing or linking to the pulse, via the Gmail MCP server.

## Deliverables
| Deliverable | Details |
|---|---|
| **Weekly Pulse (Google Doc)** | Top 3 themes, 3 real user quotes, 3 action ideas; scannable, ≤ 250 words |
| **Draft Email (Gmail)** | Contains or links to the weekly pulse; addressed to self or alias |

## Target Audience
| Audience | Value |
|---|---|
| Product / Growth | Prioritize fixes and improvements from real user signals |
| Support | Align messaging with what users are actually saying |
| Leadership | One-page health check without drowning in raw reviews |

## Integration Approach
- **MCP-First**: Use MCP (Model Context Protocol) servers for Google Docs and Gmail. MCP servers expose tools the agent/app can call, handling auth and HTTP plumbing.
- **No Manual API Wiring**: Do not build bespoke OAuth clients or REST integrations. Rely on MCP servers/connectors the environment provides.

## Key Constraints
- **Reviews**: Public exports only — no scraping behind store logins or ToS-violating automation.
- **Themes**: Maximum 5 themes for clustering; the pulse highlights the top 3.
- **Length**: Weekly note must be scannable and ≤ 250 words.
- **Privacy**: No PII (usernames, emails, device IDs) in any artifact. Quotes must be anonymous/stripped.
