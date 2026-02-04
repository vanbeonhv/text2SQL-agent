"""SQL generation tool using LLM Gateway with few-shot learning."""
from typing import Dict, Any, List
from ..services.llm_gateway.factory import LLMProviderFactory
from ..config import settings


class SQLWriter:
    """Generates SQL queries using LLM with conversation context and few-shot examples."""
    
    def __init__(self):
        self.llm = LLMProviderFactory.get_provider(
            model_tier="thinking"  # Use accurate model for SQL generation
        )
    
    async def generate_sql(
        self,
        question: str,
        schema: str,
        conversation_history: List[Dict[str, str]] = None,
        similar_examples: List[Dict[str, Any]] = None,
        intent: str = None
    ) -> Dict[str, str]:
        """Generate SQL query from natural language question.
        
        Args:
            question: User's question
            schema: Database schema description
            conversation_history: Previous conversation messages
            similar_examples: Similar question-SQL pairs for few-shot learning
            intent: Detected intent (optional)
            
        Returns:
            Dictionary with 'sql' and optional 'explanation'
        """
        prompt = self._build_prompt(
            question=question,
            schema=schema,
            conversation_history=conversation_history,
            similar_examples=similar_examples,
            intent=intent
        )
        
        # Define response schema
        response_schema = {
            "sql": "string - the SQL query",
            "explanation": "string - brief explanation of what the query does"
        }
        
        result = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=response_schema,
            temperature=0.2  # Lower temperature for more consistent SQL
        )
        
        return result
    
    def _build_prompt(
        self,
        question: str,
        schema: str,
        conversation_history: List[Dict[str, str]] = None,
        similar_examples: List[Dict[str, Any]] = None,
        intent: str = None
    ) -> str:
        """Build SQL generation prompt with all context.
        
        Args:
            question: Current question
            schema: Database schema
            conversation_history: Previous messages
            similar_examples: Few-shot examples
            intent: Detected intent
            
        Returns:
            Formatted prompt
        """
        prompt = "You are an expert SQL query generator.\n\n"
        
        # Add schema
        prompt += f"{schema}\n\n"
        
        # Add conversation context
        if conversation_history:
            context = self.llm.format_conversation_history(conversation_history)
            prompt += f"{context}\n"
        
        # Add few-shot examples
        if similar_examples:
            prompt += "Here are some similar examples:\n\n"
            for i, example in enumerate(similar_examples[:3], 1):  # Limit to top 3
                prompt += f"Example {i}:\n"
                prompt += f"Question: {example['question']}\n"
                prompt += f"SQL: {example['sql']}\n\n"
        
        # Add intent context
        if intent:
            prompt += f"Detected intent: {intent}\n\n"
        
        # Add current question and instructions
        prompt += f"""Current question: "{question}"

Generate a SQL query for this question following these rules:
1. ONLY use SELECT statements (no UPDATE, DELETE, INSERT, etc.)
2. Only query tables and columns that exist in the schema
3. Use proper SQL syntax (SQLite flavor)
4. Include appropriate WHERE, JOIN, GROUP BY, ORDER BY clauses as needed
5. Use LIMIT to restrict results if appropriate
6. Consider the conversation context when generating the query

Respond with JSON containing:
- sql: The complete SQL query
- explanation: A brief explanation of what the query does

Example response:
{{
  "sql": "SELECT name, price FROM products WHERE price > 100 ORDER BY price DESC LIMIT 10",
  "explanation": "Retrieves the top 10 products with price greater than 100, ordered by price from highest to lowest"
}}
"""
        return prompt


# Global SQL writer instance
sql_writer = SQLWriter()
