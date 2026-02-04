"""Error correction tool using LLM."""
from typing import Dict, Any, List
from ..services.llm_gateway.factory import LLMProviderFactory
from ..config import settings


class ErrorCorrector:
    """Corrects SQL errors using LLM."""
    
    def __init__(self):
        self.llm = LLMProviderFactory.get_provider(
            provider_type=settings.llm_provider,
            api_key=settings.gemini_api_key
        )
    
    async def correct_sql_error(
        self,
        question: str,
        failed_sql: str,
        error_message: str,
        schema: str,
        conversation_history: List[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> Dict[str, str]:
        """Correct a failed SQL query.
        
        Args:
            question: Original user question
            failed_sql: SQL query that failed
            error_message: Error message from execution
            schema: Database schema
            conversation_history: Conversation context
            retry_count: Current retry attempt number
            
        Returns:
            Dictionary with corrected 'sql' and 'explanation'
        """
        prompt = self._build_prompt(
            question=question,
            failed_sql=failed_sql,
            error_message=error_message,
            schema=schema,
            conversation_history=conversation_history,
            retry_count=retry_count
        )
        
        response_schema = {
            "sql": "string - the corrected SQL query",
            "explanation": "string - what was wrong and how it was fixed"
        }
        
        result = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            temperature=0.3
        )
        
        return result
    
    def _build_prompt(
        self,
        question: str,
        failed_sql: str,
        error_message: str,
        schema: str,
        conversation_history: List[Dict[str, str]] = None,
        retry_count: int = 0
    ) -> str:
        """Build error correction prompt.
        
        Args:
            question: Original question
            failed_sql: Failed SQL
            error_message: Error message
            schema: Database schema
            conversation_history: Conversation context
            retry_count: Retry attempt
            
        Returns:
            Formatted prompt
        """
        prompt = "You are an expert SQL debugger.\n\n"
        
        # Add schema
        prompt += f"{schema}\n\n"
        
        # Add conversation context
        if conversation_history:
            context = self.llm.format_conversation_history(conversation_history)
            prompt += f"{context}\n"
        
        # Add error details
        prompt += f"""Original question: "{question}"

Failed SQL query:
```sql
{failed_sql}
```

Error message:
{error_message}

Retry attempt: {retry_count + 1}/{settings.max_retry_attempts}

Analyze the error and generate a corrected SQL query following these rules:
1. ONLY use SELECT statements
2. Only query tables and columns that exist in the schema
3. Fix the specific error mentioned in the error message
4. Maintain the intent of the original query
5. Use proper SQL syntax (SQLite flavor)

Common error fixes:
- Column not found: Check column names in schema
- Table not found: Check table names in schema
- Syntax errors: Fix SQL syntax
- Ambiguous columns: Use table prefixes (e.g., table.column)
- Missing GROUP BY: Add GROUP BY when using aggregate functions

Respond with JSON containing:
- sql: The corrected SQL query
- explanation: What was wrong and how you fixed it

Example response:
{{
  "sql": "SELECT name, price FROM products WHERE price > 100",
  "explanation": "Fixed column name from 'product_name' to 'name' which exists in the products table"
}}
"""
        return prompt


# Global error corrector instance
error_corrector = ErrorCorrector()
