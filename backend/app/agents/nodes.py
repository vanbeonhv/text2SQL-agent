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
from ..database.history import history_manager
from ..config import settings


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
    
    return state


async def retrieve_schema_node(state: AgentState) -> AgentState:
    """Retrieve database schema."""
    state["current_stage"] = "retrieving_schema"
    
    # Load schema as text for LLM
    schema_text = schema_manager.get_schema_as_text()
    schema_dict = schema_manager.load_schema()
    
    state["schema"] = {
        "text": schema_text,
        "dict": schema_dict
    }
    
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


async def validate_sql_node(state: AgentState) -> AgentState:
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
        conversation_history=state.get("conversation_history", [])
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
        response_content = f"SQL: {state['generated_sql']}\nReturned {state['execution_result'].get('count', 0)} rows"
    
    await conversation_service.save_assistant_response(
        conversation_id=state["conversation_id"],
        sql=state["generated_sql"],
        result_summary=response_content
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
        sql=state["generated_sql"],
        result_summary=f"Failed after {state['retry_count']} attempts: {state.get('error_message', 'Unknown error')}"
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
