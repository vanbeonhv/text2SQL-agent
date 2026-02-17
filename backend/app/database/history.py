"""Chat history and conversation memory database operations."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from .connection import history_db


class HistoryManager:
    """Manages conversation history and query history in SQLite."""
    
    async def init_database(self):
        """Initialize database schema."""
        # Create conversations table
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT
            )
        """)
        
        # Create conversation_messages table (for conversation memory)
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        # Create query_history table (for few-shot learning)
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                question TEXT NOT NULL,
                intent TEXT,
                generated_sql TEXT NOT NULL,
                execution_result TEXT,
                success BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        # Create indexes
        await history_db.execute("""
            CREATE INDEX IF NOT EXISTS idx_conv_messages 
            ON conversation_messages(conversation_id, timestamp)
        """)
        
        await history_db.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_question 
            ON query_history(question)
        """)
        
        await history_db.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_success 
            ON query_history(success)
        """)
    
    async def create_conversation(self, conversation_id: str, user_id: Optional[str] = None):
        """Create a new conversation.
        
        Args:
            conversation_id: UUID for the conversation
            user_id: Optional user identifier
        """
        await history_db.execute(
            "INSERT INTO conversations (id, user_id) VALUES (?, ?)",
            (conversation_id, user_id)
        )
    
    async def conversation_exists(self, conversation_id: str) -> bool:
        """Check if conversation exists.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            True if conversation exists
        """
        row = await history_db.fetchone(
            "SELECT 1 FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        return row is not None
    
    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str
    ):
        """Save a message to conversation history.
        
        Args:
            conversation_id: Conversation UUID
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        await history_db.execute(
            "INSERT INTO conversation_messages (conversation_id, role, content) VALUES (?, ?, ?)",
            (conversation_id, role, content)
        )
        
        # Update conversation updated_at timestamp
        await history_db.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,)
        )
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation message history.
        
        Args:
            conversation_id: Conversation UUID
            limit: Maximum number of recent messages to return
            
        Returns:
            List of messages with role, content, and timestamp
        """
        query = """
            SELECT role, content, timestamp
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY timestamp DESC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        rows = await history_db.fetchall(query, (conversation_id,))
        
        # Reverse to get chronological order
        messages = []
        for row in reversed(rows):
            messages.append({
                "role": row["role"],
                "content": row["content"],
                "timestamp": row["timestamp"]
            })
        
        return messages
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get full conversation details.
        
        Args:
            conversation_id: Conversation UUID
            
        Returns:
            Conversation details with messages
        """
        # Get conversation metadata
        conv_row = await history_db.fetchone(
            "SELECT id, created_at, updated_at, user_id FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        
        if not conv_row:
            return None
        
        # Get messages
        messages = await self.get_conversation_messages(conversation_id)
        
        return {
            "id": conv_row["id"],
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "user_id": conv_row["user_id"],
            "messages": messages
        }
    
    async def get_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conversations with summary info.
        
        Args:
            limit: Maximum number of conversations to return (sorted by recent first)
            
        Returns:
            List of conversations with id, created_at, updated_at, and first message as preview
        """
        rows = await history_db.fetchall(
            """
            SELECT id, created_at, updated_at, user_id
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        conversations = []
        for row in rows:
            # Get first message for preview/title
            first_message = await history_db.fetchone(
                """
                SELECT content FROM conversation_messages
                WHERE conversation_id = ? AND role = 'user'
                ORDER BY timestamp ASC
                LIMIT 1
                """,
                (row["id"],)
            )
            
            title = "New Conversation"
            if first_message:
                content = first_message["content"]
                # Truncate to first 50 chars for title
                title = content[:50] + ("..." if len(content) > 50 else "")
            
            conversations.append({
                "id": row["id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "title": title
            })
        
        return conversations
    
    async def save_query(
        self,
        conversation_id: str,
        question: str,
        generated_sql: str,
        intent: Optional[str] = None,
        execution_result: Optional[str] = None,
        success: bool = True
    ):
        """Save a query to query history (for few-shot learning).
        
        Args:
            conversation_id: Conversation UUID
            question: User's question
            generated_sql: Generated SQL query
            intent: Detected intent
            execution_result: JSON string of execution result
            success: Whether query executed successfully
        """
        await history_db.execute(
            """
            INSERT INTO query_history 
            (conversation_id, question, intent, generated_sql, execution_result, success)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, question, intent, generated_sql, execution_result, success)
        )
    
    async def get_successful_queries(
        self,
        limit: int = 100,
        exclude_conversation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get successful queries for similarity search.
        
        Args:
            limit: Maximum number of queries to return
            exclude_conversation_id: Exclude queries from this conversation
            
        Returns:
            List of successful query records
        """
        query = """
            SELECT question, intent, generated_sql, timestamp
            FROM query_history
            WHERE success = 1
        """
        
        params = []
        if exclude_conversation_id:
            query += " AND conversation_id != ?"
            params.append(exclude_conversation_id)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        rows = await history_db.fetchall(query, tuple(params))
        
        return [
            {
                "question": row["question"],
                "intent": row["intent"],
                "sql": row["generated_sql"],
                "timestamp": row["timestamp"]
            }
            for row in rows
        ]


# Global history manager instance
history_manager = HistoryManager()
