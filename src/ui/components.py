"""
Clean UI Components
Main UI components without embedded CSS
"""

import streamlit as st
from src.ui.layouts import LayoutComponents
from src.ui.forms import FormComponents
from src.ui.transit import TransitComponents

class UIComponents:
    """Main UI components coordinator"""

    def __init__(self):
        self.layout = LayoutComponents()
        self.forms = FormComponents()
        self.transit = TransitComponents()

    # -------------------------------------------------------------------------
    # Page setup
    # -------------------------------------------------------------------------
    def setup_page(self):
        """Setup page configuration and load CSS"""
        self.layout.setup_page()

    # -------------------------------------------------------------------------
    # Header / Main Layout
    # -------------------------------------------------------------------------
    def render_header(self):
        """Render the main application header"""
        self.layout.render_header()

    # -------------------------------------------------------------------------
    # Search / Input Interface
    # -------------------------------------------------------------------------
    def render_search_interface(self):
        """Render the main search interface"""
        return self.forms.render_search_interface()

    # -------------------------------------------------------------------------
    # Transit / Results
    # -------------------------------------------------------------------------
    def render_transit_results(self, transit_data):
        """Render transit options results"""
        self.transit.render_transit_results(transit_data)

    def render_map(self, lat, lon, transit_data):
        """Render map with transit options"""
        self.transit.render_map(lat, lon, transit_data)

    # -------------------------------------------------------------------------
    # Message utilities (used across app.py)
    # -------------------------------------------------------------------------
    def render_error_message(self, message: str):
        """Render error message"""
        st.error(f"❌ {message}")

    def render_info_message(self, message: str):
        """Render info message"""
        st.info(f"ℹ️ {message}")

    def render_success_message(self, message: str):
        """Render success message"""
        st.success(f"✅ {message}")
