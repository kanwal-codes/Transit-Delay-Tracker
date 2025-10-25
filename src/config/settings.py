"""
Configuration settings for Maple Mover
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class Settings:
    """Application configuration settings"""

    # API Configuration
    BASE_URL = "https://myttc.ca"
    API_RATE_LIMIT = 0.1  # seconds between requests
    REQUEST_TIMEOUT = 10  # seconds

    # Application Settings
    MAX_STATIONS = 3      # reduced for faster responses
    MAX_ARRIVALS = 3
    CACHE_TTL = 300       # 5-minute caching for geocoding + TTC data

    # Default Location (Downtown Toronto)
    DEFAULT_LAT = 43.6532
    DEFAULT_LON = -79.3832

    # Mapbox (optional)
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", None)

    # Logging Configuration
    LOG_LEVEL = "WARNING"

    # Streamlit Configuration
    PAGE_TITLE = "🍁 Maple Mover"
    PAGE_ICON = "🍁"
    PAGE_LAYOUT = "wide"
    SIDEBAR_STATE = "collapsed"
