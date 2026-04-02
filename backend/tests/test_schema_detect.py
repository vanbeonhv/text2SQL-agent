import asyncio

from fastapi.testclient import TestClient

from app.database.history import history_manager
from app.main import app


def test_schema_detect_heuristic_matches_table_and_columns():
    asyncio.run(history_manager.reset_database())

    client = TestClient(app)

    client.post(
        "/api/schema/tables",
        json={
            "table_name": "products",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "price", "type": "INTEGER"},
                {"name": "name", "type": "TEXT"},
            ],
            "relationships": [],
            "description": "Products",
            "tags": ["catalog"],
            "is_active": True,
        },
    )

    client.post(
        "/api/schema/tables",
        json={
            "table_name": "customers",
            "columns": [
                {"name": "id", "type": "INTEGER", "primary_key": True},
                {"name": "email", "type": "TEXT"},
            ],
            "relationships": [],
            "description": "Customers",
            "tags": ["crm"],
            "is_active": True,
        },
    )

    resp = client.post(
        "/api/schema/detect",
        json={"question": "Show products where price > 100"},
    )
    assert resp.status_code == 200

    data = resp.json()
    assert "products" in data["target_tables"]
    assert data["strategy"] == "heuristic"
    assert data["confidence"] >= 0.5
    assert len(data.get("matched_reasons", [])) >= 1

