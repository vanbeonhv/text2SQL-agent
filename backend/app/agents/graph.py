"""LangGraph state graph definition."""
from langgraph.graph import StateGraph, END
from ..models.state import AgentState
from .nodes import (
    load_conversation_node,
    analyze_intent_node,
    retrieve_schema_node,
    search_history_node,
    generate_sql_node,
    validate_sql_node,
    execute_sql_node,
    correct_error_node,
    save_success_node,
    fail_node,
    should_retry,
    is_valid_sql,
    is_execution_success
)


def create_agent_graph() -> StateGraph:
    """Create the LangGraph state graph for the agent workflow.
    
    Returns:
        Compiled state graph
    """
    # Create graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("load_conversation", load_conversation_node)
    workflow.add_node("analyze_intent", analyze_intent_node)
    workflow.add_node("retrieve_schema", retrieve_schema_node)
    workflow.add_node("search_history", search_history_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("correct_error", correct_error_node)
    workflow.add_node("save_success", save_success_node)
    workflow.add_node("fail", fail_node)
    
    # Set entry point
    workflow.set_entry_point("load_conversation")
    
    # Add edges (sequential flow)
    workflow.add_edge("load_conversation", "analyze_intent")
    workflow.add_edge("analyze_intent", "retrieve_schema")
    workflow.add_edge("retrieve_schema", "search_history")
    workflow.add_edge("search_history", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")
    
    # Conditional edge: validation result
    workflow.add_conditional_edges(
        "validate_sql",
        is_valid_sql,
        {
            "valid": "execute_sql",
            "invalid": "fail"  # Validation failed, cannot proceed
        }
    )
    
    # Conditional edge: execution result
    workflow.add_conditional_edges(
        "execute_sql",
        is_execution_success,
        {
            "success": "save_success",
            "error": "correct_error"
        }
    )
    
    # Conditional edge: retry decision
    workflow.add_conditional_edges(
        "correct_error",
        should_retry,
        {
            "retry": "validate_sql",  # Go back to validate corrected SQL
            "fail": "fail"
        }
    )
    
    # End nodes
    workflow.add_edge("save_success", END)
    workflow.add_edge("fail", END)
    
    # Compile graph
    return workflow.compile()


# Global graph instance
agent_graph = create_agent_graph()
