# Real-Time vs Hardcoded Data

## ✅ YES - You CAN Use lat/lon → Address

The system **already does this**! Here's how:

### Reverse Geocoding (lat/lon → Address)
**Location**: `src/geocoding/service.py` line 69-94

```python
def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
    """Convert coordinates to readable address with caching."""
    
    # Check cache first (hardcoded/static)
    cache_key = f"reverse_geocode:{lat:.6f},{lon:.6f}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result  # ⚠️ RETURNING CACHED DATA
    
    # Real-time API call
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    address = data.get("display_name")
    
    # Cache for 1 hour
    cache.set(cache_key, address, ttl=3600)
    return address  # ✅ RETURNING REAL-TIME DATA
```

## 📊 Real-Time Data vs Hardcoded

### ✅ REAL-TIME (from APIs)
1. **GPS Location**: From user's browser (real-time)
2. **Address → Coordinates**: Google Maps API (real-time, cached 1 hour)
3. **Coordinates → Address**: OpenStreetMap (real-time, cached 1 hour)
4. **TTC Route Discovery**: NextBus API (real-time, cached on first load)
5. **Stop Locations**: NextBus API (real-time, cached on first load)
6. **Arrival Predictions**: NextBus API (real-time, updated every few seconds)
7. **Vehicle GPS Locations**: NextBus API (real-time, updates every few seconds)

### ⚠️ HARDCODED/CACHED
1. **Toronto Bounds**: Hardcoded in `geocoding/service.py` line 17-18
   ```python
   self.min_lat, self.max_lat = 43.60, 43.80
   self.min_lon, self.max_lon = -79.60, -79.20
   ```

2. **Addresses**: Cached for 1 hour (lines 88-89)
   ```python
   cache.set(cache_key, address, ttl=3600)  # 1 hour cache
   ```

3. **Route Discovery**: Cached until app restart
   ```python
   self.routes_cache = {}  # Cached in memory
   ```

4. **Stop ID → Route Mapping**: Cached until app restart
   ```python
   self.route_stops_cache = {}  # Cached in memory
   ```

## 🔄 Data Flow

### When User Searches "Spadina and College"
```
1. User types "Spadina and College"
   ↓ REAL-TIME: Google API geocode
2. Gets coordinates: (43.66, -79.40)
   ↓ CHECK CACHE: Cache exists? (1 hour TTL)
   ✅ Cache HIT → return cached coords
   ❌ Cache MISS → API call → cache result
   ↓
3. Reverse geocode to get readable address
   ↓ REAL-TIME: OpenStreetMap reverse geocode
4. Gets: "Spadina Avenue / College Street, Toronto, ON"
   ↓ CHECK CACHE: Cache exists? (1 hour TTL)
   ✅ Cache HIT → return cached address
   ❌ Cache MISS → API call → cache result
   ↓
5. Find nearby TTC stops
   ↓ REAL-TIME: NextBus API route discovery
6. Gets: "Spadina / College" stop with routes [506, 510]
   ↓ CHECK CACHE: Routes cached? (until restart)
   ✅ Cache HIT → use cached routes
   ❌ Cache MISS → discover all routes → cache results
   ↓
7. Get arrival predictions
   ↓ REAL-TIME: NextBus predictions API
8. Gets: "Route 506 arriving in 5 min (vehicle 1234)"
   ↓ REAL-TIME: NextBus vehicle locations API
9. Gets: "Vehicle 1234 at lat 43.6550, lon -79.4010"
   ↓ DISPLAY
10. Shows: "Route 506 at Spadina/College → 5 min"
    Location: Live GPS (lat, lon)
```

## 🎯 Summary

### What You Asked
> "If I have lat and lon, can I use Google API to get address? What is real-time and what is hardcoded?"

### Answer:
- ✅ **YES** - The system uses Google/OpenStreetMap API for reverse geocoding
- ✅ **REAL-TIME** - Address lookup happens live via API
- ⚠️ **CACHED** - Results cached for 1 hour
- ⚠️ **HARDCODED** - Toronto bounds only (geographic boundary)

### Real-Time vs Hardcoded Breakdown

| Component | Source | Cache Duration | Real-Time? |
|-----------|--------|----------------|-----------|
| User GPS location | Browser | None | ✅ Real-time |
| Address → Coords | Google API | 1 hour | ⚠️ Cached |
| Coords → Address | OpenStreetMap | 1 hour | ⚠️ Cached |
| Toronto bounds | Code (hardcoded) | Forever | ❌ Hardcoded |
| TTC Routes | NextBus API | Until restart | ⚠️ Cached |
| Stop locations | NextBus API | Until restart | ⚠️ Cached |
| Arrival times | NextBus API | 30 seconds | ✅ Real-time |
| Vehicle locations | NextBus API | None | ✅ Real-time |

### How It Works NOW

**Current Implementation:**
```python
# In geocoding/service.py

# REAL-TIME reverse geocoding
def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
    # Check cache (hardcoded/static)
    cache_key = f"reverse_geocode:{lat:.6f},{lon:.6f}"
    cached = cache.get(cache_key)
    if cached:
        return cached  # ⚠️ Using cached data
    
    # Make API call (real-time)
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}"
    response = requests.get(url)
    address = response.json().get("display_name")
    
    # Cache for 1 hour
    cache.set(cache_key, address, ttl=3600)
    return address  # ✅ Real-time address
```

**Usage:**
```python
# In app.py or anywhere else
geo = GeocodingService()
lat, lon = 43.6532, -79.3832
address = geo.reverse_geocode(lat, lon)
print(address)  # "Downtown Toronto, ON, Canada"
```



