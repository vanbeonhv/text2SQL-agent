"""Database connection management."""
import aiosqlite
from typing import Optional
from ..config import settings


class DatabaseManager:
    """Async SQLite database connection manager."""
    
    def __init__(self, db_path: str):
        """Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> aiosqlite.Connection:
        """Get or create database connection.
        
        Returns:
            Active database connection
        """
        if self._connection is None:
            self._connection = await aiosqlite.connect(self.db_path)
            self._connection.row_factory = aiosqlite.Row
        return self._connection
    
    async def close(self):
        """Close database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
    
    async def execute(self, query: str, params: tuple = ()):
        """Execute a query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Cursor after execution
        """
        conn = await self.connect()
        cursor = await conn.execute(query, params)
        await conn.commit()
        return cursor
    
    async def fetchone(self, query: str, params: tuple = ()):
        """Execute query and fetch one result.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            Single row result or None
        """
        conn = await self.connect()
        cursor = await conn.execute(query, params)
        return await cursor.fetchone()
    
    async def fetchall(self, query: str, params: tuple = ()):
        """Execute query and fetch all results.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of rows
        """
        conn = await self.connect()
        cursor = await conn.execute(query, params)
        return await cursor.fetchall()


# Global database managers
history_db = DatabaseManager(settings.history_db_path)
target_db = DatabaseManager(settings.target_db_path)
