#!/bin/bash

# URL of the S&P 500 constituents CSV
CSV_URL="https://raw.githubusercontent.com/datasets/s-and-p-500-companies/refs/heads/main/data/constituents.csv"

# Fetch the CSV using curl and parse/sort it using the Windows Python launcher (py)
curl -s "$CSV_URL" | py -c '
import csv, sys, re

reader = csv.reader(sys.stdin)
next(reader)  # Skip the header row

companies = []
for row in reader:
    if len(row) >= 8:
        company = row[1].strip()
        location = row[4].strip()
        founded = row[7].strip()
        
        # Extract the first 4-digit year for sorting
        year_match = re.search(r"\d{4}", founded)
        sort_year = int(year_match.group()) if year_match else 9999
        
        companies.append((sort_year, company, location, founded))

# Sort the list by the extracted founding year
companies.sort(key=lambda x: x[0])

# Print the formatted output
print(f"{'\''Company'\'':<45} | {'\''Location'\'':<35} | {'\''Founded'\''}")
print("-" * 100)
for c in companies:
    display_year = c[3] if c[3] else "N/A"
    print(f"{c[1]:<45} | {c[2]:<35} | {display_year}")
'