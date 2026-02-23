"""Build fast responses for non-data intents (greeting, goodbye, unknown, schema_request)."""
from typing import Dict, Any, Optional

# Generic suggestion questions (constant list for any schema)
SUGGESTION_QUESTIONS = [
    "How many records are in each table?",
    "List all items with a filter (e.g. price > 100)",
    "Show me the top 10 by some column",
    "What is the average or sum of a numeric column?",
    "Join two tables and show related data",
]


def _format_schema_as_markdown(schema: Dict[str, Any]) -> str:
    """Format schema dict as human-readable markdown."""
    lines = ["### Tables and columns\n"]
    for table in schema.get("tables", []):
        name = table.get("name", "?")
        cols = table.get("columns", [])
        col_list = ", ".join(
            f"**{c.get('name', '?')}** ({c.get('type', '')})"
            for c in cols
        )
        lines.append(f"- **{name}**: {col_list}\n")
    if schema.get("relationships"):
        lines.append("\n### Relationships\n")
        for rel in schema["relationships"]:
            lines.append(f"- {rel.get('from', '')} → {rel.get('to', '')} ({rel.get('type', '')})\n")
    return "".join(lines)


def _suggestions_block() -> str:
    """Return markdown block with suggestion questions."""
    bullet = "\n".join(f"- {q}" for q in SUGGESTION_QUESTIONS)
    return f"\n### You can ask things like\n{bullet}"


def build_fast_response(
    intent: str,
    schema: Optional[Dict[str, Any]] = None,
) -> str:
    """Build markdown response for non-data intents.

    Args:
        intent: One of greeting, goodbye, schema_request, unknown
        schema: Optional schema dict (from schema_manager.load_schema())

    Returns:
        Markdown string for the assistant response
    """
    schema = schema or {}
    suggestions = _suggestions_block()

    if intent == "greeting":
        return (
            "Hello! I can help you query the database in plain language.\n\n"
            + suggestions
        )

    if intent == "goodbye":
        return "Goodbye! Feel free to come back if you have more questions."

    if intent == "unknown":
        intro = (
            "I'm not sure how to answer that. I'm built to answer questions about the data. "
            "Here are the tables you can ask about:\n\n"
        )
        body = _format_schema_as_markdown(schema) if schema.get("tables") else "*(No schema loaded.)*\n"
        return intro + body + suggestions

    if intent == "schema_request":
        intro = "Here are the tables and columns in the database:\n\n"
        body = _format_schema_as_markdown(schema) if schema.get("tables") else "*(No schema loaded.)*\n"
        return intro + body + suggestions

    # Fallback for any other non-data intent
    return (
        "I'm here to help with data questions. "
        "You can ask about the tables and columns in the database.\n\n"
        + (_format_schema_as_markdown(schema) if schema.get("tables") else "")
        + suggestions
    )
