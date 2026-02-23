"""Constants for stage messages and other app-wide values."""

# User-friendly messages for each processing stage
STAGE_MESSAGES = {
    "initializing": "Starting your request...",
    "loading_conversation": "Loading conversation history...",
    "analyzing_intent": "Analyzing your question...",
    "retrieving_schema": "Retrieving database schema...",
    "searching_history": "Finding similar past queries...",
    "generating_sql": "Generating SQL query...",
    "validating_sql": "Validating SQL query...",
    "executing_sql": "Executing query...",
    "correcting_error": "SQL error detected, attempting to fix...",
    "formatting_response": "Formatting results...",
    "fast_response": "Preparing response...",
    "completed": "Query completed successfully!",
    "failed": "Failed to process your request."
}

# Icons for frontend display
STAGE_ICONS = {
    "initializing": "🚀",
    "loading_conversation": "💬",
    "analyzing_intent": "🔍",
    "retrieving_schema": "📊",
    "searching_history": "🔎",
    "generating_sql": "⚙️",
    "validating_sql": "✅",
    "executing_sql": "▶️",
    "correcting_error": "🔧",
    "formatting_response": "📝",
    "fast_response": "⚡",
    "completed": "🎉",
    "failed": "❌"
}

# SQL validation constants
ALLOWED_SQL_KEYWORDS = {"SELECT"}
BLOCKED_SQL_KEYWORDS = {
    "UPDATE", "DELETE", "INSERT", "DROP", "ALTER", 
    "TRUNCATE", "GRANT", "REVOKE", "CREATE", "REPLACE"
}

# Intent types
INTENT_TYPES = [
    "data_retrieval",
    "aggregation",
    "filtering",
    "sorting",
    "joining",
    "greeting",
    "goodbye",
    "schema_request",
    "unknown"
]

# Intents that trigger the fast path (no SQL generation)
FAST_PATH_INTENTS = {"greeting", "goodbye", "schema_request", "unknown"}
