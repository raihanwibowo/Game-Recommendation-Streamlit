"""Gaming knowledge base service"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GamingKnowledgeBase:
    """Service for managing gaming knowledge base"""
    
    def __init__(self, data_dir: str = None):
        """Initialize knowledge base"""
        # Determine correct path based on where the script is run from
        if data_dir is None:
            # Get the absolute path to this file's directory
            current_file = Path(__file__).resolve()
            # This file is at: project_root/src/backend/services/knowledge_base.py
            # Go up 3 levels to get project_root
            project_root = current_file.parent.parent.parent.parent
            # Data is at project_root/src/data/knowledge
            self.data_dir = project_root / "src" / "data" / "knowledge"
            
            # Create if doesn't exist
            self.data_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.data_dir = Path(data_dir)
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # logger.info(f"Knowledge base path: {self.data_dir.absolute()}")
        
        self.games_db = self._load_json("games_database.json")
        self.genres_db = self._load_json("genres.json")
        self.platforms_db = self._load_json("platforms.json")
        
        logger.info(f"Loaded knowledge base: {len(self.games_db)} games, {len(self.genres_db)} genres")
    
    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from data directory"""
        filepath = self.data_dir / filename
        # logger.info(f"Attempting to load: {filepath.absolute()}")
        
        if filepath.exists():
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"Successfully loaded {filename}: {len(data)} entries")
                    return data
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {filename}: {e}")
            except Exception as e:
                logger.error(f"Failed to load {filename}: {e}")
        else:
            logger.warning(f"File not found: {filepath.absolute()}")
        
        return {}
    
    def get_game_info(self, game_name: str) -> Optional[Dict]:
        """Get information about a specific game"""
        game_name_lower = game_name.lower()
        for game_id, game_data in self.games_db.items():
            if game_data.get('name', '').lower() == game_name_lower:
                return game_data
        return None
    
    def get_genre_info(self, genre: str) -> Optional[Dict]:
        """Get information about a genre"""
        return self.genres_db.get(genre.lower())
    
    def get_platform_info(self, platform: str) -> Optional[Dict]:
        """Get information about a platform"""
        return self.platforms_db.get(platform.lower())
    
    def search_games_by_genre(self, genre: str) -> List[Dict]:
        """Search games by genre"""
        genre_lower = genre.lower()
        results = []
        for game_id, game_data in self.games_db.items():
            if genre_lower in [g.lower() for g in game_data.get('genres', [])]:
                results.append(game_data)
        return results[:10]  # Return top 10
    
    def search_games_by_keyword(self, keyword: str) -> List[Dict]:
        """Search games by keyword in name or description"""
        keyword_lower = keyword.lower()
        results = []
        scored_results = []  # (score, game_data)
        
        logger.info(f"Searching for keyword: '{keyword}' in {len(self.games_db)} games")
        
        # Extract potential game names from the query (words with 3+ chars)
        words = keyword_lower.split()
        search_terms = [w for w in words if len(w) >= 3 and w not in ['what', 'the', 'from', 'rating', 'about', 'game', 'tell']]
        
        for game_id, game_data in self.games_db.items():
            name = game_data.get('name', '').lower()
            description = game_data.get('description', '').lower()
            game_id_lower = game_id.lower()
            
            score = 0
            
            # Highest priority: Full keyword matches
            if keyword_lower in name or keyword_lower in game_id_lower:
                score = 1000
                logger.info(f"Found exact match: {game_data.get('name')}")
            else:
                # Count matching terms
                matching_terms = sum(1 for term in search_terms if term in name or term in game_id_lower)
                if matching_terms > 0:
                    score = matching_terms * 10  # More matches = higher score
                    logger.info(f"Found match ({matching_terms} terms): {game_data.get('name')}")
            
            if score > 0:
                scored_results.append((score, game_data))
        
        # Sort by score (highest first)
        scored_results.sort(key=lambda x: x[0], reverse=True)
        results = [game for score, game in scored_results]
        
        logger.info(f"Search returned {len(results)} games")
        return results[:10]
    
    def get_popular_games(self, limit: int = 10) -> List[Dict]:
        """Get popular games"""
        games = list(self.games_db.values())
        # Sort by rating if available
        games.sort(key=lambda x: x.get('rating', 0), reverse=True)
        return games[:limit]
    
    def get_knowledge_context(self, query: str) -> str:
        """Get relevant knowledge context for a query"""
        logger.info(f"Getting knowledge context for query: '{query}'")
        logger.info(f"Available games: {len(self.games_db)}, genres: {len(self.genres_db)}")
        
        context = "\n--- GAMING KNOWLEDGE BASE ---\n"
        
        # Search for relevant games
        games = self.search_games_by_keyword(query)
        logger.info(f"Search returned {len(games)} games")
        
        if games:
            context += "\nRelevant Games:\n"
            for game in games[:3]:
                logger.info(f"Adding game to context: {game.get('name')} (rating: {game.get('rating')})")
                context += f"- {game.get('name')}: {game.get('description', 'N/A')}\n"
                context += f"  Genres: {', '.join(game.get('genres', []))}\n"
                context += f"  Platforms: {', '.join(game.get('platforms', []))}\n"
                if game.get('release_year'):
                    context += f"  Release Year: {game.get('release_year')}\n"
                if game.get('rating'):
                    context += f"  Rating: {game.get('rating')}\n"
        else:
            logger.warning("No games found in search!")
        
        # Check for genre information
        for genre in self.genres_db.keys():
            if genre in query.lower():
                genre_info = self.genres_db[genre]
                context += f"\nGenre Info - {genre.title()}:\n"
                context += f"  {genre_info.get('description', 'N/A')}\n"
                context += f"  Popular games: {', '.join(genre_info.get('popular_games', []))}\n"
        
        context += "--- END KNOWLEDGE BASE ---\n\n"
        
        has_content = len(context) > 100
        logger.info(f"Knowledge context generated: {len(context)} chars, has_content: {has_content}")
        logger.info(f"Context preview: {context[:200]}...")
        
        return context if has_content else ""


    def reload(self):
        """Reload knowledge base from files"""
        logger.info("Reloading knowledge base...")
        self.games_db = self._load_json("games_database.json")
        self.genres_db = self._load_json("genres.json")
        self.platforms_db = self._load_json("platforms.json")
        logger.info(f"Reloaded: {len(self.games_db)} games, {len(self.genres_db)} genres")


# Singleton instance
_knowledge_base = None

def get_knowledge_base() -> GamingKnowledgeBase:
    """Get or create knowledge base instance"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = GamingKnowledgeBase()
    return _knowledge_base

def reload_knowledge_base():
    """Force reload of knowledge base"""
    global _knowledge_base
    if _knowledge_base is not None:
        _knowledge_base.reload()
    else:
        _knowledge_base = GamingKnowledgeBase()
