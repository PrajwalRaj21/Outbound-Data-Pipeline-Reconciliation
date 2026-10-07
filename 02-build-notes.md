Model used: Claude Haiku 4.5 (small tier, extended reasoning mode). Selected per the brief's instruction to pick the middle or smallest model.
Session link: https://claude.ai/share/63026d4a-b8a5-40af-a00c-9bf5a47c6cb6



What my first attempt got wrong:
Claude gave me a script that used an absolute path from its own sandbox: /mnt/user-data/uploads/leads_raw.csv. That path does not exist on my machine. It also wrote output to clean_leads.csv instead of send_ready.csv.
Was the cause the data or my instruction: my instruction. I did not specify relative paths or the exact output filename.


What my second attempt got wrong:
Claude corrected the path but used ../leads_raw.csv, which resolves to D:\leads_raw.csv, one folder above where the file actually lives. Still wrong.
What my third attempt got right:
I told Claude to use the literal string leads_raw.csv with no directory logic, and send_ready.csv for output. That ran clean. 26 input, 15 output, 11 exclusions. Reconciles exactly.


Ambiguous rules and my decisions:
Misaligned rows: excluded, not repaired. Misalignment is a data integrity signal.
Personal emails (gmail): allowed. A personal email is not a generic role inbox.
Spaced emails (like s. marchetti@...): rejected as invalid format. A space inside an email is corruption.
High-bounce domains: flagged, not auto-suppressed in this exercise. In production I would suppress them until they recover.
What I would not trust the model to do unattended:
Reconcile the exclusion categories, not just the totals. The math held. But the categories can change between runs on the same input. A human has to read the categories, not just the reconciliation number.


Part 3: Catch the Model
Failure 1 (sandbox path):
Quote: ERROR: Failed to read input file: [Errno 2] No such file or directory: '/mnt/user-data/uploads/leads_raw.csv'
Defect: Claude used an absolute path from its own sandbox environment. The path does not exist on my machine.
How I caught it: I ran the script locally and it failed immediately on file read.
Fix: Told Claude the file is in the current working directory and to use the literal relative path leads_raw.csv with no directory logic.
Failure 2 (wrong relative path):
Quote: ERROR: Failed to read input file: [Errno 2] No such file or directory: '../leads_raw.csv'
Defect: Claude overcorrected. It used ../ which resolves one folder above where the file actually lives.
How I caught it: Ran the script again. Same class of error, different path.
Fix: Told Claude to use exactly leads_raw.csv, no prefix.
Failure 3 (wrong output filename):
Quote: The script wrote clean_leads.csv instead of send_ready.csv.
Defect: The output filename was hardcoded wrong.
How I caught it: I checked the folder after running. The expected output file was missing and a wrong-named file appeared.
Fix: Told Claude the output must be send_ready.csv. Specific edit, not a vague request.
The lesson:
Every fix I sent was a specific edit to the spec, not a vague appeal. A clean reconciliation does not mean clean data. The gate protects against silent drops. It does not protect against misclassification. You still have to read the output file.