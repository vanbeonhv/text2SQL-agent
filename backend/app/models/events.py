"""SSE event models for streaming responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StageEvent(BaseModel):
    """Progress stage update event."""
    stage: str = Field(..., description="Current processing stage")
    message: str = Field(..., description="User-friendly status message")
    icon: Optional[str] = Field(None, description="Icon emoji for display")


class ConversationIdEvent(BaseModel):
    """Conversation ID event (sent first)."""
    conversation_id: str = Field(..., description="Conversation UUID")


class IntentEvent(BaseModel):
    """Intent analysis result event."""
    intent: str = Field(..., description="Detected intent type")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional intent details")


class SchemaEvent(BaseModel):
    """Database schema event."""
    tables: List[Dict[str, Any]] = Field(..., description="Database tables")
    relationships: Optional[List[Dict[str, Any]]] = Field(None, description="Table relationships")


class SimilarExamplesEvent(BaseModel):
    """Similar queries event."""
    count: int = Field(..., description="Number of similar examples found")
    examples: List[Dict[str, Any]] = Field(..., description="Similar question-SQL pairs")


class SQLEvent(BaseModel):
    """Generated SQL event."""
    sql: str = Field(..., description="Generated SQL query")
    explanation: Optional[str] = Field(None, description="SQL explanation")


class ValidationEvent(BaseModel):
    """SQL validation event."""
    valid: bool = Field(..., description="Whether SQL passed validation")
    errors: Optional[List[str]] = Field(None, description="Validation errors if any")


class ResultEvent(BaseModel):
    """Query execution result event."""
    rows: List[Dict[str, Any]] = Field(..., description="Query result rows")
    count: int = Field(..., description="Number of rows")
    columns: Optional[List[str]] = Field(None, description="Column names")


class ErrorEvent(BaseModel):
    """Error event."""
    error: str = Field(..., description="Error message")
    retry_count: Optional[int] = Field(None, description="Current retry attempt")


class FormattedResponseEvent(BaseModel):
    """Formatted response event (markdown with optional insights)."""
    markdown: str = Field(..., description="Formatted markdown response")
    format_method: str = Field(..., description="Method used: 'python', 'hybrid', or 'llm'")
    has_llm_summary: bool = Field(..., description="Whether LLM-generated insights were included")


class ConversationHistoryEvent(BaseModel):
    """Loaded conversation history event."""
    count: int = Field(..., description="Number of messages in conversation history")
    messages: List[Dict[str, Any]] = Field(..., description="Conversation history messages")


class CompleteEvent(BaseModel):
    """Workflow completion event."""
    success: bool = Field(..., description="Whether workflow completed successfully")
    message: Optional[str] = Field(None, description="Completion message")
