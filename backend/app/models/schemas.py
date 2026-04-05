"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str = Field(..., description="User's natural language question")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (creates new if not provided)")
    schema: Optional[Dict[str, Any]] = Field(
        None,
        description="Optional runtime schema JSON to use and persist for this conversation",
    )


class QueryResult(BaseModel):
    """SQL query execution result."""
    success: Optional[bool] = Field(None, description="Whether execution succeeded")
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="Query result rows")
    count: int = Field(0, description="Number of rows returned")
    columns: Optional[List[str]] = Field(None, description="Column names")
    error: Optional[str] = Field(None, description="Execution error message")


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    id: int = Field(..., description="Message ID")
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    sql: Optional[str] = Field(None, description="Generated SQL query")
    results: Optional[QueryResult] = Field(None, description="Structured query result")
    error: Optional[str] = Field(None, description="Message-level error")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")
    feedback: Optional[str] = Field(None, description="User feedback: 'like', 'dislike', or null")
    timestamp: datetime = Field(..., description="Message timestamp")


class ConversationResponse(BaseModel):
    """Response model for conversation history endpoint."""
    id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")
    schema: Optional[Dict[str, Any]] = Field(None, description="Conversation-level custom schema JSON")
    messages: List[ConversationMessage] = Field(..., description="List of messages in conversation")


class ConversationListItem(BaseModel):
    """Conversation item for list view."""
    id: str = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title (from first message)")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")


class ConversationsListResponse(BaseModel):
    """Response model for conversations list endpoint."""
    conversations: List[ConversationListItem] = Field(..., description="List of conversations")
    count: int = Field(..., description="Total number of conversations returned")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class IntentResult(BaseModel):
    """Intent analysis result."""
    intent: str = Field(..., description="Detected intent type")
    confidence: Optional[float] = Field(None, description="Confidence score")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional intent details")


class SQLValidationResult(BaseModel):
    """SQL validation result."""
    valid: bool = Field(..., description="Whether SQL is valid")
    errors: Optional[List[str]] = Field(None, description="List of validation errors")


class SimilarExample(BaseModel):
    """A similar question-SQL pair for few-shot learning."""
    question: str = Field(..., description="Similar question")
    sql: str = Field(..., description="Corresponding SQL query")
    similarity_score: Optional[float] = Field(None, description="Similarity score")


class FeedbackRequest(BaseModel):
    """Request model for submitting like/dislike feedback."""
    conversation_id: str = Field(..., description="Conversation ID")
    sql: str = Field(..., description="Generated SQL query to identify the message")
    status: Literal["like", "dislike", "none"] = Field(..., description="Feedback status ('none' clears feedback)")


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""
    status: str = Field(..., description="Saved feedback status")
    message: str = Field(..., description="Confirmation message")


class ConversationSchemaRequest(BaseModel):
    """Set/update conversation schema request."""
    schema: Dict[str, Any] = Field(..., description="Schema JSON with tables/columns/relationships")


class ConversationSchemaResponse(BaseModel):
    """Conversation schema response payload."""
    conversation_id: str = Field(..., description="Conversation ID")
    schema: Optional[Dict[str, Any]] = Field(None, description="Schema JSON if configured")
    source: str = Field(..., description="Schema source: conversation|default|introspected")


class SchemaTableDefinitionRequest(BaseModel):
    """Request body for creating/updating a table-level schema definition."""
    table_name: str = Field(..., description="Logical table name")
    columns: List[Dict[str, Any]] = Field(..., description="Column definitions")
    relationships: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="Relationship definitions (from/to/etc.)",
    )
    description: Optional[str] = Field(None, description="Human-friendly table description")
    tags: List[str] = Field(default_factory=list, description="Optional tags for matching")
    is_active: Optional[bool] = Field(True, description="Whether this table definition is active")


class SchemaTableDefinitionResponse(BaseModel):
    """Response payload for a table-level schema definition."""
    table_name: str
    columns: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    description: Optional[str]
    tags: List[str]
    is_active: bool


class SchemaBusinessContextRequest(BaseModel):
    """Update registry-level business_context (mirrors root `business_context` in schema.json)."""
    business_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="String-keyed business rules and query patterns for the LLM",
    )


class SchemaBusinessContextResponse(BaseModel):
    """Registry business_context for admin and transparency."""
    business_context: Dict[str, Any] = Field(default_factory=dict)
    explicit: bool = Field(
        False,
        description="True if a DB row exists; False means file fallback applies when using registry schema",
    )


class SchemaDetectRequest(BaseModel):
    """Request for detecting relevant tables for a question."""
    question: str = Field(..., description="User question / intent")
    active_only: bool = Field(True, description="Only consider active schema table definitions")
    allow_llm_fallback: bool = Field(
        True,
        description="Allow calling LLM if heuristic confidence is low (requires provider API key).",
    )


class SchemaDetectResponse(BaseModel):
    """Response payload for schema detection."""
    target_tables: List[str]
    confidence: float
    strategy: Literal["heuristic", "llm_fallback"]
    matched_reasons: List[str]
