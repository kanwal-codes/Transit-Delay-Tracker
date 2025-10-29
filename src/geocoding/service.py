"""
Geocoding service with Google Maps API fallback, Toronto validation, and caching.
"""
import requests
import urllib.parse
import structlog
import os
from typing import Optional, Tuple, List
from src.utils.cache import cache
from src.config.settings import Settings

logger = structlog.get_logger("maple_mover.geocoding")

class GeocodingService:
    def __init__(self):
        # More precise Toronto city bounds (excluding all GTA suburbs)
        self.min_lat, self.max_lat = 43.60, 43.80  # Toronto proper latitude range (more restrictive)
        self.min_lon, self.max_lon = -79.60, -79.20  # Toronto proper longitude range (more restrictive)
        
        # Google Maps API configuration
        self.google_api_key = Settings.GOOGLE_MAPS_API_KEY
        self.use_google_api = bool(self.google_api_key)
        
        if self.use_google_api:
            logger.info("✅ Google Maps API enabled for geocoding")
        else:
            logger.warning("⚠️ Google Maps API key not found. Using OpenStreetMap Nominatim only.")
    
    # -------------------------------------------------------------------------
    # Address → Coordinates
    # -------------------------------------------------------------------------
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates with Google Maps API and fallback to Nominatim."""
        if not address or not address.strip():
            return None

        # Check cache first
        cache_key = f"geocode:{address.strip().lower()}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"✅ Geocoded '{address}' from cache: {cached_result}")
            return cached_result

        # Try Google Maps API first (if available)
        if self.use_google_api:
            coords = self._query_google_maps(address.strip())
            if coords:
                cache.set(cache_key, coords, ttl=3600)
                logger.info(f"✅ Geocoded '{address}' to {coords} using Google Maps API")
                return coords

        # Fallback to Nominatim with address variants
        address_variants = self._generate_address_variants(address.strip())
        
        for variant in address_variants:
            coords = self._query_nominatim(variant)
            if coords:
                # Cache the result for 1 hour (addresses don't change often)
                cache.set(cache_key, coords, ttl=3600)
                logger.info(f"✅ Geocoded '{address}' to {coords} using Nominatim variant: {variant}")
                return coords

        logger.warning(f"❌ No geocoding results for '{address}'")
        return None
    
    # -------------------------------------------------------------------------
    # Coordinates → Address
    # -------------------------------------------------------------------------
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """Convert coordinates to readable address with caching."""
        # Check cache first - use 6 decimal places to allow for small GPS variations
        cache_key = f"reverse_geocode:{lat:.6f},{lon:.6f}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"✅ Reverse geocoded ({lat}, {lon}) from cache: {cached_result}")
            return cached_result

        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        headers = {"User-Agent": "MapleMover/1.0 (Transit Finder)"}
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            address = data.get("display_name", None)
            
            if address:
                # Cache the result for 1 hour
                cache.set(cache_key, address, ttl=3600)
                logger.info(f"✅ Reverse geocoded ({lat}, {lon}) to: {address}")
            
            return address
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    # -------------------------------------------------------------------------
    # Helper: call Google Maps API
    # -------------------------------------------------------------------------
    def _query_google_maps(self, query: str) -> Optional[Tuple[float, float]]:
        """Perform a single geocoding request using Google Maps API with Toronto context."""
        try:
            # Add Toronto context for ambiguous searches
            enhanced_query = self._enhance_query_for_toronto(query)
            encoded = urllib.parse.quote(enhanced_query)
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded}&key={self.google_api_key}"
            
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("status") == "OK" and data.get("results"):
                result = data["results"][0]
                location = result["geometry"]["location"]
                lat = float(location["lat"])
                lon = float(location["lng"])
                
                # Log the formatted address for debugging
                formatted_address = result.get("formatted_address", query)
                logger.debug(f"Google Maps geocoded '{query}' to '{formatted_address}' at ({lat}, {lon})")
                
                return lat, lon
            else:
                logger.warning(f"Google Maps API returned status: {data.get('status')} for query: {query}")
                return None
                
        except Exception as e:
            logger.error(f"Google Maps API query failed for '{query}': {e}")
            return None

    # -------------------------------------------------------------------------
    # Helper: enhance query for Toronto context
    # -------------------------------------------------------------------------
    def _enhance_query_for_toronto(self, query: str) -> str:
        """Add Toronto context to ambiguous queries to improve geocoding accuracy."""
        query_lower = query.lower().strip()
        
        # Common ambiguous landmarks that need Toronto context
        ambiguous_landmarks = {
            'union station': 'Union Station Toronto Ontario Canada',
            'cn tower': 'CN Tower Toronto Ontario Canada', 
            'eaton centre': 'Eaton Centre Toronto Ontario Canada',
            'eaton center': 'Eaton Centre Toronto Ontario Canada',
            'rom': 'Royal Ontario Museum Toronto Ontario Canada',
            'royal ontario museum': 'Royal Ontario Museum Toronto Ontario Canada',
            'casa loma': 'Casa Loma Toronto Ontario Canada',
            'high park': 'High Park Toronto Ontario Canada',
            'pearson airport': 'Toronto Pearson Airport Ontario Canada',
            'toronto airport': 'Toronto Pearson Airport Ontario Canada',
            'yorkdale': 'Yorkdale Shopping Centre Toronto Ontario Canada',
            'scarborough town centre': 'Scarborough Town Centre Toronto Ontario Canada',
            'scarborough town center': 'Scarborough Town Centre Toronto Ontario Canada',
            'dundas square': 'Dundas Square Toronto Ontario Canada',
            'nathan phillips square': 'Nathan Phillips Square Toronto Ontario Canada',
            'city hall': 'Toronto City Hall Ontario Canada',
            'toronto city hall': 'Toronto City Hall Ontario Canada'
        }
        
        # Don't enhance if query already has specific address details (unit numbers, postal codes, etc.)
        # as these indicate a specific address
        has_specific_details = any(
            indicator in query_lower 
            for indicator in ['unit', 'units', 'suite', 'apt', 'apartment', '#', 'm5x', 'm4', 'm3', 'm2', 'm1']
        )
        
        if has_specific_details:
            # Keep original query - it's already specific enough
            logger.debug(f"Keeping specific address as-is: '{query}'")
            return query
        
        # Check if query matches any ambiguous landmark
        for landmark, enhanced in ambiguous_landmarks.items():
            if landmark in query_lower:
                logger.debug(f"Enhanced ambiguous query '{query}' to '{enhanced}'")
                return enhanced
        
        # If query doesn't contain "toronto" or "ontario" or "canada", add Toronto context
        if not any(context in query_lower for context in ['toronto', 'ontario', 'canada', 'on']):
            enhanced_query = f"{query}, Toronto, Ontario, Canada"
            logger.debug(f"Added Toronto context to '{query}' -> '{enhanced_query}'")
            return enhanced_query
        
        # Return original query if it already has sufficient context
        return query

    # -------------------------------------------------------------------------
    # Helper: call Nominatim
    # -------------------------------------------------------------------------
    def _generate_address_variants(self, address: str) -> List[str]:
        """Generate multiple address variants to improve geocoding success rate"""
        import re
        variants = []
        
        # Original address
        variants.append(address)
        
        # Remove unit numbers (e.g., "Units CL5, CL6, CL7")
        cleaned = re.sub(r'\s+Units?\s+[^,]+', '', address, flags=re.IGNORECASE)
        if cleaned != address and cleaned.strip():
            variants.append(cleaned.strip())
        
        # Remove postal codes (e.g., "M5X 1A9")
        cleaned2 = re.sub(r',?\s*[A-Z]\d[A-Z]\s*\d[A-Z]\d', '', address)
        if cleaned2 != address and cleaned2.strip():
            variants.append(cleaned2.strip())
        
        # Remove both units and postal codes
        cleaned3 = re.sub(r'\s+Units?\s+[^,]+', '', address, flags=re.IGNORECASE)
        cleaned3 = re.sub(r',?\s*[A-Z]\d[A-Z]\s*\d[A-Z]\d', '', cleaned3)
        if cleaned3 != address and cleaned3.strip():
            variants.append(cleaned3.strip())
        
        # Simple approach: remove everything after the first comma
        if ',' in address:
            street_only = address.split(',')[0].strip()
            variants.append(f"{street_only}, Toronto, Ontario, Canada")
        
        # Try with "West" instead of "W" in the cleaned version
        if ' W ' in cleaned:
            west_variant = cleaned.replace(' W ', ' West ')
            variants.append(west_variant)
        
        # Simple approach: remove everything after the first comma
        if ',' in address:
            street_only = address.split(',')[0].strip()
            variants.append(f"{street_only}, Toronto, Ontario, Canada")
        
        # Try with just street name and number (before any comma)
        street_match = re.match(r'(\d+\s+[^,]+)', address)
        if street_match:
            street_only = street_match.group(1)
            variants.append(f"{street_only}, Toronto, Ontario, Canada")
        
        # Add Toronto context to variants that don't have it
        for variant in variants[:]:  # Copy list to avoid modification during iteration
            if 'toronto' not in variant.lower():
                variants.append(f"{variant}, Toronto, Ontario, Canada")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variants = []
        for variant in variants:
            if variant not in seen:
                seen.add(variant)
                unique_variants.append(variant)
        
        logger.debug(f"Generated {len(unique_variants)} address variants for: {address}")
        return unique_variants

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
