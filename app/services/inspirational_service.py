"""Inspirational content service for Quranic verses and Hadith.

This service handles loading and managing Quranic verses and Hadith from JSON files
instead of database tables, providing better performance and easier content management.
"""

import json
import os
import random
from typing import Any, Dict, List, Optional

from app.config.settings import Config
from .base_service import BaseService


class InspirationalService(BaseService):
    """Service for managing Quranic verses and Hadith from JSON files."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the inspirational service.

        Args:
            config: Configuration instance. If None, will use current app config.
        """
        super().__init__(config)
        self._content_cache = None
        self._json_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'inspirational_content.json'
        )

    def _load_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load inspirational content from JSON file.
        
        Returns:
            Dict containing quranic_verses and hadith lists
        """
        if self._content_cache is None:
            try:
                with open(self._json_file_path, 'r', encoding='utf-8') as file:
                    self._content_cache = json.load(file)
                    self.logger.info(f"Loaded inspirational content from {self._json_file_path}")
            except FileNotFoundError:
                self.logger.error(f"Inspirational content file not found: {self._json_file_path}")
                self._content_cache = {"quranic_verses": [], "hadith": []}
            except json.JSONDecodeError as e:
                self.logger.error(f"Error parsing inspirational content JSON: {e}")
                self._content_cache = {"quranic_verses": [], "hadith": []}
        
        return self._content_cache

    def get_random_verse(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a random Quranic verse, optionally filtered by category.
        
        Args:
            category: Optional category filter (e.g., 'prayer', 'patience', 'guidance')
            
        Returns:
            Dict containing verse data or None if no verses found
        """
        try:
            content = self._load_content()
            verses = content.get('quranic_verses', [])
            
            if category:
                verses = [v for v in verses if v.get('category') == category]
            
            if not verses:
                self.logger.warning(f"No Quranic verses found for category: {category}")
                return None
                
            verse = random.choice(verses)
            self.logger.debug(f"Selected random verse: {verse.get('reference', 'Unknown')}")
            return verse
            
        except Exception as e:
            self.logger.error(f"Error getting random verse: {e}")
            return None

    def get_random_hadith(self, category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a random Hadith, optionally filtered by category.
        
        Args:
            category: Optional category filter (e.g., 'prayer', 'patience', 'motivation')
            
        Returns:
            Dict containing hadith data or None if no hadith found
        """
        try:
            content = self._load_content()
            hadiths = content.get('hadith', [])
            
            if category:
                hadiths = [h for h in hadiths if h.get('category') == category]
            
            if not hadiths:
                self.logger.warning(f"No Hadith found for category: {category}")
                return None
                
            hadith = random.choice(hadiths)
            self.logger.debug(f"Selected random hadith: {hadith.get('reference', 'Unknown')}")
            return hadith
            
        except Exception as e:
            self.logger.error(f"Error getting random hadith: {e}")
            return None

    def get_verse_by_id(self, verse_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific Quranic verse by ID.
        
        Args:
            verse_id: ID of the verse to retrieve
            
        Returns:
            Dict containing verse data or None if not found
        """
        try:
            content = self._load_content()
            verses = content.get('quranic_verses', [])
            
            for verse in verses:
                if verse.get('id') == verse_id:
                    return verse
                    
            self.logger.warning(f"Verse with ID {verse_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting verse by ID {verse_id}: {e}")
            return None

    def get_hadith_by_id(self, hadith_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific Hadith by ID.
        
        Args:
            hadith_id: ID of the hadith to retrieve
            
        Returns:
            Dict containing hadith data or None if not found
        """
        try:
            content = self._load_content()
            hadiths = content.get('hadith', [])
            
            for hadith in hadiths:
                if hadith.get('id') == hadith_id:
                    return hadith
                    
            self.logger.warning(f"Hadith with ID {hadith_id} not found")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting hadith by ID {hadith_id}: {e}")
            return None

    def get_verses_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get Quranic verses filtered by category.
        
        Args:
            category: Category to filter by
            limit: Optional limit on number of verses returned
            
        Returns:
            List of verse dictionaries
        """
        try:
            content = self._load_content()
            verses = content.get('quranic_verses', [])
            
            filtered_verses = [v for v in verses if v.get('category') == category]
            
            if limit:
                filtered_verses = filtered_verses[:limit]
                
            return filtered_verses
            
        except Exception as e:
            self.logger.error(f"Error getting verses by category {category}: {e}")
            return []

    def get_hadith_by_category(self, category: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get Hadith filtered by category.
        
        Args:
            category: Category to filter by
            limit: Optional limit on number of hadith returned
            
        Returns:
            List of hadith dictionaries
        """
        try:
            content = self._load_content()
            hadiths = content.get('hadith', [])
            
            filtered_hadiths = [h for h in hadiths if h.get('category') == category]
            
            if limit:
                filtered_hadiths = filtered_hadiths[:limit]
                
            return filtered_hadiths
            
        except Exception as e:
            self.logger.error(f"Error getting hadith by category {category}: {e}")
            return []

    def get_available_categories(self) -> Dict[str, List[str]]:
        """Get all available categories for verses and hadith.
        
        Returns:
            Dict with 'verses' and 'hadith' keys containing category lists
        """
        try:
            content = self._load_content()
            
            verse_categories = list(set(
                v.get('category') for v in content.get('quranic_verses', [])
                if v.get('category')
            ))
            
            hadith_categories = list(set(
                h.get('category') for h in content.get('hadith', [])
                if h.get('category')
            ))
            
            return {
                'verses': sorted(verse_categories),
                'hadith': sorted(hadith_categories)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting available categories: {e}")
            return {'verses': [], 'hadith': []}

    def reload_content(self) -> bool:
        """Reload content from JSON file, clearing cache.
        
        Returns:
            True if reload successful, False otherwise
        """
        try:
            self._content_cache = None
            self._load_content()
            self.logger.info("Inspirational content reloaded successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error reloading content: {e}")
            return False
