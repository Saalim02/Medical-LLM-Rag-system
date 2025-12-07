🔍 How It Works (RAG Pipeline Summary)
This chatbot uses a Retrieval-Augmented Generation (RAG) workflow to answer medical questions accurately.

1️⃣ Clean the textbook
PDF pages are extracted and cleaned
Headers, footers, noise, and page numbers removed
Saved as .txt files inside clean_pages/

2️⃣ Chunk the text
Each page split into overlapping chunks (512–1024 tokens)
Helps retrieval for small and specific questions

3️⃣ Create embeddings
Each chunk converted into a vector using OpenAI embeddings
Vectors capture meaning instead of keywords

4️⃣ Store in FAISS index
All vectors stored in a FAISS vector database
Enables fast semantic similarity search

5️⃣ Retrieve relevant chunks
When a user asks a question:
The question → converted into an embedding
FAISS returns top-K relevant chunks
Page numbers + source file metadata attached

6️⃣ LLM generates the answer
Retrieved chunks passed into the LLM
Model reads medical context
Produces grounded answer
Includes citations

7️⃣ Streamlit UI
The interface displays:
The final answer
The supporting sources + page numbers
Button to view the full original page

🩺 Example Queries (From SRB Surgery)
Try questions like:
“Define acute inflammation.”
“Explain the steps of coagulation.”
“What are the symptoms of compartment syndrome?”
“Page 74” (retrieve specific chunks)
