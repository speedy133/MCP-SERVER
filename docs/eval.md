# Evaluation Parameters

## 1. Deployment and Hosting
* **Frontend Accessibility**: Is the frontend correctly hosted on Vercel and accessible publicly without requiring a Vercel team login?
* **Backend Accessibility**: Is the backend correctly hosted on Railway and accepting API requests?
* **Environment Configuration**: Are the required variables (e.g., `VITE_API_URL` for frontend) properly set in the deployed environments?

## 2. Core Functional Requirements
* **Data Ingestion**: Can the system pull recent App Store and Play Store reviews for a specified product?
* **Clustering**: Are the reviews successfully grouped into at most 5 themes?
* **Pulse Generation**: Does the pulse note contain exactly the top 3 themes, 3 user quotes, and 3 actionable ideas?
* **Word Count Constraint**: Is the final generated pulse note 250 words or fewer?
* **Privacy & Sanitization**: Are all user identifiable details (PII) successfully stripped from the output?

## 3. Integration Requirements
* **MCP Architecture**: Are MCP servers used for Docs and Gmail interactions instead of direct OAuth / REST APIs?
* **Google Docs Integration**: Does the system successfully create or update a Google Doc report?
* **Gmail Integration**: Does the system successfully create a draft email addressed to the user containing or linking to the pulse?
