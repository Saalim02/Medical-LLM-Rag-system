# verify_split.py
import os
from pathlib import Path

DIR = Path("clean_pages")
files = sorted(DIR.glob("page_*.txt"))

print(f"Total page files found: {len(files)}")

# Show first 3 and last 3 filenames
print("\nSample files:")
for p in (files[:3] + files[-3:]):
    print(" ", p.name)

# Check for empty or suspiciously small files
print("\nChecking file sizes:")
for p in files:
    if p.stat().st_size < 20:  # likely empty or broken
        print(f" !! {p.name} is too small -> check this file manually")

# Show first 10 lines of first and last pages
print("\nPreview page 1:")
f1 = files[0].read_text(encoding="utf-8").splitlines()[:10]
for line in f1:
    print(line)

print("\nPreview last page:")
fl = files[-1].read_text(encoding="utf-8").splitlines()[:10]
for line in fl:
    print(line)

print("\nIf everything looks fine, reply: OK VERIFIED")
