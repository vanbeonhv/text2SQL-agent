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
        """Generate brief insight/summary about query results.
        
        Uses lightweight model for speed (300-800ms vs 1500-3000ms).
        
        Args:
            question: User's original question
            sql: Generated SQL query
            result: Query execution result
            intent: Detected intent
            
        Returns:
            1-2 sentence insight
        """
        count = result.get("count", 0)
        rows = result.get("rows", [])
        
        # Don't generate insights for empty results
        if count == 0:
            return ""
        
        # Sample first 5 rows for LLM context (reduce token usage)
        sample_data = rows[:5]
        
        # Build concise prompt
        prompt = f"""Analyze this SQL query result and provide a brief insight.

Question: "{question}"
Intent: {intent}
SQL: {sql}
Result: {count} rows returned

Sample data (first 5 rows):
{sample_data}

Provide a 1-2 sentence insight that:
- Highlights the key finding or pattern
- Mentions notable numbers or trends
- Is conversational and helpful
- Does NOT just restate the row count

Examples:
- "The data shows most products are priced between $50-$200, with Electronics being the most common category."
- "Sales peaked in Q4 with $1.2M revenue, representing a 35% increase from Q3."
- "The average order value is $156, with the top 3 customers accounting for 40% of total orders."

Your insight:"""
        
        try:
            # Fast generation with lightweight model
            insight = await self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=150  # Keep it brief!
            )
            
            return f"\n\n### 💡 Insights\n\n{insight.strip()}"
        
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
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Format query response with optimal strategy.
        
        Routes to:
        - Python-only for simple queries (fastest)
        - Hybrid (Python + LLM) for aggregations
        - Full LLM for complex cases
        
        Args:
            question: User's question
            intent: Detected intent
            sql: Generated SQL
            result: Query execution result
            conversation_history: Previous messages
            
        Returns:
            {
                "markdown": str,
                "has_summary": bool,
                "format_method": "python" | "hybrid" | "llm"
            }
        """
        count = result.get("count", 0)
        
        # FAST PATH: Simple queries - Python only
        if intent in ["data_retrieval", "filtering", "sorting"]:
            markdown = self.python_formatter.format_table(result, intent, question)
            
            # Add simple summary
            if count > 0:
                markdown += self.python_formatter.format_simple_summary(result, intent)
            
            return {
                "markdown": markdown,
                "has_summary": False,
                "format_method": "python",
                "latency_ms": "~5"  # Approximate
            }
        
        # HYBRID PATH: Aggregations and joins
        elif intent in ["aggregation", "joining"]:
            # Check if insights are enabled and result size is reasonable
            should_generate_insights = (
                settings.enable_llm_insights 
                and 0 < count < settings.format_with_llm_threshold
            )
            
            if should_generate_insights:
                # Parallel: Format table + Generate insights
                table_md, insight = await asyncio.gather(
                    self._format_table_async(result, intent, question),
                    self.llm_summarizer.generate_insight(question, sql, result, intent)
                )
                
                markdown = table_md + insight
                
                return {
                    "markdown": markdown,
                    "has_summary": True,
                    "format_method": "hybrid",
                    "latency_ms": "~350"
                }
            else:
                # Python only if insights disabled or too many rows
                markdown = self.python_formatter.format_table(result, intent, question)
                markdown += self.python_formatter.format_simple_summary(result, intent)
                
                return {
                    "markdown": markdown,
                    "has_summary": False,
                    "format_method": "python",
                    "latency_ms": "~5"
                }
        
        # FALLBACK: Complex/Unknown queries - Full LLM
        else:
            markdown = await self.llm_summarizer.format_full_response(
                question=question,
                sql=sql,
                result=result,
                conversation_history=conversation_history
            )
            
            return {
                "markdown": markdown,
                "has_summary": True,
                "format_method": "llm",
                "latency_ms": "~2000"
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
