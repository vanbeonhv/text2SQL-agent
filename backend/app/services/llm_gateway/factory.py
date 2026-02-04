"""LLM provider factory."""
from typing import Optional
from .base import BaseLLMProvider
from .gemini import GeminiProvider
from ...config import settings


class LLMProviderFactory:
    """Factory for creating LLM provider instances."""
    
    _instances = {}  # Singleton cache
    
    @classmethod
    def get_provider(
        cls,
        provider_type: Optional[str] = None,
        api_key: Optional[str] = None,
        model_tier: str = "thinking",
        **kwargs
    ) -> BaseLLMProvider:
        """Get or create an LLM provider instance.
        
        Args:
            provider_type: Provider type ('gemini', 'openai', 'claude'). Defaults to config.
            api_key: API key for the provider. Defaults to config.
            model_tier: Model tier - 'thinking' (accurate, slower) or 'lightweight' (fast, cheaper)
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM provider instance
            
        Raises:
            ValueError: If provider type is unsupported or API key is missing
        """
        # Use defaults from config
        if provider_type is None:
            provider_type = settings.llm_provider
        if api_key is None:
            api_key = settings.gemini_api_key  # TODO: Make dynamic based on provider
        
        provider_type = provider_type.lower()
        
        # Select model based on tier
        if model_tier == "thinking":
            model_name = settings.thinking_model
        elif model_tier == "lightweight":
            model_name = settings.lightweight_model
        else:
            raise ValueError(f"Invalid model_tier: {model_tier}. Use 'thinking' or 'lightweight'")
        
        # Check if instance already exists
        cache_key = f"{provider_type}_{model_name}_{api_key}"
        if cache_key in cls._instances:
            return cls._instances[cache_key]
        
        # Create new instance
        if provider_type == "gemini":
            if not api_key:
                raise ValueError("Gemini API key is required")
            instance = GeminiProvider(api_key=api_key, model_name=model_name, **kwargs)
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
