"""FastAPI routes with SSE streaming."""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from ..models.schemas import (
    ChatRequest,
    ConversationResponse,
    ConversationsListResponse,
    ConversationListItem,
    HealthResponse
)
from ..models.events import (
    StageEvent,
    ConversationIdEvent,
    ConversationHistoryEvent,
    IntentEvent,
    SchemaEvent,
    SimilarExamplesEvent,
    SQLEvent,
    ValidationEvent,
    ResultEvent,
    ErrorEvent,
    FormattedResponseEvent,
    CompleteEvent
)
from ..agents.graph import agent_graph
from ..services.conversation import conversation_service
from ..constants import STAGE_MESSAGES, STAGE_ICONS


router = APIRouter(prefix="/api")


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as SSE event.
    
    Args:
        event_type: Type of event (e.g., 'stage', 'sql', 'result')
        data: Event data dictionary
        
    Returns:
        Formatted SSE string
    """
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


async def stream_graph_with_full_state(graph, initial_state):
    """Stream graph execution with full accumulated state after each node.
    
    Helper to handle LangGraph's {node_name: state_update} format
    and merge updates into accumulated state.
    
    Args:
        graph: Compiled LangGraph
        initial_state: Initial state dict
        
    Yields:
        Full accumulated state dictionary after each node
    """
    accumulated_state = initial_state.copy()
    
    # LangGraph astream() returns {node_name: state_update}
    async for state_update_dict in graph.astream(initial_state):
        # Merge state update from current node
        for node_name, state_update in state_update_dict.items():
            accumulated_state.update(state_update)
        
        # Yield full accumulated state
        yield accumulated_state


async def stream_agent_execution(
    question: str,
    conversation_id: str
) -> AsyncGenerator[str, None]:
    """Stream agent execution with progress updates.
    
    Args:
        question: User's question
        conversation_id: Conversation UUID
        
    Yields:
        SSE formatted events
    """
    # Send conversation ID first
    yield format_sse_event("conversation_id", {"conversation_id": conversation_id})
    
    # Initialize state
    initial_state = {
        "question": question,
        "conversation_id": conversation_id,
        "retry_count": 0,
        "is_complete": False
    }
    
    # Track last values to avoid duplicate emissions
    last_stage = None
    last_intent = None
    last_schema = None
    last_similar_examples = None
    last_generated_sql = None
    conversation_history_emitted = False
    
    # Stream agent execution with full state after each node
    async for state in stream_graph_with_full_state(agent_graph, initial_state):
        # Get current stage
        current_stage = state.get("current_stage")
        
        # Emit stage event (if changed)
        if current_stage and current_stage != last_stage:
            stage_event = StageEvent(
                stage=current_stage,
                message=STAGE_MESSAGES.get(current_stage, "Processing..."),
                icon=STAGE_ICONS.get(current_stage)
            )
            yield format_sse_event("stage", stage_event.model_dump())
            last_stage = current_stage
        
        # Emit conversation history event when loading_conversation stage is reached
        if current_stage == "loading_conversation" and not conversation_history_emitted:
            conversation_history = state.get("conversation_history", [])
            history_event = ConversationHistoryEvent(
                count=len(conversation_history),
                messages=conversation_history
            )
            yield format_sse_event("conversation_history", history_event.model_dump())
            conversation_history_emitted = True
        
        # Emit specific data events based on what's available
        # Only emit if value changed to avoid duplicates
        current_intent = state.get("intent")
        if current_intent and current_intent != last_intent:
            intent_event = IntentEvent(
                intent=current_intent,
                details={}
            )
            yield format_sse_event("intent", intent_event.model_dump())
            last_intent = current_intent
        
        current_schema = state.get("schema")
        if current_schema and current_schema != last_schema:
            schema_data = current_schema.get("dict", {})
            schema_event = SchemaEvent(
                tables=schema_data.get("tables", []),
                relationships=schema_data.get("relationships", [])
            )
            yield format_sse_event("schema", schema_event.model_dump())
            last_schema = current_schema
        
        current_examples = state.get("similar_examples")
        if current_examples and current_examples != last_similar_examples:
            examples_event = SimilarExamplesEvent(
                count=len(current_examples),
                examples=current_examples
            )
            yield format_sse_event("similar_examples", examples_event.model_dump())
            last_similar_examples = current_examples
        
        current_sql = state.get("generated_sql")
        if current_sql and current_sql != last_generated_sql:
            sql_event = SQLEvent(
                sql=current_sql,
                explanation=None
            )
            yield format_sse_event("sql", sql_event.model_dump())
            last_generated_sql = current_sql
        
        if "validation_result" in state and state["validation_result"]:
            validation = state["validation_result"]
            validation_event = ValidationEvent(
                valid=validation.get("valid", False),
                errors=validation.get("errors")
            )
            yield format_sse_event("validation", validation_event.model_dump())
        
        if "execution_result" in state and state["execution_result"]:
            result = state["execution_result"]
            if result.get("success"):
                result_event = ResultEvent(
                    rows=result.get("rows", []),
                    count=result.get("count", 0),
                    columns=result.get("columns", [])
                )
                yield format_sse_event("result", result_event.model_dump())
            else:
                error_event = ErrorEvent(
                    error=result.get("error", "Unknown error"),
                    retry_count=state.get("retry_count", 0)
                )
                yield format_sse_event("error", error_event.model_dump())
        
        # Emit formatted response (markdown with insights)
        if "formatted_response" in state and state["formatted_response"]:
            formatted_event = FormattedResponseEvent(
                markdown=state["formatted_response"],
                format_method=state.get("format_method", "python"),
                has_llm_summary=state.get("has_llm_summary", False)
            )
            yield format_sse_event("formatted_response", formatted_event.model_dump())
        
        # Check for completion
        if state.get("is_complete"):
            success = state.get("current_stage") == "completed"
            complete_event = CompleteEvent(
                success=success,
                message="Query completed successfully!" if success else "Query failed"
            )
            yield format_sse_event("complete", complete_event.model_dump())
            break


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """Stream chat response with progress updates.
    
    Args:
        request: Chat request with question and optional conversation_id
        
    Returns:
        SSE stream of events
    """
    # Get or create conversation
    conversation_id = await conversation_service.get_or_create_conversation(
        request.conversation_id
    )
    
    # Return streaming response
    return StreamingResponse(
        stream_agent_execution(request.question, conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )


@router.get("/conversations", response_model=ConversationsListResponse)
async def get_conversations(limit: int = 50):
    """Get list of all conversations.
    
    Args:
        limit: Maximum number of conversations to return (default 50)
        
    Returns:
        List of conversations with summary info
    """
    conversations = await conversation_service.get_all_conversations(limit)
    
    items = [
        ConversationListItem(
            id=conv["id"],
            title=conv["title"],
            created_at=conv["created_at"],
            updated_at=conv["updated_at"]
        )
        for conv in conversations
    ]
    
    return ConversationsListResponse(
        conversations=items,
        count=len(items)
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(conversation_id: str):
    """Get conversation history.
    
    Args:
        conversation_id: Conversation UUID
        
    Returns:
        Full conversation with messages
    """
    conversation = await conversation_service.get_full_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint.
    
    Returns:
        Service status and version
    """
    return HealthResponse(
        status="ok",
        version="1.0.0"
    )
