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
            return "No results found for your query."

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

Generate a complete markdown response that:
1. Opens with 1 sentence directly answering the user's question
2. Shows the data as a proper markdown table using | column | syntax
3. Ends with 1-2 key insights or notable findings from the data

Rules:
- Return only markdown content, no preamble like "Here is your answer"
- The table must use standard markdown: header row, separator row (|---|), data rows
- Keep insights concise and data-driven (mention specific values/names)
- If count > 20, note that only 20 rows are shown out of {count} total"""

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
            markdown = f"Query returned {result.get('count', 0)} row(s)."

        return {
            "markdown": markdown,
            "has_summary": True,
            "format_method": "llm",
        }


# Global formatter instance
response_formatter = ResponseFormatter()
