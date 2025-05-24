import os
# from supabase import create_client, Client # Remove this
import asyncpg # Add this
from app.core.config import settings
from typing import List, Dict, Any, Optional

# Consider renaming SupabaseDB to something like AppDB or DatabaseService
# as it no longer uses the Supabase client library directly.
class SupabaseDB:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def init_db_pool(cls):
        if cls._pool is None:
            if not settings.DATABASE_URL:
                print("CRITICAL: DATABASE_URL is not set. Cannot initialize database pool.")
                # This will stop the application if DATABASE_URL is missing
                raise ConnectionError("DATABASE_URL is not set. Cannot initialize database pool.")
            try:
                cls._pool = await asyncpg.create_pool(
                    dsn=settings.DATABASE_URL,
                    min_size=1, # Minimum number of connections in the pool
                    max_size=10 # Maximum number of connections in the pool
                )
                print("Successfully connected to the database and created connection pool.")
            except Exception as e:
                print(f"CRITICAL: Failed to create database connection pool: {e}")
                # Re-raising the exception here is key.
                # If the pool can't be created (e.g., DB is down, bad credentials),
                # this exception will propagate up and halt FastAPI startup.
                raise

    @classmethod
    async def close_db_pool(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None
            print("Database connection pool closed.")

    def __init__(self):
        # __init__ is now very simple. The pool is managed at class level.
        if self.__class__._pool is None:
            # This indicates init_db_pool was not called or failed.
            # Methods will check and fail if pool isn't ready.
            print("Warning: SupabaseDB instance created but pool is not initialized. Call SupabaseDB.init_db_pool() at application startup.")
            pass

    async def save_chat_message(self, session_id: Optional[str], user_message: str, ai_response: str) -> None:
        if self.__class__._pool is None:
            print("Error: Database pool not initialized. Cannot save chat message.")
            raise RuntimeError("Database pool not initialized. Call SupabaseDB.init_db_pool() at application startup.")

        query = """
            INSERT INTO chat_history (session_id, user_message, ai_response)
            VALUES ($1, $2, $3)
            RETURNING id;
        """
        try:
            async with self.__class__._pool.acquire() as conn:
                # Ensure table and column names match your schema exactly.
                # Supabase default table 'chat_history' might have UUID 'id' and 'created_at' with default.
                result = await conn.fetchrow(query, session_id, user_message, ai_response)
            if result and result['id']:
                print(f"Successfully saved chat message with ID: {result['id']}")
            else:
                print(f"Failed to save chat message or retrieve ID. Response: {result}")
        except Exception as e:
            print(f"Error saving chat message to database: {e}")
            # Optionally re-raise or handle more gracefully

    async def get_chat_history(self, session_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        if self.__class__._pool is None:
            print("Error: Database pool not initialized. Cannot get chat history.")
            raise RuntimeError("Database pool not initialized. Call SupabaseDB.init_db_pool() at application startup.")

        try:
            async with self.__class__._pool.acquire() as conn:
                if session_id:
                    sql_query = """
                        SELECT * FROM chat_history
                        WHERE session_id = $1
                        ORDER BY created_at ASC
                        LIMIT $2;
                    """
                    records = await conn.fetch(sql_query, session_id, limit)
                else:
                    sql_query = """
                        SELECT * FROM chat_history
                        ORDER BY created_at ASC
                        LIMIT $1;
                    """
                    records = await conn.fetch(sql_query, limit)
            
            return [dict(record) for record in records]
        except Exception as e:
            print(f"Error getting chat history from database: {e}")
            return []

    async def clear_chat_history(self, session_id: str) -> bool:
        """Clear all chat history for a specific session"""
        if self.__class__._pool is None:
            print("Error: Database pool not initialized. Cannot clear chat history.")
            raise RuntimeError("Database pool not initialized. Call SupabaseDB.init_db_pool() at application startup.")

        query = """
            DELETE FROM chat_history 
            WHERE session_id = $1;
        """
        try:
            async with self.__class__._pool.acquire() as conn:
                result = await conn.execute(query, session_id)
                print(f"Successfully cleared chat history for session {session_id}. Rows affected: {result}")
                return True
        except Exception as e:
            print(f"Error clearing chat history for session {session_id}: {e}")
            return False

# Global instance
supabase_db = SupabaseDB()

async def get_supabase_db():
    return supabase_db