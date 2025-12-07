# split_pages.py
import re
from pathlib import Path

# Name of your big file — change only if yours has a different name
BIG_FILE = "SRB.txt"

IN = Path(BIG_FILE)
OUT_DIR = Path("clean_pages")
OUT_DIR.mkdir(exist_ok=True)

if not IN.exists():
    print(f"ERROR: Could not find {BIG_FILE} in current folder. Rename your big file to '{BIG_FILE}' or edit the script.")
    raise SystemExit(1)

raw = IN.read_text(encoding="utf-8")

# Try several robust page-mark patterns. We will capture the marker and the following text.
# Examples matched: ==PAGE 1==  , == PAGE 001 == , ==PAGE:1== , ==PAGE-1== (case-insensitive)
page_marker_pattern = re.compile(r"(==\s*PAGE\b[^=\n]*==\s*)", flags=re.IGNORECASE)

# If we find the explicit markers, split on them but keep marker as header of each page.
markers = list(page_marker_pattern.finditer(raw))
if markers:
    print(f"Detected {len(markers)} page markers using '==PAGE...==' pattern.")
    # Build splits: include from one marker to the next
    spans = []
    for i, m in enumerate(markers):
        start = m.start()
        end = markers[i+1].start() if i+1 < len(markers) else len(raw)
        spans.append((m.group(1).strip(), raw[start:end].strip()))
else:
    # Fallback: try lines like "==PAGE 1==" without surrounding equals, or "Page 1" headers
    print("No '==PAGE...==' markers found. Trying alternate patterns (e.g., 'PAGE 1', 'Page 1').")
    alt_pattern = re.compile(r"(^\s*PAGE\s+(\d{1,4})\s*$)|(^\s*Page\s+(\d{1,4})\s*$)", flags=re.IGNORECASE | re.MULTILINE)
    alt_markers = list(alt_pattern.finditer(raw))
    if alt_markers:
        print(f"Detected {len(alt_markers)} page headers using alternate 'Page' pattern.")
        spans = []
        for i, m in enumerate(alt_markers):
            start = m.start()
            end = alt_markers[i+1].start() if i+1 < len(alt_markers) else len(raw)
            header = m.group(0).strip()
            spans.append((header, raw[start:end].strip()))
    else:
        # Final fallback: try splitting on repeated form-feed characters or multiple newlines with 'PAGE' word
        print("Alternate patterns failed. Trying to split on form-feed '\\f' or lines '==== page' heuristics.")
        if "\f" in raw:
            parts = raw.split("\f")
            spans = [("page_split_ff_"+str(i+1), p.strip()) for i,p in enumerate(parts) if p.strip()]
            print(f"Split into {len(spans)} parts using form-feed.")
        else:
            # As last resort, attempt to find lines containing the word "PAGE" and a number anywhere
            generic = re.compile(r"(^.*PAGE.*\d{1,4}.*$)", flags=re.IGNORECASE | re.MULTILINE)
            generic_markers = list(generic.finditer(raw))
            if generic_markers:
                spans = []
                for i, m in enumerate(generic_markers):
                    start = m.start()
                    end = generic_markers[i+1].start() if i+1 < len(generic_markers) else len(raw)
                    header = m.group(0).strip()
                    spans.append((header, raw[start:end].strip()))
                print(f"Found {len(spans)} generic PAGE-like headers.")
            else:
                print("ERROR: Could not detect page breaks automatically. If your file uses a different page marker, tell me its exact form or rename markers to '==PAGE X=='.")
                raise SystemExit(1)

# Now write out files with normalized page numbers where possible
written = 0
for idx, (header, text) in enumerate(spans, start=1):
    # Attempt to extract page number from header
    num_search = re.search(r"(\d{1,4})", header)
    if num_search:
        pn = int(num_search.group(1))
    else:
        # fallback to using sequence index if no number found
        pn = idx
    filename = OUT_DIR / f"page_{pn:03d}.txt"
    # Ensure we don't overwrite pages accidentally: if exists, append suffix
    if filename.exists():
        filename = OUT_DIR / f"page_{pn:03d}_{idx:02d}.txt"
    filename.write_text(text, encoding="utf-8")
    written += 1

print(f"Wrote {written} page files to '{OUT_DIR}'. Example files:")
for i, p in enumerate(sorted(OUT_DIR.glob("page_*.txt"))[:5], start=1):
    print("  ", p.name)
print("If you see gaps or wrong numbers, open a few files to confirm. Reply with DONE when you run this and it looks correct, or paste the script output if there are errors.")
