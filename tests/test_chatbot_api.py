import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from dashboard.models import ChatbotFeedback

@pytest.mark.django_db
def test_rag_chatbot_success(client, monkeypatch):
    # Mock RAG pipeline
    monkeypatch.setattr('dashboard.views.retrieve_context', lambda q: ["context1", "context2"])
    monkeypatch.setattr('dashboard.views.rag_answer', lambda q: "Test answer.")
    user = User.objects.create_user(username='testuser', password='testpass')
    client.force_login(user)
    resp = client.post(reverse('rag_chatbot'), data={"query": "Test?"}, content_type='application/json')
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data
    assert "context" in data

@pytest.mark.django_db
def test_rag_chatbot_rate_limit(client, monkeypatch, settings):
    monkeypatch.setattr('dashboard.views.retrieve_context', lambda q: ["context1"])
    monkeypatch.setattr('dashboard.views.rag_answer', lambda q: "Test answer.")
    settings.RAG_RATE_LIMIT = 2
    user = User.objects.create_user(username='ratelimit', password='testpass')
    client.force_login(user)
    url = reverse('rag_chatbot')
    for _ in range(2):
        resp = client.post(url, data={"query": "Test?"}, content_type='application/json')
        assert resp.status_code == 200
    # Third request should be rate limited
    resp = client.post(url, data={"query": "Test?"}, content_type='application/json')
    assert resp.status_code == 429
    assert "rate limit" in resp.json()["error"].lower()

@pytest.mark.django_db
def test_chatbot_feedback(client):
    user = User.objects.create_user(username='feedback', password='testpass')
    feedback = ChatbotFeedback.objects.create(user=user, query="Q", answer="A", context="C")
    resp = client.post(reverse('chatbot_feedback'), data={"feedback_id": feedback.id, "rating": 1}, content_type='application/json')
    assert resp.status_code == 200
    feedback.refresh_from_db()
    assert feedback.rating == 1 