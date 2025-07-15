# RAG pipeline temporarily disabled for low-memory deployment on Render Free tier.
# import os
# import faiss
# import numpy as np
# import pandas as pd
# from sentence_transformers import SentenceTransformer
# from transformers import pipeline
# from django.conf import settings
# from dashboard.models import GoogleAdsData, LinkedInAdsData, MailchimpData, ZohoData, DemandbaseData
# import re
#
# EMBEDDING_MODEL_NAME = getattr(settings, 'RAG_EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
# LLM_MODEL_NAME = getattr(settings, 'RAG_LLM_MODEL', 'mistralai/Mixtral-8x7B-Instruct-v0.1')
# FAISS_INDEX_PATH = getattr(settings, 'RAG_FAISS_INDEX_PATH', os.path.join(settings.BASE_DIR, 'faiss_index.bin'))
# TEXTS_PATH = getattr(settings, 'RAG_TEXTS_PATH', os.path.join(settings.BASE_DIR, 'faiss_texts.npy'))
# META_PATH = getattr(settings, 'RAG_META_PATH', os.path.join(settings.BASE_DIR, 'faiss_meta.npy'))
# CHUNK_SIZE = getattr(settings, 'RAG_CHUNK_SIZE', 512)
# TOP_K = getattr(settings, 'RAG_TOP_K', 5)
#
# embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
# llm = pipeline("text-generation", model=LLM_MODEL_NAME, device_map="auto")
#
# # --- Chunking and Metadata ---
# def extract_chunks_and_meta():
#     all_chunks = []
#     all_meta = []
#     for model, platform in [
#         (GoogleAdsData, 'google_ads'),
#         (LinkedInAdsData, 'linkedin_ads'),
#         (MailchimpData, 'mailchimp'),
#         (ZohoData, 'zoho'),
#         (DemandbaseData, 'demandbase'),
#     ]:
#         for entry in model.objects.all():
#             data = entry.data if isinstance(entry.data, list) else [entry.data]
#             for record in data:
#                 chunk = str(record)
#                 meta = {
#                     'platform': platform,
#                     'date': record.get('date') or record.get('Date'),
#                     'campaign': record.get('campaign_name') or record.get('name'),
#                 }
#                 all_chunks.append(chunk)
#                 all_meta.append(meta)
#     return all_chunks, all_meta
#
# # --- Build/Update Index ---
# def build_faiss_index(texts):
#     embeddings = embedder.encode(texts, convert_to_numpy=True)
#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)
#     faiss.write_index(index, FAISS_INDEX_PATH)
#     np.save(TEXTS_PATH, np.array(texts))
#
# def update_rag_index_from_db():
#     chunks, meta = extract_chunks_and_meta()
#     if not chunks:
#         print("[RAG] No data found to index.")
#         return
#     build_faiss_index(chunks)
#     np.save(META_PATH, np.array(meta, dtype=object))
#     print(f"[RAG] Indexed {len(chunks)} chunks.")
#
# # --- Hybrid Search ---
# def parse_query_filters(query):
#     # Simple regex for platform and date
#     platforms = ['google_ads', 'linkedin_ads', 'mailchimp', 'zoho', 'demandbase']
#     platform = next((p for p in platforms if p in query.lower()), None)
#     date_match = re.search(r'(\d{4}-\d{2}-\d{2})', query)
#     date = date_match.group(1) if date_match else None
#     return platform, date
#
# def retrieve_context(query, top_k=None):
#     if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(TEXTS_PATH) or not os.path.exists(META_PATH):
#         return []
#     index = faiss.read_index(FAISS_INDEX_PATH)
#     texts = np.load(TEXTS_PATH, allow_pickle=True)
#     meta = np.load(META_PATH, allow_pickle=True)
#     platform, date = parse_query_filters(query)
#     # Filter by platform/date if present
#     filtered_idxs = [i for i, m in enumerate(meta) if (not platform or m['platform'] == platform) and (not date or m['date'] == date)]
#     k = top_k if top_k is not None else TOP_K
#     if filtered_idxs:
#         filtered_texts = [texts[i] for i in filtered_idxs]
#         filtered_embs = embedder.encode(filtered_texts, convert_to_numpy=True)
#         query_emb = embedder.encode([query], convert_to_numpy=True)
#         D = np.linalg.norm(filtered_embs - query_emb, axis=1)
#         top_idxs = np.argsort(D)[:k]
#         return [filtered_texts[i] for i in top_idxs]
#     # Fallback: full vector search
#     query_emb = embedder.encode([query], convert_to_numpy=True)
#     D, I = index.search(query_emb, k)
#     return [texts[i] for i in I[0] if i < len(texts)]
#
# # --- Prompt Engineering ---
# def rag_answer(query, history=None):
#     context_chunks = retrieve_context(query)
#     context = '\n'.join(context_chunks)
#     history = history or []
#     history_str = ''
#     for turn in history[-5:]:
#         if turn['role'] == 'user':
#             history_str += f"User: {turn['content']}\n"
#         elif turn['role'] == 'bot':
#             history_str += f"Assistant: {turn['content']}\n"
#     prompt = f"""
# You are a helpful analytics assistant. Use the provided context and conversation history to answer the user's question. If the answer is not in the context, say you don't know.
#
# Conversation history:
# {history_str}
# Context:
# {context}
#
# Question: {query}
# Answer as a helpful analytics expert:
# """
#     response = llm(prompt, max_new_tokens=256, do_sample=True)[0]['generated_text']
#     return response.strip() 