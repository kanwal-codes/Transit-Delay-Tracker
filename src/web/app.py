"""
TTC Delay Predictor - Streamlit Dashboard
Main web interface for the AI-powered transit delay tracker
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_collection.collector import TTCDataCollector
from utils.data_processor import TTCDataProcessor
from ml.predictor import DelayPredictor
from ml.anomaly_detector import AnomalyDetector
from utils.weather_integration import WeatherIntegration
from utils.nlp_processor import TTCQueryProcessor
from utils.error_handler import error_handler, data_validator, performance_monitor

# Page configuration
st.set_page_config(
    page_title="TTC Delay Predictor",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .prediction-box {
        background-color: #e8f4fd;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border: 2px solid #1f77b4;
        margin: 1rem 0;
    }
    .anomaly-alert {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_current_delays():
    """Load current delay data with caching"""
    collector = TTCDataCollector()
    delays = collector.fetch_ttc_delays()
    if delays:
        return pd.DataFrame(delays)
    return pd.DataFrame()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_historical_data():
    """Load historical data for ML training"""
    collector = TTCDataCollector()
    # Try to load existing historical data
    historical_files = [f for f in os.listdir('data') if f.startswith('historical_delays')]
    if historical_files:
        latest_file = max(historical_files)
        return collector.load_historical_data(latest_file)
    return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🚌 TTC Delay Predictor</h1>', unsafe_allow_html=True)
    st.markdown("### AI-Powered Transit Delay Prediction & Anomaly Detection")
    
    # Sidebar
    st.sidebar.title("🎛️ Controls")
    
    # Route selection
    route_options = ['All Routes', '501', '504', '505', '506', '509', '510', '511', '512']
    selected_route = st.sidebar.selectbox("Select Route", route_options)
    
    # Time range selection
    time_range = st.sidebar.selectbox("Time Range", ["Last Hour", "Last 4 Hours", "Last 24 Hours"])
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=True)
    
    # Natural Language Query Interface
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🤖 Ask Questions")
    
    query_text = st.sidebar.text_input(
        "Ask about delays:",
        placeholder="e.g., 'Which routes are delayed now?'"
    )
    
    if query_text:
        try:
            query_processor = TTCQueryProcessor()
            query_result = query_processor.process_query(query_text, current_delays)
            
            st.sidebar.markdown("**Response:**")
            st.sidebar.info(query_result['response'])
            st.sidebar.markdown(f"*Confidence: {query_result['confidence']:.2f}*")
            
            # Show suggested queries
            if st.sidebar.button("Show Suggestions"):
                suggestions = query_processor.get_suggested_queries()
                st.sidebar.markdown("**Try these:**")
                for suggestion in suggestions[:5]:
                    st.sidebar.markdown(f"• {suggestion}")
        except Exception as e:
            st.sidebar.error(f"Query processing error: {str(e)}")
    
    if auto_refresh:
        st.rerun()
    
    # Load data
    with st.spinner("Loading current delay data..."):
        current_delays = load_current_delays()
        historical_data = load_historical_data()
    
    if current_delays.empty:
        st.error("Unable to load delay data. Please check your connection.")
        return
    
    # Filter data based on selections
    if selected_route != 'All Routes':
        current_delays = current_delays[current_delays['route'] == selected_route]
    
    # Main dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        st.metric("Active Delays", len(current_delays))
    
    with col2:
        avg_delay = current_delays['delay_minutes'].mean() if not current_delays.empty else 0
        st.metric("Avg Delay", f"{avg_delay:.1f} min")
    
    with col3:
        max_delay = current_delays['delay_minutes'].max() if not current_delays.empty else 0
        st.metric("Max Delay", f"{max_delay:.1f} min")
    
    with col4:
        on_time_percentage = (current_delays['status'] == 'On Time').mean() * 100 if not current_delays.empty else 0
        st.metric("On-Time Rate", f"{on_time_percentage:.1f}%")
    
    # Charts section
    st.markdown("---")
    st.markdown("## 📊 Delay Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Delay distribution
        if not current_delays.empty:
            fig_hist = px.histogram(
                current_delays, 
                x='delay_minutes',
                title="Delay Distribution",
                labels={'delay_minutes': 'Delay (minutes)', 'count': 'Frequency'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Route comparison
        if not current_delays.empty:
            route_delays = current_delays.groupby('route')['delay_minutes'].mean().reset_index()
            fig_bar = px.bar(
                route_delays,
                x='route',
                y='delay_minutes',
                title="Average Delay by Route",
                labels={'delay_minutes': 'Avg Delay (minutes)', 'route': 'Route'},
                color='delay_minutes',
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # AI Predictions Section
    st.markdown("---")
    st.markdown("## 🤖 AI Predictions")
    
    if not historical_data.empty:
        # Initialize ML models
        predictor = DelayPredictor()
        anomaly_detector = AnomalyDetector()
        
        # Train models
        with st.spinner("Training AI models..."):
            predictor.train(historical_data)
            anomaly_detector.train(historical_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Next hour prediction
            st.markdown("### 🔮 Next Hour Prediction")
            
            if selected_route != 'All Routes':
                next_hour = datetime.now() + timedelta(hours=1)
                prediction = predictor.predict_delay(selected_route, next_hour)
                
                st.markdown(f"""
                <div class="prediction-box">
                    <h4>Route {selected_route}</h4>
                    <p><strong>Predicted Delay:</strong> {prediction:.1f} minutes</p>
                    <p><strong>Time:</strong> {next_hour.strftime('%H:%M')}</p>
                    <p><strong>Confidence:</strong> {'High' if prediction < 5 else 'Medium' if prediction < 10 else 'Low'}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Select a specific route to see predictions")
        
        with col2:
            # Anomaly detection
            st.markdown("### ⚠️ Anomaly Detection")
            
            anomalies = anomaly_detector.detect_anomalies(current_delays)
            
            if not anomalies.empty:
                st.markdown(f"""
                <div class="anomaly-alert">
                    <h4>🚨 {len(anomalies)} Anomalies Detected</h4>
                    <p>Unusual delay patterns detected in the system</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show anomaly details
                st.dataframe(anomalies[['route', 'delay_minutes', 'timestamp']].head())
            else:
                st.success("✅ No anomalies detected - delays are within normal patterns")
    
    else:
        st.warning("⚠️ Historical data not available. AI predictions require training data.")
        st.info("💡 Run the data collector to gather historical data for ML training")
    
    # Real-time data table
    st.markdown("---")
    st.markdown("## 📋 Current Delays")
    
    if not current_delays.empty:
        # Format timestamp for display
        display_delays = current_delays.copy()
        display_delays['timestamp'] = pd.to_datetime(display_delays['timestamp']).dt.strftime('%H:%M:%S')
        
        st.dataframe(
            display_delays[['route', 'direction', 'delay_minutes', 'status', 'stop_name', 'timestamp']],
            use_container_width=True
        )
    else:
        st.info("No delays found for the selected criteria")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; margin-top: 2rem;'>
        <p>🚌 TTC Delay Predictor | Built with Python, Streamlit & AI/ML</p>
        <p>Real-time data • Predictive analytics • Anomaly detection</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

