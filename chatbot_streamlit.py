# app_streamlit.py
import os
import streamlit as st
from pathlib import Path
from qa_with_openai import answer_with_openai  # uses your existing function
from retriever import retrieve  # optional: to fetch sources separately

# UI config
st.set_page_config(page_title="Textbook Chat", layout="wide")

PROJECT_ROOT = Path.cwd()
CLEAN_PAGES_DIR = PROJECT_ROOT / "clean_pages"

st.title("📚 Textbook Chat — Ask & cite by page")
st.caption("Ask questions about your cleaned textbook. Answers include page citations derived from retrieved chunks.")

# session state for chat history
if "history" not in st.session_state:
    st.session_state.history = []  # list of (user, bot, retrieved) tuples

# simple sidebar controls
with st.sidebar:
    st.header("Controls")
    st.markdown(
        "- Type questions in the box below and press Enter\n"
        "- Click a source to view the full page text\n"
        "- Keep your `.env` or set OPENAI_API_KEY in Streamlit secrets for deployment"
    )
    st.markdown("### Quick examples")
    st.write("- Define acute inflammation")
    st.write("- Explain the steps of coagulation")
    st.write("- Explain compartment syndrome")
    if st.button("Clear chat"):
        st.session_state.history = []
        st.experimental_rerun()

# input box
with st.form("ask_form", clear_on_submit=True):
    user_question = st.text_input("Ask a question (or type 'page 74')", placeholder="e.g. Define acute inflammation")
    submit = st.form_submit_button("Ask")

if submit and user_question:
    # call your existing function which returns (answer_text, retrieved_list)
    try:
        answer_text, retrieved = answer_with_openai(user_question)
    except Exception as e:
        st.error(f"Error when calling model: {e}")
        st.stop()

    # store history
    st.session_state.history.append({"user": user_question, "answer": answer_text, "retrieved": retrieved})

# show chat history (most recent last)
for turn in st.session_state.history:
    st.markdown(f"**You:** {turn['user']}")
    st.markdown(f"**Bot:** {turn['answer']}")
    # sources area
    with st.expander("Sources (click to expand)"):
        for i, r in enumerate(turn["retrieved"], start=1):
            page_no = r.get("page_number")
            chunk_file = r.get("chunk_file")
            score = r.get("score", 0.0)
            # preview is first lines — we don't have preview in the retriever but chunk text is present in r['text']
            preview = (r.get("text") or "")[:400].replace("\n", " ")
            cols = st.columns([1, 8, 1])
            cols[0].markdown(f"**{i}.**")
            cols[1].markdown(f"**page {page_no}** — `{chunk_file}`  \n\n{preview}...")
            # show full page button
            key = f"show_page_{page_no}_{i}"
            if cols[2].button("Show full page", key=key):
                # read full page file if exists
                page_fname = CLEAN_PAGES_DIR / f"page_{int(page_no):03d}.txt"
                if page_fname.exists():
                    full = page_fname.read_text(encoding="utf-8")
                    st.code(full, language="text")
                else:
                    st.warning(f"Full page file not found: {page_fname}")

    st.markdown("---")
