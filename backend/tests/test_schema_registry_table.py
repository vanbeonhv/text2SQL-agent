import asyncio

from app.database.connection import history_db
from app.database.history import history_manager


def test_schema_registry_table_created():
    """history_manager.init_database should create schema registry table."""
    asyncio.run(history_manager.reset_database())

    tables = {"schema_table_definitions", "schema_registry_business_context"}
    rows = asyncio.run(
        history_db.fetchall(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name IN ('schema_table_definitions', 'schema_registry_business_context')
            """
        )
    )

    found = {r["name"] for r in rows}
    assert tables.issubset(found)

