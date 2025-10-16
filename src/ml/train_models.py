"""
Training Script for TTC Delay Predictor
Trains ML models and saves them for use in the web application
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_collection.collector import TTCDataCollector
from ml.predictor import DelayPredictor
from ml.anomaly_detector import AnomalyDetector

def generate_synthetic_training_data():
    """
    Generate synthetic training data if no real data is available
    """
    print("Generating synthetic training data...")
    
    # Create realistic delay patterns
    np.random.seed(42)
    n_records = 1000
    
    routes = ['501', '504', '505', '506', '509', '510', '511', '512']
    directions = ['Eastbound', 'Westbound', 'Northbound', 'Southbound']
    
    data = []
    base_time = datetime.now() - timedelta(days=30)
    
    for i in range(n_records):
        # Time progression
        timestamp = base_time + timedelta(hours=i*0.5)
        
        # Route selection
        route = np.random.choice(routes)
        direction = np.random.choice(directions)
        
        # Time-based delay patterns
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Base delay varies by time of day
        if hour in [7, 8, 17, 18]:  # Rush hours
            base_delay = np.random.normal(8, 3)
        elif hour in [22, 23, 0, 1, 2, 3, 4, 5]:  # Night
            base_delay = np.random.normal(2, 1)
        else:  # Regular hours
            base_delay = np.random.normal(4, 2)
        
        # Weekend effect
        if day_of_week in [5, 6]:  # Weekend
            base_delay *= 0.8
        
        # Route-specific patterns
        route_multipliers = {
            '501': 1.2,  # Queen St - busier
            '504': 1.1,  # King St - busy
            '505': 0.9,  # Dundas - moderate
            '506': 1.0,  # Carlton - average
            '509': 0.8,  # Harbourfront - less busy
            '510': 0.9,  # Spadina - moderate
            '511': 0.7,  # Bathurst - less busy
            '512': 0.8   # St Clair - moderate
        }
        
        base_delay *= route_multipliers.get(route, 1.0)
        
        # Add some randomness and ensure non-negative
        delay_minutes = max(0, base_delay + np.random.normal(0, 1))
        
        # Status based on delay
        if delay_minutes < 2:
            status = 'On Time'
        elif delay_minutes < 5:
            status = 'Slight Delay'
        else:
            status = 'Delayed'
        
        record = {
            'timestamp': timestamp.isoformat(),
            'route': route,
            'direction': direction,
            'delay_minutes': round(delay_minutes, 1),
            'stop_id': f"stop_{np.random.randint(1000, 9999)}",
            'stop_name': f"Stop {np.random.randint(1, 100)}",
            'vehicle_id': f"vehicle_{np.random.randint(10000, 99999)}",
            'status': status,
            'weather_factor': np.random.uniform(0.8, 1.2),
            'day_of_week': day_of_week,
            'hour': hour
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def main():
    """
    Main training function
    """
    print("🚌 TTC Delay Predictor - Model Training")
    print("=" * 50)
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    
    # Try to load real data first
    collector = TTCDataCollector()
    historical_files = [f for f in os.listdir('data') if f.startswith('historical_delays')] if os.path.exists('data') else []
    
    if historical_files:
        print("Loading historical data...")
        latest_file = max(historical_files)
        df = collector.load_historical_data(latest_file)
        print(f"Loaded {len(df)} historical records")
    else:
        print("No historical data found, generating synthetic data...")
        df = generate_synthetic_training_data()
        
        # Save synthetic data for future use
        os.makedirs("data", exist_ok=True)
        synthetic_filename = f"data/synthetic_training_data_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(synthetic_filename, index=False)
        print(f"Synthetic data saved to {synthetic_filename}")
    
    if df.empty:
        print("❌ No training data available!")
        return
    
    print(f"📊 Training with {len(df)} records")
    print(f"📅 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"🚌 Routes: {df['route'].nunique()} unique routes")
    print(f"⏱️  Average delay: {df['delay_minutes'].mean():.1f} minutes")
    
    # Train Delay Predictor
    print("\n🤖 Training Delay Predictor...")
    predictor = DelayPredictor()
    predictor_results = predictor.train(df)
    
    if predictor_results:
        print(f"✅ Delay Predictor trained successfully!")
        print(f"   📈 Mean Absolute Error: {predictor_results['mae']:.2f} minutes")
        print(f"   📊 R² Score: {predictor_results['r2']:.2f}")
    
    # Train Anomaly Detector
    print("\n⚠️  Training Anomaly Detector...")
    detector = AnomalyDetector()
    detector.train(df)
    
    # Test anomaly detection
    anomalies = detector.detect_anomalies(df)
    anomaly_summary = detector.get_anomaly_summary(df)
    
    print(f"✅ Anomaly Detector trained successfully!")
    print(f"   🚨 Detected {anomaly_summary['total_anomalies']} anomalies in training data")
    print(f"   📊 Anomaly rate: {anomaly_summary['anomaly_rate']:.1f}%")
    
    # Test predictions
    print("\n🔮 Testing predictions...")
    test_routes = ['501', '504', '505']
    next_hour = datetime.now() + timedelta(hours=1)
    
    for route in test_routes:
        prediction = predictor.predict_delay(route, next_hour)
        print(f"   Route {route} at {next_hour.strftime('%H:%M')}: {prediction:.1f} min delay")
    
    print("\n🎉 Training completed successfully!")
    print("📁 Models saved to 'models/' directory")
    print("🚀 Ready to run the Streamlit dashboard!")

if __name__ == "__main__":
    main()

