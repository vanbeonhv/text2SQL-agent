"""Pydantic models for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    question: str = Field(..., description="User's natural language question")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID (creates new if not provided)")


class ConversationMessage(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(..., description="Message timestamp")


class ConversationResponse(BaseModel):
    """Response model for conversation history endpoint."""
    id: str = Field(..., description="Conversation ID")
    created_at: datetime = Field(..., description="Conversation creation time")
    updated_at: datetime = Field(..., description="Last update time")
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


class QueryResult(BaseModel):
    """SQL query execution result."""
    rows: List[Dict[str, Any]] = Field(..., description="Query result rows")
    count: int = Field(..., description="Number of rows returned")
    columns: Optional[List[str]] = Field(None, description="Column names")


class SimilarExample(BaseModel):
    """A similar question-SQL pair for few-shot learning."""
    question: str = Field(..., description="Similar question")
    sql: str = Field(..., description="Corresponding SQL query")
    similarity_score: Optional[float] = Field(None, description="Similarity score")
