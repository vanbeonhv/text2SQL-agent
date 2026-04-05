"""Response formatting tools - LLM-based full markdown generation."""

from typing import Dict, Any
from ..services.llm_gateway.factory import LLMProviderFactory


class LLMSummarizer:
    """LLM-based full response formatting using lightweight model."""

    def __init__(self):
        self.llm = LLMProviderFactory.get_provider(model_tier="lightweight")

    async def generate_insight(
        self, question: str, sql: str, result: Dict[str, Any], intent: str = "unknown"
    ) -> str:
        """Generate a full markdown response: answer + table + insights.

        Args:
            question: User's original question
            sql: Generated SQL query
            result: Query execution result
            intent: Detected intent

        Returns:
            Full markdown string (table + insight), or empty string on failure
        """
        count = result.get("count", 0)
        rows = result.get("rows", [])
        columns = result.get("columns", [])

        if count == 0:
            return "Không có kết quả nào cho truy vấn của bạn."

        sample_data = rows[:20]

        prompt = f"""You are a helpful data analyst. A user asked a question and the following SQL was run to answer it.

User question: "{question}"
Intent: {intent}

SQL executed:
```sql
{sql}
```

Results: {count} row(s) returned
Columns: {columns}
Data (up to 20 rows):
{sample_data}

Produce a complete markdown response with this structure:
1. One opening sentence that directly answers the user's question
2. A proper markdown data table (| header | syntax)
3. One or two brief insights or notable findings from the data

Language and naming (critical):
- Write ALL user-facing prose in Vietnamese: the opening sentence, insights, and any notes (e.g. row limits).
- Keep markdown table column headers exactly as listed in Columns (same spelling/casing as the database).
- Do not translate table or column names into Vietnamese.
- Keep SQL inside code fences unchanged. Preserve literal cell values as returned (including English text).
- Use standard international technical terms where natural (e.g. SQL) without translating them awkwardly.

Formatting rules:
- Return only markdown content; do not start with phrases like "Here is your answer" / "Đây là câu trả lời".
- Table: header row, separator row (|---|), then data rows.
- Keep insights concise and grounded in the data (cite specific values or names).
- If count > 20, state in Vietnamese that only 20 rows are shown out of {count} total."""

        try:
            markdown = await self.llm.generate(
                prompt=prompt, temperature=0.3, max_tokens=4000
            )
            return markdown.strip()
        except Exception as e:
            print(f"LLM formatting failed: {e}")
            return ""


class ResponseFormatter:
    """Formats query responses using LLM for full markdown output."""

    def __init__(self):
        self.llm_summarizer = LLMSummarizer()

    async def format_response(
        self,
        question: str,
        intent: str,
        sql: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format query response using LLM to generate full markdown.

        Args:
            question: User's question
            intent: Detected intent
            sql: Generated SQL
            result: Query execution result

        Returns:
            {
                "markdown": str,
                "has_summary": bool,
                "format_method": "llm"
            }
        """
        markdown = await self.llm_summarizer.generate_insight(
            question, sql, result, intent
        )

        if not markdown:
            markdown = f"Truy vấn trả về {result.get('count', 0)} dòng."

        return {
            "markdown": markdown,
            "has_summary": True,
            "format_method": "llm",
        }


# Global formatter instance
response_formatter = ResponseFormatter()
