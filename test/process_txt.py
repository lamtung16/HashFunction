import csv
import re

input_file = "input.txt"
output_file = "output.csv"

# Regex to capture host, username, password
pattern = re.compile(r"(https?://[^/]+)/get\.php\?username=([^&]+)&password=([^&]+)")

rows = []
seen = set()  # Track unique entries to avoid duplicates

with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        line = line.strip()
        match = pattern.search(line)
        if match:
            host = match.group(1)
            username = match.group(2)
            password = match.group(3)
            
            row = (host, username, password)
            if row not in seen:
                seen.add(row)
                rows.append(list(row))

# Write to CSV
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["host", "username", "password"])
    writer.writerows(rows)

print(f"Saved {len(rows)} unique entries to {output_file}")