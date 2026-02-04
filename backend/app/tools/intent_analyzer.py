"""Intent analysis tool using LLM Gateway."""
from typing import Dict, Any, List
from ..services.llm_gateway.factory import LLMProviderFactory
from ..config import settings
from ..constants import INTENT_TYPES


class IntentAnalyzer:
    """Analyzes user question intent using LLM."""
    
    def __init__(self):
        self.llm = LLMProviderFactory.get_provider(
            provider_type=settings.llm_provider,
            api_key=settings.gemini_api_key
        )
    
    async def analyze_intent(
        self,
        question: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Analyze user's question intent.
        
        Args:
            question: User's natural language question
            conversation_history: Previous conversation for context
            
        Returns:
            Intent analysis result with type and details
        """
        # Build prompt with conversation context
        prompt = self._build_prompt(question, conversation_history)
        
        # Define response schema
        schema = {
            "intent": "string (one of: data_retrieval, aggregation, filtering, sorting, joining, unknown)",
            "confidence": "float between 0 and 1",
            "details": "object with additional information"
        }
        
        # Call LLM for structured response
        result = await self.llm.generate_structured(
            prompt=prompt,
            response_schema=schema,
            temperature=0.3
        )
        
        return result
    
    def _build_prompt(
        self,
        question: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Build intent analysis prompt.
        
        Args:
            question: Current question
            conversation_history: Previous messages
            
        Returns:
            Formatted prompt
        """
        prompt = "You are an intent classifier for a text-to-SQL system.\n\n"
        
        # Add conversation context
        if conversation_history:
            context = self.llm.format_conversation_history(conversation_history)
            prompt += f"{context}\n"
        
        prompt += f"""Current question: "{question}"

Analyze the intent of this question and classify it into one of these categories:
- data_retrieval: Fetching specific data rows
- aggregation: Using COUNT, SUM, AVG, MIN, MAX
- filtering: Using WHERE conditions
- sorting: Using ORDER BY
- joining: Querying multiple related tables
- unknown: Cannot determine intent

Respond with JSON containing:
- intent: The classification (one of the above)
- confidence: Your confidence score (0.0 to 1.0)
- details: Additional information like detected columns, conditions, etc.

Example response:
{{
  "intent": "filtering",
  "confidence": 0.9,
  "details": {{
    "detected_conditions": ["price > 100"],
    "detected_columns": ["name", "price"]
  }}
}}
"""
        return prompt


# Global intent analyzer instance
intent_analyzer = IntentAnalyzer()
