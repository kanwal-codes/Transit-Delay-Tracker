"""
Data Processing Pipeline
Comprehensive data cleaning, feature engineering, and preprocessing for TTC delay data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class TTCDataProcessor:
    def __init__(self):
        self.feature_columns = []
        self.scalers = {}
        self.encoders = {}
        self.is_fitted = False
        
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate TTC delay data
        """
        logger.info(f"Cleaning {len(df)} records")
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Convert timestamp to datetime
        if 'timestamp' in df_clean.columns:
            df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], errors='coerce')
        
        # Handle missing values
        df_clean = self._handle_missing_values(df_clean)
        
        # Remove outliers
        df_clean = self._remove_outliers(df_clean)
        
        # Validate data ranges
        df_clean = self._validate_ranges(df_clean)
        
        # Add derived features
        df_clean = self._add_derived_features(df_clean)
        
        logger.info(f"Cleaned data: {len(df_clean)} records remaining")
        return df_clean
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset"""
        
        # Fill missing delays with median
        if 'delay_minutes' in df.columns:
            median_delay = df['delay_minutes'].median()
            df['delay_minutes'] = df['delay_minutes'].fillna(median_delay)
        
        # Fill missing routes with 'Unknown'
        if 'route' in df.columns:
            df['route'] = df['route'].fillna('Unknown')
        
        # Fill missing directions with 'Unknown'
        if 'direction' in df.columns:
            df['direction'] = df['direction'].fillna('Unknown')
        
        # Fill missing status with 'Unknown'
        if 'status' in df.columns:
            df['status'] = df['status'].fillna('Unknown')
        
        # Fill missing weather factor with 1.0 (neutral)
        if 'weather_factor' in df.columns:
            df['weather_factor'] = df['weather_factor'].fillna(1.0)
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove extreme outliers from delay data"""
        
        if 'delay_minutes' not in df.columns:
            return df
        
        # Use IQR method to remove outliers
        Q1 = df['delay_minutes'].quantile(0.25)
        Q3 = df['delay_minutes'].quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier bounds (more lenient than standard 1.5*IQR)
        lower_bound = Q1 - 3 * IQR
        upper_bound = Q3 + 3 * IQR
        
        # Remove outliers
        initial_count = len(df)
        df = df[(df['delay_minutes'] >= lower_bound) & (df['delay_minutes'] <= upper_bound)]
        removed_count = initial_count - len(df)
        
        if removed_count > 0:
            logger.info(f"Removed {removed_count} outliers from delay data")
        
        return df
    
    def _validate_ranges(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and correct data ranges"""
        
        # Ensure delays are non-negative
        if 'delay_minutes' in df.columns:
            df['delay_minutes'] = df['delay_minutes'].clip(lower=0)
        
        # Ensure weather factor is reasonable
        if 'weather_factor' in df.columns:
            df['weather_factor'] = df['weather_factor'].clip(lower=0.1, upper=3.0)
        
        # Ensure hour is valid
        if 'hour' in df.columns:
            df['hour'] = df['hour'].clip(lower=0, upper=23)
        
        # Ensure day of week is valid
        if 'day_of_week' in df.columns:
            df['day_of_week'] = df['day_of_week'].clip(lower=0, upper=6)
        
        return df
    
    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features for better ML performance"""
        
        if 'timestamp' not in df.columns:
            return df
        
        # Time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['year'] = df['timestamp'].dt.year
        
        # Categorical time features
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_rush_hour'] = df['hour'].isin([7, 8, 17, 18]).astype(int)
        df['is_night'] = df['hour'].isin([22, 23, 0, 1, 2, 3, 4, 5]).astype(int)
        df['is_morning'] = df['hour'].isin([6, 7, 8, 9]).astype(int)
        df['is_evening'] = df['hour'].isin([17, 18, 19, 20]).astype(int)
        
        # Cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        # Route-specific features
        if 'route' in df.columns:
            df['route_length'] = df['route'].str.len()  # Simple route complexity
            df['is_express'] = df['route'].str.contains('E|X').astype(int)
        
        # Delay-based features
        if 'delay_minutes' in df.columns:
            df['delay_category'] = pd.cut(
                df['delay_minutes'], 
                bins=[0, 2, 5, 10, float('inf')], 
                labels=['On Time', 'Slight Delay', 'Moderate Delay', 'Major Delay']
            )
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Comprehensive feature engineering for ML models
        """
        logger.info("Engineering features for ML models")
        
        df_features = df.copy()
        
        # Add rolling statistics
        df_features = self._add_rolling_features(df_features)
        
        # Add lag features
        df_features = self._add_lag_features(df_features)
        
        # Add interaction features
        df_features = self._add_interaction_features(df_features)
        
        # Add route-specific patterns
        df_features = self._add_route_patterns(df_features)
        
        return df_features
    
    def _add_rolling_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add rolling window statistics"""
        
        if 'delay_minutes' not in df.columns:
            return df
        
        # Sort by timestamp for rolling calculations
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        # Rolling statistics for delays
        window_sizes = [5, 10, 30]  # Different window sizes
        
        for window in window_sizes:
            df[f'delay_rolling_mean_{window}'] = df['delay_minutes'].rolling(window=window, min_periods=1).mean()
            df[f'delay_rolling_std_{window}'] = df['delay_minutes'].rolling(window=window, min_periods=1).std()
            df[f'delay_rolling_max_{window}'] = df['delay_minutes'].rolling(window=window, min_periods=1).max()
            df[f'delay_rolling_min_{window}'] = df['delay_minutes'].rolling(window=window, min_periods=1).min()
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features"""
        
        if 'delay_minutes' not in df.columns:
            return df
        
        # Lag features for delays
        lag_periods = [1, 2, 3, 5]  # Different lag periods
        
        for lag in lag_periods:
            df[f'delay_lag_{lag}'] = df['delay_minutes'].shift(lag)
        
        return df
    
    def _add_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add interaction features between variables"""
        
        # Hour and day interactions
        if 'hour' in df.columns and 'day_of_week' in df.columns:
            df['hour_day_interaction'] = df['hour'] * df['day_of_week']
        
        # Rush hour and weekend interaction
        if 'is_rush_hour' in df.columns and 'is_weekend' in df.columns:
            df['rush_weekend_interaction'] = df['is_rush_hour'] * df['is_weekend']
        
        # Weather and time interactions
        if 'weather_factor' in df.columns and 'hour' in df.columns:
            df['weather_hour_interaction'] = df['weather_factor'] * df['hour']
        
        return df
    
    def _add_route_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add route-specific delay patterns"""
        
        if 'route' not in df.columns or 'delay_minutes' not in df.columns:
            return df
        
        # Calculate route-specific statistics
        route_stats = df.groupby('route')['delay_minutes'].agg([
            'mean', 'std', 'median', 'min', 'max'
        ]).add_prefix('route_')
        
        # Merge route statistics back to main dataframe
        df = df.merge(route_stats, left_on='route', right_index=True, how='left')
        
        # Fill missing values with overall statistics
        for col in route_stats.columns:
            df[col] = df[col].fillna(df['delay_minutes'].agg(col.split('_')[1]))
        
        return df
    
    def prepare_ml_features(self, df: pd.DataFrame, target_column: str = 'delay_minutes') -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare final features for ML training
        """
        logger.info("Preparing features for ML training")
        
        # Select feature columns
        feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour', 
            'is_night', 'is_morning', 'is_evening', 'weather_factor',
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos',
            'route_length', 'is_express'
        ]
        
        # Add rolling features
        rolling_cols = [col for col in df.columns if 'rolling' in col]
        feature_columns.extend(rolling_cols)
        
        # Add lag features
        lag_cols = [col for col in df.columns if 'lag' in col]
        feature_columns.extend(lag_cols)
        
        # Add interaction features
        interaction_cols = [col for col in df.columns if 'interaction' in col]
        feature_columns.extend(interaction_cols)
        
        # Add route statistics
        route_cols = [col for col in df.columns if col.startswith('route_')]
        feature_columns.extend(route_cols)
        
        # Filter to existing columns
        feature_columns = [col for col in feature_columns if col in df.columns]
        
        # Prepare features and target
        X = df[feature_columns].fillna(0)
        y = df[target_column] if target_column in df.columns else None
        
        # Store feature columns for later use
        self.feature_columns = feature_columns
        
        logger.info(f"Prepared {len(feature_columns)} features for ML")
        return X, y
    
    def get_feature_importance(self, model, feature_names: List[str] = None) -> pd.DataFrame:
        """
        Get feature importance from trained model
        """
        if feature_names is None:
            feature_names = self.feature_columns
        
        if hasattr(model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            logger.warning("Model does not support feature importance")
            return pd.DataFrame()

def main():
    """Test the data processor"""
    from data_collection.collector import TTCDataCollector
    
    # Load test data
    collector = TTCDataCollector()
    test_delays = collector.fetch_ttc_delays()
    
    if test_delays:
        df = pd.DataFrame(test_delays)
        
        # Process data
        processor = TTCDataProcessor()
        df_clean = processor.clean_data(df)
        df_features = processor.engineer_features(df_clean)
        
        print(f"Original data: {len(df)} records")
        print(f"Cleaned data: {len(df_clean)} records")
        print(f"Features engineered: {len(df_features.columns)} columns")
        
        # Prepare for ML
        X, y = processor.prepare_ml_features(df_features)
        print(f"ML features: {X.shape}")
        print(f"Target variable: {y.shape if y is not None else 'None'}")

if __name__ == "__main__":
    main()

