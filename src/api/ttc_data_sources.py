# File: src/api/ttc_data_sources.py
"""
Multiple TTC Data Sources Integration
Implements NextBus API, GTFS static data, and third-party APIs with fallbacks
"""

import requests
import time
import structlog
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger("maple_mover.ttc_sources")

class DataSource(Enum):
    NEXTBUS = "nextbus"
    GTFS_STATIC = "gtfs_static"
    THIRD_PARTY = "third_party"
    MOCK = "mock"

@dataclass
class TransitData:
    """Unified transit data structure"""
    route_name: str
    route_type: str
    station_name: str
    closest_arrival: float
    next_arrivals: List[Dict[str, float]]
    data_source: DataSource
    last_updated: float

class NextBusAPIClient:
    """NextBus API client for real-time TTC data"""
    
    def __init__(self):
        self.base_url = "https://retro.umoiq.com/service/publicJSONFeed"
        self.agency = "ttc"
        self.timeout = 10
        
        # Map station names to actual NextBus stop IDs
        self.station_stop_ids = {
            "union_station": "425",  # Union Station stop
            "king_station": "425",   # Same stop as Union
            "queen_station": "425",  # Same stop as Union
            "dundas_station": "425", # Same stop as Union
            "college_station": "425", # Same stop as Union
            "wellesley_station": "425", # Same stop as Union
            "rosedale_station": "425", # Same stop as Union
            "spadina_station": "5265", # Spadina Station
            "eglinton_station": "14242", # Eglinton Station
            "bloor_yonge_station": "9126", # Bloor-Yonge Station
        }
        
    def get_vehicle_locations(self) -> Optional[Dict]:
        """Get real-time vehicle locations"""
        try:
            url = f"{self.base_url}?command=vehicleLocations&a={self.agency}&t=0"
            logger.info(f"🔄 Fetching NextBus vehicle locations from {url}")
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ NextBus vehicle locations fetched: {len(data.get('vehicle', []))} vehicles")
            return data
            
        except Exception as e:
            logger.error(f"❌ NextBus vehicle locations failed: {e}")
            return None
    
    def get_predictions(self, station_id: str) -> Optional[Dict]:
        """Get arrival predictions for a specific station"""
        try:
            # Convert station name to stop ID
            stop_id = self.station_stop_ids.get(station_id)
            if not stop_id:
                logger.warning(f"No stop ID mapping for station: {station_id}")
                return None
                
            url = f"{self.base_url}?command=predictions&a={self.agency}&stopId={stop_id}"
            logger.info(f"🔄 Fetching NextBus predictions for stop {stop_id} ({station_id})")
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ NextBus predictions fetched for stop {stop_id}")
            return data
            
        except Exception as e:
            logger.error(f"❌ NextBus predictions failed for station {station_id}: {e}")
            return None
    
    def get_routes(self) -> Optional[Dict]:
        """Get all available routes"""
        try:
            url = f"{self.base_url}?command=routeList&a={self.agency}"
            logger.info(f"🔄 Fetching NextBus routes")
            
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ NextBus routes fetched: {len(data.get('route', []))} routes")
            return data
            
        except Exception as e:
            logger.error(f"❌ NextBus routes failed: {e}")
            return None

class GTFSStaticClient:
    """GTFS static data client"""
    
    def __init__(self):
        self.gtfs_urls = [
            "https://www.transsee.ca/gtfslist?a=ttc",  # TransSee archive
            "https://www.ttc.ca/transit/gtfs",         # Official TTC GTFS
        ]
        self.timeout = 15
        
    def get_stops_nearby(self, lat: float, lon: float, radius: float = 0.5) -> List[Dict]:
        """Get stops within radius of coordinates"""
        # This would typically parse GTFS stops.txt
        # For now, return a placeholder structure
        logger.info(f"🔄 GTFS: Finding stops near ({lat}, {lon}) within {radius}km")
        
        # Placeholder - in real implementation, this would parse GTFS stops.txt
        return [
            {
                "stop_id": "union_station",
                "stop_name": "Union Station",
                "stop_lat": 43.6452,
                "stop_lon": -79.3806,
                "distance": 0.1
            }
        ]
    
    def get_routes_for_stop(self, stop_id: str) -> List[Dict]:
        """Get routes that serve a specific stop"""
        logger.info(f"🔄 GTFS: Getting routes for stop {stop_id}")
        
        # Placeholder - in real implementation, this would parse GTFS routes.txt and stop_times.txt
        return [
            {
                "route_id": "1",
                "route_short_name": "1",
                "route_long_name": "Yonge-University Line",
                "route_type": "1"  # Subway
            }
        ]

class ThirdPartyAPIClient:
    """Third-party transit API clients"""
    
    def __init__(self):
        self.apis = {
            "transitland": "https://transit.land/api/v2/",
            "opentransit": "https://api.opentransit.city/",
        }
        self.timeout = 10
        
    def get_transit_data(self, lat: float, lon: float) -> Optional[Dict]:
        """Get transit data from third-party APIs"""
        logger.info(f"🔄 Third-party: Getting transit data for ({lat}, {lon})")
        
        # Placeholder - implement actual third-party API calls
        # For now, return None to trigger fallback
        return None

class UnifiedTTCService:
    """Unified TTC data service with multiple sources and fallbacks"""
    
    def __init__(self):
        self.nextbus = NextBusAPIClient()
        self.gtfs = GTFSStaticClient()
        self.third_party = ThirdPartyAPIClient()
        
        # Import new NextBus transit service
        try:
            from src.api.dynamic_transit import NextBusTransitService
            self.nextbus_service = NextBusTransitService()
            logger.info("✅ NextBus transit service initialized")
        except ImportError as e:
            logger.warning(f"⚠️ NextBus transit service not available: {e}")
            self.nextbus_service = None
        
        # Station coordinates (fallback for station finding)
        self.station_coordinates = {
            "union_station": (43.6452, -79.3806),
            "spadina_station": (43.6709, -79.4000),
            "bloor_yonge_station": (43.6709, -79.3868),
            "dundas_station": (43.6561, -79.3802),
            "eglinton_station": (43.7200, -79.4000),
            "king_station": (43.6484, -79.3775),
            "queen_station": (43.6526, -79.3794),
            "college_station": (43.6613, -79.3830),
            "wellesley_station": (43.6656, -79.3846),
            "rosedale_station": (43.6719, -79.3862),
        }
    
    def find_nearby_stations(self, lat: float, lon: float, max_stations: int = 5) -> List[Tuple[str, float, float, float]]:
        """Find nearby stations using multiple methods"""
        stations = []
        
        # Method 1: Use dynamic Google Places API (most accurate)
        if self.dynamic_service:
            try:
                dynamic_stops = self.dynamic_service.find_transit_stops(lat, lon, radius=1000)
                for stop in dynamic_stops[:max_stations]:
                    stations.append((stop.name, stop.lat, stop.lon, stop.distance_meters))
                
                if stations:
                    logger.info(f"✅ Found {len(stations)} stations using dynamic service")
                    return stations
            except Exception as e:
                logger.warning(f"⚠️ Dynamic service failed, falling back to static: {e}")
        
        # Method 2: Use station coordinates (fallback)
        for station_id, (station_lat, station_lon) in self.station_coordinates.items():
            distance = self._calculate_distance(lat, lon, station_lat, station_lon)
            stations.append((station_id, station_lat, station_lon, distance))
        
        # Sort by distance and return top N
        stations.sort(key=lambda x: x[3])
        return stations[:max_stations]
    
    def get_transit_data_for_location(self, lat: float, lon: float) -> List[Dict]:
        """Get comprehensive transit data for a location using NextBus API discovery"""
        all_transit_data = []
        
        # Use NextBus service to discover and find nearby stops
        if self.nextbus_service:
            try:
                transit_data = self.nextbus_service.get_transit_data_for_location(lat, lon, radius_m=500)
                all_transit_data.extend(transit_data)
                
                logger.info(f"✅ NextBus service found {len(transit_data)} stops with data")
            except Exception as e:
                logger.warning(f"⚠️ NextBus service failed: {e}")
        
        # Fallback to static stations if NextBus service fails or returns no data
        if not all_transit_data:
            logger.info("🔄 Falling back to static station lookup")
            stations = self.find_nearby_stations(lat, lon, max_stations=5)
            
            for station_name, station_lat, station_lon, distance in stations:
                station_data = self.get_transit_data(station_name)
                if station_data:
                    # Convert TransitData to dict format
                    for data in station_data:
                        all_transit_data.append({
                            'stop_name': station_name,
                            'stop_id': station_name,
                            'lat': station_lat,
                            'lon': station_lon,
                            'distance': distance,
                            'route_name': data.route_name,
                            'arrival_time': data.arrival_time,
                            'data_source': data.data_source.value,
                            'last_updated': data.last_updated
                        })
        
        return all_transit_data

    def get_transit_data(self, station_id: str) -> Optional[List[TransitData]]:
        """Get transit data for a station using multiple sources with fallbacks"""
        
        # Try NextBus API first (real-time data)
        nextbus_data = self._try_nextbus_data(station_id)
        if nextbus_data:
            return nextbus_data
        
        # Try GTFS static data
        gtfs_data = self._try_gtfs_data(station_id)
        if gtfs_data:
            return gtfs_data
        
        # Try third-party APIs
        third_party_data = self._try_third_party_data(station_id)
        if third_party_data:
            return third_party_data
        
        # Final fallback: mock data
        logger.warning(f"⚠️ All data sources failed for {station_id}, using mock data")
        return self._get_mock_data(station_id)
    
    def _try_nextbus_data(self, station_id: str) -> Optional[List[TransitData]]:
        """Try to get data from NextBus API"""
        try:
            # Get predictions for the station
            predictions = self.nextbus.get_predictions(station_id)
            if not predictions:
                return None
            
            # Parse NextBus predictions format
            transit_data = []
            predictions_obj = predictions.get('predictions', {})
            
            if predictions_obj:
                route_title = predictions_obj.get('routeTitle', 'Unknown Route')
                direction = predictions_obj.get('direction', {})
                prediction_list = direction.get('prediction', [])
                
                if prediction_list:
                    # Convert predictions to minutes
                    arrivals = []
                    for pred in prediction_list[:3]:  # Get up to 3 predictions
                        minutes = float(pred.get('minutes', 0))
                        arrivals.append({"minutes": minutes})
                    
                    if arrivals:
                        transit_data.append(TransitData(
                            route_name=route_title,
                            route_type="TTC",
                            station_name=station_id.replace('_', ' ').title(),
                            closest_arrival=arrivals[0]["minutes"],
                            next_arrivals=arrivals,
                            data_source=DataSource.NEXTBUS,
                            last_updated=time.time()
                        ))
            
            logger.info(f"✅ NextBus data: {len(transit_data)} routes for {station_id}")
            return transit_data
            
        except Exception as e:
            logger.error(f"❌ NextBus data failed for {station_id}: {e}")
            return None
    
    def _try_gtfs_data(self, station_id: str) -> Optional[List[TransitData]]:
        """Try to get data from GTFS static feeds"""
        try:
            # This would parse GTFS data
            # For now, return None to trigger next fallback
            logger.info(f"🔄 GTFS data not implemented yet for {station_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ GTFS data failed for {station_id}: {e}")
            return None
    
    def _try_third_party_data(self, station_id: str) -> Optional[List[TransitData]]:
        """Try to get data from third-party APIs"""
        try:
            # This would call third-party APIs
            # For now, return None to trigger mock data
            logger.info(f"🔄 Third-party data not implemented yet for {station_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Third-party data failed for {station_id}: {e}")
            return None
    
    def _get_mock_data(self, station_id: str) -> List[TransitData]:
        """Generate mock transit data as final fallback"""
        now = time.time()
        
        mock_routes = [
            ("Line 1", "Subway", 3.5, [3.5, 8.2, 12.7]),
            ("Line 2", "Subway", 2.1, [2.1, 6.8, 11.3]),
            ("501", "Streetcar", 4.2, [4.2, 9.1, 14.5]),
            ("504", "Streetcar", 1.8, [1.8, 7.3, 13.2]),
        ]
        
        transit_data = []
        for route_name, route_type, closest, arrivals in mock_routes:
            transit_data.append(TransitData(
                route_name=route_name,
                route_type=route_type,
                station_name=station_id.replace('_', ' ').title(),
                closest_arrival=closest,
                next_arrivals=[{"minutes": arr} for arr in arrivals],
                data_source=DataSource.MOCK,
                last_updated=now
            ))
        
        logger.info(f"🔄 Mock data: {len(transit_data)} routes for {station_id}")
        return transit_data
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates using Haversine formula"""
        import math
        
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon/2) * math.sin(dlon/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
