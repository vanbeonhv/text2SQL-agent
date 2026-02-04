"""SQL execution tool with safety limits."""
import asyncio
from typing import Dict, Any, List
from ..database.connection import target_db
from ..config import settings


class SQLExecutor:
    """Executes SQL queries with safety limits."""
    
    async def execute_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query with timeout and row limits.
        
        Args:
            sql: Validated SQL query to execute
            
        Returns:
            Dictionary with execution result or error
        """
        try:
            # Add LIMIT clause if not present (safety measure)
            sql_with_limit = self._ensure_limit(sql)
            
            # Execute with timeout
            rows = await asyncio.wait_for(
                target_db.fetchall(sql_with_limit),
                timeout=settings.query_timeout_seconds
            )
            
            # Convert rows to list of dicts
            results = []
            columns = []
            
            if rows:
                # Get column names from first row
                columns = list(rows[0].keys())
                
                # Convert each row
                for row in rows:
                    results.append(dict(row))
            
            return {
                "success": True,
                "rows": results,
                "count": len(results),
                "columns": columns
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": f"Query execution timeout (>{settings.query_timeout_seconds}s)",
                "error_type": "timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def _ensure_limit(self, sql: str) -> str:
        """Ensure SQL has a LIMIT clause for safety.
        
        Args:
            sql: SQL query
            
        Returns:
            SQL with LIMIT clause
        """
        sql_upper = sql.upper().strip()
        
        # Remove trailing semicolon if present
        if sql_upper.endswith(';'):
            sql = sql[:-1].strip()
        
        # Check if LIMIT already present
        if 'LIMIT' not in sql_upper:
            sql += f" LIMIT {settings.max_rows_return}"
        
        return sql


# Global SQL executor instance
sql_executor = SQLExecutor()
