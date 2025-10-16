"""
Comprehensive Testing Suite for TTC Delay Predictor
Tests all components including data collection, ML models, and web interface
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
import tempfile
import shutil

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_collection.collector import TTCDataCollector
from utils.data_processor import TTCDataProcessor
from ml.predictor import DelayPredictor
from ml.anomaly_detector import AnomalyDetector
from utils.weather_integration import WeatherIntegration
from utils.nlp_processor import TTCQueryProcessor
from utils.error_handler import ErrorHandler, DataValidator, PerformanceMonitor

class TestTTCDataCollector(unittest.TestCase):
    """Test TTC data collection functionality"""
    
    def setUp(self):
        self.collector = TTCDataCollector()
        self.temp_dir = tempfile.mkdtemp()
        self.collector.data_dir = self.temp_dir
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_generate_mock_data(self):
        """Test mock data generation"""
        mock_data = self.collector.generate_mock_data()
        
        self.assertIsInstance(mock_data, list)
        self.assertGreater(len(mock_data), 0)
        
        # Check data structure
        if mock_data:
            record = mock_data[0]
            required_fields = ['timestamp', 'route', 'delay_minutes', 'status']
            for field in required_fields:
                self.assertIn(field, record)
    
    def test_save_and_load_data(self):
        """Test data saving and loading"""
        mock_data = self.collector.generate_mock_data()
        filename = "test_delays.csv"
        
        # Save data
        self.collector.save_delays_to_csv(mock_data, filename)
        
        # Check file exists
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath))
        
        # Load data
        loaded_df = self.collector.load_historical_data(filename)
        self.assertIsInstance(loaded_df, pd.DataFrame)
        self.assertEqual(len(loaded_df), len(mock_data))

class TestTTCDataProcessor(unittest.TestCase):
    """Test data processing functionality"""
    
    def setUp(self):
        self.processor = TTCDataProcessor()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'route': np.random.choice(['501', '504', '505'], 100),
            'delay_minutes': np.random.normal(5, 2, 100),
            'status': np.random.choice(['On Time', 'Delayed'], 100),
            'weather_factor': np.random.uniform(0.8, 1.2, 100)
        })
    
    def test_clean_data(self):
        """Test data cleaning"""
        # Add some problematic data
        dirty_data = self.test_data.copy()
        dirty_data.loc[0, 'delay_minutes'] = np.nan
        dirty_data.loc[1, 'route'] = None
        dirty_data.loc[2, 'delay_minutes'] = -5  # Negative delay
        
        cleaned_data = self.processor.clean_data(dirty_data)
        
        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertEqual(len(cleaned_data), len(dirty_data))
        
        # Check that negative delays are handled
        self.assertTrue((cleaned_data['delay_minutes'] >= 0).all())
    
    def test_engineer_features(self):
        """Test feature engineering"""
        features = self.processor.engineer_features(self.test_data)
        
        self.assertIsInstance(features, pd.DataFrame)
        self.assertGreater(len(features.columns), len(self.test_data.columns))
        
        # Check for derived features
        expected_features = ['hour', 'day_of_week', 'is_weekend', 'is_rush_hour']
        for feature in expected_features:
            self.assertIn(feature, features.columns)
    
    def test_prepare_ml_features(self):
        """Test ML feature preparation"""
        processed_data = self.processor.engineer_features(self.test_data)
        X, y = self.processor.prepare_ml_features(processed_data)
        
        self.assertIsInstance(X, pd.DataFrame)
        self.assertIsInstance(y, pd.Series)
        self.assertEqual(len(X), len(y))
        self.assertGreater(len(X.columns), 0)

class TestDelayPredictor(unittest.TestCase):
    """Test delay prediction functionality"""
    
    def setUp(self):
        self.predictor = DelayPredictor()
        
        # Create training data
        self.training_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=200, freq='H'),
            'route': np.random.choice(['501', '504', '505'], 200),
            'delay_minutes': np.random.normal(5, 2, 200),
            'hour': np.random.randint(0, 24, 200),
            'day_of_week': np.random.randint(0, 7, 200),
            'is_weekend': np.random.choice([0, 1], 200),
            'is_rush_hour': np.random.choice([0, 1], 200),
            'weather_factor': np.random.uniform(0.8, 1.2, 200)
        })
    
    def test_train_model(self):
        """Test model training"""
        results = self.predictor.train(self.training_data)
        
        self.assertIsInstance(results, dict)
        self.assertIn('mae', results)
        self.assertIn('r2', results)
        self.assertTrue(self.predictor.is_trained)
    
    def test_predict_delay(self):
        """Test delay prediction"""
        # Train model first
        self.predictor.train(self.training_data)
        
        # Test prediction
        test_time = datetime.now() + timedelta(hours=1)
        prediction = self.predictor.predict_delay('501', test_time)
        
        self.assertIsInstance(prediction, float)
        self.assertGreaterEqual(prediction, 0)  # Should be non-negative
    
    def test_predict_batch(self):
        """Test batch prediction"""
        # Train model first
        self.predictor.train(self.training_data)
        
        # Test batch prediction
        test_data = self.training_data.head(10)
        predictions = self.predictor.predict_batch(test_data)
        
        self.assertIsInstance(predictions, np.ndarray)
        self.assertEqual(len(predictions), len(test_data))
        self.assertTrue((predictions >= 0).all())  # All predictions should be non-negative

class TestAnomalyDetector(unittest.TestCase):
    """Test anomaly detection functionality"""
    
    def setUp(self):
        self.detector = AnomalyDetector()
        
        # Create test data with some anomalies
        normal_data = np.random.normal(5, 1, 90)
        anomaly_data = np.random.normal(15, 2, 10)  # Clear anomalies
        
        self.test_data = pd.DataFrame({
            'timestamp': pd.date_range('2024-01-01', periods=100, freq='H'),
            'route': np.random.choice(['501', '504'], 100),
            'delay_minutes': np.concatenate([normal_data, anomaly_data]),
            'hour': np.random.randint(0, 24, 100),
            'day_of_week': np.random.randint(0, 7, 100),
            'is_weekend': np.random.choice([0, 1], 100),
            'is_rush_hour': np.random.choice([0, 1], 100)
        })
    
    def test_train_detector(self):
        """Test anomaly detector training"""
        result = self.detector.train(self.test_data)
        
        self.assertTrue(result)
        self.assertTrue(self.detector.is_trained)
    
    def test_detect_anomalies(self):
        """Test anomaly detection"""
        # Train detector first
        self.detector.train(self.test_data)
        
        # Detect anomalies
        anomalies = self.detector.detect_anomalies(self.test_data)
        
        self.assertIsInstance(anomalies, pd.DataFrame)
        # Should detect some anomalies in our test data
        self.assertGreater(len(anomalies), 0)
    
    def test_anomaly_summary(self):
        """Test anomaly summary generation"""
        # Train detector first
        self.detector.train(self.test_data)
        
        # Get summary
        summary = self.detector.get_anomaly_summary(self.test_data)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_anomalies', summary)
        self.assertIn('anomaly_rate', summary)
        self.assertGreater(summary['total_anomalies'], 0)

class TestWeatherIntegration(unittest.TestCase):
    """Test weather integration functionality"""
    
    def setUp(self):
        self.weather = WeatherIntegration()
    
    def test_generate_mock_weather(self):
        """Test mock weather generation"""
        weather_data = self.weather._generate_mock_weather()
        
        self.assertIsInstance(weather_data, dict)
        required_fields = ['temperature', 'humidity', 'weather_main', 'timestamp']
        for field in required_fields:
            self.assertIn(field, weather_data)
    
    def test_calculate_weather_impact(self):
        """Test weather impact calculation"""
        weather_data = {
            'temperature': -15,  # Very cold
            'weather_main': 'Snow',  # Snowy
            'wind_speed': 25,  # Strong wind
            'visibility': 500  # Poor visibility
        }
        
        impact = self.weather.calculate_weather_impact(weather_data)
        
        self.assertIsInstance(impact, float)
        self.assertGreater(impact, 1.0)  # Should increase delays
        self.assertLessEqual(impact, 3.0)  # Should be capped at 3x
    
    def test_get_weather_features(self):
        """Test weather feature extraction"""
        weather_data = self.weather._generate_mock_weather()
        features = self.weather.get_weather_features(weather_data)
        
        self.assertIsInstance(features, dict)
        expected_features = ['temperature', 'humidity', 'is_rainy', 'weather_impact']
        for feature in expected_features:
            self.assertIn(feature, features)

class TestTTCQueryProcessor(unittest.TestCase):
    """Test natural language query processing"""
    
    def setUp(self):
        self.processor = TTCQueryProcessor()
        
        # Create test data
        self.test_data = pd.DataFrame({
            'route': ['501', '504', '505'],
            'delay_minutes': [5, 3, 8],
            'status': ['Delayed', 'On Time', 'Delayed']
        })
    
    def test_extract_route(self):
        """Test route extraction from queries"""
        test_cases = [
            ("How is route 501 doing?", "501"),
            ("What about the Queen Street route?", "501"),
            ("Tell me about route 504", "504"),
            ("No route mentioned", None)
        ]
        
        for query, expected_route in test_cases:
            result = self.processor._extract_route(query.lower())
            self.assertEqual(result, expected_route)
    
    def test_classify_question(self):
        """Test question classification"""
        test_cases = [
            ("Which routes are delayed?", "delay_status"),
            ("Predict delay for route 501", "prediction"),
            ("Compare route 501 vs 504", "comparison"),
            ("Are there any anomalies?", "anomaly"),
            ("Tell me about route 501", "route_info")
        ]
        
        for query, expected_type in test_cases:
            result = self.processor._classify_question(query.lower())
            self.assertEqual(result, expected_type)
    
    def test_process_query(self):
        """Test complete query processing"""
        query = "How is route 501 performing?"
        result = self.processor.process_query(query, self.test_data)
        
        self.assertIsInstance(result, dict)
        self.assertIn('query', result)
        self.assertIn('route', result)
        self.assertIn('response', result)
        self.assertIn('confidence', result)
        
        self.assertEqual(result['route'], '501')
        self.assertGreater(result['confidence'], 0)

class TestErrorHandler(unittest.TestCase):
    """Test error handling and monitoring"""
    
    def setUp(self):
        self.error_handler = ErrorHandler()
        self.data_validator = DataValidator()
    
    def test_log_error(self):
        """Test error logging"""
        test_error = ValueError("Test error")
        context = {'function': 'test_function', 'data_size': 100}
        
        self.error_handler.log_error(test_error, context)
        
        self.assertEqual(len(self.error_handler.error_history), 1)
        self.assertEqual(self.error_handler.error_counts['ValueError'], 1)
    
    def test_validate_delay_data(self):
        """Test delay data validation"""
        # Valid data
        valid_data = pd.DataFrame({
            'timestamp': ['2024-01-01', '2024-01-02'],
            'route': ['501', '504'],
            'delay_minutes': [5, 3]
        })
        
        result = self.data_validator.validate_delay_data(valid_data)
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
        
        # Invalid data
        invalid_data = pd.DataFrame({
            'timestamp': ['2024-01-01'],
            'delay_minutes': [5]  # Missing 'route' column
        })
        
        result = self.data_validator.validate_delay_data(invalid_data)
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.collector = TTCDataCollector()
        self.processor = TTCDataProcessor()
        self.predictor = DelayPredictor()
        self.detector = AnomalyDetector()
    
    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        # Generate data
        raw_data = self.collector.generate_mock_data()
        df_raw = pd.DataFrame(raw_data)
        
        # Process data
        df_clean = self.processor.clean_data(df_raw)
        df_features = self.processor.engineer_features(df_clean)
        
        # Train models
        predictor_results = self.predictor.train(df_features)
        detector.train(df_features)
        
        # Make predictions
        test_time = datetime.now() + timedelta(hours=1)
        prediction = self.predictor.predict_delay('501', test_time)
        
        # Detect anomalies
        anomalies = self.detector.detect_anomalies(df_features)
        
        # Verify results
        self.assertIsInstance(predictor_results, dict)
        self.assertIsInstance(prediction, float)
        self.assertIsInstance(anomalies, pd.DataFrame)
        self.assertTrue(self.predictor.is_trained)
        self.assertTrue(self.detector.is_trained)

def run_all_tests():
    """Run all test suites"""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestTTCDataCollector,
        TestTTCDataProcessor,
        TestDelayPredictor,
        TestAnomalyDetector,
        TestWeatherIntegration,
        TestTTCQueryProcessor,
        TestErrorHandler,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

def main():
    """Main function to run tests"""
    print("🧪 Running TTC Delay Predictor Test Suite")
    print("=" * 50)
    
    result = run_all_tests()
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

