"""Gemini LLM provider implementation."""
import json
import google.generativeai as genai
from typing import Dict, Any, AsyncGenerator, Optional, List
from .base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Gemini API provider implementation."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-pro"):
        """Initialize Gemini provider.
        
        Args:
            api_key: Gemini API key
            model_name: Model to use (default: gemini-pro)
        """
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate text completion using Gemini.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instruction (prepended to prompt)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Configure generation parameters
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Generate response
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config
        )
        
        return response.text
    
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
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Yields:
            Text chunks as they are generated
        """
        # Combine system prompt and user prompt
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        # Configure generation parameters
        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens
        
        # Stream response
        response = self.model.generate_content(
            full_prompt,
            generation_config=generation_config,
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    async def generate_structured(
        self,
        prompt: str,
        response_schema: Dict[str, Any],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured JSON output.
        
        Args:
            prompt: The user prompt
            response_schema: Expected JSON schema
            system_prompt: Optional system instruction
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON response
        """
        # Add JSON formatting instruction to prompt
        schema_str = json.dumps(response_schema, indent=2)
        structured_prompt = f"{prompt}\n\nRespond with valid JSON matching this schema:\n{schema_str}"
        
        # Generate response
        response_text = await self.generate(
            structured_prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            **kwargs
        )
        
        # Parse JSON from response
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
    
    def format_conversation_history(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Format conversation history as a string for Gemini.
        
        Args:
            conversation_history: List of messages with 'role' and 'content'
            
        Returns:
            Formatted conversation string
        """
        if not conversation_history:
            return ""
        
        formatted = "Previous conversation:\n"
        for msg in conversation_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted += f"{role}: {msg['content']}\n"
        
        return formatted
