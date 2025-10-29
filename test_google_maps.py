#!/usr/bin/env python3
"""
Test Google Maps Geocoding API
Simple script to verify API key configuration
"""

import requests
import urllib.parse
import os

def test_google_maps_api():
    """Test Google Maps Geocoding API with the provided key"""
    
    # Your API key
    api_key = "AIzaSyCDtAo8wuWrB1f9J39vNBGq1N4vuln8jrY"
    
    # Test addresses
    test_addresses = [
        "130 King Street West, Toronto, ON",
        "Union Station, Toronto, ON",
        "Eaton Centre, Toronto, ON"
    ]
    
    print("🧪 Testing Google Maps Geocoding API")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    for address in test_addresses:
        print(f"📍 Testing: {address}")
        
        try:
            # Encode address for URL
            encoded = urllib.parse.quote(address)
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded}&key={api_key}"
            
            # Make request
            response = requests.get(url, timeout=10)
            data = response.json()
            
            # Check status
            status = data.get("status")
            print(f"   Status: {status}")
            
            if status == "OK" and data.get("results"):
                result = data["results"][0]
                location = result["geometry"]["location"]
                formatted = result.get("formatted_address", "N/A")
                print(f"   ✅ SUCCESS: ({location['lat']}, {location['lng']})")
                print(f"   📍 Formatted: {formatted}")
            elif status == "REQUEST_DENIED":
                print(f"   ❌ REQUEST_DENIED: {data.get('error_message', 'No error message')}")
                print("   💡 Check API key restrictions and enabled APIs")
            elif status == "ZERO_RESULTS":
                print(f"   ⚠️ ZERO_RESULTS: Address not found")
            else:
                print(f"   ❌ ERROR: {data.get('error_message', 'Unknown error')}")
                
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
        
        print()

if __name__ == "__main__":
    test_google_maps_api()



