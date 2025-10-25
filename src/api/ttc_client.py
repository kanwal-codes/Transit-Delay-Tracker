"""
TTC API Client
Handles station fetching and parsing
"""

import requests
import time
import structlog
from typing import Dict, List, Optional, Tuple
from src.config.settings import Settings

logger = structlog.get_logger("maple_mover.api")

class TTCAPIClient:
    """Simplified TTC API client"""

    def __init__(self):
        self.base_url = Settings.BASE_URL
        self.rate_limit = Settings.API_RATE_LIMIT
        self.timeout = Settings.REQUEST_TIMEOUT
        self.working_stations = {
            "union_station": (43.6452, -79.3806),
            "spadina_station": (43.6709, -79.4000),
            "bloor_yonge_station": (43.6709, -79.3868),
            "dundas_station": (43.6561, -79.3802),
            "eglinton_station": (43.7200, -79.4000),
        }

    def fetch_station_data(self, station_uri: str) -> Optional[Dict]:
        url = f"{self.base_url}/{station_uri}.json"
        try:
            logger.info(f"🔄 Fetching TTC data from {url}")
            r = requests.get(url, timeout=self.timeout)
            if r.status_code == 200:
                logger.info(f"✅ Successfully fetched {station_uri}")
                return r.json()
            logger.warning(f"HTTP {r.status_code} for {url}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch {station_uri}: {e}")
            # Return mock data when API is down
            return self._get_mock_station_data(station_uri)
        return None

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
        stations = []
        for name, (slat, slon) in self.working_stations.items():
            dist = ((lat - slat) ** 2 + (lon - slon) ** 2) ** 0.5
            stations.append((name, slat, slon, dist))
        stations.sort(key=lambda x: x[3])
        return stations[:Settings.MAX_STATIONS]

    def extract_transit_options(self, data: Dict, station_name: str) -> List[Dict]:
        """Parse TTC JSON and extract routes"""
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
                    options.append({
                        "station_name": station_name,
                        "route_name": route.get("name", "Unknown Route"),
                        "route_type": route.get("agency", "TTC"),
                        "closest_arrival": arrivals[0]["minutes"],
                        "next_arrivals": arrivals
                    })
        return options
