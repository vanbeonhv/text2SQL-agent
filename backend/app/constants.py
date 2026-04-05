"""Constants for stage messages and other app-wide values."""

# User-friendly messages for each processing stage
STAGE_MESSAGES = {
    "initializing": "Đang bắt đầu xử lý yêu cầu...",
    "loading_conversation": "Đang tải lịch sử hội thoại...",
    "analyzing_intent": "Đang phân tích câu hỏi...",
    "retrieving_schema": "Đang lấy schema cơ sở dữ liệu...",
    "searching_history": "Đang tìm các truy vấn tương tự trong quá khứ...",
    "generating_sql": "Đang sinh câu truy vấn SQL...",
    "validating_sql": "Đang kiểm tra câu SQL...",
    "executing_sql": "Đang thực thi truy vấn...",
    "correcting_error": "Phát hiện lỗi SQL, đang thử sửa...",
    "formatting_response": "Đang định dạng kết quả...",
    "fast_response": "Đang chuẩn bị phản hồi...",
    "completed": "Truy vấn hoàn tất thành công!",
    "failed": "Không thể xử lý yêu cầu của bạn."
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
