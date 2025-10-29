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
with open('HOMEPAGE_REFERENCE_HTML.html', 'r') as f:
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

# Add location detection JavaScript at the end of the HTML
location_detection_js = """
<script>
(function() {
    // Only run if not already detected
    if (!document.getElementById('searchInput').value) {
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
                        document.getElementById('searchInput').value = address;
                        
                        // Store in parent window for Streamlit
                        if (window.parent && window.parent.postMessage) {
                            window.parent.postMessage({
                                type: 'location_detected',
                                address: address,
                                lat: lat,
                                lon: lon
                            }, '*');
                        }
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
})();
</script>
"""

# Append JavaScript to HTML
html_content = html_content.replace('</body>', location_detection_js + '</body>')

# Render the modified HTML
components.html(html_content, height=2000, scrolling=True)
