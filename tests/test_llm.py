import pytest
from app.llm import OpenRouterLLM

@pytest.fixture
def llm():
    return OpenRouterLLM(key="fakekey", base_url="https://fake.url", model="fake-model")

def test_fetch_candidates(monkeypatch, llm):
    dummy_docs = [
        {"id": "doc1", "company_id": "123", "section_type": "innovation_description", "text": "AI innovation"},
        {"id": "doc2", "company_id": "123", "section_type": "market_analysis", "text": "Market growth"}
    ]
    monkeypatch.setattr(llm, "_OpenRouterLLM__fetch_candidates__", lambda company_id: dummy_docs)
    docs = llm._OpenRouterLLM__fetch_candidates__("123")
    assert len(docs) == 2
    assert docs[0]["id"] == "doc1"

def test_retrieve_top_k(llm):
    candidates = [
        {"id": "1", "text": "AI innovation"},
        {"id": "2", "text": "Market analysis and innovation"},
        {"id": "3", "text": "Unrelated content"}
    ]
    result = llm._OpenRouterLLM__retrieve_top_k__("innovation", candidates, k=2)
    assert len(result) == 2
    assert all("innovation" in doc["text"] for doc in result)

def test_format_contexts_for_llm(llm):
    contexts = [
        {"section_type": "innovation_description", "text": "Doc1"},
        {"section_type": "market_analysis", "text": "Doc2"}
    ]
    prompt_context = llm._OpenRouterLLM__format_contexts_for_llm__(contexts)
    assert "[INNOVATION_DESCRIPTION]" in prompt_context
    assert "[MARKET_ANALYSIS]" in prompt_context

def test_system_prompt_for_section(llm):
    result = llm._OpenRouterLLM__system_prompt_for_section__("ip_strategy")
    assert "IP_STRATEGY" in result
    assert "context snippets" in result

def test_generate_section(monkeypatch, llm):
    dummy_docs = [
        {"id": "doc1", "section_type": "innovation_description", "text": "Test doc"}
    ]
    monkeypatch.setattr(llm, "_OpenRouterLLM__fetch_candidates__", lambda cid: dummy_docs)
    monkeypatch.setattr(llm, "_OpenRouterLLM__retrieve_top_k__", lambda text, docs, k=3: docs)
    monkeypatch.setattr(llm, "_OpenRouterLLM__format_contexts_for_llm__", lambda docs: "[INNOVATION_DESCRIPTION]\nTest doc")
    monkeypatch.setattr(llm, "_OpenRouterLLM__system_prompt_for_section__", lambda st: "System prompt")
    monkeypatch.setattr(llm, "query_openrouter", lambda up, max_tokens, sp: "Generated Text")

    result = llm.generate_section("input", "123", "innovation_description", k=1)
    assert result["generated_text"] == "Generated Text"
    assert result["sources"] == ["doc1"]

def test_query_openrouter(llm, monkeypatch):
    class FakeClient:
        class Chat:
            class Completions:
                @staticmethod
                def create(*args, **kwargs):
                    return type("MockResp", (), {"choices": [type("C", (), {"message": type("M", (), {"content": "LLM Output"})})]})
            completions = Completions()
        chat = Chat()

    monkeypatch.setattr(llm, "client", FakeClient())
    output = llm.query_openrouter("prompt", 30, "system")
    assert output == "LLM Output"
