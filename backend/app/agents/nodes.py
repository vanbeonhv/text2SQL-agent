"""LangGraph workflow nodes."""
import json
from typing import Dict, Any
from ..models.state import AgentState
from ..services.conversation import conversation_service
from ..services.history_search import history_search_service
from ..database.schema import schema_manager
from ..tools.intent_analyzer import intent_analyzer
from ..tools.sql_writer import sql_writer
from ..tools.sql_validator import sql_validator
from ..tools.sql_executor import sql_executor
from ..tools.error_corrector import error_corrector
from ..tools.response_formatter import response_formatter
from ..tools.fast_response_builder import build_fast_response
from ..database.history import history_manager
from ..config import settings
from ..constants import FAST_PATH_INTENTS


async def load_conversation_node(state: AgentState) -> AgentState:
    """Load conversation history for context."""
    state["current_stage"] = "loading_conversation"
    
    conversation_id = state.get("conversation_id")
    if conversation_id:
        history = await conversation_service.load_conversation_history(conversation_id)
        state["conversation_history"] = history
    else:
        state["conversation_history"] = []
    
    return state


async def analyze_intent_node(state: AgentState) -> AgentState:
    """Analyze user question intent."""
    state["current_stage"] = "analyzing_intent"
    
    result = await intent_analyzer.analyze_intent(
        question=state["question"],
        conversation_history=state.get("conversation_history", [])
    )
    
    state["intent"] = result.get("intent", "unknown")
    state["intent_details"] = result.get("details", {}) or {}

    # Detect target tables for data intents only (intent routing uses FAST_PATH_INTENTS).
    # For non-data intents, schema will be built from all active registry tables (fallback) in retrieve_schema_node.
    if state["intent"] not in FAST_PATH_INTENTS:
        detection = await intent_analyzer.detect_target_tables(
            question=state["question"],
            active_only=True,
            allow_llm_fallback=True,
        )
        state["target_tables"] = detection.get("target_tables", []) or []
        # Keep detection metadata attached for downstream/use in the response formatter.
        state["intent_details"] = {
            **state.get("intent_details", {}),
            "table_detection": detection,
        }

    return state


async def retrieve_schema_node(state: AgentState) -> AgentState:
    """Retrieve database schema."""
    state["current_stage"] = "retrieving_schema"

    target_tables = state.get("target_tables") or []

    schema_dict = None
    schema_text = None
    schema_source = "default"

    # 1) Build from registry: either selected target_tables or all active definitions.
    registry_defs = []
    if target_tables:
        for tn in target_tables:
            td = await history_manager.get_table_definition(tn)
            if td and td.get("is_active", False):
                registry_defs.append(td)
    else:
        registry_defs = await history_manager.list_table_definitions(active_only=True)

    if registry_defs:
        schema_source = "registry"
        bc_db, bc_explicit = await history_manager.get_registry_business_context()
        if bc_explicit:
            business_context = bc_db
        else:
            business_context = schema_manager.load_schema().get("business_context") or {}
        schema_dict = {
            "tables": [
                {
                    "name": td["table_name"],
                    "columns": td.get("columns", []) or [],
                }
                for td in registry_defs
            ],
            "relationships": [
                r
                for td in registry_defs
                for r in (td.get("relationships", []) or [])
            ],
            "business_context": business_context,
        }
        schema_text = schema_manager.format_schema_as_text(schema_dict)

    # 2) Fallback to default schema file if registry is empty.
    if schema_dict is None:
        schema_source = "default"
        schema_dict = schema_manager.load_schema()
        schema_text = schema_manager.get_schema_as_text()

    state["schema"] = {"text": schema_text, "dict": schema_dict}
    state["schema_source"] = schema_source
    return state


def is_data_intent(state: AgentState) -> str:
    """Route to data path or fast path after retrieve_schema.
    Returns 'data' for SQL pipeline, 'fast' for greeting/goodbye/unknown/schema_request."""
    intent = state.get("intent") or "unknown"
    if intent in FAST_PATH_INTENTS:
        return "fast"
    return "data"


def fast_response_node(state: AgentState) -> AgentState:
    """Build and store a fast response for non-data intents (no SQL)."""
    state["current_stage"] = "fast_response"
    schema_dict = state.get("schema", {}).get("dict") if state.get("schema") else None
    markdown = build_fast_response(
        intent=state.get("intent", "unknown"),
        schema=schema_dict,
    )
    state["formatted_response"] = markdown
    return state


async def save_fast_response_node(state: AgentState) -> AgentState:
    """Save user message and fast response to conversation (no SQL/history)."""
    state["current_stage"] = "completed"
    state["is_complete"] = True
    await conversation_service.save_user_message(
        conversation_id=state["conversation_id"],
        question=state["question"]
    )
    await conversation_service.save_assistant_response(
        conversation_id=state["conversation_id"],
        content=state.get("formatted_response", ""),
        sql=None,
        result=None,
    )
    return state


async def search_history_node(state: AgentState) -> AgentState:
    """Search for similar past queries."""
    state["current_stage"] = "searching_history"
    
    similar = await history_search_service.find_similar_queries(
        question=state["question"],
        top_k=5,
        exclude_conversation_id=state.get("conversation_id")
    )
    
    state["similar_examples"] = similar
    
    return state


async def generate_sql_node(state: AgentState) -> AgentState:
    """Generate SQL query using LLM."""
    state["current_stage"] = "generating_sql"
    
    result = await sql_writer.generate_sql(
        question=state["question"],
        schema=state["schema"]["text"],
        conversation_history=state.get("conversation_history", []),
        similar_examples=state.get("similar_examples", []),
        intent=state.get("intent")
    )
    
    state["generated_sql"] = result["sql"]
    
    return state


def validate_sql_node(state: AgentState) -> AgentState:
    """Validate SQL query for safety."""
    state["current_stage"] = "validating_sql"
    
    validation = sql_validator.validate_sql(state["generated_sql"])
    state["validation_result"] = validation
    
    return state


async def execute_sql_node(state: AgentState) -> AgentState:
    """Execute SQL query."""
    state["current_stage"] = "executing_sql"
    
    result = await sql_executor.execute_query(state["generated_sql"])
    state["execution_result"] = result
    
    return state


async def correct_error_node(state: AgentState) -> AgentState:
    """Correct SQL error using LLM."""
    state["current_stage"] = "correcting_error"
    
    # Increment retry counter
    retry_count = state.get("retry_count", 0)
    state["retry_count"] = retry_count + 1
    
    # Get error message
    error_msg = state["execution_result"].get("error", "Unknown error")
    state["error_message"] = error_msg
    
    # Call error corrector
    result = await error_corrector.correct_sql_error(
        question=state["question"],
        failed_sql=state["generated_sql"],
        error_message=error_msg,
        schema=state["schema"]["text"],
        conversation_history=state.get("conversation_history", []),
        retry_count=retry_count
    )
    
    # Update state with corrected SQL
    state["generated_sql"] = result["sql"]
    
    return state


async def format_response_node(state: AgentState) -> AgentState:
    """Format query results to markdown with optional LLM insights."""
    state["current_stage"] = "formatting_response"
    
    # Format response based on intent
    formatted = await response_formatter.format_response(
        question=state["question"],
        intent=state.get("intent", "unknown"),
        sql=state["generated_sql"],
        result=state["execution_result"],
    )
    
    # Store formatted response
    state["formatted_response"] = formatted["markdown"]
    state["format_method"] = formatted["format_method"]
    state["has_llm_summary"] = formatted["has_summary"]
    
    return state


async def save_success_node(state: AgentState) -> AgentState:
    """Save successful query to history."""
    state["current_stage"] = "completed"
    state["is_complete"] = True
    
    # Save to conversation messages
    await conversation_service.save_user_message(
        conversation_id=state["conversation_id"],
        question=state["question"]
    )
    
    # Save assistant response with formatted markdown
    response_content = state.get("formatted_response", "")
    if not response_content:
        # Fallback if formatting failed
        response_content = (
            f"SQL: {state['generated_sql']}\n"
            f"Đã trả về {state['execution_result'].get('count', 0)} dòng"
        )
    
    await conversation_service.save_assistant_response(
        conversation_id=state["conversation_id"],
        content=response_content,
        sql=state["generated_sql"],
        result=state.get("execution_result"),
        metadata={
            "format_method": state.get("format_method", "python"),
            "has_llm_summary": state.get("has_llm_summary", False),
        }
    )
    
    # Save to query history for few-shot learning
    await history_manager.save_query(
        conversation_id=state["conversation_id"],
        question=state["question"],
        generated_sql=state["generated_sql"],
        intent=state.get("intent"),
        execution_result=json.dumps(state["execution_result"]),
        success=True
    )
    
    return state


async def fail_node(state: AgentState) -> AgentState:
    """Handle final failure after max retries."""
    state["current_stage"] = "failed"
    state["is_complete"] = True
    
    # Save user message but not the failed query
    await conversation_service.save_user_message(
        conversation_id=state["conversation_id"],
        question=state["question"]
    )
    
    await conversation_service.save_assistant_response(
        conversation_id=state["conversation_id"],
        content=(
            f"Không thể xử lý sau {state['retry_count']} lần thử: "
            f"{state.get('error_message', 'Unknown error')}"
        ),
        sql=state.get("generated_sql"),
        error=state.get("error_message", "Unknown error"),
        metadata={
            "retry_count": state.get("retry_count", 0),
            "failed": True,
        }
    )
    
    return state


# Decision functions for conditional edges

def should_retry(state: AgentState) -> str:
    """Decide whether to retry after error.
    
    Returns:
        'retry' if should retry, 'fail' if max retries exceeded
    """
    retry_count = state.get("retry_count", 0)
    if retry_count < settings.max_retry_attempts:
        return "retry"
    return "fail"


def is_valid_sql(state: AgentState) -> str:
    """Check if SQL validation passed.
    
    Returns:
        'valid' if passed, 'invalid' if failed
    """
    validation = state.get("validation_result", {})
    if validation.get("valid", False):
        return "valid"
    return "invalid"


def is_execution_success(state: AgentState) -> str:
    """Check if SQL execution succeeded.
    
    Returns:
        'success' if succeeded, 'error' if failed
    """
    result = state.get("execution_result", {})
    if result.get("success", False):
        return "success"
    return "error"
