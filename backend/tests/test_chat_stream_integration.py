import asyncio

from fastapi.testclient import TestClient

from app.agents import nodes as nodes_mod
from app.database.history import history_manager
from app.main import app


def test_chat_stream_reaches_complete_event(monkeypatch):
    """Minimal chat-stream integration test with LLM/SQL mocked."""
    asyncio.run(history_manager.reset_database())

    # Seed at least one registered table so schema retrieval works without default file coupling.
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "price", "type": "INTEGER"},
            ],
            relationships=[],
            description="Products",
            tags=["catalog"],
            is_active=True,
        )
    )

    async def fake_analyze_intent(question, conversation_history=None):
        return {"intent": "filtering", "details": {}, "confidence": 0.9}

    async def fake_generate_sql(question, schema, conversation_history=None, similar_examples=None, intent=None):
        return {"sql": "SELECT id FROM products WHERE price > 100", "explanation": "filter products by price"}

    async def fake_execute_query(sql):
        return {
            "success": True,
            "rows": [{"id": 1}],
            "count": 1,
            "columns": ["id"],
        }

    async def fake_format_response(question, intent, sql, result):
        return {
            "markdown": "ok",
            "has_summary": False,
            "format_method": "python",
        }

    monkeypatch.setattr(nodes_mod.intent_analyzer, "analyze_intent", fake_analyze_intent)
    monkeypatch.setattr(nodes_mod.sql_writer, "generate_sql", fake_generate_sql)
    monkeypatch.setattr(nodes_mod.sql_executor, "execute_query", fake_execute_query)
    monkeypatch.setattr(nodes_mod.response_formatter, "format_response", fake_format_response)

    client = TestClient(app)
    resp = client.post(
        "/api/chat/stream",
        json={"question": "Show products where price > 100"},
    )
    assert resp.status_code == 200

    body = resp.text
    assert "event: sql" in body
    assert "SELECT id FROM products WHERE price > 100" in body
    assert "event: complete" in body

