"""Registry business_context API and retrieve_schema merge behavior."""
import asyncio
import json

from fastapi.testclient import TestClient

from app.agents import nodes as nodes_mod
from app.config import settings
from app.database.connection import history_db
from app.database.history import history_manager
from app.database.schema import schema_manager
from app.main import app


async def _clear_registry_business_context():
    await history_db.execute("DELETE FROM schema_registry_business_context WHERE id = 1")


def test_api_get_put_business_context():
    asyncio.run(history_manager.reset_database())
    asyncio.run(_clear_registry_business_context())

    client = TestClient(app)

    schema_manager.clear_cache()
    expected_file_bc = schema_manager.load_schema().get("business_context") or {}

    get_r = client.get("/api/schema/business-context")
    assert get_r.status_code == 200
    body = get_r.json()
    assert body["business_context"] == expected_file_bc
    assert body["explicit"] is False

    put_r = client.put("/api/schema/business-context", json={"business_context": {"k": "v"}})
    assert put_r.status_code == 200
    put_body = put_r.json()
    assert put_body["explicit"] is True
    assert put_body["business_context"] == {"k": "v"}

    get2 = client.get("/api/schema/business-context")
    assert get2.json()["business_context"] == {"k": "v"}
    assert get2.json()["explicit"] is True


def test_retrieve_schema_registry_uses_db_business_context():
    asyncio.run(history_manager.reset_database())
    asyncio.run(_clear_registry_business_context())
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}],
            relationships=[],
            description="Products",
            tags=[],
            is_active=True,
        )
    )
    asyncio.run(history_manager.set_registry_business_context({"custom_note": "use_this"}))
    schema_manager.clear_cache()

    state = {
        "question": "list products",
        "intent": "data_retrieval",
        "target_tables": ["products"],
    }
    asyncio.run(nodes_mod.retrieve_schema_node(state))

    assert state["schema"]["dict"]["business_context"] == {"custom_note": "use_this"}
    assert "use_this" in state["schema"]["text"]


def test_retrieve_schema_registry_falls_back_to_file_business_context(monkeypatch, tmp_path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(
        json.dumps(
            {
                "tables": [{"name": "dummy", "columns": []}],
                "relationships": [],
                "business_context": {"file_only": "from_file_marker"},
            }
        )
    )
    monkeypatch.setattr(settings, "schema_path", str(schema_file))
    schema_manager.clear_cache()

    asyncio.run(history_manager.reset_database())
    asyncio.run(_clear_registry_business_context())
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}],
            relationships=[],
            description="Products",
            tags=[],
            is_active=True,
        )
    )

    state = {
        "question": "list products",
        "intent": "data_retrieval",
        "target_tables": ["products"],
    }
    asyncio.run(nodes_mod.retrieve_schema_node(state))

    assert state["schema"]["dict"]["business_context"].get("file_only") == "from_file_marker"
    assert "from_file_marker" in state["schema"]["text"]


def test_retrieve_schema_explicit_empty_skips_file_business_context(monkeypatch, tmp_path):
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(
        json.dumps(
            {
                "tables": [],
                "relationships": [],
                "business_context": {"file_only": "should_not_appear"},
            }
        )
    )
    monkeypatch.setattr(settings, "schema_path", str(schema_file))
    schema_manager.clear_cache()

    asyncio.run(history_manager.reset_database())
    asyncio.run(history_manager.set_registry_business_context({}))
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="t1",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}],
            relationships=[],
            description="",
            tags=[],
            is_active=True,
        )
    )

    state = {
        "question": "q",
        "intent": "data_retrieval",
        "target_tables": ["t1"],
    }
    asyncio.run(nodes_mod.retrieve_schema_node(state))

    assert state["schema"]["dict"]["business_context"] == {}
    assert "should_not_appear" not in state["schema"]["text"]
    assert "Business Rules" not in state["schema"]["text"]
