"""
Location service: reads live geolocation from browser via Streamlit query params
"""
import streamlit as st
import structlog
from typing import Tuple, Optional

logger = structlog.get_logger("maple_mover.location")

class LocationService:
    def get_user_location(self) -> Tuple[Optional[float], Optional[float], str]:
        # ✅ Updated to use the new Streamlit API
        params = st.query_params
        try:
            if "user_lat" in params and "user_lon" in params:
                lat = float(params["user_lat"][0] if isinstance(params["user_lat"], list) else params["user_lat"])
                lon = float(params["user_lon"][0] if isinstance(params["user_lon"], list) else params["user_lon"])
                st.session_state.user_lat = lat
                st.session_state.user_lon = lon
                return lat, lon, "browser_geolocation"
        except Exception as e:
            logger.warning(f"Invalid coordinates: {e}")

        lat = st.session_state.get("user_lat")
        lon = st.session_state.get("user_lon")
        if lat and lon:
            return lat, lon, "session_state"
        return None, None, "no_location"
