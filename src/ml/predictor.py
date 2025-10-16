"""
Delay Prediction Model
Uses scikit-learn to predict TTC delays based on historical patterns
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DelayPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        self.model_path = "models/delay_predictor.pkl"
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Feature engineering for delay prediction
        """
        df = df.copy()
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_rush_hour'] = df['hour'].isin([7, 8, 17, 18]).astype(int)
        df['is_night'] = df['hour'].isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)
        
        # Route-specific features
        if 'route' in df.columns:
            df['route_numeric'] = df['route'].astype(str)
        
        # Weather features (mock for now)
        df['weather_factor'] = df.get('weather_factor', 1.0)
        
        # Previous delay features (rolling averages)
        if len(df) > 1:
            df['delay_rolling_avg'] = df['delay_minutes'].rolling(window=5, min_periods=1).mean()
            df['delay_rolling_std'] = df['delay_minutes'].rolling(window=5, min_periods=1).std()
        else:
            df['delay_rolling_avg'] = df['delay_minutes']
            df['delay_rolling_std'] = 0
        
        return df
    
    def train(self, df: pd.DataFrame):
        """
        Train the delay prediction model
        """
        if df.empty:
            logger.warning("No data available for training")
            return
        
        logger.info(f"Training delay predictor with {len(df)} records")
        
        # Prepare features
        df_processed = self.prepare_features(df)
        
        # Select features for training
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 'is_night',
            'weather_factor', 'delay_rolling_avg', 'delay_rolling_std'
        ]
        
        # Add route as categorical feature
        if 'route' in df_processed.columns:
            le_route = LabelEncoder()
            df_processed['route_encoded'] = le_route.fit_transform(df_processed['route'])
            self.label_encoders['route'] = le_route
            feature_columns.append('route_encoded')
        
        # Prepare training data
        X = df_processed[feature_columns].fillna(0)
        y = df_processed['delay_minutes']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.model.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"Model trained - MAE: {mae:.2f}, R²: {r2:.2f}")
        
        # Save model
        self.save_model()
        self.is_trained = True
        
        return {'mae': mae, 'r2': r2}
    
    def predict_delay(self, route: str, target_time: datetime) -> float:
        """
        Predict delay for a specific route at a given time
        """
        if not self.is_trained:
            logger.warning("Model not trained, returning default prediction")
            return 5.0  # Default prediction
        
        # Create feature vector
        features = {
            'hour': target_time.hour,
            'day_of_week': target_time.weekday(),
            'is_weekend': 1 if target_time.weekday() in [5, 6] else 0,
            'is_rush_hour': 1 if target_time.hour in [7, 8, 17, 18] else 0,
            'is_night': 1 if target_time.hour in [22, 23, 0, 1, 2, 3, 4, 5] else 0,
            'weather_factor': 1.0,  # Default weather
            'delay_rolling_avg': 5.0,  # Default historical average
            'delay_rolling_std': 2.0   # Default historical std
        }
        
        # Encode route if available
        if 'route' in self.label_encoders:
            try:
                features['route_encoded'] = self.label_encoders['route'].transform([route])[0]
            except ValueError:
                features['route_encoded'] = 0  # Unknown route
        else:
            features['route_encoded'] = 0
        
        # Convert to DataFrame and scale
        feature_df = pd.DataFrame([features])
        feature_scaled = self.scaler.transform(feature_df)
        
        # Make prediction
        prediction = self.model.predict(feature_scaled)[0]
        
        # Ensure non-negative prediction
        return max(0, prediction)
    
    def predict_batch(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict delays for a batch of records
        """
        if not self.is_trained:
            return np.full(len(df), 5.0)
        
        df_processed = self.prepare_features(df)
        
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend', 'is_rush_hour', 'is_night',
            'weather_factor', 'delay_rolling_avg', 'delay_rolling_std'
        ]
        
        if 'route_encoded' in df_processed.columns:
            feature_columns.append('route_encoded')
        
        X = df_processed[feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        predictions = self.model.predict(X_scaled)
        return np.maximum(0, predictions)  # Ensure non-negative
    
    def save_model(self):
        """
        Save trained model to disk
        """
        os.makedirs("models", exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """
        Load trained model from disk
        """
        if os.path.exists(self.model_path):
            model_data = joblib.load(self.model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.label_encoders = model_data['label_encoders']
            self.is_trained = model_data['is_trained']
            logger.info(f"Model loaded from {self.model_path}")
            return True
        return False

def main():
    """Test the delay predictor"""
    from data_collection.collector import TTCDataCollector
    
    # Load some test data
    collector = TTCDataCollector()
    test_delays = collector.fetch_ttc_delays()
    
    if test_delays:
        df = pd.DataFrame(test_delays)
        
        # Train predictor
        predictor = DelayPredictor()
        results = predictor.train(df)
        
        if results:
            print(f"Training completed - MAE: {results['mae']:.2f}, R²: {results['r2']:.2f}")
            
            # Test prediction
            next_hour = datetime.now() + timedelta(hours=1)
            prediction = predictor.predict_delay("501", next_hour)
            print(f"Predicted delay for Route 501 at {next_hour.strftime('%H:%M')}: {prediction:.1f} minutes")

if __name__ == "__main__":
    main()

