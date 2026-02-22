"""Conversation memory management service."""
from typing import List, Dict, Any, Optional
import uuid
from ..database.history import history_manager
from ..config import settings


class ConversationService:
    """Service for managing conversation memory."""
    
    async def get_or_create_conversation(
        self,
        conversation_id: Optional[str] = None
    ) -> str:
        """Get existing conversation or create new one.
        
        Args:
            conversation_id: Optional existing conversation ID
            
        Returns:
            Conversation ID (existing or newly created)
        """
        if conversation_id:
            exists = await history_manager.conversation_exists(conversation_id)
            if exists:
                return conversation_id
        
        # Create new conversation
        new_id = str(uuid.uuid4())
        await history_manager.create_conversation(new_id)
        return new_id
    
    async def load_conversation_history(
        self,
        conversation_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Load conversation history for context.
        
        Args:
            conversation_id: Conversation ID
            max_messages: Maximum number of recent messages (default from config)
            
        Returns:
            List of messages with 'role' and 'content'
        """
        if max_messages is None:
            max_messages = settings.max_conversation_messages
        
        messages = await history_manager.get_conversation_messages(
            conversation_id,
            limit=max_messages
        )
        
        # Return only role and content (remove timestamp)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    async def save_user_message(
        self,
        conversation_id: str,
        question: str
    ):
        """Save user message to conversation.
        
        Args:
            conversation_id: Conversation ID
            question: User's question
        """
        await history_manager.save_message(
            conversation_id=conversation_id,
            role="user",
            content=question
        )
    
    async def save_assistant_response(
        self,
        conversation_id: str,
        content: str,
        sql: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Save assistant response to conversation.
        
        Args:
            conversation_id: Conversation ID
            content: Assistant response content (markdown/text)
            sql: Generated SQL query
            result: Structured query result
            error: Error message
            metadata: Additional structured metadata
        """
        await history_manager.save_message(
            conversation_id=conversation_id,
            role="assistant",
            content=content,
            sql=sql,
            result=result,
            error=error,
            metadata=metadata,
        )
    
    async def get_full_conversation(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get full conversation with metadata.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Full conversation details or None if not found
        """
        return await history_manager.get_conversation(conversation_id)
    
    async def get_all_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all conversations with summary info.
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversations
        """
        return await history_manager.get_all_conversations(limit)


# Global conversation service instance
conversation_service = ConversationService()
