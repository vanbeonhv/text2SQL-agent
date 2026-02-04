"""Base LLM provider interface."""
from abc import ABC, abstractmethod
from typing import Dict, Any, AsyncGenerator, Optional, List


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.
    
    All LLM providers (Gemini, OpenAI, Claude, etc.) must implement this interface.
    """
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text completion.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    async def generate_streaming(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate text completion with streaming.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Text chunks as they are generated
        """
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured output (JSON).
        
        Args:
            prompt: The user prompt
            response_schema: Expected JSON schema for the response
            system_prompt: Optional system instruction
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Parsed JSON response matching the schema
        """
        pass
    
    def format_conversation_history(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> Any:
        """Format conversation history for this provider.
        
        Args:
            conversation_history: List of messages with 'role' and 'content'
            
        Returns:
            Provider-specific conversation format
        """
        return conversation_history
