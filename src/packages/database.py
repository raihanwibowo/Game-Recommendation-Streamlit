"""Database operations for chat history using PostgreSQL"""
import os
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import json

logger = logging.getLogger(__name__)


class ChatDatabase:
    """PostgreSQL database handler for chat history"""
    
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Get database URL from environment or use default
            database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/game_recommendation')
            
            self.conn = psycopg2.connect(database_url)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            with self.conn.cursor() as cur:
                # Create sessions table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create messages table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                    )
                """)
                
                # Create index for faster queries
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_session 
                    ON messages(session_id, created_at)
                """)
                
                self.conn.commit()
                logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            self.conn.rollback()
            raise
    
    def create_session(self, session_id):
        """Create a new session"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO sessions (session_id)
                    VALUES (%s)
                    ON CONFLICT (session_id) DO NOTHING
                """, (session_id,))
                self.conn.commit()
                # logger.info(f"Session created: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            self.conn.rollback()
    
    def save_message(self, session_id, role, content):
        """Save a single message to database"""
        try:
            with self.conn.cursor() as cur:
                # Ensure session exists
                self.create_session(session_id)
                
                # Insert message
                cur.execute("""
                    INSERT INTO messages (session_id, role, content)
                    VALUES (%s, %s, %s)
                """, (session_id, role, content))
                
                # Update session timestamp
                cur.execute("""
                    UPDATE sessions 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE session_id = %s
                """, (session_id,))
                
                self.conn.commit()
                # logger.info(f"Message saved for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            self.conn.rollback()
    
    def get_messages(self, session_id, limit=None):
        """Get all messages for a session"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                if limit:
                    cur.execute("""
                        SELECT role, content, created_at
                        FROM messages
                        WHERE session_id = %s
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (session_id, limit))
                else:
                    cur.execute("""
                        SELECT role, content, created_at
                        FROM messages
                        WHERE session_id = %s
                        ORDER BY created_at ASC
                    """, (session_id,))
                
                messages = cur.fetchall()
                
                # Convert to list of dicts
                result = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages
                ]
                
                logger.info(f"Retrieved {len(result)} messages for session {session_id}")
                return result
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
    
    def get_recent_messages(self, session_id, limit=10):
        """Get recent messages for a session"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT role, content, created_at
                    FROM messages
                    WHERE session_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (session_id, limit))
                
                messages = cur.fetchall()
                
                # Reverse to get chronological order
                result = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in reversed(messages)
                ]
                
                return result
        except Exception as e:
            logger.error(f"Failed to get recent messages: {e}")
            return []
    
    def clear_session(self, session_id):
        """Clear all messages for a session (but keep session)"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM messages
                    WHERE session_id = %s
                """, (session_id,))
                self.conn.commit()
                logger.info(f"Cleared messages for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            self.conn.rollback()
    
    def delete_session(self, session_id):
        """Delete a session and all its messages"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM sessions
                    WHERE session_id = %s
                """, (session_id,))
                self.conn.commit()
                logger.info(f"Deleted session {session_id}")
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            self.conn.rollback()
    
    def get_message_count(self, session_id):
        """Get total message count for a session"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) as count
                    FROM messages
                    WHERE session_id = %s
                """, (session_id,))
                result = cur.fetchone()
                return result[0] if result else 0
        except Exception as e:
            logger.error(f"Failed to get message count: {e}")
            return 0
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Singleton instance
_db_instance = None

def get_database():
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ChatDatabase()
    return _db_instance
