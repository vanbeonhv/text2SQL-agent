import asyncio

from app.database.connection import history_db
from app.database.history import history_manager


def test_schema_registry_table_created():
    """history_manager.init_database should create schema registry table."""
    asyncio.run(history_manager.reset_database())

    rows = asyncio.run(
        history_db.fetchall(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'schema_table_definitions'
            """
        )
    )

    assert len(rows) == 1

