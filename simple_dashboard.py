"""
Simple TTC Transit App - Real-time Bus Tracking
A simplified version focusing on core transit features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import requests
import json

# Page configuration
st.set_page_config(
    page_title="TTC Transit Tracker",
    page_icon="🚌",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .bus-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .delay-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
    .on-time-badge {
        background-color: #51cf66;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚌 TTC Transit Tracker</h1>', unsafe_allow_html=True)
st.markdown("**Real-time bus tracking and delay predictions**")

# Sidebar
st.sidebar.title("🎛️ Controls")
st.sidebar.markdown("---")

# Location input
st.sidebar.subheader("📍 Your Location")
latitude = st.sidebar.number_input("Latitude", value=43.6532, format="%.4f")
longitude = st.sidebar.number_input("Longitude", value=-79.3832, format="%.4f")

# Route filter
st.sidebar.subheader("🚌 Route Filter")
selected_routes = st.sidebar.multiselect(
    "Select routes to track",
    ["501", "504", "505", "506", "510", "511", "512", "514", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
    default=["501", "504", "505"]
)

# Auto-refresh
auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh (30s)", value=True)
if auto_refresh:
    st.sidebar.markdown("⏱️ Last updated: " + datetime.now().strftime("%H:%M:%S"))

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ Live Bus Map")
    
    # Generate mock bus data around your location
    np.random.seed(42)
    n_buses = 15
    
    bus_data = []
    for i in range(n_buses):
        route = np.random.choice(selected_routes) if selected_routes else np.random.choice(["501", "504", "505"])
        
        # Generate bus position near your location
        lat_offset = np.random.normal(0, 0.01)  # ~1km radius
        lon_offset = np.random.normal(0, 0.01)
        
        bus_lat = latitude + lat_offset
        bus_lon = longitude + lon_offset
        
        # Generate delay
        delay = np.random.exponential(2) if np.random.random() < 0.3 else 0
        status = "Delayed" if delay > 2 else "On Time"
        
        bus_data.append({
            "route": route,
            "latitude": bus_lat,
            "longitude": bus_lon,
            "delay_minutes": round(delay, 1),
            "status": status,
            "direction": np.random.choice(["North", "South", "East", "West"]),
            "next_stop": f"Stop {np.random.randint(1000, 9999)}",
            "passengers": np.random.randint(5, 50),
            "speed": np.random.randint(15, 45)
        })
    
    # Create map
    df_buses = pd.DataFrame(bus_data)
    
    fig = px.scatter_mapbox(
        df_buses,
        lat="latitude",
        lon="longitude",
        color="route",
        size="delay_minutes",
        hover_data=["status", "direction", "next_stop", "passengers", "speed"],
        mapbox_style="open-street-map",
        zoom=12,
        height=500,
        title="Live Bus Positions"
    )
    
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=latitude, lon=longitude)
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Bus Status")
    
    # Show bus cards
    for _, bus in df_buses.iterrows():
        with st.container():
            st.markdown(f"""
            <div class="bus-card">
                <h4>🚌 Route {bus['route']}</h4>
                <p><strong>Status:</strong> 
                <span class="{'delay-badge' if bus['status'] == 'Delayed' else 'on-time-badge'}">
                {bus['status']}</span></p>
                <p><strong>Delay:</strong> {bus['delay_minutes']} min</p>
                <p><strong>Direction:</strong> {bus['direction']}</p>
                <p><strong>Next Stop:</strong> {bus['next_stop']}</p>
                <p><strong>Passengers:</strong> {bus['passengers']}</p>
                <p><strong>Speed:</strong> {bus['speed']} km/h</p>
            </div>
            """, unsafe_allow_html=True)

# Bottom section
st.markdown("---")
col3, col4, col5 = st.columns(3)

with col3:
    st.subheader("📈 Delay Statistics")
    delay_stats = df_buses.groupby('route')['delay_minutes'].agg(['mean', 'count']).round(1)
    st.dataframe(delay_stats)

with col4:
    st.subheader("🚨 Alerts")
    alerts = [
        "Route 501: 15 min delay due to construction",
        "Route 504: Service disruption at King St",
        "Route 505: Normal service resumed"
    ]
    for alert in alerts:
        st.warning(alert)

with col5:
    st.subheader("🔮 Predictions")
    st.info("Next hour predictions:")
    st.write("• Route 501: 5-8 min delays expected")
    st.write("• Route 504: Normal service")
    st.write("• Route 505: 2-4 min delays")

# Auto-refresh
if auto_refresh:
    st.rerun()

# Footer
st.markdown("---")
st.markdown("**TTC Transit Tracker** - Real-time bus monitoring with AI predictions")
