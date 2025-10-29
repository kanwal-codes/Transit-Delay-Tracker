"""
Search bar that auto-populates with detected address (high-precision coords)
Clean rewrite to match Homepage design exactly
"""
import streamlit as st
import streamlit.components.v1 as components

class FormComponents:
    def render_search_interface(self):
        # --- GEOLOCATION JS ---
        components.html("""
        <script>
        (function() {
            const url = new URL(window.parent.location);
            if (url.searchParams.get('user_lat') && url.searchParams.get('user_lon')) return;
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        url.searchParams.set('user_lat', pos.coords.latitude);
                        url.searchParams.set('user_lon', pos.coords.longitude);
                        window.parent.location.replace(url.toString());
                    },
                    function(err) { console.log("Geolocation error:", err); },
                    { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
                );
            }
        })();
        </script>
        """, height=0)

        # --- PAGE TITLE (matching Homepage) ---
        st.markdown("""
        <div style="text-align:center; margin-bottom:1.5rem;">
            <h2 style="font-size:3rem; color:#1c1b1f; font-weight:800; margin:0;">Find Your Route</h2>
            <p style="font-size:1.25rem; color:#49454f; margin:0;">
                Real-time transit information across Canada
            </p>
        </div>
        """, unsafe_allow_html=True)

        detected_address = st.session_state.get("search_address", "")
        
        # --- WRAP ENTIRE SECTION IN CONTAINER ---
        st.markdown("""
        <div class="search-container">
        <div style="width: 100%; max-width: 28rem; margin: 0 auto;">
        """, unsafe_allow_html=True)
        
        # Search input
        address = st.text_input(
            "Search Address",
            value=detected_address,
            placeholder="Search for routes, stops, or destinations...",
            label_visibility="collapsed",
            key="search_input",
        )

        # Location button
        if st.button("Use My Location", use_container_width=True, key="location_btn"):
            st.session_state.location_requested = True
            st.rerun()
        
        st.markdown("</div></div>", unsafe_allow_html=True)

        # --- CURRENT LOCATION LABEL ---
        if detected_address:
            st.markdown(f"""
            <div style="margin-top:0.5rem; padding:0.5rem; background:#F0F9FF; border-radius:8px; border:1px solid #BAE6FD; max-width:42rem; margin-left:auto; margin-right:auto;">
                <span style="color:#0369A1; font-size:0.9rem;">
                    📍 <strong>Current Location:</strong> {detected_address}
                </span>
            </div>
            """, unsafe_allow_html=True)

        return address