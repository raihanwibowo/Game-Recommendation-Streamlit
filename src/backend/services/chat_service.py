"""Chat service for conversation management"""
import logging
from typing import List, Dict
from models import Message
from .knowledge_base import get_knowledge_base
from .database_service import get_database_service

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat conversations"""
    
    @staticmethod
    def build_conversation_context(messages: List[Message]) -> str:
        """Build conversation context from messages"""
        context = ""
        
        logger.info(f"Building context from {len(messages)} messages")
        
        # Summarize old messages if more than 10
        if len(messages) > 10:
            context += ChatService._summarize_old_messages(messages[:-10])
        
        # Add recent messages in full detail
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        if recent_messages:
            context += "\n--- RECENT CONVERSATION (Full Detail) ---\n"
            for msg in recent_messages:
                context += f"{msg.role.capitalize()}: {msg.content}\n\n"
            context += "--- END RECENT CONVERSATION ---\n\n"
            logger.info(f"Added {len(recent_messages)} recent messages")
        
        return context
    
    @staticmethod
    def _summarize_old_messages(messages: List[Message]) -> str:
        """Summarize older messages to extract key information"""
        logger.info(f"Summarizing {len(messages)} old messages")
        
        user_preferences = []
        games_discussed = []
        
        for msg in messages:
            content = msg.content.lower()
            if msg.role == 'user':
                # Extract preferences
                if any(word in content for word in ['like', 'love', 'prefer', 'favorite', 'suka', 'favorit']):
                    user_preferences.append(msg.content[:100])
                
                # Extract game names (capitalized words)
                words = msg.content.split()
                for word in words:
                    if len(word) > 3 and word[0].isupper():
                        games_discussed.append(word)
        
        # Log extracted data
        logger.info(f"Extracted {len(user_preferences)} preferences")
        logger.info(f"Extracted {len(set(games_discussed))} unique games")
        
        if not user_preferences and not games_discussed:
            return ""
        
        # Build summary
        summary = "\n--- CONVERSATION SUMMARY (Older Messages) ---\n"
        
        if user_preferences:
            summary += "User Preferences:\n"
            for pref in user_preferences[:5]:
                summary += f"- {pref}\n"
        
        if games_discussed:
            unique_games = list(set(games_discussed))[:10]
            summary += f"\nGames Discussed: {', '.join(unique_games)}\n"
        
        summary += "--- END SUMMARY ---\n\n"
        
        return summary
    
    @staticmethod
    def get_system_message() -> str:
        """Get system message for the AI"""
        return """You are a gaming expert AI assistant. Answer questions using the information provided in the context.

INFORMATION SOURCES (in priority order):
1. GAMING KNOWLEDGE BASE - Our curated game database (HIGHEST PRIORITY)
2. INTERNET SEARCH RESULTS - Current information from the web
3. Database knowledge - Learned from past conversations
4. Your training data - Use ONLY if no other source has the information

CRITICAL RULES:
1. If game information is provided in "GAMING KNOWLEDGE BASE" section, use ONLY that data
2. NEVER use your training data if knowledge base has the information
3. If knowledge base shows a rating, release year, or description - use it EXACTLY as provided
4. When asked about a game's rating, check the "Rating:" field in the knowledge base first
5. If the knowledge base has data about a game, that game EXISTS - do not say it hasn't been released
6. If knowledge base and internet search conflict, PREFER the knowledge base
7. When using internet search results, cite the source
8. Answer questions about games ONLY - decline other topics politely

LANGUAGE: Match the user's language (English or Bahasa Indonesia)

Be helpful and enthusiastic about gaming!"""
    
    @staticmethod
    def build_full_prompt(
        user_prompt: str,
        messages: List[Message],
        use_search: bool = False
    ) -> str:
        """Build complete prompt for the model"""
        
        system_message = ChatService.get_system_message()
        conversation_context = ChatService.build_conversation_context(messages)
        
        # Add gaming knowledge base context (from JSON files)
        knowledge_base = get_knowledge_base()
        knowledge_context = knowledge_base.get_knowledge_context(user_prompt)
        
        # Add learned knowledge from PostgreSQL database
        try:
            db_service = get_database_service()
            db_knowledge = db_service.extract_gaming_knowledge()
            logger.info("Added database knowledge to context")
        except Exception as e:
            logger.warning(f"Could not load database knowledge: {e}")
            db_knowledge = ""
        
        # Add internet search results if enabled
        internet_context = ""
        if use_search:
            try:
                logger.info(f"Performing internet search for: {user_prompt}")
                search_results = search_internet(user_prompt, max_results=3)
                if search_results and "No search results found" not in search_results:
                    internet_context = f"\n--- INTERNET SEARCH RESULTS ---\n{search_results}\n--- END SEARCH RESULTS ---\n\n"
                    logger.info(f"Added internet search results: {len(search_results)} chars")
                else:
                    logger.info("No internet search results found")
            except Exception as e:
                logger.warning(f"Internet search failed: {e}")
        
        full_prompt = f"{system_message}{knowledge_context}{db_knowledge}{internet_context}{conversation_context}\n\nUser: {user_prompt}\n\nAssistant:"
        
        # Log prompt size
        prompt_tokens = len(full_prompt.split())
        logger.info(f"Prompt size: ~{prompt_tokens} tokens (includes DB knowledge{' and internet search' if use_search else ''})")
        
        return full_prompt


# Singleton instance
_chat_service = None

def get_chat_service() -> ChatService:
    """Get or create chat service instance"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
