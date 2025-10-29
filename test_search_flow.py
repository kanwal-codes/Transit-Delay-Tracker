#!/usr/bin/env python3
"""
Simulate what happens when you put "130 King Street W Units CL5..." in the search bar
"""
import sys
sys.path.insert(0, '/Users/kanwal/Projects/MapleMover')

from src.geocoding.service import GeocodingService
from src.api.ttc_client import TTCAPIClient

print("🧪 Simulating what happens in the app when you search for:")
print("   '130 King Street W Units CL5, CL6, CL7, Toronto, ON M5X 1A9'")
print("=" * 70)
print()

# Step 1: Geocode (what app.py line 101 does)
print("1️⃣ Geocoding address...")
geocoder = GeocodingService()
address = "130 King Street W Units CL5, CL6, CL7, Toronto, ON M5X 1A9"

coords = geocoder.geocode_address(address)
if not coords:
    print("❌ Could not geocode address")
    exit(1)

lat, lon = coords
print(f"✅ Geocoded to: ({lat}, {lon})")

# Reverse geocode to see what address was found
address_found = geocoder.reverse_geocode(lat, lon)
print(f"📍 Address: {address_found}")
print()

# Step 2: Check if in Toronto (what app.py line 118 does)
print("2️⃣ Checking if in Toronto bounds...")
is_toronto = geocoder._is_toronto_area(lat, lon)
if not is_toronto:
    print("❌ NOT in Toronto - would show 'coming soon' message")
    exit(0)
print("✅ Within Toronto bounds")
print()

# Step 3: Find transit (what app.py line 123 does)
print("3️⃣ Finding nearby transit stops...")
api = TTCAPIClient()
transit_data = api.ttc_service.get_transit_data_for_location(lat, lon)

print(f"✅ Found {len(transit_data)} stops within 500m")
print()

# Step 4: Show results
print("4️⃣ Nearby transit stops (closest first):")
print("-" * 70)

if transit_data:
    for i, data in enumerate(transit_data[:10], 1):
        stop_name = data.get('stop_name', 'Unknown')
        distance = data.get('distance', 0)
        routes = data.get('routes', [])
        predictions = data.get('predictions', [])
        
        print(f"{i}. {stop_name}")
        print(f"   Distance: {distance:.0f}m")
        print(f"   Routes: {', '.join(routes)}")
        
        if predictions:
            print(f"   ⏰ Predictions:")
            for pred in predictions[:2]:
                route = pred.get('route_tag', '')
                mins = pred.get('arrival_minutes', 0)
                print(f"      - Route {route}: {mins} min")
        else:
            print(f"   ⏰ (No predictions available)")
        print()
else:
    print("No transit stops found")

print("=" * 70)
print("✅ This is what you would see in the browser!")




