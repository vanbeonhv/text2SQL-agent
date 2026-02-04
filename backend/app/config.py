"""Configuration management using Pydantic Settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # LLM Provider Configuration
    llm_provider: str = "gemini"
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database Paths
    target_db_path: str = "data/target.db"
    history_db_path: str = "data/history.db"
    schema_path: str = "data/schema.json"
    
    # Agent Configuration
    max_retry_attempts: int = 3
    query_timeout_seconds: int = 30
    max_rows_return: int = 1000
    max_conversation_messages: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
