"""Build fast responses for non-data intents (greeting, goodbye, unknown, schema_request)."""
from typing import Dict, Any, Optional

# Generic suggestion questions (constant list for any schema)
SUGGESTION_QUESTIONS = [
    "Mỗi bảng có bao nhiêu bản ghi?",
    "Liệt kê các mục theo điều kiện (ví dụ `price > 100`)",
    "Top 10 theo một cột bất kỳ",
    "Giá trị trung bình hoặc tổng của một cột số",
    "JOIN hai bảng và hiển thị dữ liệu liên quan",
]


def _format_schema_as_markdown(schema: Dict[str, Any]) -> str:
    """Format schema dict as human-readable markdown."""
    lines = ["### Bảng và cột\n"]
    for table in schema.get("tables", []):
        name = table.get("name", "?")
        cols = table.get("columns", [])
        col_list = ", ".join(
            f"**{c.get('name', '?')}** ({c.get('type', '')})"
            for c in cols
        )
        lines.append(f"- **{name}**: {col_list}\n")
    if schema.get("relationships"):
        lines.append("\n### Quan hệ\n")
        for rel in schema["relationships"]:
            lines.append(f"- {rel.get('from', '')} → {rel.get('to', '')} ({rel.get('type', '')})\n")
    return "".join(lines)


def _suggestions_block() -> str:
    """Return markdown block with suggestion questions."""
    bullet = "\n".join(f"- {q}" for q in SUGGESTION_QUESTIONS)
    return f"\n### Bạn có thể hỏi như sau\n{bullet}"


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
            "Xin chào! Tôi có thể giúp bạn truy vấn cơ sở dữ liệu bằng ngôn ngữ tự nhiên.\n\n"
            + suggestions
        )

    if intent == "goodbye":
        return "Tạm biệt! Hẹn gặp lại khi bạn còn câu hỏi."

    if intent == "unknown":
        intro = (
            "Tôi chưa chắc cách trả lời câu đó. Tôi được thiết kế để trả lời các câu hỏi về dữ liệu. "
            "Dưới đây là các bảng bạn có thể hỏi:\n\n"
        )
        body = _format_schema_as_markdown(schema) if schema.get("tables") else "*(Chưa tải schema.)*\n"
        return intro + body + suggestions

    if intent == "schema_request":
        intro = "Đây là các bảng và cột trong cơ sở dữ liệu:\n\n"
        body = _format_schema_as_markdown(schema) if schema.get("tables") else "*(Chưa tải schema.)*\n"
        return intro + body + suggestions

    # Fallback for any other non-data intent
    return (
        "Tôi có thể hỗ trợ các câu hỏi về dữ liệu. "
        "Bạn có thể hỏi về các bảng và cột trong cơ sở dữ liệu.\n\n"
        + (_format_schema_as_markdown(schema) if schema.get("tables") else "")
        + suggestions
    )
