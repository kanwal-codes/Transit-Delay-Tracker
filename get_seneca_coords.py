#!/usr/bin/env python3
"""
Get correct coordinates for Seneca College Newnham Campus
"""
import requests
from src.geocoding.service import GeocodingService

print("🔍 Getting correct coordinates for Seneca College Newnham Campus...")
print("=" * 60)

geocoder = GeocodingService()

# Try different variations
queries = [
    "Seneca College Newnham Campus Toronto",
    "1750 Finch Avenue East Toronto",
    "Seneca College Toronto"
]

for query in queries:
    print(f"\nTrying: {query}")
    coords = geocoder.geocode_address(query)
    if coords:
        lat, lon = coords
        print(f"✅ Found: {query}")
        print(f"   Coordinates: ({lat}, {lon})")
        
        # Get formatted address from reverse geocode
        address = geocoder.reverse_geocode(lat, lon)
        print(f"   Address: {address}")
        break
else:
    print("❌ Could not geocode Seneca College")




