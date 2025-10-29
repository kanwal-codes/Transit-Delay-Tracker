"""
Clean UI Components
Main UI components without embedded CSS
"""

import streamlit as st
from src.ui.layouts import LayoutComponents
from src.ui.forms import FormComponents
from src.ui.transit import TransitComponents
from src.utils.cache import cache

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
    
    def render_featured_routes(self):
        """Render landing page with featured routes"""
        self.transit.render_featured_routes()

    # -------------------------------------------------------------------------
    # Message utilities (used across app.py)
    # -------------------------------------------------------------------------
    def render_error_message(self, message: str):
        """Render error message"""
        st.error(f"❌ {message}")

    def render_info_message(self, message: str):
        """Render info message"""
        st.info(f"ℹ️ {message}")

    def render_out_of_area_message(self):
        """Render a Material You styled, centered message for out-of-area notice."""
        st.markdown(
            """
            <div style="display:flex; justify-content:center; margin: 2rem 0;">
                <div style="
                    max-width: 720px;
                    width: 100%;
                    padding: 1.25rem 1.5rem;
                    border-radius: 16px;
                    background: linear-gradient(135deg, #eaddff 0%, #ffd8e4 100%);
                    border: 1px solid rgba(103, 80, 164, 0.25);
                    box-shadow: 0 6px 16px rgba(103, 80, 164, 0.18);
                    text-align: center;
                ">
                    <div style="color:#21005d; font-weight:800; font-size:1.5rem; line-height:1.3;">
                        Coming soon to your area!!
                    </div>
                    <div style="color:#21005d; font-weight:600; font-size:0.95rem; opacity:0.9; margin-top:0.25rem;">
                        Now only available in Toronto
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def render_success_message(self, message: str):
        """Render success message"""
        st.success(f"✅ {message}")

    def render_footer(self):
        """Render Homepage-style footer"""
        st.markdown("""
        <div style="margin-top: 4rem; padding: 2rem; border-top: 1px solid #e7e0ec; 
                    background: rgba(255, 255, 255, 0.5);">
            <div style="text-align: center;">
                <p style="font-size: 0.875rem; color: #49454f; margin: 0;">
                    © 2025 Maple Mover • Canadian Transit Information
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def render_performance_info(self):
        """Render performance and cache information"""
        cache_size = cache.size()
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F8FAFC, #F1F5F9); 
                    padding: 1.5rem; border-radius: 12px; border: 1px solid #E2E8F0; 
                    margin: 2rem 0; box-shadow: 0 2px 4px -1px rgba(0, 0, 0, 0.1);">
            <h4 style="color: #1F2937; margin-bottom: 1rem; font-weight: 600;">
                📊 System Performance & Features
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Create columns for better layout
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 8px; 
                        border: 1px solid #E5E7EB; margin-bottom: 1rem;">
                <h5 style="color: #374151; margin-bottom: 1rem; font-weight: 600;">
                    🚀 Performance Features
                </h5>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div style="padding: 0.75rem; background: #F0FDF4; border-radius: 6px; border-left: 3px solid #22C55E;">
                        <div style="font-weight: 600; color: #166534; font-size: 0.9rem;">⚡ Parallel Processing</div>
                        <div style="color: #6B7280; font-size: 0.8rem;">3x faster API calls</div>
                    </div>
                    <div style="padding: 0.75rem; background: #FEF3C7; border-radius: 6px; border-left: 3px solid #F59E0B;">
                        <div style="font-weight: 600; color: #92400E; font-size: 0.9rem;">💾 Smart Caching</div>
                        <div style="color: #6B7280; font-size: 0.8rem;">Geocoding: 1hr, TTC: 30s</div>
                    </div>
                    <div style="padding: 0.75rem; background: #EFF6FF; border-radius: 6px; border-left: 3px solid #3B82F6;">
                        <div style="font-weight: 600; color: #1E40AF; font-size: 0.9rem;">🔄 Retry Logic</div>
                        <div style="color: #6B7280; font-size: 0.8rem;">Exponential backoff</div>
                    </div>
                    <div style="padding: 0.75rem; background: #F3E8FF; border-radius: 6px; border-left: 3px solid #A855F7;">
                        <div style="font-weight: 600; color: #7C3AED; font-size: 0.9rem;">🛡️ Fallbacks</div>
                        <div style="color: #6B7280; font-size: 0.8rem;">Multiple data sources</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 8px; 
                        border: 1px solid #E5E7EB;">
                <h5 style="color: #374151; margin-bottom: 1rem; font-weight: 600;">
                    📡 Data Sources
                </h5>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                                background: #F0FDF4; border-radius: 4px;">
                        <span>🚌</span>
                        <span style="font-weight: 500; color: #166534;">NextBus API</span>
                        <span style="color: #6B7280; font-size: 0.85rem;">Real-time TTC data</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                                background: #FEF3C7; border-radius: 4px;">
                        <span>📋</span>
                        <span style="font-weight: 500; color: #92400E;">GTFS Static</span>
                        <span style="color: #6B7280; font-size: 0.85rem;">Scheduled routes</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                                background: #EFF6FF; border-radius: 4px;">
                        <span>🔗</span>
                        <span style="font-weight: 500; color: #1E40AF;">Third-party APIs</span>
                        <span style="color: #6B7280; font-size: 0.85rem;">Backup sources</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem; 
                                background: #F3E8FF; border-radius: 4px;">
                        <span>🎭</span>
                        <span style="font-weight: 500; color: #7C3AED;">Mock Data</span>
                        <span style="color: #6B7280; font-size: 0.85rem;">Fallback when APIs fail</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: white; padding: 1.5rem; border-radius: 8px; 
                        border: 1px solid #E5E7EB; margin-bottom: 1rem;">
                <h5 style="color: #374151; margin-bottom: 1rem; font-weight: 600;">
                    💾 Cache Status
                </h5>
                <div style="text-align: center; padding: 1rem;">
                    <div style="font-size: 2rem; font-weight: 700; color: #3B82F6;">
                        {cache_size}
                    </div>
                    <div style="color: #6B7280; font-size: 0.9rem;">
                        entries cached
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ Clear Cache", use_container_width=True):
                cache.clear()
                st.success("Cache cleared!")
                st.rerun()
