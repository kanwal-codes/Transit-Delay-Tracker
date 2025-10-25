"""
Search bar that auto-populates with detected address (high-precision coords)
"""
import streamlit as st
import streamlit.components.v1 as components

class FormComponents:
    def render_search_interface(self):
        # Ask browser for geolocation and push it into the URL as query params.
        # IMPORTANT CHANGE: no rounding (no .toFixed()), so reverse geocoding is more accurate.
        components.html("""
        <script>
        (function() {
            // Only run once: if URL already has coords, don't ask again
            const url = new URL(window.parent.location);
            if (url.searchParams.get('user_lat') && url.searchParams.get('user_lon')) {
                return;
            }

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(pos) {
                        const lat = pos.coords.latitude;   // full precision
                        const lon = pos.coords.longitude;  // full precision
                        url.searchParams.set('user_lat', lat);
                        url.searchParams.set('user_lon', lon);
                        window.parent.location.replace(url.toString());
                    },
                    function(err) {
                        console.log("Geolocation error:", err);
                    },
                    {
                        enableHighAccuracy: true,
                        timeout: 15000,
                        maximumAge: 0
                    }
                );
            }
        })();
        </script>
        """, height=0)

        # UI: the "search bar" that shows the detected address
        st.markdown("### 🔍 Find Your Transit Options")

        detected_address = st.session_state.get("search_address", "")
        if detected_address:
            placeholder_text = "Detected current location"
        else:
            placeholder_text = "Detecting location..."

        address = st.text_input(
            "Search Address",
            value=detected_address,
            placeholder=placeholder_text,
            label_visibility="collapsed",
            key="search_input"
        )

        # Status line under the bar
        if detected_address:
            st.caption(f"📍 Current location: {detected_address}")
        else:
            st.caption("🌍 Waiting for GPS permission...")

        return address
