"""
Homepage Reference for Streamlit - Shows Homepage folder styling with location detection
"""
import streamlit as st
import streamlit.components.v1 as components

# Page config
st.set_page_config(
    page_title="Maple Mover - Homepage",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Check if user wants to navigate to transit page
if 'navigate_to_transit' in st.session_state and st.session_state.navigate_to_transit:
    st.switch_page("pages/2_Transit.py")

# Hide Streamlit elements
hide_streamlit = """
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp > header {height: 0; padding: 0;}
    .block-container {padding-top: 0;}
</style>
"""
st.markdown(hide_streamlit, unsafe_allow_html=True)

# Get detected address from session state (if exists)
detected_address = st.session_state.get("search_address", "")

# Read HTML content
import os
html_path = os.path.join(os.path.dirname(__file__), '..', 'HOMEPAGE_REFERENCE_HTML.html')
with open(html_path, 'r') as f:
    html_content = f.read()

# Inject the detected address into the search input
if detected_address:
    # Replace the input value with the detected address
    html_content = html_content.replace(
        '<input \n                    id="searchInput"\n                    type="text"',
        f'<input \n                    id="searchInput"\n                    type="text"\n                    value="{detected_address}"'
    )
    # Also add a visual indicator that location was detected
    html_content = html_content.replace(
        '            </button>\n        </div>\n    </section>',
        f'''            </button>
            
            <!-- Location Detected Indicator -->
            <div style="margin-top: 1rem; padding: 0.75rem; background: #F0F9FF; border-radius: 8px; border: 1px solid #BAE6FD; max-width: 28rem; margin-left: auto; margin-right: auto;">
                <span style="color: #0369A1; font-size: 0.9rem;">
                    📍 <strong>Current Location:</strong> {detected_address}
                </span>
            </div>
        </div>
    </section>'''
    )

# Add location detection and navigation JavaScript
location_detection_js = """
<script>
(function() {
    const searchInput = document.getElementById('searchInput');
    
    // Location detection
    if (!searchInput.value) {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                async function(pos) {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    
                    // Reverse geocode using Nominatim
                    try {
                        const response = await fetch(
                            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`,
                            { headers: { 'User-Agent': 'MapleMover/1.0' } }
                        );
                        const data = await response.json();
                        const address = data.display_name || '';
                        
                        // Populate search input
                        searchInput.value = address;
                    } catch (err) {
                        console.log("Reverse geocoding error:", err);
                    }
                },
                function(err) {
                    console.log("Geolocation error:", err);
                },
                { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
            );
        }
    }
    
    // Navigation: When user clicks on search or starts typing
    let navigateTimeout;
    searchInput.addEventListener('focus', function() {
        // When focused, navigate after a short delay
        navigateTimeout = setTimeout(function() {
            navigateToTransit();
        }, 300);
    });
    
    searchInput.addEventListener('keydown', function(e) {
        // On Enter key, navigate immediately
        if (e.key === 'Enter') {
            e.preventDefault();
            clearTimeout(navigateTimeout);
            navigateToTransit();
        }
        // On any key press, navigate after delay
        else {
            clearTimeout(navigateTimeout);
            navigateTimeout = setTimeout(function() {
                navigateToTransit();
            }, 500);
        }
    });
    
    function navigateToTransit() {
        const address = searchInput.value || '';
        // Use postMessage to tell parent to navigate
        if (window.parent && window.parent.postMessage) {
            window.parent.postMessage({
                type: 'navigate_to_transit',
                search_query: address
            }, '*');
        }
    }
})();
</script>
"""

# Append JavaScript to HTML
html_content = html_content.replace('</body>', location_detection_js + '</body>')

# Add message listener for navigation
navigation_listener = """
<script>
window.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'navigate_to_transit') {
        // Store search query in session storage
        if (event.data.search_query) {
            sessionStorage.setItem('search_query', event.data.search_query);
        }
    }
});
</script>
"""
html_content = html_content.replace('</body>', navigation_listener + '</body>')

# Render the modified HTML
components.html(html_content, height=2000, scrolling=True)

# Add a button below the embedded HTML for navigation
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🚀 Search Transit Routes", use_container_width=True, type="primary"):
        st.session_state.navigate_to_transit = True
        st.rerun()
