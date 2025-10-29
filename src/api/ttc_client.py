"""
TTC API Client
Updated to use multiple data sources with fallbacks
"""

import requests
import time
import structlog
from typing import Dict, List, Optional, Tuple
from src.config.settings import Settings
from src.utils.cache import cache
from src.api.ttc_data_sources import UnifiedTTCService, TransitData, DataSource

logger = structlog.get_logger("maple_mover.api")

class TTCAPIClient:
    """Enhanced TTC API client with multiple data sources"""

    def __init__(self):
        self.base_url = Settings.BASE_URL
        self.rate_limit = Settings.API_RATE_LIMIT
        self.timeout = Settings.REQUEST_TIMEOUT
        
        # Initialize unified TTC service
        self.ttc_service = UnifiedTTCService()
        
        # Legacy station coordinates (now handled by UnifiedTTCService)
        self.working_stations = self.ttc_service.station_coordinates

    def fetch_station_data(self, station_uri: str, max_retries: int = 2) -> Optional[Dict]:
        """Fetch station data using unified TTC service with multiple data sources"""
        # Check cache first (TTC data changes frequently, cache for 30 seconds)
        cache_key = f"ttc_station:{station_uri}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"✅ TTC data for {station_uri} from cache")
            return cached_result

        # Use unified TTC service to get data from multiple sources
        try:
            logger.info(f"🔄 Fetching TTC data for {station_uri} using multiple sources")
            transit_data_list = self.ttc_service.get_transit_data(station_uri)
            
            if transit_data_list:
                # Convert TransitData objects to legacy format for compatibility
                legacy_data = self._convert_to_legacy_format(transit_data_list, station_uri)
                
                # Cache for 30 seconds (transit data changes frequently)
                cache.set(cache_key, legacy_data, ttl=30)
                logger.info(f"✅ Successfully fetched {station_uri} using {transit_data_list[0].data_source.value} source")
                return legacy_data
            else:
                logger.warning(f"⚠️ No data received from any source for {station_uri}")
                return None
                
        except Exception as e:
            logger.error(f"❌ All data sources failed for {station_uri}: {e}")
            return None

    def _convert_to_legacy_format(self, transit_data_list: List[TransitData], station_uri: str) -> Dict:
        """Convert TransitData objects to legacy format for compatibility"""
        stops = []
        
        for transit_data in transit_data_list:
            route = {
                "name": transit_data.route_name,
                "agency": transit_data.route_type,
                "stop_times": []
            }
            
            # Convert arrival times to timestamps
            now = time.time()
            for arrival in transit_data.next_arrivals:
                minutes = arrival.get("minutes", 0)
                timestamp = now + (minutes * 60)  # Convert minutes to seconds
                route["stop_times"].append({"departure_timestamp": timestamp})
            
            stops.append({"routes": [route]})
        
        return {"stops": stops}

    def _get_mock_station_data(self, station_uri: str) -> Dict:
        """Return mock TTC data when API is unavailable"""
        logger.info(f"🔄 Using mock data for {station_uri}")
        import time
        now = time.time()
        
        mock_data = {
            "stops": [{
                "routes": [{
                    "name": "Line 1",
                    "agency": "TTC",
                    "stop_times": [
                        {"departure_timestamp": now + 300},  # 5 min
                        {"departure_timestamp": now + 600},  # 10 min
                        {"departure_timestamp": now + 900}   # 15 min
                    ]
                }, {
                    "name": "Line 2", 
                    "agency": "TTC",
                    "stop_times": [
                        {"departure_timestamp": now + 180},  # 3 min
                        {"departure_timestamp": now + 480},  # 8 min
                        {"departure_timestamp": now + 780}   # 13 min
                    ]
                }]
            }]
        }
        return mock_data

    def find_nearest_stations(self, lat: float, lon: float) -> List[Tuple[str, float, float, float]]:
        """Find nearest TTC stations using unified service"""
        return self.ttc_service.find_nearby_stations(lat, lon, Settings.MAX_STATIONS)

    def extract_transit_options(self, data: Dict, station_name: str) -> List[Dict]:
        """Parse TTC JSON and extract routes with data source information"""
        options = []
        now = time.time()
        for stop in data.get("stops", []):
            for route in stop.get("routes", []):
                arrivals = []
                for s in route.get("stop_times", [])[:Settings.MAX_ARRIVALS]:
                    ts = s.get("departure_timestamp", 0)
                    if ts > now:
                        diff = round((ts - now) / 60, 1)
                        arrivals.append({"minutes": diff})
                if arrivals:
                    # Determine data source from route name patterns
                    data_source = "unknown"
                    route_name = route.get("name", "Unknown Route")
                    
                    # Check if it's mock data (sample routes)
                    if any(line in route_name for line in ["Line 1", "Line 2", "501", "504"]):
                        data_source = "mock"
                    elif "TTC" in route.get("agency", ""):
                        data_source = "nextbus"  # Real TTC data
                    
                    options.append({
                        "station_name": station_name,
                        "route_name": route_name,
                        "route_type": route.get("agency", "TTC"),
                        "closest_arrival": arrivals[0]["minutes"],
                        "next_arrivals": arrivals,
                        "data_source": data_source
                    })
        return options
