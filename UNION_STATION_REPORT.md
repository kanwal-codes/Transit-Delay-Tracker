# Union Station Transit Detection Report

## 🎯 Question
**What transit services are detected when searching for Union Station?**

## ❌ Current Status: NOT WORKING

### What We Found
1. **NextBus API doesn't have Union Station as a single stop**
2. **Multiple nearby stops detected instead:**
   - Bay St At Hagerman St
   - Bay St At Albert St
   - Bay St At Queen St West
   - Front St West At Bay St
   - etc.

3. **Subway routes (1, 2) don't list Union Station as a stop**

### Why It's Not Working

**Union Station is a MAJOR transit hub** with:
- Subway (Lines 1 & 2)
- GO Train
- UP Express
- Streetcar
- Bus

But NextBus API only has **TTC bus/streetcar data**. It doesn't include:
- Subway stops (lines 1 & 2)
- GO Transit
- UP Express

### What IS Being Detected

When searching near Union Station (43.6452, -79.3806), the system finds:

```
✅ Nearby Stops (within 500m):
- Bay St At Hagerman St (Route 19)
- Bay St At Albert St (Route 19)
- Bay St At Queen St West (Route 19)
- Front St West At Bay St (Route 19)
- etc.

❌ NOT Found:
- Union Station subway stops
- GO Transit stops
- UP Express stops
```

### Real-Time vs Hardcoded

| Component | Status | Source |
|-----------|--------|--------|
| **Bus/Streetcar routes** | ✅ Real-time | NextBus API |
| **Subway Lines 1 & 2** | ❌ Not included | NextBus API limitation |
| **GO Transit** | ❌ Not included | Different transit authority |
| **UP Express** | ❌ Not included | Different transit authority |

## 🔧 How to Fix

### Option 1: Add Special Union Station Handling
```python
# In src/app.py
if "union station" in search_query.lower():
    # Return predefined Union Station transit options
    return {
        "subway_line_1": "Union Station (Line 1)",
        "subway_line_2": "Union Station (Line 2)",
        "go_transit": "Union Station GO",
        "up_express": "Union Station UP Express",
        "streetcar": "Union Station Streetcar",
        "buses": nearby_bus_stops  # From NextBus
    }
```

### Option 2: Enhance with Multiple Transit APIs
```python
# Add multiple API sources
- NextBus (TTC buses/streetcars)
- TTC Subway API (separate)
- GO Transit API (separate)
- UP Express API (separate)
```

### Option 3: Use GTFS Data
Download TTC's GTFS feed which includes subway stop locations:

```python
# GTFS feed includes:
- subway stops (Union Station on Line 1, 2)
- bus/streetcar stops
- Exact coordinates
- Stop names
```

## 📊 Current Behavior

**When you search "Union Station":**
1. ✅ Geocoding works: Gets coordinates (43.6452, -79.3806)
2. ✅ Finds nearby bus/streetcar stops (~15 stops within 500m)
3. ❌ Doesn't include subway lines
4. ❌ Doesn't include GO/UP Express

**Real-time transit shown:**
- Bus routes near Union Station (Route 19, etc.)
- Arrival predictions (real-time from NextBus)
- Vehicle GPS locations (real-time from NextBus)

**Missing:**
- Subway arrival times
- GO Transit arrival times  
- UP Express arrival times

## ✅ Summary

**Your system IS working for:**
- ✅ Real-time bus arrivals near Union Station
- ✅ Real-time vehicle GPS locations
- ✅ Nearby street-level transit

**Your system is NOT showing:**
- ❌ Subway Lines 1 & 2 (Not in NextBus API)
- ❌ GO Transit (Different transit authority)
- ❌ UP Express (Different transit authority)

**To see full Union Station transit:** You need to add additional data sources beyond NextBus API.



