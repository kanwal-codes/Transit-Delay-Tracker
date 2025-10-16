"""
Anomaly Detection System
Identifies unusual delay patterns using Isolation Forest and statistical methods
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy import stats
import joblib
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = "models/anomaly_detector.pkl"
        self.threshold_zscore = 2.5  # Z-score threshold for anomalies
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for anomaly detection
        """
        df = df.copy()
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_rush_hour'] = df['hour'].isin([7, 8, 17, 18]).astype(int)
        
        # Delay-based features
        df['delay_minutes'] = df['delay_minutes'].fillna(0)
        
        # Route encoding (simple numeric encoding)
        if 'route' in df.columns:
            df['route_numeric'] = pd.Categorical(df['route']).codes
        
        return df
    
    def train(self, df: pd.DataFrame):
        """
        Train the anomaly detection model
        """
        if df.empty:
            logger.warning("No data available for anomaly detection training")
            return
        
        logger.info(f"Training anomaly detector with {len(df)} records")
        
        # Prepare features
        df_processed = self.prepare_features(df)
        
        # Select features for anomaly detection
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 
            'delay_minutes', 'route_numeric'
        ]
        
        X = df_processed[feature_columns].fillna(0)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Isolation Forest
        self.isolation_forest.fit(X_scaled)
        
        # Calculate baseline statistics for Z-score method
        self.baseline_mean = df['delay_minutes'].mean()
        self.baseline_std = df['delay_minutes'].std()
        
        # Save model
        self.save_model()
        self.is_trained = True
        
        logger.info("Anomaly detector trained successfully")
        
        return True
    
    def detect_anomalies(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Detect anomalies in delay data
        """
        if df.empty or not self.is_trained:
            return pd.DataFrame()
        
        df_processed = self.prepare_features(df)
        
        # Method 1: Isolation Forest
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 
            'delay_minutes', 'route_numeric'
        ]
        
        X = df_processed[feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict anomalies
        anomaly_scores = self.isolation_forest.decision_function(X_scaled)
        is_anomaly_if = self.isolation_forest.predict(X_scaled) == -1
        
        # Method 2: Z-score method
        z_scores = np.abs(stats.zscore(df['delay_minutes']))
        is_anomaly_zscore = z_scores > self.threshold_zscore
        
        # Method 3: Statistical outliers (IQR method)
        Q1 = df['delay_minutes'].quantile(0.25)
        Q3 = df['delay_minutes'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        is_anomaly_iqr = (df['delay_minutes'] < lower_bound) | (df['delay_minutes'] > upper_bound)
        
        # Combine methods (any method flags as anomaly)
        is_anomaly = is_anomaly_if | is_anomaly_zscore | is_anomaly_iqr
        
        # Add anomaly information to dataframe
        df_result = df.copy()
        df_result['is_anomaly'] = is_anomaly
        df_result['anomaly_score'] = anomaly_scores
        df_result['z_score'] = z_scores
        df_result['anomaly_type'] = 'Normal'
        
        # Classify anomaly types
        df_result.loc[is_anomaly_if, 'anomaly_type'] = 'Isolation Forest'
        df_result.loc[is_anomaly_zscore, 'anomaly_type'] = 'Statistical Outlier'
        df_result.loc[is_anomaly_iqr, 'anomaly_type'] = 'IQR Outlier'
        
        # Return only anomalies
        anomalies = df_result[df_result['is_anomaly']].copy()
        
        if not anomalies.empty:
            logger.info(f"Detected {len(anomalies)} anomalies")
        
        return anomalies
    
    def get_anomaly_summary(self, df: pd.DataFrame) -> dict:
        """
        Get summary statistics of anomalies
        """
        anomalies = self.detect_anomalies(df)
        
        if anomalies.empty:
            return {
                'total_anomalies': 0,
                'anomaly_rate': 0.0,
                'avg_anomaly_delay': 0.0,
                'max_anomaly_delay': 0.0,
                'anomaly_routes': []
            }
        
        summary = {
            'total_anomalies': len(anomalies),
            'anomaly_rate': len(anomalies) / len(df) * 100,
            'avg_anomaly_delay': anomalies['delay_minutes'].mean(),
            'max_anomaly_delay': anomalies['delay_minutes'].max(),
            'anomaly_routes': anomalies['route'].unique().tolist() if 'route' in anomalies.columns else []
        }
        
        return summary
    
    def save_model(self):
        """
        Save trained model to disk
        """
        os.makedirs("models", exist_ok=True)
        
        model_data = {
            'isolation_forest': self.isolation_forest,
            'scaler': self.scaler,
            'baseline_mean': self.baseline_mean,
            'baseline_std': self.baseline_std,
            'threshold_zscore': self.threshold_zscore,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Anomaly detector saved to {self.model_path}")
    
    def load_model(self):
        """
        Load trained model from disk
        """
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.isolation_forest = model_data['isolation_forest']
            self.scaler = model_data['scaler']
            self.baseline_mean = model_data['baseline_mean']
            self.baseline_std = model_data['baseline_std']
            self.threshold_zscore = model_data['threshold_zscore']
            self.is_trained = model_data['is_trained']
            logger.info(f"Anomaly detector loaded from {self.model_path}")
            return True
        return False

def main():
    """Test the anomaly detector"""
    from data_collection.collector import TTCDataCollector
    
    # Load some test data
    collector = TTCDataCollector()
    test_delays = collector.fetch_ttc_delays()
    
    if test_delays:
        df = pd.DataFrame(test_delays)
        
        # Train detector
        detector = AnomalyDetector()
        detector.train(df)
        
        # Detect anomalies
        anomalies = detector.detect_anomalies(df)
        
        if not anomalies.empty:
            print(f"Detected {len(anomalies)} anomalies:")
            print(anomalies[['route', 'delay_minutes', 'anomaly_type']].head())
        else:
            print("No anomalies detected")

if __name__ == "__main__":
    main()

