"""LLM provider factory."""
from typing import Optional
from .base import BaseLLMProvider
from .gemini import GeminiProvider


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _instances = {}  # Singleton cache
    
    @classmethod
    def get_provider(
        cls,
        provider_type: str,
        api_key: Optional[str] = None,
        **kwargs
    ) -> BaseLLMProvider:
        """Get or create an LLM provider instance.
        
        Args:
            provider_type: Provider type ('gemini', 'openai', 'claude')
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider type is unsupported or API key is missing
        """
        provider_type = provider_type.lower()
        
        # Check if instance already exists
        cache_key = f"{provider_type}_{api_key}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Create new instance
        if provider_type == "gemini":
            if not api_key:
                raise ValueError("Gemini API key is required")
            instance = GeminiProvider(api_key=api_key, **kwargs)
        elif provider_type == "openai":
            raise NotImplementedError("OpenAI provider not yet implemented")
        elif provider_type == "claude":
            raise NotImplementedError("Claude provider not yet implemented")
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
        
        # Cache and return
        cls._instances[cache_key] = instance
        return instance
    
    @classmethod
    def clear_cache(cls):
        """Clear the provider instance cache."""
        cls._instances.clear()
