# Outbound Data Pipeline Reconciliation Gate

A Python pipeline that cleans raw vendor lead exports before they touch a live outbound campaign. It answers one question: **where did every single row go?**

## Scope

Build a data quality gate for a B2B outbound campaign that had been running for 90 days with:
- A 3.1% reply rate
- 5 meetings from 13,000 contacts
- Two of five sending domains bouncing above 6%
- A handoff note with numbers that did not match the actual data

The goal was to stop the bleeding before any more volume was sent.

## What the Pipeline Does

1. Parses the raw CSV with `csv.DictReader` (not line counting)
2. Normalizes and deduplicates emails
3. Validates email format and drops generic inboxes
4. Drops suppressed domains
5. Filters by employee count and title
6. Runs a reconciliation gate: `input == output + sum(exclusions)`
7. Writes `send_ready.csv` and prints a QA report

If the gate fails, the script exits non-zero and refuses to write the file. A pipeline that cannot prove where every row went is a pipeline that quietly drops leads.