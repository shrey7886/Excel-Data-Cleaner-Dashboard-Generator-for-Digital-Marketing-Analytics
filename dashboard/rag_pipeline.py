import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# 1. Load embedding model and LLM pipeline (do this once at startup)
EMBEDDING_MODEL_NAME = 'all-MiniLM-L6-v2'
LLM_MODEL_NAME = 'mistralai/Mixtral-8x7B-Instruct-v0.1'

embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
llm = pipeline("text-generation", model=LLM_MODEL_NAME, device_map="auto")

# 2. Paths for FAISS index and text data
FAISS_INDEX_PATH = "faiss_index.bin"
TEXTS_PATH = "faiss_texts.npy"

def build_faiss_index(texts):
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    faiss.write_index(index, FAISS_INDEX_PATH)
    np.save(TEXTS_PATH, np.array(texts))
    return index

def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH):
        return None, None
    index = faiss.read_index(FAISS_INDEX_PATH)
    texts = np.load(TEXTS_PATH, allow_pickle=True).tolist()
    return index, texts

def update_rag_index_from_db():
    # Example: Pull all campaign/report summaries from your DB
    from dashboard.models import GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData
    all_texts = []
    for model in [GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData]:
        for entry in model.objects.all():
            summary = str(entry.data)  # You can customize this to be more readable
            all_texts.append(summary)
    build_faiss_index(all_texts)

def rag_answer(query, k=5):
    index, texts = load_faiss_index()
    if index is None or texts is None:
        return "Knowledge base is not built yet. Please update the RAG index."
    query_embedding = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_embedding, k)
    retrieved_chunks = [texts[i] for i in I[0]]
    context = "\n".join(retrieved_chunks)
    prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    response = llm(prompt, max_new_tokens=200)[0]['generated_text']
    return response 