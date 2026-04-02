import asyncio

from fastapi.testclient import TestClient

from app.database.history import history_manager
from app.main import app


def test_schema_table_crud_flow():
    """CRUD for schema table definitions (table-level registry)."""
    asyncio.run(history_manager.reset_database())

    client = TestClient(app)

    base_payload = {
        "table_name": "products",
        "columns": [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "name", "type": "TEXT"},
        ],
        "relationships": [],
        "description": "Products table",
        "tags": ["catalog"],
    }

    # Create
    create_resp = client.post("/api/schema/tables", json=base_payload)
    assert create_resp.status_code in (200, 201)
    created = create_resp.json()
    assert created["table_name"] == "products"
    assert created["is_active"] is True
    assert len(created["columns"]) == 2

    # List
    list_resp = client.get("/api/schema/tables")
    assert list_resp.status_code == 200
    items = list_resp.json()
    # We keep response shape flexible; accept either list or {items: []}
    if isinstance(items, list):
        assert any(x["table_name"] == "products" for x in items)
    else:
        assert any(x["table_name"] == "products" for x in items["items"])

    # Get
    get_resp = client.get("/api/schema/tables/products")
    assert get_resp.status_code == 200
    got = get_resp.json()
    assert got["table_name"] == "products"
    assert got["description"] == "Products table"

    # Update
    update_payload = {**base_payload, "description": "Updated products"}
    put_resp = client.put("/api/schema/tables/products", json=update_payload)
    assert put_resp.status_code in (200, 201)
    updated = put_resp.json()
    assert updated["description"] == "Updated products"
    assert updated["table_name"] == "products"

    # Delete (soft)
    del_resp = client.delete("/api/schema/tables/products")
    assert del_resp.status_code in (200, 204)

    get_after_delete = client.get("/api/schema/tables/products")
    assert get_after_delete.status_code == 200
    after = get_after_delete.json()
    assert after["is_active"] is False

