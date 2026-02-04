"""Tests for agent tools."""
import pytest
from app.tools.sql_validator import sql_validator


def test_sql_validator_valid_select():
    """Test SQL validator accepts valid SELECT query."""
    sql = "SELECT * FROM products WHERE price > 100"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is True
    assert result["errors"] is None


def test_sql_validator_blocks_update():
    """Test SQL validator blocks UPDATE query."""
    sql = "UPDATE products SET price = 200 WHERE id = 1"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is False
    assert len(result["errors"]) > 0


def test_sql_validator_blocks_delete():
    """Test SQL validator blocks DELETE query."""
    sql = "DELETE FROM products WHERE id = 1"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is False
    assert "DELETE" in str(result["errors"])


def test_sql_validator_blocks_drop():
    """Test SQL validator blocks DROP statement."""
    sql = "DROP TABLE products"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is False
    assert "DROP" in str(result["errors"])


def test_sql_validator_blocks_multiple_statements():
    """Test SQL validator blocks multiple statements."""
    sql = "SELECT * FROM products; DROP TABLE products;"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is False


def test_sql_validator_blocks_comments():
    """Test SQL validator blocks SQL comments."""
    sql = "SELECT * FROM products -- comment"
    result = sql_validator.validate_sql(sql)
    
    assert result["valid"] is False
    assert "comment" in str(result["errors"]).lower()
