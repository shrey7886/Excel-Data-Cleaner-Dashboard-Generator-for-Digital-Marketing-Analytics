# DashFlow RAG Pipeline Documentation

## Overview
DashFlow uses a modern Retrieval-Augmented Generation (RAG) pipeline to power its context-aware AI chatbot. This combines vector search (FAISS), Hugging Face models, and a state-of-the-art LLM for accurate, context-rich answers from your real marketing data.

---

## Architecture

```mermaid
flowchart TD
    A[User Query] -->|POST /api/rag-chatbot/| B[Backend API]
    B --> C[Retrieve Context (FAISS + Metadata)]
    C --> D[Prompt Engineering]
    D --> E[LLM (Hugging Face)]
    E --> F[Answer + Context]
    F -->|Response| A
    F --> G[Store Feedback]
    G -->|Admin/Analytics| H[Feedback Dashboard]
```

- **Embeddings:** Uses Sentence Transformers (configurable) to embed marketing data.
- **Vector Store:** FAISS index for fast similarity search.
- **LLM:** Hugging Face pipeline (configurable, e.g., Mixtral, Llama) for answer generation.
- **Hybrid Search:** Supports vector + metadata filtering (platform, date).
- **Feedback Loop:** User feedback is stored for continuous improvement.

---

## Example Queries & Answers
- **Q:** How did my Google Ads perform last month?
  **A:** Your Google Ads campaign had 12,000 impressions, 1,200 clicks, and a spend of $1,500 last month.
- **Q:** Which platform had the best ROI?
  **A:** LinkedIn Ads had the highest ROI of 2.1 last month.
- **Q:** Show me Mailchimp campaign results for March 2024.
  **A:** Your Mailchimp campaign "Spring Launch" had an open rate of 35% and a click rate of 7% in March 2024.

---

## How It Works
1. **Data Ingestion:** Data from Google Ads, LinkedIn Ads, Mailchimp, Zoho, and Demandbase is loaded into the database.
2. **Indexing:**
   - Run `python manage.py update_rag_index` to (asynchronously) build/update the FAISS index from all marketing data.
   - This triggers a Celery background task (`update_rag_index_task`).
3. **Querying:**
   - The chatbot UI sends POST requests to `/api/rag-chatbot/` with a user query.
   - The backend retrieves relevant context chunks, constructs a prompt, and generates an answer using the LLM.
   - User feedback is collected via `/api/chatbot-feedback/`.

---

## API Usage
### `/api/rag-chatbot/` (POST)
- **Request:** `{ "query": "How did my Google Ads perform last month?" }`
- **Response:** `{ "answer": "...", "context": [ ... ] }`
- **Rate Limiting:** Default 5 requests/minute per user/IP (configurable via `RAG_RATE_LIMIT`). Returns HTTP 429 if exceeded.

### `/api/chatbot-feedback/` (POST)
- **Request:** `{ "feedback_id": 123, "rating": 1 }` (1=up, -1=down, 0=neutral)
- **Response:** `{ "status": "success" }`

---

## Settings & Configuration
All RAG settings are in `sales_dashboard/sales_dashboard/settings.py`:
- `RAG_EMBEDDING_MODEL`, `RAG_LLM_MODEL`, `RAG_FAISS_INDEX_PATH`, `RAG_TEXTS_PATH`, `RAG_META_PATH`, `RAG_CHUNK_SIZE`, `RAG_TOP_K`, `RAG_RATE_LIMIT`
- Can be overridden via environment variables.

---

## Updating the Index
- **Manual:** `python manage.py update_rag_index` (runs async via Celery)
- **Automatic:** You can schedule the Celery task as needed.

---

## Admin & Analytics
- **Feedback Dashboard:** Admins can view all chatbot feedback in the Django admin or a custom dashboard.
- **Export Feedback:** Feedback can be exported as CSV for analysis or model improvement.
- **Usage Stats:** Track number of queries, average rating, and most common questions.

---

## Troubleshooting
- **No Answer/Context:** Ensure the FAISS index is built and up to date. Run `python manage.py update_rag_index` if needed.
- **Rate Limit Errors:** Wait 1 minute or increase `RAG_RATE_LIMIT` in settings.
- **LLM Errors:** Check Hugging Face model availability and GPU/CPU resources.
- **Celery Not Running:** Ensure `celery -A sales_dashboard worker` is running for async tasks.

---

## Testing
- See `tests/test_rag_pipeline.py` and `tests/test_chatbot_api.py` for examples.
- To run all tests: `pytest` (ensure test dependencies are installed).

---

## Contributing
- Follow best practices for Django, Celery, and Hugging Face.
- Add/expand tests for new features.
- Document any changes in this file. 