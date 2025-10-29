"""
Search bar that auto-populates with detected address (high-precision coords)
Clean rewrite to match Homepage design exactly
"""
import streamlit as st
import streamlit.components.v1 as components

class FormComponents:
    def render_search_interface(self):
        # Auto-detection disabled - now handled by location button only

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
        
        # Search input
        address = st.text_input(
            "Search Address",
            value=detected_address,
            placeholder="Enter an address and press Enter or click Search...",
            label_visibility="collapsed",
            key="search_input",
        )
        
        # Add JavaScript for Enter key detection
        st.markdown("""
        <script>
        (function() {
            const input = window.parent.document.querySelector('input[data-testid="stTextInput"] input');
            if (input) {
                input.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter' && input.value.trim()) {
                        // Trigger search button click
                        const searchBtn = window.parent.document.querySelector('button[kind="primary"]');
                        if (searchBtn) {
                            searchBtn.click();
                        }
                    }
                });
            }
        })();
        </script>
        """, unsafe_allow_html=True)

        # Global style to force same height on all buttons
        st.markdown("""
        <style>
        /* Force columns to align items to top */
        div[data-testid*="column"] {
            align-items: flex-start !important;
            vertical-align: top !important;
        }
        /* Force ALL buttons to same height and align to top */
        button[kind="primary"], button[kind="secondary"] {
            height: 5rem !important;
            min-height: 5rem !important;
            vertical-align: top !important;
            color: white !important;
        }
        /* Make hover effect consistent for all buttons */
        button:hover {
            background: linear-gradient(135deg, #2D5016, #4A7C59) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Two buttons side by side: Search (big) and Location (small)
        col1, col2 = st.columns([3, 1], gap="small")
        
        with col1:
            # Search button (main button, 3/4 width)
            if st.button("🔍 Search", use_container_width=True, key="search_btn", type="primary"):
                st.session_state.search_requested = True
                st.rerun()

        with col2:
            # Location button (small, with text)
            if st.button("Detect Location", use_container_width=True, key="location_btn", help="Use my current location"):
                st.session_state.location_requested = True
                st.rerun()

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