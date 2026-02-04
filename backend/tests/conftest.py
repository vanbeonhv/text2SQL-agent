"""Pytest configuration and fixtures."""
import pytest
import os
import tempfile
from app.config import settings


@pytest.fixture(scope="session")
def temp_db_dir():
    """Create temporary directory for test databases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Override database paths for testing
        settings.history_db_path = os.path.join(tmpdir, "test_history.db")
        settings.target_db_path = os.path.join(tmpdir, "test_target.db")
        settings.schema_path = os.path.join(tmpdir, "test_schema.json")
        
        yield tmpdir


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing."""
    return {
        "sql": "SELECT * FROM products",
        "explanation": "Get all products"
    }
