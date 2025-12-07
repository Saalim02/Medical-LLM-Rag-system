# qa_with_openai.py
import os
import json
import pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
import openai
from dotenv import load_dotenv

# === CONFIG ===
VECTOR_DIR = Path("vectorstore")
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 4
OPENAI_MODEL = "gpt-4o-mini"   # change if not available; you can use "gpt-4o" or "gpt-4o-mini"
MAX_TOKENS = 200  
TEMPERATURE = 0.0

# === load env ===
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise SystemExit("Set OPENAI_API_KEY in your environment or a .env file.")

# === load resources ===
print("Loading embedding model:", MODEL_NAME)
embed_model = SentenceTransformer(MODEL_NAME)

print("Loading FAISS index and metadata...")
index = faiss.read_index(str(VECTOR_DIR / "faiss_index.bin"))
with open(VECTOR_DIR / "texts.pkl","rb") as f:
    texts = pickle.load(f)
with open(VECTOR_DIR / "metas.pkl","rb") as f:
    metas = pickle.load(f)

def retrieve(query, top_k=TOP_K):
    q_emb = embed_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb.astype("float32"), top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        meta = metas[idx] if isinstance(metas[idx], dict) else {}
        results.append({
            "score": float(score),
            "page_number": meta.get("page_number"),
            "chunk_file": meta.get("chunk_file"),
            "text": texts[idx]
        })
    return results

SYSTEM_PROMPT = (
    "You are a precise medical-study assistant. Use ONLY the provided SOURCE TEXTS to answer. "
    "If the answer is found in the sources, cite the page number(s) in square brackets after the sentence or clause, e.g. [page 74]. "
    "If the answer is not in the provided sources, say: 'I cannot find a reliable answer in the provided pages.' Do NOT hallucinate."
)

def compose_system_and_user(query, retrieved):
    # Build a context that lists sources clearly
    ctx = ""
    for i, r in enumerate(retrieved, start=1):
        pn = r.get("page_number")
        ctx += f"--- SOURCE {i} (page {pn}) ---\n{r['text']}\n\n"
    user_message = (
        f"QUESTION: {query}\n\n"
        "Answer concisely in simple language suitable for a student. Include short citations like [page 74] "
        "immediately after any factual statement taken from the sources. If multiple pages support the same fact, you may include multiple citations, e.g. [page 74, page 76]."
    )
    return ctx, user_message

def answer_with_openai(query):
    # retrieve
    retrieved = retrieve(query, top_k=TOP_K)
    ctx, user_message = compose_system_and_user(query, retrieved)
    # build messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"CONTEXT:\n{ctx}\n\n{user_message}"}
    ]
    resp = openai.ChatCompletion.create(
        model=OPENAI_MODEL,
        messages=messages,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE
    )
    return resp["choices"][0]["message"]["content"], retrieved

if __name__ == "__main__":
    print("Chatbot ready! Type 'exit' to quit.\n")
    while True:
        q = input("You: ").strip()
        if q.lower() in ["exit", "quit", "bye"]:
            print("Exiting...")
            break
        
        answer, retrieved = answer_with_openai(q)
        
        print("\nBot:", answer)
        
        print("\nSources:")
        for i, r in enumerate(retrieved, start=1):
            print(f"[{i}] page: {r['page_number']} | file: {r['chunk_file']} | score: {r['score']:.4f}")
        print("\n" + "-"*50 + "\n")
