"""FastAPI routes with SSE streaming."""
import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator
from ..models.schemas import (
    ChatRequest,
    ConversationResponse,
    HealthResponse
)
from ..models.events import (
    StageEvent,
    ConversationIdEvent,
    IntentEvent,
    SchemaEvent,
    SimilarExamplesEvent,
    SQLEvent,
    ValidationEvent,
    ResultEvent,
    ErrorEvent,
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
    
    # Track last stage to avoid duplicates
    last_stage = None
    
    # Stream agent execution
    async for state in agent_graph.astream(initial_state):
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
        
        # Emit specific data events based on what's available
        if "intent" in state and state["intent"]:
            intent_event = IntentEvent(
                intent=state["intent"],
                details={}
            )
            yield format_sse_event("intent", intent_event.model_dump())
        
        if "schema" in state and state["schema"]:
            schema_data = state["schema"].get("dict", {})
            schema_event = SchemaEvent(
                tables=schema_data.get("tables", []),
                relationships=schema_data.get("relationships", [])
            )
            yield format_sse_event("schema", schema_event.model_dump())
        
        if "similar_examples" in state and state["similar_examples"]:
            examples_event = SimilarExamplesEvent(
                count=len(state["similar_examples"]),
                examples=state["similar_examples"]
            )
            yield format_sse_event("similar_examples", examples_event.model_dump())
        
        if "generated_sql" in state and state["generated_sql"]:
            sql_event = SQLEvent(
                sql=state["generated_sql"],
                explanation=None
            )
            yield format_sse_event("sql", sql_event.model_dump())
        
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
