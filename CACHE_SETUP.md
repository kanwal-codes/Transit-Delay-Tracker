# Routes Cache Setup

## 🚀 Faster App Startup with Routes Cache

This app uses a persistent cache for TTC routes data to dramatically improve startup and search performance. Supports both Redis (production, multi-server) and disk (local/single-server) caching.

### ⚡ Performance Improvement

**Without cache:**
- First search: 20-30 seconds (discovers all 200+ routes)
- Subsequent searches: 20-30 seconds

**With cache:**
- First search: 2-5 seconds (loads from disk)
- Subsequent searches: 2-5 seconds

### 📋 Setup Instructions

#### Option A: Redis Cache (Recommended for Production)

For multi-server deployments or shared cache:

```bash
# Install Redis (if not installed)
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server

# Start Redis
redis-server

# Set environment variables (optional, defaults shown)
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=0

# Run cache setup script
python create_routes_cache.py
```

**Benefits:**
- Shared cache across multiple server instances
- Survives server restarts
- Fast access (~2-10ms)
- All users benefit from same cached data

#### Option B: Disk Cache (Local/Single Server)

For local development or single server:

```bash
# Just run the cache setup script
python create_routes_cache.py
```

**Benefits:**
- Fastest access (~0.001s)
- No external dependencies
- Works offline

#### 1. Pre-populate the cache (one-time setup)

Before deploying or running the app for the first time:

```bash
python create_routes_cache.py
```

This will:
- Fetch all 200+ TTC routes from NextBus API
- Download all stops for each route (~9,000 stops)
- Save to `cache/routes_cache.pkl` (~2.7 MB)
- Take 3-5 minutes on first run

#### 2. App will auto-load cache

The app automatically:
- ✅ Loads cache from disk on startup
- ✅ Uses cached data for fast searches
- ✅ Saves updated cache when routes change

### 🔄 Cache Management

**Cache location:**
- Binary: `cache/routes_cache.pkl` (fast loading)
- JSON: `cache/routes_cache.json` (human-readable backup)

**Cache age:**
- Cache is valid indefinitely (routes don't change often)
- To refresh: Delete cache files and re-run setup script

**To refresh cache:**
```bash
rm -rf cache/
python create_routes_cache.py
```

### 📊 What's Cached

- 209 TTC routes
- ~9,000 transit stops
- Route configurations
- Stop-to-route mappings

### 🎯 For Deployment

1. **Local Development:**
   - Run `create_routes_cache.py` once
   - App will be fast on subsequent runs

2. **Production Deployment:**
   - Option A: Pre-generate cache and include in deployment
   - Option B: Generate cache on first deployment (one-time slow start)

3. **Demo/Recruiter:**
   - Pre-generate cache before demo
   - Smooth, fast demo experience!

### 💡 Technical Details

**Cache implementation:**
- Uses Python pickle for fast serialization
- Stores RouteInfo and TransitStop objects
- Loads in-memory on app startup
- Memory footprint: ~50-100 MB

**Files modified:**
- `src/api/dynamic_transit.py` - Loads/saves cache
- `src/utils/routes_cache.py` - Cache utilities
- `create_routes_cache.py` - Cache generation script

**Ignored in git:**
- `cache/` directory
- `*.pkl` files

