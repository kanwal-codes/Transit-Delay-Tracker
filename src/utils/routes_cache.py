"""
Persistent cache for TTC routes data
Saves routes to disk or Redis to avoid re-discovering on every app start
"""

import json
import os
import pickle
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import structlog

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = structlog.get_logger("routes_cache")

CACHE_DIR = "cache"
ROUTES_CACHE_FILE = os.path.join(CACHE_DIR, "routes_cache.json")
ROUTES_CACHE_PICKLE = os.path.join(CACHE_DIR, "routes_cache.pkl")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_KEY = "maple_mover:routes_cache"

# Initialize Redis client
redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=False  # We're storing pickled data
        )
        # Test connection
        redis_client.ping()
        logger.info(f"✅ Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}. Falling back to disk cache.")
        redis_client = None

@dataclass
class TransitStop:
    """Represents a TTC transit stop with routes"""
    stop_id: str
    stop_code: str
    title: str
    lat: float
    lon: float
    routes: List[str]
    distance_meters: float = 0.0
    
    def to_dict(self):
        return {
            'stop_id': self.stop_id,
            'stop_code': self.stop_code,
            'title': self.title,
            'lat': self.lat,
            'lon': self.lon,
            'routes': self.routes,
            'distance_meters': self.distance_meters
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            stop_id=data['stop_id'],
            stop_code=data['stop_code'],
            title=data['title'],
            lat=data['lat'],
            lon=data['lon'],
            routes=data['routes'],
            distance_meters=data.get('distance_meters', 0.0)
        )

@dataclass
class RouteInfo:
    """Information about a transit route"""
    tag: str
    title: str
    stops: List[TransitStop]
    
    def to_dict(self):
        return {
            'tag': self.tag,
            'title': self.title,
            'stops': [stop.to_dict() for stop in self.stops]
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            tag=data['tag'],
            title=data['title'],
            stops=[TransitStop.from_dict(stop) for stop in data['stops']]
        )

def save_routes_cache(routes_cache: Dict, stops_cache: Dict, route_stops_cache: Dict):
    """Save routes cache to Redis (if available) or disk"""
    try:
        # Convert to serializable format
        routes_dict = {}
        for route_tag, route_info in routes_cache.items():
            routes_dict[route_tag] = route_info.to_dict() if hasattr(route_info, 'to_dict') else asdict(route_info)
        
        stops_dict = {}
        for stop_id, stop in stops_cache.items():
            stops_dict[stop_id] = stop.to_dict() if hasattr(stop, 'to_dict') else asdict(stop)
        
        cache_data = {
            'routes': routes_dict,
            'stops': stops_dict,
            'route_stops': route_stops_cache,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        # Try Redis first (fastest, shared across servers)
        if redis_client:
            try:
                pickled_data = pickle.dumps(cache_data)
                redis_client.set(REDIS_KEY, pickled_data)
                logger.info(f"✅ Saved routes cache to Redis: {len(routes_cache)} routes, {len(stops_cache)} stops")
                return True
            except Exception as e:
                logger.warning(f"⚠️ Redis save failed: {e}. Using disk fallback.")
        
        # Fallback to disk
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        # Save using pickle for performance
        with open(ROUTES_CACHE_PICKLE, 'wb') as f:
            pickle.dump(cache_data, f)
        
        # Also save as JSON for human readability
        with open(ROUTES_CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        logger.info(f"✅ Saved routes cache to disk: {len(routes_cache)} routes, {len(stops_cache)} stops")
        logger.info(f"📁 Cache file: {ROUTES_CACHE_PICKLE}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to save routes cache: {e}")
        return False

def load_routes_cache() -> Optional[Tuple]:
    """Load routes cache from Redis (if available) or disk"""
    try:
        # Try Redis first (fastest, shared across servers)
        if redis_client:
            try:
                pickled_data = redis_client.get(REDIS_KEY)
                if pickled_data:
                    cache_data = pickle.loads(pickled_data)
                    
                    # Convert back to objects
                    routes_cache = {}
                    for route_tag, route_data in cache_data['routes'].items():
                        routes_cache[route_tag] = RouteInfo.from_dict(route_data)
                    
                    stops_cache = {}
                    for stop_id, stop_data in cache_data['stops'].items():
                        stops_cache[stop_id] = TransitStop.from_dict(stop_data)
                    
                    route_stops_cache = cache_data.get('route_stops', {})
                    
                    timestamp = cache_data.get('timestamp', 'unknown')
                    logger.info(f"✅ Loaded routes cache from Redis ({timestamp})")
                    logger.info(f"📋 Cache contains: {len(routes_cache)} routes, {len(stops_cache)} stops")
                    
                    return routes_cache, stops_cache, route_stops_cache
            except Exception as e:
                logger.warning(f"⚠️ Redis load failed: {e}. Using disk fallback.")
        
        # Fallback to disk
        if not os.path.exists(ROUTES_CACHE_PICKLE):
            logger.info("📋 No routes cache found (Redis or disk)")
            return None, None, None
        
        # Load using pickle
        with open(ROUTES_CACHE_PICKLE, 'rb') as f:
            cache_data = pickle.load(f)
        
        # Convert back to objects
        routes_cache = {}
        for route_tag, route_data in cache_data['routes'].items():
            routes_cache[route_tag] = RouteInfo.from_dict(route_data)
        
        stops_cache = {}
        for stop_id, stop_data in cache_data['stops'].items():
            stops_cache[stop_id] = TransitStop.from_dict(stop_data)
        
        route_stops_cache = cache_data.get('route_stops', {})
        
        timestamp = cache_data.get('timestamp', 'unknown')
        logger.info(f"✅ Loaded routes cache from disk ({timestamp})")
        logger.info(f"📋 Cache contains: {len(routes_cache)} routes, {len(stops_cache)} stops")
        
        return routes_cache, stops_cache, route_stops_cache
        
    except Exception as e:
        logger.error(f"❌ Failed to load routes cache: {e}")
        return None, None, None

def cache_exists() -> bool:
    """Check if routes cache file exists"""
    return os.path.exists(ROUTES_CACHE_PICKLE)

def get_cache_age() -> int:
    """Get age of cache in days"""
    if not cache_exists():
        return -1
    
    try:
        file_time = os.path.getmtime(ROUTES_CACHE_PICKLE)
        cache_time = datetime.fromtimestamp(file_time)
        age = (datetime.now() - cache_time).days
        return age
    except:
        return -1

