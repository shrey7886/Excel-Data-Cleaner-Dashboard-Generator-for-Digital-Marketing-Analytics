import pytest
from dashboard import rag_pipeline
import numpy as np
import os

@pytest.mark.django_db
def test_embedding_generation():
    text = "Test marketing data chunk."
    emb = rag_pipeline.embedder.encode([text], convert_to_numpy=True)
    assert isinstance(emb, np.ndarray)
    assert emb.shape[0] == 1

@pytest.mark.django_db
def test_faiss_index_build_and_search(tmp_path, monkeypatch):
    texts = ["Chunk 1", "Chunk 2", "Chunk 3"]
    monkeypatch.setattr(rag_pipeline, 'FAISS_INDEX_PATH', str(tmp_path / 'faiss_index.bin'))
    monkeypatch.setattr(rag_pipeline, 'TEXTS_PATH', str(tmp_path / 'faiss_texts.npy'))
    monkeypatch.setattr(rag_pipeline, 'META_PATH', str(tmp_path / 'faiss_meta.npy'))
    rag_pipeline.build_faiss_index(texts)
    # Simulate meta
    meta = np.array([{'platform': 'google_ads', 'date': '2024-01-01', 'campaign': 'A'} for _ in texts], dtype=object)
    np.save(rag_pipeline.META_PATH, meta)
    # Search
    results = rag_pipeline.retrieve_context("Chunk 1", top_k=2)
    assert len(results) > 0

@pytest.mark.django_db
def test_prompt_generation():
    query = "What is my best performing campaign?"
    context = ["Campaign A: ROI 2.0", "Campaign B: ROI 1.5"]
    prompt = f"""
You are a helpful analytics assistant. Use the provided context to answer the user's question. If the answer is not in the context, say you don't know.\n\nContext:\n{chr(10).join(context)}\n\nQuestion: {query}\nAnswer as a helpful analytics expert:\n"""
    assert "Context:" in prompt
    assert query in prompt

@pytest.mark.django_db
def test_missing_index(monkeypatch, tmp_path):
    monkeypatch.setattr(rag_pipeline, 'FAISS_INDEX_PATH', str(tmp_path / 'missing_index.bin'))
    monkeypatch.setattr(rag_pipeline, 'TEXTS_PATH', str(tmp_path / 'missing_texts.npy'))
    monkeypatch.setattr(rag_pipeline, 'META_PATH', str(tmp_path / 'missing_meta.npy'))
    results = rag_pipeline.retrieve_context("Test query")
    assert results == []

@pytest.mark.django_db
def test_malformed_query(monkeypatch, tmp_path):
    # Should not raise error on weird input
    texts = ["Chunk 1"]
    monkeypatch.setattr(rag_pipeline, 'FAISS_INDEX_PATH', str(tmp_path / 'faiss_index.bin'))
    monkeypatch.setattr(rag_pipeline, 'TEXTS_PATH', str(tmp_path / 'faiss_texts.npy'))
    monkeypatch.setattr(rag_pipeline, 'META_PATH', str(tmp_path / 'faiss_meta.npy'))
    rag_pipeline.build_faiss_index(texts)
    meta = np.array([{'platform': 'google_ads', 'date': '2024-01-01', 'campaign': 'A'}], dtype=object)
    np.save(rag_pipeline.META_PATH, meta)
    results = rag_pipeline.retrieve_context("!@#$%^&*()")
    assert isinstance(results, list)

@pytest.mark.django_db
def test_llm_timeout(monkeypatch):
    def fake_llm(*args, **kwargs):
        raise TimeoutError("LLM timed out")
    monkeypatch.setattr(rag_pipeline, 'llm', fake_llm)
    with pytest.raises(TimeoutError):
        rag_pipeline.rag_answer("Test query")

@pytest.mark.django_db
def test_rag_pipeline_end_to_end(monkeypatch, tmp_path):
    # Full flow: build index, retrieve, answer (mocked LLM)
    texts = ["Chunk 1", "Chunk 2"]
    monkeypatch.setattr(rag_pipeline, 'FAISS_INDEX_PATH', str(tmp_path / 'faiss_index.bin'))
    monkeypatch.setattr(rag_pipeline, 'TEXTS_PATH', str(tmp_path / 'faiss_texts.npy'))
    monkeypatch.setattr(rag_pipeline, 'META_PATH', str(tmp_path / 'faiss_meta.npy'))
    rag_pipeline.build_faiss_index(texts)
    meta = np.array([{'platform': 'google_ads', 'date': '2024-01-01', 'campaign': 'A'} for _ in texts], dtype=object)
    np.save(rag_pipeline.META_PATH, meta)
    monkeypatch.setattr(rag_pipeline, 'llm', lambda prompt, **kwargs: [{'generated_text': 'Mocked answer.'}])
    answer = rag_pipeline.rag_answer("Chunk 1")
    assert "Mocked answer" in answer 