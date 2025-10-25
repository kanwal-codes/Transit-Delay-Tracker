"""
Main Maple Mover app — restrict TTC routes to Toronto only
"""

import streamlit as st
import structlog
import time
from src.api.ttc_client import TTCAPIClient
from src.geocoding.service import GeocodingService
from src.services.location import LocationService
from src.ui.components import UIComponents

logger = structlog.get_logger("maple_mover.app")

class MapleMoverApp:
    def __init__(self):
        self.api = TTCAPIClient()
        self.geo = GeocodingService()
        self.loc = LocationService()
        self.ui = UIComponents()

    def find_transit(self, lat, lon):
        """Find nearby TTC transit stations around a Toronto coordinate."""
        stations = self.api.find_nearest_stations(lat, lon)
        all_opts = []
        for sid, slat, slon, _ in stations:
            time.sleep(0.2)
            data = self.api.fetch_station_data(sid)
            if data:
                opts = self.api.extract_transit_options(data, sid.replace("_", " ").title())
                all_opts.extend(opts)
        all_opts.sort(key=lambda x: x["closest_arrival"])
        return {"transit_options": all_opts}

    def run(self):
        self.ui.setup_page()
        self.ui.render_header()

        # Step 1: detect location
        lat, lon, source = self.loc.get_user_location()

        # Step 2: reverse-geocode to full address if available
        if lat and lon:
            addr = self.geo.reverse_geocode(lat, lon)
            if addr:
                st.session_state.search_address = addr
                st.session_state.location_source = source

        # Step 3: show the search bar always
        address = self.ui.render_search_interface()

        # Step 4: handle manual input / override
        if address and address.strip():
            coords = self.geo.geocode_address(address)
            if coords:
                lat, lon = coords
                st.session_state.user_lat = lat
                st.session_state.user_lon = lon
                st.session_state.search_address = address
                st.session_state.location_source = "manual"
            else:
                self.ui.render_error_message("❌ Could not locate that address.")
                return

        # Step 5: if no location detected yet
        if not lat or not lon:
            self.ui.render_info_message("🌍 Detecting your location... Please allow GPS access.")
            return

        # ✅ Step 6: check Toronto boundaries BEFORE any TTC calls
        if not self.geo._is_toronto_area(lat, lon):
            self.ui.render_info_message("🗺️ Now only available in Toronto — coming soon to your area!")
            return  # ❗ stop here, do NOT call TTC API

        # Step 7: in Toronto → fetch TTC routes
        data = self.find_transit(lat, lon)

        # Step 8: render results + map
        if not data["transit_options"]:
            self.ui.render_info_message("No TTC routes found nearby.")
        else:
            self.ui.render_transit_results(data)
            self.ui.render_map(lat, lon, data)


if __name__ == "__main__":
    MapleMoverApp().run()
