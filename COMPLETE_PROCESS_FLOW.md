# Complete Process Flow - How Everything Works Now

## 🎯 What Happens When You Type an Address

### Example: User types "Spadina and College"

---

## 📍 STEP 1: User Input
```
User types: "Spadina and College"
```
**Location**: `src/ui/forms.py` - Search interface
**Code**:
```python
address = st.text_input(
    "Search Address",
    value=detected_address,
    placeholder="Search for a different address..."
)
```

---

## 🔄 STEP 2: Geocode Address → Coordinates

**File**: `src/app.py` (lines 131-142)  
**Function**: `GeocodingService.geocode_address()`

### Process:
1. **Check Cache First** (1 hour TTL)
   ```python
   cache_key = f"geocode:{address.strip().lower()}"
   cached_result = cache.get(cache_key)
   if cached_result:
       return cached_result  # Return cached lat/lon
   ```

2. **Try Google Maps API First**
   ```python
   if self.use_google_api:
       coords = self._query_google_maps(address)
       cache.set(cache_key, coords, ttl=3600)
       return coords  # (lat, lon)
   ```

3. **Fallback to OpenStreetMap**
   ```python
   address_variants = generate_address_variants(address)
   for variant in address_variants:
       coords = query_nominatim(variant)
       if coords:
           return coords
   ```

### Result:
```
Input: "Spadina and College"
Output: (43.6667, -79.4000)  # Coordinates
```

---

## ✅ STEP 3: Check Toronto Bounds

**File**: `src/geocoding/service.py` (lines 263-267)  
**Function**: `GeocodingService._is_toronto_area()`

### Process:
```python
# Check if coordinates are within Toronto
in_bounds = (
    self.min_lat <= lat <= self.max_lat and 
    self.min_lon <= lon <= self.max_lon
)

# Bounds: 43.60-43.80 lat, -79.60 to -79.20 lon
```

### Result:
- **If outside Toronto**: Show "🗺️ Now only available in Toronto"
- **If inside Toronto**: Continue to next step

---

## 🗺️ STEP 4: Reverse Geocode (Optional)

**File**: `src/app.py` (lines 120-125)  
**Function**: `GeocodingService.reverse_geocode()`

### Process:
```python
# Convert coordinates back to readable address
address = geo.reverse_geocode(lat, lon)
# Returns: "Spadina Avenue / College Street, Toronto, ON"

# Display it to user
st.session_state.search_address = address
```

### Result:
```
User sees: "📍 Spadina Avenue / College Street"
```

---

## 🚌 STEP 5: Find Transit Routes & Stops

**File**: `src/api/ttc_data_sources.py` (lines 228-264)  
**Function**: `UnifiedTTCService.get_transit_data_for_location()`

### Process A: Fast Mode (Default)
**File**: `src/api/dynamic_transit.py` (lines 278-339)

```python
def _get_transit_data_fast(self, lat, lon, radius_m):
    # 1. Get list of TTC routes (first 50 for speed)
    routes_data = requests.get("...routeList&a=ttc")
    routes = routes_data.get('route', [])[:50]
    
    # 2. For each route, get all stops
    for route in routes:
        route_config = requests.get("...routeConfig&a=ttc&r={tag}")
        stops = route_config.get('route', {}).get('stop', [])
        
        # 3. Filter stops within 500m
        for stop in stops:
            stop_lat = float(stop.get('lat'))
            stop_lon = float(stop.get('lon'))
            distance = calculate_distance(user_lat, user_lon, stop_lat, stop_lon)
            
            if distance * 1000 <= 500:  # Within 500m
                nearby_stops.append({
                    'stop_id': stop.get('stopId'),
                    'stop_name': stop.get('title'),
                    'lat': stop_lat,
                    'lon': stop_lon,
                    'distance': distance * 1000,
                    'routes': [route_tag]
                })
    
    # Sort by distance, take closest 10
    return sorted_stops[:10]
```

### Example Result:
```
Found nearby stops:
1. "Spadina / College" (120m, routes: [506, 510])
2. "College / Bathurst" (280m, routes: [506])
3. "Spadina / Dundas" (350m, routes: [510])
```

---

## ⏰ STEP 6: Get Real-Time Predictions

**File**: `src/api/dynamic_transit.py` (lines 185-251)  
**Function**: `NextBusTransitService.get_real_time_predictions()`

### Process:
```python
def get_real_time_predictions(self, stop_id, route_tags):
    # 1. Get ALL vehicle locations (real-time)
    vehicle_locations = self._get_all_vehicle_locations()
    # Returns: {vehicle_id: {lat, lon, heading, speed}}
    
    # 2. Get predictions for the stop
    url = "...command=predictions&stopId={stop_id}"
    data = requests.get(url)
    
    predictions = []
    for direction in data.get('direction', []):
        route_tag = direction.get('routeTag')
        route_title = direction.get('routeTitle')
        
        for pred in direction.get('prediction', []):
            vehicle_id = pred.get('vehicle')
            minutes = float(pred.get('minutes'))
            
            # 3. Get vehicle location from vehicle_locations map
            vehicle_lat = vehicle_locations[vehicle_id]['lat']
            vehicle_lon = vehicle_locations[vehicle_id]['lon']
            
            predictions.append({
                'route_tag': route_tag,
                'route_title': route_title,
                'arrival_minutes': minutes,
                'vehicle_id': vehicle_id,
                'vehicle_lat': vehicle_lat,  # Real GPS location
                'vehicle_lon': vehicle_lon   # Real GPS location
            })
    
    return predictions
```

### Example Result:
```json
[
  {
    "route_tag": "506",
    "route_title": "506-Carlton",
    "arrival_minutes": 5,
    "vehicle_id": "1234",
    "vehicle_lat": 43.6550,
    "vehicle_lon": -79.4010
  },
  {
    "route_tag": "510",
    "route_title": "510-Spadina", 
    "arrival_minutes": 12,
    "vehicle_id": "5678",
    "vehicle_lat": 43.6600,
    "vehicle_lon": -79.4050
  }
]
```

---

## 🎨 STEP 7: Display Results

**File**: `src/app.py` (lines 33-78)  
**Function**: `MapleMoverApp.find_transit()`

### Process:
```python
def find_transit(self, lat, lon):
    # Get transit data
    transit_data = api.ttc_service.get_transit_data_for_location(lat, lon)
    
    all_opts = []
    for data in transit_data:
        stop_name = data.get('stop_name')
        predictions = data.get('predictions', [])
        
        for pred in predictions[:3]:
            all_opts.append({
                'route_name': f"{pred['route_tag']} - {pred['route_title']}",
                'station_name': stop_name,
                'closest_arrival': f"{int(pred['arrival_minutes'])}",
                'vehicle_lat': pred['vehicle_lat'],
                'vehicle_lon': pred['vehicle_lon']
            })
    
    return {"transit_options": all_opts}
```

### Display:
**File**: `src/ui/transit.py` (lines 9-129)

```python
def render_transit_results(self, data):
    for opt in data["transit_options"]:
        # Display route card
        st.markdown(f"""
        <div style="background: gradient; padding: 1.5rem; border-radius: 12px">
            <h4>{opt['route_name']}</h4>
            <p>📍 {opt['station_name']}</p>
            <p>⏰ {opt['closest_arrival']} min</p>
        </div>
        """)
```

---

## 🗺️ STEP 8: Display Map

**File**: `src/ui/transit.py` (lines 130-235)  
**Function**: `TransitComponents.render_map()`

### Process:
```python
def render_map(self, lat, lon, data):
    # Create map points
    points = [{
        "Label": "📍 Your Location",
        "Lat": lat,
        "Lon": lon,
        "ColorGroup": "You",
        "Size": 15
    }]
    
    # Add station markers
    for opt in data["transit_options"]:
        points.append({
            "Label": f"🚌 {opt['station_name']}",
            "Lat": opt.get('vehicle_lat'),
            "Lon": opt.get('vehicle_lon'),
            "ColorGroup": "Stations"
        })
    
    # Create Plotly map
    fig = px.scatter_mapbox(points, lat="Lat", lon="Lon")
    st.plotly_chart(fig)
```

---

## 📊 Complete Data Flow Diagram

```
USER TYPES: "Spadina and College"
    ↓
[1] Geocode Service
    ├─ Check cache (1 hour)
    ├─ Google Maps API (if no cache)
    └─ Returns: (43.6667, -79.4000)
    ↓
[2] Toronto Validation
    ├─ Check: 43.60 ≤ lat ≤ 43.80
    └─ Check: -79.60 ≤ lon ≤ -79.20
    ↓ (PASS)
[3] Reverse Geocode
    ├─ OpenStreetMap API
    └─ Returns: "Spadina Avenue / College Street"
    ↓
[4] Find Transit Stops
    ├─ NextBus API: Get routes
    ├─ NextBus API: Get stops for each route
    ├─ Filter stops within 500m
    └─ Returns: ["Spadina / College", "College / Bathurst"]
    ↓
[5] Get Real-Time Predictions
    ├─ NextBus API: Get vehicle locations
    ├─ NextBus API: Get predictions for stops
    └─ Returns: [
          {route: "506", time: 5 min, vehicle: "1234", 
           lat: 43.6550, lon: -79.4010},
          {route: "510", time: 12 min, vehicle: "5678",
           lat: 43.6600, lon: -79.4050}
       ]
    ↓
[6] Display Results
    ├─ Show route cards
    ├─ Show arrival times
    ├─ Show vehicle locations
    └─ Show interactive map
    ↓
USER SEES:
┌────────────────────────────────────────┐
│ 🚌 Route 506 - Carlton              │
│ 📍 Spadina / College                 │
│ ⏰ 5 min                              │
│ 🚌 Route 510 - Spadina               │
│ 📍 Spadina / College                 │
│ ⏰ 12 min                             │
└────────────────────────────────────────┘
```

---

## 🔄 Real-Time Updates

### What Updates Every Few Seconds:
1. **Arrival Times**: "5 min" → "4 min" → "Arriving now"
2. **Vehicle Locations**: GPS position updates continuously
3. **Vehicle Speeds**: Current speed in km/h
4. **Vehicle Headings**: Direction (0-359°)

### What's Cached:
1. **Geocoded Coordinates**: 1 hour cache
2. **Route Discovery**: Until app restart
3. **Stop Locations**: Until app restart

---

## 🎯 Summary

**When you type an address:**

1. ✅ **Geocoding** (Google/OpenStreetMap) - Real-time or cached
2. ✅ **Toronto Validation** (Hardcoded bounds)
3. ✅ **Reverse Geocoding** (OpenStreetMap) - Shows readable address
4. ✅ **Route Discovery** (NextBus API) - Cached after first load
5. ✅ **Find Nearby Stops** (NextBus API) - Real-time
6. ✅ **Get Predictions** (NextBus API) - **REAL-TIME ⚡**
7. ✅ **Get Vehicle Locations** (NextBus API) - **REAL-TIME ⚡**
8. ✅ **Display Results** (Streamlit UI) - Shows all data with map

**All transit data (arrival times, vehicle locations, speeds) is REAL-TIME!** 🎉



