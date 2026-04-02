import asyncio

from app.agents import nodes as nodes_mod
from app.database.history import history_manager


def test_retrieve_schema_node_filters_by_target_tables():
    asyncio.run(history_manager.reset_database())

    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}, {"name": "price", "type": "INTEGER"}],
            relationships=[],
            description="Products",
            tags=["catalog"],
            is_active=True,
        )
    )
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="customers",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}, {"name": "email", "type": "TEXT"}],
            relationships=[],
            description="Customers",
            tags=["crm"],
            is_active=True,
        )
    )

    state = {
        "question": "Show products where price > 100",
        "intent": "filtering",
        "target_tables": ["products"],
    }
    asyncio.run(nodes_mod.retrieve_schema_node(state))

    tables = state["schema"]["dict"]["tables"]
    assert [t["name"] for t in tables] == ["products"]


def test_retrieve_schema_node_uses_all_active_when_no_target_tables():
    asyncio.run(history_manager.reset_database())

    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}, {"name": "price", "type": "INTEGER"}],
            relationships=[],
            description="Products",
            tags=["catalog"],
            is_active=True,
        )
    )
    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="customers",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}, {"name": "email", "type": "TEXT"}],
            relationships=[],
            description="Customers",
            tags=["crm"],
            is_active=True,
        )
    )

    state = {
        "question": "Show all active schemas",
        "intent": "schema_request",
        # intentionally omit target_tables
    }
    asyncio.run(nodes_mod.retrieve_schema_node(state))

    tables = state["schema"]["dict"]["tables"]
    assert set(t["name"] for t in tables) == {"products", "customers"}


def test_analyze_intent_node_sets_target_tables_for_data_intents(monkeypatch):
    asyncio.run(history_manager.reset_database())

    asyncio.run(
        history_manager.upsert_table_definition(
            table_name="products",
            columns=[{"name": "id", "type": "INTEGER", "primary_key": True}, {"name": "price", "type": "INTEGER"}],
            relationships=[],
            description="Products",
            tags=["catalog"],
            is_active=True,
        )
    )

    async def fake_analyze_intent(question, conversation_history=None):
        return {"intent": "filtering", "details": {"fake": True}}

    monkeypatch.setattr(nodes_mod.intent_analyzer, "analyze_intent", fake_analyze_intent)

    state = {
        "question": "Show products where price > 100",
        "intent": "unknown",  # will be overwritten by fake analyzer result
        "conversation_history": [],
    }

    asyncio.run(nodes_mod.analyze_intent_node(state))

    assert state["intent"] == "filtering"
    assert state["target_tables"] == ["products"]
    assert "table_detection" in state["intent_details"]

