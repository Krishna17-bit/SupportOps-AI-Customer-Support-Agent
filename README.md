# SupportOps AI — Customer Support Ticket Triage & Resolution Agent

SupportOps AI is a customer support operations workspace for ticket triage, evidence-grounded reply drafting, refund review, SLA risk, churn-risk scoring, support QA, knowledge-base gap detection, and audit-ready export.

It is built for small SaaS teams, e-commerce teams, agencies, IT service firms, and startups that want support intelligence without immediately moving into a heavy helpdesk platform.

## What it does

- Bulk uploads support tickets from CSV, XLSX, JSON, or TXT.
- Uploads knowledge base files: PDF, DOCX, TXT, MD, CSV, XLSX, or JSON.
- Classifies each ticket by category.
- Scores urgency, sentiment, churn risk, SLA risk, and resolution confidence.
- Retrieves supporting evidence from uploaded policies, FAQs, product docs, and order exports.
- Drafts customer-ready replies with policy grounding.
- Flags missing information and unsafe requests.
- Reviews refund eligibility and escalation requirements.
- Scores reply quality.
- Detects weak knowledge-base coverage and suggests support macros.
- Exports triaged tickets CSV and audit JSON.

## Market gap targeted

Most customer support AI tools are full helpdesk platforms. SupportOps AI focuses on a lightweight, upload-first support intelligence workflow:

- bulk ticket triage,
- evidence-grounded answers,
- refund and SLA decision support,
- human-review safety gates,
- audit packages,
- knowledge-base gap detection,
- support QA scoring.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## API key

Copy `.env.example` to `.env` and add your key:

```bash
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-pro
```

The UI intentionally does not show the provider or model name.

## Run

```bash
streamlit run app.py
```

## How to test quickly

1. Start the app.
2. Do not upload anything first.
3. Keep “Include sample support knowledge base” checked.
4. Click **Run support analysis**.
5. Open each tab: Ticket Triage, Reply Assistant, Evidence Map, Refund & Escalation, SLA + Churn Risk, Support Analytics, KB Gaps + Macros, Audit + Export.

## Input ticket columns

Recommended ticket columns:

```text
ticket_id, customer_name, email, subject, body, channel, created_at, order_id
```

Missing columns are filled safely.

## Safety

- The app does not auto-send emails.
- Refunds and credits are not auto-approved.
- Unsafe instructions and possible sensitive-data issues are flagged.
- Drafts should be reviewed by a human before being sent.
