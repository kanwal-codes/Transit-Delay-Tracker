# File: src/utils/geo_utils.py
"""
Geographic utility functions
Shared distance and bounds utilities
"""

import math
from typing import Tuple

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat/2) * math.sin(dlat/2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon/2) * math.sin(dlon/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def is_within_toronto_bounds(lat: float, lon: float) -> bool:
    """
    Check if coordinates are within Toronto proper (excluding GTA suburbs)
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if coordinates are in Toronto proper
    """
    # Toronto proper bounds (excluding all GTA suburbs)
    min_lat, max_lat = 43.60, 43.80  # Toronto proper latitude range (more restrictive)
    min_lon, max_lon = -79.60, -79.20  # Toronto proper longitude range (more restrictive)
    
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon

def format_distance(distance_km: float) -> str:
    """
    Format distance for display
    
    Args:
        distance_km: Distance in kilometers
        
    Returns:
        Formatted distance string
    """
    if distance_km < 1:
        return f"{distance_km * 1000:.0f}m"
    else:
        return f"{distance_km:.1f}km"

def get_toronto_center() -> Tuple[float, float]:
    """
    Get Toronto city center coordinates
    
    Returns:
        Tuple of (latitude, longitude)
    """
    return (43.6532, -79.3832)
