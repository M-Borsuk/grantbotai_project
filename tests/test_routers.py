from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_generate_section_endpoint(monkeypatch):
    from app.routers.generate import openrouter_llm

    monkeypatch.setattr(
        openrouter_llm,
        "generate_section",
        lambda input_text, company_id, section_type, k=3: {
            "generated_text": "Test output",
            "sources": ["id1", "id2"],
        },
    )
    payload = {
        "company_id": "123",
        "section_type": "innovation_description",
        "text": "describe the innovation",
    }
    resp = client.post("/generate-section", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["generated_text"] == "Test output"
    assert "sources" in data


def test_history_endpoint(monkeypatch):
    from app.db import mongo

    monkeypatch.setattr(
        mongo,
        "history",
        type(
            "C",
            (),
            {
                "find": lambda self, query: [
                    {
                        "request_id": "r1",
                        "section_type": "innovation_description",
                        "created_at": "now",
                        "sources": ["id1", "id2"],
                    }
                ],
            },
        )(),
    )
    client = TestClient(app)
    resp = client.get("/history/123")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company_id"] == "123"
    assert len(data["items"]) == 1
    assert data["items"][0]["section_type"] == "innovation_description"
