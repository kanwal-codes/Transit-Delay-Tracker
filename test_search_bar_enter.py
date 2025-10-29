#!/usr/bin/env python3
"""
Simulate pressing Enter in search bar with "130 King Street W Units CL5, CL6, CL7, Toronto, ON M5X 1A9"
"""
import sys
sys.path.insert(0, '/Users/kanwal/Projects/MapleMover')

from src.geocoding.service import GeocodingService
from src.api.ttc_client import TTCAPIClient

print("🔍 Simulating search bar: typing and pressing Enter")
print("=" * 70)
print()

# Simulate what happens when user types in search bar and presses Enter
address = "130 King Street W Units CL5, CL6, CL7, Toronto, ON M5X 1A9"
print(f"📝 User types: '{address}'")
print()

# This is what app.py does on line 101
geocoder = GeocodingService()
coords = geocoder.geocode_address(address)

if not coords:
    print("❌ Could not locate that address.")
    exit(1)

lat, lon = coords
print(f"✅ Geocoded to: ({lat}, {lon})")
print()

# Reverse geocode to see what was found
address_found = geocoder.reverse_geocode(lat, lon)
print(f"📍 Address found: {address_found}")
print()

# Check if this is downtown
downtown_king_lat = 43.647
downtown_king_lon = -79.385

if abs(lat - downtown_king_lat) < 0.01 and abs(lon - downtown_king_lon) < 0.01:
    print("✅ This is the CORRECT downtown Toronto location!")
    print()
    print("Now finding nearby transit...")
    print()
    
    # Get transit data (this is what happens next in the app)
    api = TTCAPIClient()
    transit_data = api.ttc_service.get_transit_data_for_location(lat, lon)
    
    print(f"🚌 Found {len(transit_data)} stops within 500m")
    print()
    print("Nearby transit (closest first):")
    for i, data in enumerate(transit_data[:5], 1):
        stop_name = data.get('stop_name', 'Unknown')
        distance = data.get('distance', 0)
        routes = data.get('routes', [])
        print(f"{i}. {stop_name} ({distance:.0f}m)")
        print(f"   Routes: {', '.join(routes)}")
        print()
        
else:
    print("❌ This is NOT downtown Toronto!")
    print(f"   Expected: (~43.647, -79.385)")
    print(f"   Got: ({lat}, {lon})")




