#!/usr/bin/env python3

import csv
import sys
import re
from collections import defaultdict
from pathlib import Path

def validate_email(email):
    """Check if email matches basic format: something@something.domain"""
    pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    return bool(re.match(pattern, email))

def get_email_prefix(email):
    """Extract prefix (local part) of email before @"""
    if '@' not in email:
        return None
    return email.split('@')[0].lower()

def is_generic_inbox(email_prefix):
    """Check if email prefix is a generic inbox address"""
    generic_prefixes = {'info', 'sales', 'warehouse'}
    return email_prefix in generic_prefixes

def main():
    input_file = 'leads_raw.csv'
    output_file = 'send_ready.csv'
    
    # Domains to suppress
    suppressed_domains = {'ridgeline3pl.com', 'norvind.com', 'bellwether-scm.com'}
    
    # Track all records and exclusions
    input_records = []
    exclusions = defaultdict(int)
    valid_records = []
    seen_emails = set()
    
    # Read input CSV
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            input_records = []
            for row in reader:
                # Remove None key if it exists (from malformed rows)
                if None in row:
                    del row[None]
                input_records.append(row)
    except Exception as e:
        print(f"ERROR: Failed to read input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    input_count = len(input_records)
    
    # Extract fieldnames from first record (excluding None if present)
    fieldnames = [k for k in input_records[0].keys() if k is not None] if input_records else []
    
    # Process each record
    for record in input_records:
        email = record.get('email', '').strip()
        title = record.get('title', '').strip()
        company_domain = record.get('company_domain', '').strip()
        employees_str = record.get('employees', '').strip()
        
        exclusion_reason = None
        
        # Check 1: Missing email
        if not email:
            exclusion_reason = 'missing_email'
        
        # Check 2: Invalid email format
        elif not validate_email(email):
            exclusion_reason = 'invalid_email_format'
        
        # Check 3: Generic inbox
        else:
            email_prefix = get_email_prefix(email)
            if is_generic_inbox(email_prefix):
                exclusion_reason = 'generic_inbox'
        
        # Check 4: Suppressed domain
        if not exclusion_reason and company_domain.lower() in suppressed_domains:
            exclusion_reason = 'suppressed_domain'
        
        # Check 5: Title contains "owner"
        if not exclusion_reason and 'owner' in title.lower():
            exclusion_reason = 'title_contains_owner'
        
        # Check 6: Employee count out of range
        if not exclusion_reason:
            try:
                emp_count = int(employees_str) if employees_str else None
                if emp_count is None:
                    exclusion_reason = 'missing_employee_count'
                elif emp_count < 250:
                    exclusion_reason = 'employees_below_250'
                elif emp_count > 10000:
                    exclusion_reason = 'employees_above_10000'
            except ValueError:
                exclusion_reason = 'invalid_employee_count'
        
        # Record exclusion or add to valid set
        if exclusion_reason:
            exclusions[exclusion_reason] += 1
        else:
            # Normalize email: lowercase
            email_normalized = email.lower()
            
            # Check for duplicate (case-insensitive)
            if email_normalized in seen_emails:
                exclusions['duplicate_email'] += 1
            else:
                seen_emails.add(email_normalized)
                # Store with normalized email
                clean_record = record.copy()
                clean_record['email'] = email_normalized
                valid_records.append(clean_record)
    
    output_count = len(valid_records)
    
    # Verify reconciliation
    accounted_for = output_count + sum(exclusions.values())
    if accounted_for != input_count:
        print("QA REPORT", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        print(f"Input records:     {input_count}", file=sys.stderr)
        print(f"Output records:    {output_count}", file=sys.stderr)
        print(f"Excluded records:  {sum(exclusions.values())}", file=sys.stderr)
        print(f"Total accounted:   {accounted_for}", file=sys.stderr)
        print("", file=sys.stderr)
        print("ERROR: Reconciliation failed - counts do not match!", file=sys.stderr)
        print("", file=sys.stderr)
        print("Exclusions by reason:", file=sys.stderr)
        for reason in sorted(exclusions.keys()):
            print(f"  {reason}: {exclusions[reason]}", file=sys.stderr)
        sys.exit(1)
    
    # Sort by email
    valid_records.sort(key=lambda r: r['email'].lower())
    
    # Write output CSV
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            # Clean records before writing (remove None keys)
            for record in valid_records:
                if None in record:
                    del record[None]
                writer.writerow(record)
    except Exception as e:
        print(f"ERROR: Failed to write output file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print QA report to stdout
    print("QA REPORT")
    print("=" * 60)
    print(f"Input records:     {input_count}")
    print(f"Output records:    {output_count}")
    print(f"Excluded records:  {sum(exclusions.values())}")
    print()
    print("Exclusions by reason:")
    for reason in sorted(exclusions.keys()):
        print(f"  {reason}: {exclusions[reason]}")
    print()
    print("Reconciliation: OK" if accounted_for == input_count else "FAILED")
    print(f"Output file:       {output_file}")

if __name__ == '__main__':
    main()