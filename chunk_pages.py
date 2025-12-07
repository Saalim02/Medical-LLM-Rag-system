# chunk_pages.py
import os
import json
from pathlib import Path
import math

PAGES_DIR = Path("clean_pages")
OUT_DIR = Path("chunks")
OUT_DIR.mkdir(exist_ok=True)

# Adjust these if you want larger/smaller chunks.
# chunk_size_chars ~ controls chunk length (~200-800 tokens depending on text)
CHUNK_SIZE = 2000      # characters per chunk (tweak if too long/short)
CHUNK_OVERLAP = 200    # characters overlap between consecutive chunks

def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    if size <= 0:
        raise ValueError("size must be > 0")
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    chunks = []
    start = 0
    text_len = len(text)
    while start < text_len:
        end = start + size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        if end >= text_len:
            break
        start = end - overlap
    return chunks

metadata = []
page_files = sorted([p for p in PAGES_DIR.glob("page_*.txt")])

if not page_files:
    print("ERROR: No page_*.txt files found in 'clean_pages'. Make sure you've run split_pages.py first.")
    raise SystemExit(1)

total_chunks = 0
for pf in page_files:
    page_text = pf.read_text(encoding="utf-8").strip()
    if not page_text:
        print(f"Warning: {pf.name} is empty — skipping.")
        continue
    page_num = int(pf.stem.split("_")[1])
    chunks = chunk_text(page_text)
    for i, ch in enumerate(chunks, start=1):
        chunk_name = f"{pf.stem}_chunk_{i:02d}.txt"
        out_path = OUT_DIR / chunk_name
        out_path.write_text(ch, encoding="utf-8")
        meta = {
            "chunk_file": chunk_name,
            "page_file": pf.name,
            "page_number": page_num,
            "chunk_index": i,
            "char_length": len(ch),
            "preview": ch[:120].replace("\n"," ")
        }
        metadata.append(meta)
        total_chunks += 1

# write metadata json
meta_path = OUT_DIR / "metadata.json"
meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

print(f"Chunking complete. Created {total_chunks} chunk files in '{OUT_DIR}'.")
print(f"Metadata written to '{meta_path}'. Example entries:")
for m in metadata[:5]:
    print(" ", m["chunk_file"], "-> page", m["page_number"], "(len:", m["char_length"], ")")
