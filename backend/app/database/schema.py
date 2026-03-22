"""Database schema management."""
import json
from typing import Dict, Any
from ..config import settings


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
    
    def get_schema_as_text(self) -> str:
        """Get schema as formatted text for LLM prompts.

        Returns:
            Human-readable schema description including business context
        """
        schema = self.load_schema()

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
    
    def clear_cache(self):
        """Clear schema cache (useful for tests)."""
        self._schema_cache = None


# Global schema manager instance
schema_manager = SchemaManager()
