Part 4: Scale, Cost, Skill

A. Scale - How does this run on thousands of rows?
The order of steps:
1. Read the CSV properly (free)
2. Clean emails and remove duplicates (free)
3. Check email format and drop generic inboxes (free)
4. Drop suppressed domains (free)
5. Filter by employee count and job title (free)
6. Run the reconciliation gate. If the numbers don't add up, stop. Don't write the file. (free)
7. Verify the emails (costs money)
8. Enrich missing data (costs money)
9. Write the clean file (free)
10. Send the campaign (costs money)
Free steps first. Paid steps last. This way we only pay for rows that survive all the filters.
Before spending money, I run 100 rows through the paid steps first. If the sample looks good, I run the rest.
If the script dies at row 3,000 of 9,000, it saves a checkpoint every 500 rows. When it restarts, it picks up from row 3,001. It does not start over. The broken row goes into a separate file so we can look at it later.

B. Cost - What does one pass cost?
The previous engineer said $0.42 per row. That is too high.
Real prices: email verification is about $0.003 to $0.01 per email. Enrichment is about $0.05 to $0.15 per contact. Real total is about $0.06 to $0.16 per row.
At $0.42 per row: 14,203 rows = about $5,965. At $0.10 per row: about $1,420.
I would run the free steps first so we only pay for rows that survive. Verify before enriching. Use more than one vendor. Cap the spending.

C. Before we buy anything
Dev wants to buy 20,000 more contacts. Here is what we already have.
The data pack shows 8,457 verified leads. Only 6,027 were contacted. That means 2,430 verified leads were never emailed. We already paid to verify them.
The handoff note claims 14,203 leads. The data pack shows 9,100. About 5,103 records are missing.
So we have at least 2,430 leads already paid for and never used.
What is it worth? At 3.1% reply rate, that is about 75 replies. Enough to learn what works.
What does it cost to use them? About $24 for verification and $243 for enrichment. Under $300 total.
Buying 20,000 new contacts would cost $8,400 at $0.42 per row, or $2,000 at $0.10 per row.
My recommendation: do not buy yet. Run the 2,430 through the fixed pipeline first. Measure the reply rate. Then decide.

D. The Skill - The repeatable playbook
Name: Lead Pipeline Reconciliation Gate
What it does: reads a raw vendor CSV, applies the rules, writes a clean send file, and proves where every row went.
Steps:
1. Parse with csv.DictReader. Never count lines.
2. Save fieldnames inside the with block.
3. If there is no header, stop.
4. Check every row for None keys (malformed rows).
5. Lowercase emails. Remove duplicates.
6. Check email format. Reject spaces in emails.
7. Drop generic inboxes (info@, sales@, warehouse@).
8. Drop suppressed domains. Lowercase domains first.
9. Remove spaces before converting employees to a number.
10. Apply employee and title filters.
11. Sort by email so the output is the same every time.
12. Print the QA report with input count, output count, and every exclusion reason.
13. If input does not equal output plus exclusions, stop. Do not write the file.
Failure modes I hit:
Silent no-op. If the __main__ guard is missing, the script runs and does nothing. Always check that the QA report prints.
Closed file. Saving fieldnames after the with block crashes the script. Save them inside.
Empty file. If the file has no header, the script crashes. Check for this.
Malformed rows. Extra commas push values into a None key. Count these and drop them.
Wrong labels. Misaligned rows get labeled "missing email" when they are not. The math still works but the reasons are wrong. A human has to check.
Spaces in numbers. " 2400" crashes int(). Always strip first.
What a naive agent would get wrong:
Count lines instead of records.
Enrich before filtering. Waste money on suppressed domains.
Trust the reconciliation total without reading the categories.
Assume a clean report means a clean file.
What needs human review:
The category labels, not just the totals.
Any row marked malformed.
Any domain with a bounce rate above 2%.