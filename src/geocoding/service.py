"""
Geocoding service with fallback and Toronto validation.
"""
import requests
import urllib.parse
import structlog
from typing import Optional, Tuple

logger = structlog.get_logger("maple_mover.geocoding")

class GeocodingService:
    def __init__(self):
        # More precise Toronto city bounds (excluding suburbs like Brampton)
        self.min_lat, self.max_lat = 43.58, 43.85  # Toronto proper latitude range
        self.min_lon, self.max_lon = -79.65, -79.0  # Toronto proper longitude range

    # -------------------------------------------------------------------------
    # Address → Coordinates
    # -------------------------------------------------------------------------
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates with fallback and better accuracy."""
        if not address or not address.strip():
            return None

        # Try raw address first
        coords = self._query_nominatim(address.strip())
        if not coords:
            # Retry with Toronto context
            coords = self._query_nominatim(f"{address.strip()}, Toronto, Ontario, Canada")

        if coords:
            logger.info(f"✅ Geocoded '{address}' to {coords}")
            return coords

        logger.warning(f"❌ No geocoding results for '{address}'")
        return None

    # -------------------------------------------------------------------------
    # Coordinates → Address
    # -------------------------------------------------------------------------
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Convert coordinates to readable address."""
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "MapleMover/1.0 (Transit Finder)"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            return data.get("display_name", None)
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None

    # -------------------------------------------------------------------------
    # Helper: call Nominatim
    # -------------------------------------------------------------------------
    def _query_nominatim(self, query: str) -> Optional[Tuple[float, float]]:
        """Perform a single geocoding request."""
        try:
            encoded = urllib.parse.quote(query)
            url = f"https://nominatim.openstreetmap.org/search?q={encoded}&format=json&limit=1&countrycodes=ca"
            headers = {"User-Agent": "MapleMover/1.0 (Transit Finder)"}
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon
        except Exception as e:
            logger.error(f"Nominatim query failed for '{query}': {e}")
        return None

    # -------------------------------------------------------------------------
    # Toronto bounds validation
    # -------------------------------------------------------------------------
    def _is_toronto_area(self, lat: float, lon: float) -> bool:
        """Return True if coordinates are within Toronto area."""
        in_bounds = self.min_lat <= lat <= self.max_lat and self.min_lon <= lon <= self.max_lon
        logger.info(f"📍 Location ({lat:.6f}, {lon:.6f}) - Toronto bounds check: {in_bounds}")
        return in_bounds
