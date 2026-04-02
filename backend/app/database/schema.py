"""Database schema management."""
import json
from typing import Dict, Any, List
from ..config import settings
from .connection import target_db


class SchemaManager:
    """Manages database schema loading and caching."""
    
    def __init__(self):
        self._schema_cache: Dict[str, Any] = None
    
    def load_schema(self) -> Dict[str, Any]:
        """Load database schema from file.
        
        Returns:
            Schema dictionary with tables and relationships
        """
        if self._schema_cache is not None:
            return self._schema_cache
        
        with open(settings.schema_path, 'r') as f:
            self._schema_cache = json.load(f)
        
        return self._schema_cache
    
    def format_schema_as_text(self, schema: Dict[str, Any]) -> str:
        """Format any schema dict as text for LLM prompts."""
        text = "Database Schema:\n\n"

        # Add tables
        for table in schema.get("tables", []):
            text += f"Table: {table['name']}\n"
            text += "Columns:\n"

            for col in table.get("columns", []):
                col_desc = f"  - {col['name']} ({col['type']})"
                if col.get("primary_key"):
                    col_desc += " [PRIMARY KEY]"
                if col.get("description"):
                    col_desc += f" -- {col['description']}"
                text += col_desc + "\n"

            text += "\n"

        # Add relationships
        if schema.get("relationships"):
            text += "Relationships:\n"
            for rel in schema["relationships"]:
                text += f"  - {rel['from']} -> {rel['to']} ({rel['type']})\n"
            text += "\n"

        # Add business context
        business_context = schema.get("business_context", {})
        if business_context:
            text += "Business Rules & Query Patterns:\n\n"
            labels = {
                "employment_status": "Employment Status",
                "temporal_query_patterns": "Temporal Query Patterns",
                "date_sentinel_values": "Date Sentinel Values",
                "cost_center_mappings": "Cost Center Mappings",
                "query_notes": "Query Notes",
            }
            for key, value in business_context.items():
                label = labels.get(key, key.replace("_", " ").title())
                text += f"{label}:\n{value}\n\n"

        return text

    def get_schema_as_text(self) -> str:
        """Get default schema file as formatted text for LLM prompts."""
        schema = self.load_schema()
        return self.format_schema_as_text(schema)
    
    def clear_cache(self):
        """Clear schema cache (useful for tests)."""
        self._schema_cache = None


# Global schema manager instance
schema_manager = SchemaManager()


async def introspect_target_database_schema() -> Dict[str, Any]:
    """Build schema JSON dynamically from current target SQLite database."""
    table_rows = await target_db.fetchall(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )

    tables: List[Dict[str, Any]] = []
    for row in table_rows:
        table_name = row["name"]
        columns_info = await target_db.fetchall(f"PRAGMA table_info({table_name})")
        columns: List[Dict[str, Any]] = []
        for col in columns_info:
            columns.append(
                {
                    "name": col["name"],
                    "type": col["type"] or "TEXT",
                    "primary_key": bool(col["pk"]),
                }
            )
        tables.append({"name": table_name, "columns": columns})

    return {
        "tables": tables,
        "relationships": [],
        "business_context": {},
    }
