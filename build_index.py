# build_index.py
from sentence_transformers import SentenceTransformer
from pathlib import Path
import faiss
import numpy as np
import pickle
import json
from tqdm import tqdm

CHUNKS_DIR = Path("chunks")
VECTOR_DIR = Path("vectorstore")
VECTOR_DIR.mkdir(exist_ok=True)

MODEL_NAME = "all-MiniLM-L6-v2"
BATCH_SIZE = 64

print("Loading model:", MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)

# find chunk files
chunk_files = sorted([p for p in CHUNKS_DIR.glob("page_*_chunk_*.txt")])
if not chunk_files:
    print("ERROR: No chunk files found in 'chunks/'. Make sure chunk_pages.py created them.")
    raise SystemExit(1)

# load metadata.json if present for richer info
meta_path = CHUNKS_DIR / "metadata.json"
meta_map = {}
if meta_path.exists():
    with open(meta_path, "r", encoding="utf-8") as f:
        metas_all = json.load(f)
    meta_map = {m["chunk_file"]: m for m in metas_all}

texts = []
metas = []
for p in chunk_files:
    txt = p.read_text(encoding="utf-8").strip()
    texts.append(txt)
    m = meta_map.get(p.name, {"chunk_file": p.name, "page_file": "unknown", "page_number": None})
    metas.append(m)

print(f"Loaded {len(texts)} chunk texts. Computing embeddings in batches...")

# compute embeddings
emb_list = []
for i in tqdm(range(0, len(texts), BATCH_SIZE)):
    batch = texts[i:i+BATCH_SIZE]
    emb = model.encode(batch, convert_to_numpy=True, show_progress_bar=False)
    emb_list.append(emb)
embeddings = np.vstack(emb_list).astype("float32")

# normalize embeddings for cosine similarity
faiss.normalize_L2(embeddings)

d = embeddings.shape[1]
print(f"Embedding dim: {d}. Building FAISS index (IndexFlatIP)...")
index = faiss.IndexFlatIP(d)
index.add(embeddings)
print(f"Added {index.ntotal} vectors to index.")

# save index + metadata
faiss.write_index(index, str(VECTOR_DIR / "faiss_index.bin"))
with open(VECTOR_DIR / "texts.pkl", "wb") as f:
    pickle.dump(texts, f)
with open(VECTOR_DIR / "metas.pkl", "wb") as f:
    pickle.dump(metas, f)
with open(VECTOR_DIR / "metas.json", "w", encoding="utf-8") as f:
    json.dump(metas, f, ensure_ascii=False, indent=2)

print("Saved vectorstore to 'vectorstore/'")
print("Done.")
