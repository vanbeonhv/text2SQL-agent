"""Response formatting tools - Python-based and LLM-based."""
import asyncio
from typing import Dict, Any, List, Optional
from ..services.llm_gateway.factory import LLMProviderFactory
from ..config import settings


class PythonFormatter:
    """Fast Python-based markdown formatting (no LLM calls)."""
    
    # Predefined opening templates based on intent
    OPENING_TEMPLATES = {
        "data_retrieval": "Here are the results:",
        "filtering": "I found **{count}** records matching your criteria:",
        "sorting": "Here are the results sorted as requested:",
        "aggregation": "Here's the summary:",
        "joining": "Here are the combined results:",
        "unknown": "Query results:",
    }
    
    def format_table(
        self,
        result: Dict[str, Any],
        intent: str = "unknown",
        question: Optional[str] = None
    ) -> str:
        """Format SQL results to markdown table.
        
        Args:
            result: Execution result with 'rows', 'count', 'columns'
            intent: Query intent for appropriate opening
            question: Optional user question for context
            
        Returns:
            Markdown string with opening + table
        """
        rows = result.get("rows", [])
        count = result.get("count", 0)
        columns = result.get("columns", [])
        
        # Build opening line
        opening = self.OPENING_TEMPLATES.get(intent, "Query results:")
        opening = opening.format(count=count)
        
        markdown = f"{opening}\n\n"
        
        # Handle empty results
        if count == 0:
            return markdown + "No results found."
        
        # Handle no columns
        if not columns:
            return markdown + f"Query returned {count} rows but no column information available."
        
        # Build markdown table
        # Header
        markdown += "| " + " | ".join(columns) + " |\n"
        markdown += "|" + "|".join(["---"] * len(columns)) + "|\n"
        
        # Rows (limit display)
        max_display = min(count, settings.max_display_rows)
        for row in rows[:max_display]:
            values = [self._format_cell_value(row.get(col, "")) for col in columns]
            markdown += "| " + " | ".join(values) + " |\n"
        
        # Add note if truncated
        if count > max_display:
            markdown += f"\n*Showing {max_display} of {count} results*\n"
        
        return markdown
    
    def _format_cell_value(self, value: Any) -> str:
        """Format a single cell value for markdown.
        
        Args:
            value: Cell value (any type)
            
        Returns:
            String representation suitable for markdown table
        """
        if value is None:
            return "NULL"
        
        # Format numbers
        if isinstance(value, float):
            # Format with 2 decimal places for readability
            return f"{value:.2f}"
        
        # Convert to string and escape pipes
        str_value = str(value)
        str_value = str_value.replace("|", "\\|")
        
        # Truncate very long values
        if len(str_value) > 100:
            str_value = str_value[:97] + "..."
        
        return str_value
    
    def format_simple_summary(
        self,
        result: Dict[str, Any],
        intent: str = "unknown"
    ) -> str:
        """Create a simple summary without LLM.
        
        Args:
            result: Execution result
            intent: Query intent
            
        Returns:
            Simple summary string
        """
        count = result.get("count", 0)
        
        if intent == "aggregation":
            return f"\n**Summary:** Query returned {count} aggregated {'result' if count == 1 else 'results'}."
        elif intent == "filtering":
            return f"\n**Summary:** {count} {'record matches' if count == 1 else 'records match'} your filters."
        else:
            return f"\n**Summary:** {count} {'row' if count == 1 else 'rows'} returned."


class LLMSummarizer:
    """LLM-based summarization using lightweight model."""
    
    def __init__(self):
        # Use lightweight model for fast summaries
        self.llm = LLMProviderFactory.get_provider(model_tier="lightweight")
    
    async def generate_insight(
        self,
        question: str,
        sql: str,
        result: Dict[str, Any],
        intent: str = "unknown"
    ) -> str:
        """Generate insight/summary about query results using SQL + data context.

        Uses lightweight model for speed (300-800ms vs 1500-3000ms).

        Args:
            question: User's original question
            sql: Generated SQL query
            result: Query execution result
            intent: Detected intent

        Returns:
            2-3 sentence insight that directly answers the user's question
        """
        count = result.get("count", 0)
        rows = result.get("rows", [])
        columns = result.get("columns", [])

        # Don't generate insights for empty results
        if count == 0:
            return ""

        # Sample up to 10 rows for LLM context
        sample_data = rows[:10]

        # Build prompt with full SQL + data context
        prompt = f"""You are a helpful data analyst. A user asked a question and an SQL query was run to answer it.

User question: "{question}"
Intent: {intent}

SQL query that was executed:
```sql
{sql}
```

Query results: {count} row(s) returned
Columns: {columns}

Sample data (up to 10 rows):
{sample_data}

Write a 2-3 sentence summary that:
- Directly answers the user's question based on the data
- Highlights key findings, patterns, or notable values
- Mentions specific numbers or names from the data when relevant
- Is conversational and easy to understand
- Does NOT just restate the row count or describe what the query does

Your summary:"""

        try:
            insight = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=200
            )

            return f"\n\n### 💡 Summary\n\n{insight.strip()}"

        except Exception as e:
            # Fail gracefully - return empty string if LLM fails
            print(f"LLM insight generation failed: {e}")
            return ""
    
    async def format_full_response(
        self,
        question: str,
        sql: str,
        result: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Full LLM-based formatting (fallback for complex cases).
        
        Args:
            question: User's question
            sql: Generated SQL
            result: Query results
            conversation_history: Previous messages for context
            
        Returns:
            Fully formatted markdown response
        """
        count = result.get("count", 0)
        rows = result.get("rows", [])
        columns = result.get("columns", [])
        
        # Build context
        context = ""
        if conversation_history:
            context = "Previous conversation:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                role = "User" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
            context += "\n"
        
        prompt = f"""{context}Format this SQL query result into a clear, helpful markdown response.

Question: "{question}"
SQL: {sql}
Results: {count} rows, columns: {columns}

Sample data:
{rows[:10]}

Create a response that includes:
1. A brief conversational opening
2. A markdown table (if appropriate)
3. Key insights or findings
4. Answer the user's question directly

Format your response in markdown. Be concise but informative."""
        
        try:
            # Use thinking model for complex formatting
            formatted = await self.llm.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=500
            )
            
            return formatted.strip()
        
        except Exception as e:
            # Fallback to Python formatting
            print(f"LLM full formatting failed: {e}")
            formatter = PythonFormatter()
            return formatter.format_table(result, intent="unknown", question=question)


class ResponseFormatter:
    """Routes formatting to Python or LLM based on intent and settings."""
    
    def __init__(self):
        self.python_formatter = PythonFormatter()
        self.llm_summarizer = LLMSummarizer()
    
    async def format_response(
        self,
        question: str,
        intent: str,
        sql: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format query response: Python table + LLM summary for all intents.

        Args:
            question: User's question
            intent: Detected intent
            sql: Generated SQL
            result: Query execution result
            conversation_history: Previous messages (unused, kept for API compatibility)

        Returns:
            {
                "markdown": str,
                "has_summary": bool,
                "format_method": "hybrid" | "python"
            }
        """
        # Always run Python table formatting + LLM insight in parallel
        table_md, insight = await asyncio.gather(
            self._format_table_async(result, intent, question),
            self.llm_summarizer.generate_insight(question, sql, result, intent)
        )

        markdown = table_md + insight

        return {
            "markdown": markdown,
            "has_summary": bool(insight),
            "format_method": "hybrid" if insight else "python",
        }
    
    async def _format_table_async(
        self,
        result: Dict[str, Any],
        intent: str,
        question: str
    ) -> str:
        """Async wrapper for synchronous table formatting.
        
        Allows use in asyncio.gather for parallel execution.
        """
        return self.python_formatter.format_table(result, intent, question)


# Global formatter instance
response_formatter = ResponseFormatter()
