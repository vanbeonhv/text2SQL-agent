"""SQL validation tool."""
import sqlparse
from sqlparse.sql import Statement
from sqlparse.tokens import Keyword, DML
from typing import Dict, Any, List
from ..constants import BLOCKED_SQL_KEYWORDS


class SQLValidator:
    """Validates SQL queries for safety."""

    def validate_sql(self, sql: str) -> Dict[str, Any]:
        """Validate SQL query for safety.

        Checks:
        1. Only SELECT statements allowed
        2. No dangerous keywords (UPDATE, DELETE, DROP, etc.)
        3. No multiple statements (prevents SQL injection)
        4. Proper SQL syntax

        Args:
            sql: SQL query to validate

        Returns:
            Dictionary with 'valid' (bool) and 'errors' (list of error messages)
        """
        errors = []

        # Parse SQL
        try:
            parsed = sqlparse.parse(sql)
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Lỗi phân tích SQL: {str(e)}"]
            }

        # Check for empty query
        if not parsed:
            return {
                "valid": False,
                "errors": ["Câu SQL trống"]
            }

        # Check for multiple statements
        if len(parsed) > 1:
            errors.append("Không cho phép nhiều câu SQL trong một lần gửi")

        statement = parsed[0]

        # Check statement type
        if not self._is_select_statement(statement):
            errors.append("Chỉ cho phép câu lệnh SELECT")

        # Check for blocked keywords
        blocked = self._find_blocked_keywords(sql)
        if blocked:
            errors.append(f"Phát hiện từ khóa không được phép: {', '.join(blocked)}")

        # Check for comments (potential SQL injection)
        if '--' in sql or '/*' in sql:
            errors.append("Không cho phép chú thích trong SQL")

        # Check for semicolons (multiple statements)
        if sql.count(';') > 1 or (sql.count(';') == 1 and not sql.strip().endswith(';')):
            errors.append("Nhiều câu lệnh hoặc dấu chấm phẩy không hợp lệ")

        return {
            "valid": len(errors) == 0,
            "errors": errors if errors else None
        }

    def _is_select_statement(self, statement: Statement) -> bool:
        """Check if statement is a SELECT statement.

        Args:
            statement: Parsed SQL statement

        Returns:
            True if SELECT statement
        """
        # Get first significant token
        for token in statement.tokens:
            if token.ttype in (Keyword, DML):
                return token.value.upper() == 'SELECT'
        return False

    def _find_blocked_keywords(self, sql: str) -> List[str]:
        """Find any blocked keywords in SQL.

        Args:
            sql: SQL query string

        Returns:
            List of blocked keywords found
        """
        sql_upper = sql.upper()
        found = []

        for keyword in BLOCKED_SQL_KEYWORDS:
            # Check for keyword as a whole word (not part of another word)
            if f" {keyword} " in f" {sql_upper} " or f" {keyword}(" in f" {sql_upper}":
                found.append(keyword)

        return found


# Global SQL validator instance
sql_validator = SQLValidator()
