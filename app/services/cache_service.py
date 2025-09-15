"""
Cache service for managing application-wide caching.

This service provides Redis-based caching with fallback to in-memory caching
for improved performance and scalability.
"""

import json
import pickle
import threading
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta
import redis
from app.config.settings import get_config

class CacheService:
    """
    Service for managing application-wide caching.
    
    Provides Redis-based caching with fallback to in-memory caching.
    """
    
    def __init__(self):
        """Initialize the cache service."""
        self.config = get_config()
        self._memory_cache = {}
        self._cache_lock = threading.Lock()
        
        # Try to connect to Redis
        try:
            # Parse Redis URL (default to localhost:6379 if not configured)
            if self.config.CELERY_CONFIG.broker_url.startswith('redis://'):
                redis_url = self.config.CELERY_CONFIG.broker_url
                host = redis_url.split('://')[1].split(':')[0]
                port = int(redis_url.split(':')[-1].split('/')[0])
            else:
                host = 'localhost'
                port = 6379
            
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=1,  # Use different DB than Celery
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
        except Exception as e:
            print(f"Redis not available, falling back to memory cache: {e}")
            self.redis_client = None
            self.redis_available = False
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if self.redis_available:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                print(f"Redis get error: {e}")
        
        # Fallback to memory cache
        with self._cache_lock:
            if key in self._memory_cache:
                cached_data = self._memory_cache[key]
                if datetime.now() < cached_data['expires_at']:
                    return cached_data['value']
                else:
                    del self._memory_cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if self.redis_available:
            try:
                self.redis_client.setex(key, ttl_seconds, json.dumps(value, default=str))
                return True
            except Exception as e:
                print(f"Redis set error: {e}")
        
        # Fallback to memory cache
        with self._cache_lock:
            self._memory_cache[key] = {
                'value': value,
                'expires_at': datetime.now() + timedelta(seconds=ttl_seconds)
            }
            # Clean up old entries (keep only last 1000)
            if len(self._memory_cache) > 1000:
                oldest_key = min(self._memory_cache.keys(), 
                               key=lambda k: self._memory_cache[k]['expires_at'])
                del self._memory_cache[oldest_key]
        return True
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if self.redis_available:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                print(f"Redis delete error: {e}")
        
        # Also remove from memory cache
        with self._cache_lock:
            self._memory_cache.pop(key, None)
        return True
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (supports * wildcard)
            
        Returns:
            Number of keys deleted
        """
        deleted_count = 0
        
        if self.redis_available:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    deleted_count = self.redis_client.delete(*keys)
            except Exception as e:
                print(f"Redis delete pattern error: {e}")
        
        # Also clean memory cache
        with self._cache_lock:
            keys_to_delete = [k for k in self._memory_cache.keys() if self._match_pattern(k, pattern)]
            for key in keys_to_delete:
                del self._memory_cache[key]
                deleted_count += 1
        
        return deleted_count
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Simple pattern matching for memory cache cleanup."""
        if '*' not in pattern:
            return key == pattern
        
        # Convert pattern to regex-like matching
        import re
        regex_pattern = pattern.replace('*', '.*')
        return bool(re.match(regex_pattern, key))
    
    def get_prayer_times(self, user_id: int, date_str: str) -> Optional[Dict[str, Any]]:
        """Get cached prayer times for a user and date."""
        key = self._get_cache_key('prayer_times', user_id, date_str)
        return self.get(key)
    
    def set_prayer_times(self, user_id: int, date_str: str, prayer_data: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        """Cache prayer times for a user and date."""
        key = self._get_cache_key('prayer_times', user_id, date_str)
        return self.set(key, prayer_data, ttl_seconds)
    
    def get_api_prayer_times(self, user_id: str, date_str: str, fiqh_method: str, geo_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached API response for prayer times."""
        key = self._get_cache_key('api_prayer_times', user_id, date_str, fiqh_method, geo_hash)
        return self.get(key)
    
    def set_api_prayer_times(self, user_id: str, date_str: str, fiqh_method: str, geo_hash: str, api_response: Dict[str, Any], ttl_seconds: int = 86400) -> bool:
        """Cache API response for prayer times (24 hours default)."""
        key = self._get_cache_key('api_prayer_times', user_id, date_str, fiqh_method, geo_hash)
        return self.set(key, api_response, ttl_seconds)
    
    def invalidate_prayer_times(self, user_id: int, date_str: str) -> bool:
        """Invalidate cached prayer times for a user and date."""
        key = self._get_cache_key('prayer_times', user_id, date_str)
        return self.delete(key)
    
    def invalidate_user_prayer_times(self, user_id: int) -> int:
        """Invalidate all cached prayer times for a user."""
        pattern = self._get_cache_key('prayer_times', user_id, '*')
        return self.delete_pattern(pattern)
    
    def get_dashboard_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get cached dashboard stats for a user."""
        key = self._get_cache_key('dashboard_stats', user_id)
        return self.get(key)
    
    def set_dashboard_stats(self, user_id: int, stats_data: Dict[str, Any], ttl_seconds: int = 600) -> bool:
        """Cache dashboard stats for a user."""
        key = self._get_cache_key('dashboard_stats', user_id)
        return self.set(key, stats_data, ttl_seconds)
    
    def invalidate_dashboard_stats(self, user_id: int) -> bool:
        """Invalidate cached dashboard stats for a user."""
        key = self._get_cache_key('dashboard_stats', user_id)
        return self.delete(key)
    
    def get_weekly_calendar(self, user_id: int, week_start: str) -> Optional[Dict[str, Any]]:
        """Get cached weekly calendar data for a user and week."""
        key = self._get_cache_key('weekly_calendar', user_id, week_start)
        return self.get(key)
    
    def set_weekly_calendar(self, user_id: int, week_start: str, calendar_data: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        """Cache weekly calendar data for a user and week."""
        key = self._get_cache_key('weekly_calendar', user_id, week_start)
        return self.set(key, calendar_data, ttl_seconds)
    
    def invalidate_weekly_calendar(self, user_id: int, week_start: str) -> bool:
        """Invalidate cached weekly calendar data for a user and week."""
        key = self._get_cache_key('weekly_calendar', user_id, week_start)
        return self.delete(key)
    
    def invalidate_user_calendar(self, user_id: int) -> int:
        """Invalidate all cached calendar data for a user."""
        pattern = self._get_cache_key('weekly_calendar', user_id, '*')
        return self.delete_pattern(pattern)

# Global cache service instance
cache_service = CacheService()
