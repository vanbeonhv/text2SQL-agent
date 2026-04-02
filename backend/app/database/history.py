"""Chat history and conversation memory database operations."""
from typing import List, Dict, Any, Optional
import json
from .connection import history_db


class HistoryManager:
    """Manages conversation history and query history in SQLite."""

    async def _get_table_columns(self, table_name: str) -> set[str]:
        """Get current column names for a table."""
        rows = await history_db.fetchall(f"PRAGMA table_info({table_name})")
        return {row["name"] for row in rows}

    async def init_database(self):
        """Initialize database schema."""
        # Rebuild incompatible legacy schemas (destructive)
        existing_message_columns = await self._get_table_columns("conversation_messages")
        required_message_columns = {
            "id",
            "conversation_id",
            "role",
            "content",
            "sql",
            "result_json",
            "error",
            "metadata_json",
            "timestamp",
        }
        if existing_message_columns and not required_message_columns.issubset(existing_message_columns):
            await self.reset_database()
            return

        # Create conversations table
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id TEXT,
                schema_json TEXT
            )
        """)

        # Create conversation_messages table (for conversation memory)
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS conversation_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                sql TEXT,
                result_json TEXT,
                error TEXT,
                metadata_json TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        # Create query_history table (for few-shot learning fallback)
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

        # Create schema_table_definitions table for flexible table-level schemas
        await history_db.execute("""
            CREATE TABLE IF NOT EXISTS schema_table_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL UNIQUE,
                columns_json TEXT NOT NULL,
                relationships_json TEXT,
                description TEXT,
                tags_json TEXT,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        await history_db.execute("""
            CREATE INDEX IF NOT EXISTS idx_schema_table_active
            ON schema_table_definitions(is_active)
        """)

        # Add feedback column to conversation_messages if missing (non-destructive migration)
        existing_msg_cols = await self._get_table_columns("conversation_messages")
        if "feedback" not in existing_msg_cols:
            await history_db.execute(
                "ALTER TABLE conversation_messages ADD COLUMN feedback TEXT"
            )

        existing_conv_cols = await self._get_table_columns("conversations")
        if "schema_json" not in existing_conv_cols:
            await history_db.execute(
                "ALTER TABLE conversations ADD COLUMN schema_json TEXT"
            )

    async def reset_database(self):
        """Drop and recreate all history tables (destructive)."""
        await history_db.execute("DROP TABLE IF EXISTS query_history")
        await history_db.execute("DROP TABLE IF EXISTS conversation_messages")
        await history_db.execute("DROP TABLE IF EXISTS conversations")

        await self.init_database()

    async def create_conversation(self, conversation_id: str, user_id: Optional[str] = None):
        """Create a new conversation."""
        await history_db.execute(
            "INSERT INTO conversations (id, user_id) VALUES (?, ?)",
            (conversation_id, user_id)
        )

    async def conversation_exists(self, conversation_id: str) -> bool:
        """Check if conversation exists."""
        row = await history_db.fetchone(
            "SELECT 1 FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        return row is not None

    async def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sql: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Save a message to conversation history."""
        result_json = json.dumps(result) if result is not None else None
        metadata_json = json.dumps(metadata) if metadata is not None else None

        await history_db.execute(
            """
            INSERT INTO conversation_messages
            (conversation_id, role, content, sql, result_json, error, metadata_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, role, content, sql, result_json, error, metadata_json)
        )

        await history_db.execute(
            "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conversation_id,)
        )

    async def get_conversation_messages(
        self,
        conversation_id: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get conversation message history."""
        query = """
            SELECT id, role, content, sql, result_json, error, metadata_json, feedback, timestamp
            FROM conversation_messages
            WHERE conversation_id = ?
            ORDER BY id DESC
        """

        if limit:
            query += f" LIMIT {limit}"

        rows = await history_db.fetchall(query, (conversation_id,))

        messages = []
        for row in reversed(rows):
            result = json.loads(row["result_json"]) if row["result_json"] else None
            metadata = json.loads(row["metadata_json"]) if row["metadata_json"] else None

            messages.append({
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "sql": row["sql"],
                "results": result,
                "error": row["error"],
                "metadata": metadata,
                "feedback": row["feedback"],
                "timestamp": row["timestamp"]
            })

        return messages

    async def upsert_table_definition(
        self,
        table_name: str,
        columns: List[Dict[str, Any]],
        relationships: Optional[List[Dict[str, Any]]] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        is_active: bool = True,
    ):
        """Create or update a table-level schema definition in history DB."""
        columns_json = json.dumps(columns)
        relationships_json = json.dumps(relationships or [])
        tags_json = json.dumps(tags or [])

        await history_db.execute(
            """
            INSERT INTO schema_table_definitions
                (table_name, columns_json, relationships_json, description, tags_json, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(table_name) DO UPDATE SET
                columns_json = excluded.columns_json,
                relationships_json = excluded.relationships_json,
                description = excluded.description,
                tags_json = excluded.tags_json,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
            """,
            (table_name, columns_json, relationships_json, description, tags_json, int(is_active)),
        )

    async def get_table_definition(
        self,
        table_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a table-level schema definition from history DB."""
        row = await history_db.fetchone(
            """
            SELECT table_name, columns_json, relationships_json, description, tags_json, is_active
            FROM schema_table_definitions
            WHERE table_name = ?
            """,
            (table_name,),
        )
        if not row:
            return None

        return {
            "table_name": row["table_name"],
            "columns": json.loads(row["columns_json"]) if row["columns_json"] else [],
            "relationships": json.loads(row["relationships_json"]) if row["relationships_json"] else [],
            "description": row["description"],
            "tags": json.loads(row["tags_json"]) if row["tags_json"] else [],
            "is_active": bool(row["is_active"]),
        }

    async def list_table_definitions(
        self,
        active_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """List table-level schema definitions (optionally only active)."""
        query = """
            SELECT table_name, columns_json, relationships_json, description, tags_json, is_active
            FROM schema_table_definitions
        """
        params: list[Any] = []
        if active_only:
            query += " WHERE is_active = 1"

        query += " ORDER BY table_name ASC"

        rows = await history_db.fetchall(query, tuple(params))
        return [
            {
                "table_name": r["table_name"],
                "columns": json.loads(r["columns_json"]) if r["columns_json"] else [],
                "relationships": json.loads(r["relationships_json"]) if r["relationships_json"] else [],
                "description": r["description"],
                "tags": json.loads(r["tags_json"]) if r["tags_json"] else [],
                "is_active": bool(r["is_active"]),
            }
            for r in rows
        ]

    async def set_table_definition_active(
        self,
        table_name: str,
        is_active: bool,
    ) -> bool:
        """Soft activate/deactivate a table definition."""
        cur = await history_db.execute(
            """
            UPDATE schema_table_definitions
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP
            WHERE table_name = ?
            """,
            (int(is_active), table_name),
        )
        # aiosqlite cursor has rowcount; but DatabaseManager.execute returns cursor.
        return getattr(cur, "rowcount", 0) > 0

    async def delete_table_definition(
        self,
        table_name: str,
    ) -> bool:
        """Soft-delete a table definition (sets is_active = 0)."""
        return await self.set_table_definition_active(
            table_name=table_name,
            is_active=False,
        )

    async def set_message_feedback(
        self,
        conversation_id: str,
        sql: str,
        status: Optional[str],
    ):
        """Set like/dislike feedback on an assistant message.

        Identifies the message by conversation_id + sql (most recent match).

        Args:
            conversation_id: Conversation UUID
            sql: SQL query of the message to update
            status: 'like', 'dislike', or None to clear
        """
        await history_db.execute(
            """
            UPDATE conversation_messages SET feedback = ?
            WHERE id = (
                SELECT id FROM conversation_messages
                WHERE conversation_id = ? AND sql = ? AND role = 'assistant'
                ORDER BY id DESC LIMIT 1
            )
            """,
            (status, conversation_id, sql)
        )

    async def get_liked_messages(
        self,
        limit: int = 100,
        exclude_conversation_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get liked assistant messages for few-shot similarity search.

        JOINs with the preceding user message to get the original question.

        Args:
            limit: Maximum number of records to return
            exclude_conversation_id: Exclude messages from this conversation

        Returns:
            List of {question, sql, intent, timestamp}
        """
        base_query = """
            SELECT a.sql, a.timestamp, u.content AS question
            FROM conversation_messages a
            JOIN conversation_messages u ON (
                u.id = (
                    SELECT MAX(id) FROM conversation_messages
                    WHERE conversation_id = a.conversation_id
                      AND role = 'user'
                      AND id < a.id
                )
            )
            WHERE a.feedback = 'like'
              AND a.sql IS NOT NULL
              AND a.role = 'assistant'
        """

        params = []
        if exclude_conversation_id:
            base_query += " AND a.conversation_id != ?"
            params.append(exclude_conversation_id)

        base_query += " ORDER BY a.id DESC LIMIT ?"
        params.append(limit)

        rows = await history_db.fetchall(base_query, tuple(params))

        return [
            {
                "question": row["question"],
                "sql": row["sql"],
                "intent": None,
                "timestamp": row["timestamp"],
            }
            for row in rows
        ]

    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get full conversation details."""
        conv_row = await history_db.fetchone(
            "SELECT id, created_at, updated_at, user_id FROM conversations WHERE id = ?",
            (conversation_id,)
        )

        if not conv_row:
            return None

        messages = await self.get_conversation_messages(conversation_id)

        title = "New Conversation"
        for message in messages:
            if message["role"] == "user":
                content = message["content"]
                title = content[:50] + ("..." if len(content) > 50 else "")
                break

        return {
            "id": conv_row["id"],
            "title": title,
            "created_at": conv_row["created_at"],
            "updated_at": conv_row["updated_at"],
            "user_id": conv_row["user_id"],
            "schema": await self.get_conversation_schema(conversation_id),
            "messages": messages
        }

    async def get_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conversations with summary info."""
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
        """Save a query to query history."""
        await history_db.execute(
            """
            INSERT INTO query_history
            (conversation_id, question, intent, generated_sql, execution_result, success)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (conversation_id, question, intent, generated_sql, execution_result, success)
        )

    async def set_conversation_schema(self, conversation_id: str, schema: Dict[str, Any]):
        """Persist custom schema JSON for a conversation."""
        await history_db.execute(
            """
            UPDATE conversations
            SET schema_json = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (json.dumps(schema), conversation_id),
        )

    async def clear_conversation_schema(self, conversation_id: str):
        """Clear custom schema for a conversation (fallback to default file schema)."""
        await history_db.execute(
            """
            UPDATE conversations
            SET schema_json = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,),
        )

    async def get_conversation_schema(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get custom schema JSON for conversation if configured."""
        row = await history_db.fetchone(
            "SELECT schema_json FROM conversations WHERE id = ?",
            (conversation_id,),
        )
        if not row or not row["schema_json"]:
            return None
        return json.loads(row["schema_json"])


# Global history manager instance
history_manager = HistoryManager()
