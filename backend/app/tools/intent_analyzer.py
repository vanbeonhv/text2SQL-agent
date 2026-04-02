"""Intent analysis tool using LLM Gateway."""
from typing import Dict, Any, List, Optional, Tuple
from ..services.llm_gateway.factory import LLMProviderFactory
from ..config import settings
from ..constants import INTENT_TYPES
from ..database.history import history_manager


class IntentAnalyzer:
    """Analyzes user question intent using LLM."""
    
    def __init__(self):
        self.llm = LLMProviderFactory.get_provider(
            model_tier="thinking"  # Use accurate model for intent analysis
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
            "intent": "string (one of: data_retrieval, aggregation, filtering, sorting, joining, greeting, goodbye, schema_request, unknown)",
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

    async def detect_target_tables(
        self,
        question: str,
        active_only: bool = True,
        allow_llm_fallback: bool = True,
        confidence_threshold: float = 0.6,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Detect which registered tables are relevant to the user's question.

        Hybrid approach:
        - Heuristic matching using registered `table_name`, `columns`, and `tags`
        - LLM fallback only when heuristic confidence is low.
        """
        table_defs = await history_manager.list_table_definitions(active_only=active_only)
        question_l = (question or "").lower()

        scored: List[Tuple[float, str, List[str]]] = []
        for td in table_defs:
            table_name = td.get("table_name")
            if not table_name:
                continue

            table_l = str(table_name).lower()
            score = 0.0
            reasons: List[str] = []

            if table_l and table_l in question_l:
                score += 3.0
                reasons.append(f"table_name_match:{table_name}")

            for col in td.get("columns", []) or []:
                col_name = (col.get("name") if isinstance(col, dict) else None) or None
                if not col_name:
                    continue
                col_l = str(col_name).lower()
                if col_l in question_l:
                    score += 1.0
                    reasons.append(f"column_match:{col_name}")

            for tag in td.get("tags", []) or []:
                tag_l = str(tag).lower()
                if tag_l and tag_l in question_l:
                    score += 0.5
                    reasons.append(f"tag_match:{tag}")

            if score > 0:
                scored.append((score, table_name, reasons))

        if not scored:
            # No heuristic matches at all; avoid network calls unless explicitly allowed.
            heuristic = {
                "target_tables": [],
                "confidence": 0.0,
                "strategy": "heuristic",
                "matched_reasons": [],
            }
            if not allow_llm_fallback:
                return heuristic
            # LLM fallback: still do a best-effort only if we have an API key.
            if not settings.gemini_api_key:
                return heuristic
        else:
            scored.sort(key=lambda x: x[0], reverse=True)
            best_score = scored[0][0]
            confidence = min(1.0, best_score / 4.0)  # table_name(3) + column(1) => 1.0
            target_tables = [t for _, t, _ in scored[:top_k]]
            matched_reasons = scored[0][2]

            if confidence >= confidence_threshold or not allow_llm_fallback or not settings.gemini_api_key:
                return {
                    "target_tables": target_tables,
                    "confidence": confidence,
                    "strategy": "heuristic",
                    "matched_reasons": matched_reasons,
                }

        # LLM fallback (ambiguous/low-confidence heuristic)
        # Keep prompt compact: table names + their columns.
        active_table_summaries = []
        for td in table_defs:
            tn = td.get("table_name")
            cols = [c.get("name") for c in (td.get("columns", []) or []) if isinstance(c, dict) and c.get("name")]
            active_table_summaries.append({"table_name": tn, "columns": cols[:25]})

        response_schema = {
            "target_tables": "array of strings (table names)",
            "confidence": "float between 0 and 1",
            "matched_reasons": "array of strings (why these tables are relevant)",
        }

        prompt = f"""You are a schema-aware router for a text-to-SQL system.

You must choose the most relevant table(s) for the user's question from the registered tables.

Registered tables:
{active_table_summaries}

User question: "{question}"

Return:
1) target_tables: list of best table names (may be 1..N)
2) confidence: 0..1
3) matched_reasons: brief reasons referencing table names/columns
"""

        try:
            result = await self.llm.generate_structured(
                prompt=prompt,
                response_schema=response_schema,
                temperature=0.2,
            )
        except Exception:
            # Safe fallback: if LLM fails, return the heuristic result we computed above.
            if scored:
                scored.sort(key=lambda x: x[0], reverse=True)
                return {
                    "target_tables": [t for _, t, _ in scored[:top_k]],
                    "confidence": min(0.5, scored[0][0] / 4.0),
                    "strategy": "heuristic",
                    "matched_reasons": scored[0][2],
                }
            return {
                "target_tables": [],
                "confidence": 0.0,
                "strategy": "heuristic",
                "matched_reasons": [],
            }

        return {
            "target_tables": result.get("target_tables", []) or [],
            "confidence": result.get("confidence", 0.0) or 0.0,
            "strategy": "llm_fallback",
            "matched_reasons": result.get("matched_reasons", []) or [],
        }
    
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
- greeting: Saying hello, hi, or starting a conversation
- goodbye: Saying goodbye, bye, or ending the conversation
- schema_request: Asking what tables/columns exist, show schema, list tables, what can I ask
- unknown: Cannot determine intent or not related to data

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
