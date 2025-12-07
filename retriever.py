# test_retriever.py
from sentence_transformers import SentenceTransformer
from pathlib import Path
import faiss
import pickle
import numpy as np

VECTOR_DIR = Path("vectorstore")
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4  # how many chunks to fetch per query

# load model
print("Loading embedding model:", MODEL_NAME)
model = SentenceTransformer(MODEL_NAME)

# load vectorstore
index_path = VECTOR_DIR / "faiss_index.bin"
texts_pkl = VECTOR_DIR / "texts.pkl"
metas_pkl = VECTOR_DIR / "metas.pkl"

if not index_path.exists():
    raise SystemExit("ERROR: faiss_index.bin not found in vectorstore/. Run build_index.py first.")
print("Loading FAISS index...")
index = faiss.read_index(str(index_path))

with open(texts_pkl, "rb") as f:
    texts = pickle.load(f)
with open(metas_pkl, "rb") as f:
    metas = pickle.load(f)

def retrieve(query, top_k=TOP_K):
    q_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb.astype("float32"), top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        results.append({
            "score": float(score),
            "chunk_index": int(idx),
            "chunk_file": metas[idx].get("chunk_file", "unknown") if isinstance(metas[idx], dict) else metas[idx].get("chunk_file", "unknown"),
            "page_number": metas[idx].get("page_number", None) if isinstance(metas[idx], dict) else None,
            "text_preview": texts[idx][:400].replace("\n"," ")
        })
    return results

if __name__ == "__main__":
    # Replace these two queries with your own test queries if you like.
    tests = [
        "Define acute inflammation",
        "Explain the steps of coagulation"
    ]
    for q in tests:
        print("\n\n=== QUERY ===")
        print(q)
        hits = retrieve(q, top_k=TOP_K)
        print(f"Top {TOP_K} hits:")
        for i, h in enumerate(hits, start=1):
            print(f"\n[{i}] score: {h['score']:.4f} | page: {h['page_number']} | file: {h['chunk_file']}")
            print("preview:", h["text_preview"][:300] + ("..." if len(h["text_preview"])>300 else ""))
