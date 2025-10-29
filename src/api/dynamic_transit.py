# File: src/api/dynamic_transit.py
"""
Real Transit Data Service using NextBus API Discovery
Finds all routes, stops, and real-time transit information
"""

import requests
import structlog
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from src.config.settings import Settings
from src.utils.geo_utils import calculate_distance
from src.utils.routes_cache import load_routes_cache, save_routes_cache, get_cache_age

logger = structlog.get_logger()

@dataclass
class TransitStop:
    """Represents a TTC transit stop with routes"""
    stop_id: str
    stop_code: str
    title: str  # Intersection name like "Spadina / College"
    lat: float
    lon: float
    routes: List[str]  # List of route tags that serve this stop
    distance_meters: float = 0.0
    
@dataclass
class RouteInfo:
    """Information about a transit route"""
    tag: str
    title: str
    stops: List[TransitStop]

class NextBusTransitService:
    """Service that uses NextBus API to discover routes and stops dynamically"""
    
    def __init__(self):
        self.api_url = "https://retro.umoiq.com/service/publicJSONFeed"
        self.agency = "ttc"
        self.timeout = 15
        
        # Cache for discovered data
        self.routes_cache = {}
        self.stops_cache = {}  # stop_id -> TransitStop
        self.route_stops_cache = {}  # route_tag -> [stop_ids]
        
        # Try to load from disk cache
        self._load_disk_cache()
    
    def _load_disk_cache(self):
        """Load routes cache from disk if available"""
        routes, stops, route_stops = load_routes_cache()
        if routes and stops:
            self.routes_cache = routes
            self.stops_cache = stops
            self.route_stops_cache = route_stops
            age = get_cache_age()
            logger.info(f"📋 Loaded routes from disk cache (age: {age} days)")
        
    def discover_all_routes(self) -> Dict[str, RouteInfo]:
        """Discover all TTC routes and their stops"""
        try:
            if self.routes_cache:
                logger.info("📋 Using cached routes")
                return self.routes_cache
                
            logger.info("🔍 Discovering all TTC routes and stops...")
            
            # Step 1: Get all routes
            routes_data = self._get_routes()
            if not routes_data:
                logger.error("❌ Failed to get routes")
                return {}
            
            all_routes = {}
            
            # Step 2: For each route, get all stops
            for route in routes_data.get('route', []):
                route_tag = route.get('tag')
                route_title = route.get('title', '')
                
                logger.info(f"🔄 Getting stops for route {route_tag}: {route_title}")
                
                # Get route configuration (includes stops)
                route_config = self._get_route_config(route_tag)
                if not route_config:
                    continue
                
                # Parse stops from route configuration
                stops = self._parse_stops_from_route_config(route_config, route_tag)
                
                all_routes[route_tag] = RouteInfo(
                    tag=route_tag,
                    title=route_title,
                    stops=stops
                )
                
                logger.info(f"✅ Route {route_tag} has {len(stops)} stops")
            
            self.routes_cache = all_routes
            
            # Build reverse index: stop_id -> routes that serve it
            self._build_stop_to_routes_index()
            
            # Save to disk cache for next time
            save_routes_cache(self.routes_cache, self.stops_cache, self.route_stops_cache)
            
            logger.info(f"✅ Discovered {len(all_routes)} routes with stops")
            return all_routes
            
        except Exception as e:
            logger.error(f"❌ Failed to discover routes: {e}")
            return {}
    
    def _get_routes(self) -> Optional[Dict]:
        """Get all TTC routes from NextBus API"""
        try:
            url = f"{self.api_url}?command=routeList&a={self.agency}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get routes: {e}")
            return None
    
    def _get_route_config(self, route_tag: str) -> Optional[Dict]:
        """Get route configuration including stops"""
        try:
            url = f"{self.api_url}?command=routeConfig&a={self.agency}&r={route_tag}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"❌ Failed to get route config for {route_tag}: {e}")
            return None
    
    def _parse_stops_from_route_config(self, config: Dict, route_tag: str) -> List[TransitStop]:
        """Parse stops from NextBus route configuration"""
        stops = []
        route_data = config.get('route', {})
        
        for stop in route_data.get('stop', []):
            stop_id = stop.get('stopId', '')
            title = stop.get('title', 'Unknown')
            stop_tag = stop.get('tag', '')
            lat = float(stop.get('lat', 0))
            lon = float(stop.get('lon', 0))
            
            # Add to global stops cache
            if stop_id not in self.stops_cache:
                self.stops_cache[stop_id] = TransitStop(
                    stop_id=stop_id,
                    stop_code=stop_tag,
                    title=title,
                    lat=lat,
                    lon=lon,
                    routes=[]  # Will be filled by _build_stop_to_routes_index
                )
            
            stops.append(self.stops_cache[stop_id])
            
            # Track which routes serve this stop
            if stop_id not in self.route_stops_cache:
                self.route_stops_cache[stop_id] = []
            if route_tag not in self.route_stops_cache[stop_id]:
                self.route_stops_cache[stop_id].append(route_tag)
        
        return stops
    
    def _build_stop_to_routes_index(self):
        """Build reverse index: stop_id -> routes"""
        for stop_id, stop in self.stops_cache.items():
            stop.routes = self.route_stops_cache.get(stop_id, [])
    
    def find_nearby_stops(self, user_lat: float, user_lon: float, radius_m: int = 700, max_stops: int = 10) -> List[TransitStop]:
        """Find NEAREST stops - sorts by distance, takes closest max_stops"""
        # First ensure we have all routes discovered
        if not self.routes_cache:
            self.discover_all_routes()
        
        all_stops = []
        radius_km = radius_m / 1000.0
        
        # Pre-calculate bounds for quick filtering
        lat_margin = radius_km / 111.0
        lon_margin = radius_km / (111.0 * abs(abs(user_lat) / 90.0))
        
        # Collect all stops within the radius
        for stop_id, stop in self.stops_cache.items():
            # Quick bounding box check
            lat_diff = abs(stop.lat - user_lat)
            lon_diff = abs(stop.lon - user_lon)
            
            if lat_diff > lat_margin or lon_diff > lon_margin:
                continue
            
            # Calculate exact distance
            distance = calculate_distance(user_lat, user_lon, stop.lat, stop.lon)
            distance_meters = distance * 1000
            
            if distance_meters <= radius_m:
                stop.distance_meters = distance_meters
                all_stops.append(stop)
        
        # Sort by distance (closest first)
        all_stops.sort(key=lambda x: x.distance_meters)
        
        # Take only the closest max_stops
        # If 10 found at 20m, return those 10 (don't show stops at 100m)
        # If only 5 found within 700m, return those 5
        nearby_stops = all_stops[:max_stops]
        
        logger.info(f"📍 Found {len(nearby_stops)} closest stops (sorted by distance)")
        return nearby_stops
    
    def get_real_time_predictions(self, stop_id: str, route_tags: List[str] = None, vehicle_locations: Dict = None) -> List[Dict]:
        """Get real-time predictions for a stop with optional route filter"""
        predictions = []
        
        # Get vehicle locations if not provided (for backward compatibility)
        if vehicle_locations is None:
            vehicle_locations = self._get_all_vehicle_locations()
        
        # Get predictions for the stop
        try:
            url = f"{self.api_url}?command=predictions&a={self.agency}&stopId={stop_id}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            predictions_obj = data.get('predictions', [])
            if not isinstance(predictions_obj, list):
                predictions_obj = [predictions_obj] if predictions_obj else []
            
            for pred_obj in predictions_obj:
                if not isinstance(pred_obj, dict):
                    continue
                    
                route_tag = pred_obj.get('routeTag', '')
                route_title = pred_obj.get('routeTitle', 'Unknown Route')
                
                # Filter by requested routes if specified
                if route_tags and route_tag not in route_tags:
                    continue
                
                # Get direction data
                direction = pred_obj.get('direction', {})
                if isinstance(direction, list):
                    direction = direction[0] if direction else {}
                
                if not isinstance(direction, dict):
                    continue
                
                prediction_list = direction.get('prediction', [])
                if not isinstance(prediction_list, list):
                    prediction_list = [prediction_list] if prediction_list else []
                
                # Get direction title
                dir_title = direction.get('title', direction.get('dirTitleBecauseNoPredictions', ''))
                if not dir_title:
                    # Try to get it from the message
                    dir_title = pred_obj.get('dirTitleBecauseNoPredictions', '')
                
                for pred in prediction_list[:3]:  # Get up to 3 predictions
                    if not isinstance(pred, dict):
                        continue
                        
                    minutes = float(pred.get('minutes', 0))
                    seconds = float(pred.get('seconds', minutes * 60))
                    vehicle_id = pred.get('vehicle', '')
                    
                    # Get vehicle location and heading from vehicle_locations map
                    vehicle_lat = 0
                    vehicle_lon = 0
                    vehicle_heading = 0
                    if vehicle_id in vehicle_locations:
                        vehicle_data = vehicle_locations[vehicle_id]
                        vehicle_lat = float(vehicle_data.get('lat', 0))
                        vehicle_lon = float(vehicle_data.get('lon', 0))
                        vehicle_heading = float(vehicle_data.get('heading', 0))
                    
                    predictions.append({
                        'route_tag': route_tag,
                        'route_title': route_title,
                        'direction': dir_title,  # e.g., "Eastbound", "Westbound"
                        'stop_id': stop_id,
                        'arrival_minutes': minutes,
                        'arrival_seconds': seconds,
                        'vehicle_id': vehicle_id,
                        'vehicle_lat': vehicle_lat,
                        'vehicle_lon': vehicle_lon,
                        'vehicle_heading': vehicle_heading,
                        'data_source': 'nextbus'
                    })
            
            logger.info(f"✅ Got {len(predictions)} predictions for stop {stop_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to get predictions for {stop_id}: {e}")
        
        return predictions
    
    def _get_all_vehicle_locations(self) -> Dict[str, Dict]:
        """Get all vehicle locations and cache them"""
        vehicle_map = {}
        
        try:
            url = f"{self.api_url}?command=vehicleLocations&a={self.agency}&t=0"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            vehicles = data.get('vehicle', [])
            for vehicle in vehicles:
                vehicle_id = vehicle.get('id')
                vehicle_map[vehicle_id] = {
                    'lat': vehicle.get('lat'),
                    'lon': vehicle.get('lon'),
                    'heading': vehicle.get('heading'),
                    'speedKmHr': vehicle.get('speedKmHr'),
                    'routeTag': vehicle.get('routeTag'),  # Store route for filtering
                    'dirTag': vehicle.get('dirTag')  # Store direction
                }
            
            logger.info(f"✅ Got {len(vehicle_map)} vehicle locations")
            
        except Exception as e:
            logger.error(f"❌ Failed to get vehicle locations: {e}")
        
        return vehicle_map
    
    def get_all_buses_for_route(self, route_tag: str, vehicle_locations: Dict = None) -> List[Dict]:
        """Get all buses currently running on a specific route"""
        if vehicle_locations is None:
            vehicle_locations = self._get_all_vehicle_locations()
        
        route_buses = []
        for vehicle_id, vehicle_data in vehicle_locations.items():
            if vehicle_data.get('routeTag') == route_tag:
                route_buses.append({
                    'vehicle_id': vehicle_id,
                    'lat': vehicle_data.get('lat'),
                    'lon': vehicle_data.get('lon'),
                    'heading': vehicle_data.get('heading'),
                    'speed': vehicle_data.get('speedKmHr'),
                    'direction': vehicle_data.get('dirTag')
                })
        
        logger.info(f"🚌 Route {route_tag}: Found {len(route_buses)} buses currently running")
        return route_buses
    
    def get_transit_data_for_location(self, user_lat: float, user_lon: float, radius_m: int = 700) -> List[Dict]:
        """Get complete transit data for a location - shows nearest 10 stops within 700m"""
        all_transit_data = []
        
        # Find nearest 10 stops within 700m radius
        nearby_stops = self.find_nearby_stops(user_lat, user_lon, radius_m, max_stops=10)
        
        logger.info(f"📍 Found {len(nearby_stops)} stops within {radius_m}m, getting predictions...")
        
        # Get vehicle locations ONCE for all stops (optimization)
        vehicle_locations = self._get_all_vehicle_locations()
        logger.info(f"🚌 Got {len(vehicle_locations)} vehicle locations")
        
        for stop in nearby_stops:
            # Get real-time predictions for each route serving this stop
            predictions = self.get_real_time_predictions(stop.stop_id, stop.routes, vehicle_locations)
            
            # Include stop even if no predictions (shows transit is available)
            all_transit_data.append({
                'stop_id': stop.stop_id,
                'stop_name': stop.title,  # Intersection name
                'lat': stop.lat,
                'lon': stop.lon,
                'distance': stop.distance_meters,
                'routes': stop.routes,
                'predictions': predictions,
                'data_source': 'nextbus'
            })
        
        logger.info(f"✅ Returning transit data for {len(all_transit_data)} stops")
        return all_transit_data