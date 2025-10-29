#!/usr/bin/env python3
"""
Check 121 King St W B132 with updated nearest-10 logic
"""
import sys
sys.path.insert(0, '/Users/kanwal/Projects/MapleMover')

from src.geocoding.service import GeocodingService
from src.api.ttc_client import TTCAPIClient

print("🔍 Checking: 121 King St W B132, Toronto, ON M5H 3T9")
print("=" * 70)

# Step 1: Geocode
geocoder = GeocodingService()
address = "121 King St W B132, Toronto, ON M5H 3T9"

print("1️⃣ Geocoding address...")
coords = geocoder.geocode_address(address)

if not coords:
    print("❌ Could not geocode")
    exit(1)

lat, lon = coords
print(f"✅ Coordinates: ({lat}, {lon})")

address_found = geocoder.reverse_geocode(lat, lon)
print(f"📍 Address: {address_found}")
print()

# Step 2: Find transit
api = TTCAPIClient()
print("2️⃣ Finding NEAREST 10 stops (sorted by distance)...")
print()

transit_data = api.ttc_service.get_transit_data_for_location(lat, lon)

print("=" * 70)
print(f"✅ Found {len(transit_data)} stops (closest first)")
print("=" * 70)
print()

# Show results
for i, data in enumerate(transit_data, 1):
    stop_name = data.get('stop_name', 'Unknown')
    distance = data.get('distance', 0)
    routes = data.get('routes', [])
    predictions = data.get('predictions', [])
    
    print(f"{i}. {stop_name}")
    print(f"   Distance: {distance:.0f}m")
    print(f"   Routes: {', '.join(routes[:3])}")
    
    if predictions:
        print(f"   ⏰ Predictions:")
        for pred in predictions[:2]:
            route = pred.get('route_tag', '')
            mins = pred.get('arrival_minutes', 0)
            print(f"      - Route {route}: {mins} min")
    else:
        print(f"   ⏰ (No predictions)")
    print()

print("=" * 70)
print("✅ These are the NEAREST 10 stops, sorted by distance!")




