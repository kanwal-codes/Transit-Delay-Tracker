# File: src/utils/cache.py
"""
Simple in-memory cache for geocoding and TTC data
"""

import time
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger("maple_mover.cache")

class SimpleCache:
    """Simple in-memory cache with TTL support"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = 300  # 5 minutes default
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired"""
        if key not in self._cache:
            return None
            
        entry = self._cache[key]
        if time.time() > entry['expires_at']:
            # Expired, remove from cache
            del self._cache[key]
            logger.debug(f"Cache expired for key: {key}")
            return None
            
        logger.debug(f"Cache hit for key: {key}")
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL"""
        if ttl is None:
            ttl = self._default_ttl
            
        expires_at = time.time() + ttl
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': time.time()
        }
        logger.debug(f"Cached key: {key} (TTL: {ttl}s)")
    
    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get number of cached entries"""
        return len(self._cache)
    
    def cleanup_expired(self) -> int:
        """Remove expired entries and return count"""
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if now > v['expires_at']]
        
        for key in expired_keys:
            del self._cache[key]
            
        logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
        return len(expired_keys)

# Global cache instance
cache = SimpleCache()



