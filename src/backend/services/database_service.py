"""Database service for backend to access PostgreSQL knowledge"""
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for accessing PostgreSQL database"""
    
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            database_url = os.getenv('DATABASE_URL', 'postgresql://localhost/game_recommendation')
            self.conn = psycopg2.connect(database_url)
            logger.info("Backend connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_all_conversations(self, limit: int = 100) -> List[Dict]:
        """Get all conversations from database for knowledge extraction"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT m.role, m.content, m.created_at, s.session_id
                    FROM messages m
                    JOIN sessions s ON m.session_id = s.session_id
                    ORDER BY m.created_at DESC
                    LIMIT %s
                """, (limit,))
                
                messages = cur.fetchall()
                return [dict(msg) for msg in messages]
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []
    
    def extract_gaming_knowledge(self) -> str:
        """Extract gaming knowledge from all conversations"""
        try:
            conversations = self.get_all_conversations(limit=200)
            
            if not conversations:
                return ""
            
            # Extract game mentions and preferences
            games_mentioned = set()
            user_preferences = []
            
            for msg in conversations:
                if msg['role'] == 'user':
                    content = msg['content']
                    
                    # Extract game names (capitalized words)
                    words = content.split()
                    for word in words:
                        if len(word) > 3 and word[0].isupper():
                            games_mentioned.add(word)
                    
                    # Extract preferences
                    content_lower = content.lower()
                    if any(keyword in content_lower for keyword in ['like', 'love', 'prefer', 'favorite', 'enjoy']):
                        user_preferences.append(content[:150])
            
            # Build knowledge context
            knowledge = "\n--- LEARNED KNOWLEDGE FROM DATABASE ---\n"
            
            if games_mentioned:
                games_list = list(games_mentioned)[:20]
                knowledge += f"Games discussed by users: {', '.join(games_list)}\n"
            
            if user_preferences:
                knowledge += "\nCommon user preferences:\n"
                for pref in user_preferences[:5]:
                    knowledge += f"- {pref}\n"
            
            knowledge += "--- END DATABASE KNOWLEDGE ---\n\n"
            
            logger.info(f"Extracted knowledge: {len(games_mentioned)} games, {len(user_preferences)} preferences")
            
            return knowledge if (games_mentioned or user_preferences) else ""
            
        except Exception as e:
            logger.error(f"Failed to extract knowledge: {e}")
            return ""
    
    def get_popular_topics(self, limit: int = 10) -> List[str]:
        """Get most discussed topics from database"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT content, COUNT(*) as frequency
                    FROM messages
                    WHERE role = 'user'
                    GROUP BY content
                    ORDER BY frequency DESC
                    LIMIT %s
                """, (limit,))
                
                results = cur.fetchall()
                return [row[0] for row in results]
        except Exception as e:
            logger.error(f"Failed to get popular topics: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Backend database connection closed")


# Singleton instance
_db_service = None

def get_database_service() -> DatabaseService:
    """Get or create database service instance"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service
