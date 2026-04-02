"""LangGraph agent state models."""
from typing import TypedDict, Optional, List, Dict, Any


class AgentState(TypedDict, total=False):
    """State that flows through the LangGraph workflow.
    
    Attributes:
        question: Original user question
        intent: Analyzed intent (e.g., 'data_retrieval', 'aggregation')
        schema: Retrieved database schema
        conversation_history: Full conversation messages for context
        similar_examples: Few-shot examples from other conversations
        generated_sql: LLM-generated SQL query
        validation_result: SQL validation status and errors
        execution_result: Query results or error details
        retry_count: Number of error correction attempts
        error_message: Latest error message (if any)
        conversation_id: UUID for conversation tracking
        current_stage: Current processing stage (for streaming UI updates)
        is_complete: Workflow completion flag
        formatted_response: Final markdown response (data or fast path)
        format_method: How response was formatted (python/hybrid/llm)
        has_llm_summary: Whether LLM insights were included
    """
    question: str
    intent: str
    intent_details: Dict[str, Any]
    target_tables: List[str]
    formatted_response: str
    format_method: str
    has_llm_summary: bool
    schema: Dict[str, Any]
    schema_override: Dict[str, Any]
    schema_source: str
    conversation_history: List[Dict[str, str]]
    similar_examples: List[Dict[str, Any]]
    generated_sql: str
    validation_result: Dict[str, Any]
    execution_result: Dict[str, Any]
    retry_count: int
    error_message: str
    conversation_id: str
    current_stage: str
    is_complete: bool
    # Response formatting fields
    formatted_response: str
    format_method: str
    has_llm_summary: bool
