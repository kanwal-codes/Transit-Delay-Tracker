"""
Comprehensive Error Handling and Logging System
Provides robust error handling, logging, and monitoring for the TTC Delay Predictor
"""

import logging
import traceback
import functools
import time
from datetime import datetime
from typing import Any, Callable, Dict, Optional
import pandas as pd
import numpy as np

# Configure logging
def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """
    Set up comprehensive logging configuration
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger

# Error handling decorators
def handle_errors(default_return: Any = None, log_errors: bool = True):
    """
    Decorator to handle errors gracefully
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(f"Traceback: {traceback.format_exc()}")
                
                return default_return
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry function on failure
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(func.__module__)
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"Failed after {max_retries} attempts: {str(e)}")
                        raise
                    else:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
                        time.sleep(delay)
            
        return wrapper
    return decorator

# Custom exception classes
class TTCDataError(Exception):
    """Custom exception for TTC data-related errors"""
    pass

class ModelTrainingError(Exception):
    """Custom exception for ML model training errors"""
    pass

class PredictionError(Exception):
    """Custom exception for prediction errors"""
    pass

class APIError(Exception):
    """Custom exception for API-related errors"""
    pass

# Error handling utilities
class ErrorHandler:
    """
    Centralized error handling and monitoring
    """
    
    def __init__(self):
        self.error_counts = {}
        self.error_history = []
        self.logger = logging.getLogger(__name__)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None):
        """
        Log error with context information
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        
        # Update error counts
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log the error
        self.logger.error(f"Error logged: {error_type} - {str(error)}")
        if context:
            self.logger.debug(f"Context: {context}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """
        Get summary of errors encountered
        """
        return {
            'total_errors': len(self.error_history),
            'error_counts': self.error_counts,
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
    
    def clear_history(self):
        """
        Clear error history
        """
        self.error_counts.clear()
        self.error_history.clear()

# Data validation utilities
class DataValidator:
    """
    Comprehensive data validation utilities
    """
    
    @staticmethod
    def validate_delay_data(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate TTC delay data
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Check if DataFrame is empty
            if df.empty:
                validation_results['is_valid'] = False
                validation_results['errors'].append("DataFrame is empty")
                return validation_results
            
            # Required columns
            required_columns = ['timestamp', 'route', 'delay_minutes']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                validation_results['is_valid'] = False
                validation_results['errors'].append(f"Missing required columns: {missing_columns}")
            
            # Check data types
            if 'delay_minutes' in df.columns:
                if not pd.api.types.is_numeric_dtype(df['delay_minutes']):
                    validation_results['errors'].append("delay_minutes must be numeric")
                
                # Check for negative delays
                negative_delays = (df['delay_minutes'] < 0).sum()
                if negative_delays > 0:
                    validation_results['warnings'].append(f"{negative_delays} negative delays found")
                
                # Check for extreme delays
                extreme_delays = (df['delay_minutes'] > 60).sum()
                if extreme_delays > 0:
                    validation_results['warnings'].append(f"{extreme_delays} delays over 60 minutes found")
            
            # Check timestamp format
            if 'timestamp' in df.columns:
                try:
                    pd.to_datetime(df['timestamp'])
                except:
                    validation_results['errors'].append("Invalid timestamp format")
            
            # Check route values
            if 'route' in df.columns:
                invalid_routes = df['route'].isnull().sum()
                if invalid_routes > 0:
                    validation_results['warnings'].append(f"{invalid_routes} missing route values")
            
            # Calculate basic stats
            if 'delay_minutes' in df.columns:
                validation_results['stats'] = {
                    'count': len(df),
                    'mean_delay': df['delay_minutes'].mean(),
                    'max_delay': df['delay_minutes'].max(),
                    'min_delay': df['delay_minutes'].min(),
                    'std_delay': df['delay_minutes'].std()
                }
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results
    
    @staticmethod
    def validate_model_input(X: pd.DataFrame, y: pd.Series = None) -> Dict[str, Any]:
        """
        Validate ML model input data
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            # Check if X is empty
            if X.empty:
                validation_results['is_valid'] = False
                validation_results['errors'].append("Feature matrix X is empty")
                return validation_results
            
            # Check for missing values
            missing_values = X.isnull().sum().sum()
            if missing_values > 0:
                validation_results['warnings'].append(f"{missing_values} missing values in features")
            
            # Check for infinite values
            infinite_values = np.isinf(X.select_dtypes(include=[np.number])).sum().sum()
            if infinite_values > 0:
                validation_results['warnings'].append(f"{infinite_values} infinite values found")
            
            # Check target variable if provided
            if y is not None:
                if len(y) != len(X):
                    validation_results['is_valid'] = False
                    validation_results['errors'].append("Feature matrix and target variable have different lengths")
                
                if y.isnull().sum() > 0:
                    validation_results['warnings'].append(f"{y.isnull().sum()} missing values in target")
            
            # Calculate stats
            validation_results['stats'] = {
                'n_samples': len(X),
                'n_features': len(X.columns),
                'feature_names': list(X.columns),
                'missing_values': missing_values,
                'infinite_values': infinite_values
            }
            
        except Exception as e:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Model validation error: {str(e)}")
        
        return validation_results

# Performance monitoring
class PerformanceMonitor:
    """
    Monitor performance metrics and execution times
    """
    
    def __init__(self):
        self.execution_times = {}
        self.performance_history = []
    
    def time_execution(self, func_name: str):
        """
        Decorator to time function execution
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time
                    
                    # Record execution time
                    self.execution_times[func_name] = execution_time
                    self.performance_history.append({
                        'function': func_name,
                        'execution_time': execution_time,
                        'timestamp': datetime.now().isoformat(),
                        'success': True
                    })
                    
                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.performance_history.append({
                        'function': func_name,
                        'execution_time': execution_time,
                        'timestamp': datetime.now().isoformat(),
                        'success': False,
                        'error': str(e)
                    })
                    raise
            
            return wrapper
        return decorator
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Get performance summary
        """
        if not self.performance_history:
            return {'message': 'No performance data available'}
        
        successful_executions = [p for p in self.performance_history if p['success']]
        failed_executions = [p for p in self.performance_history if not p['success']]
        
        if successful_executions:
            avg_time = np.mean([p['execution_time'] for p in successful_executions])
            max_time = np.max([p['execution_time'] for p in successful_executions])
            min_time = np.min([p['execution_time'] for p in successful_executions])
        else:
            avg_time = max_time = min_time = 0
        
        return {
            'total_executions': len(self.performance_history),
            'successful_executions': len(successful_executions),
            'failed_executions': len(failed_executions),
            'success_rate': len(successful_executions) / len(self.performance_history) if self.performance_history else 0,
            'average_execution_time': avg_time,
            'max_execution_time': max_time,
            'min_execution_time': min_time,
            'recent_executions': self.performance_history[-10:]
        }

# Global instances
error_handler = ErrorHandler()
data_validator = DataValidator()
performance_monitor = PerformanceMonitor()

# Initialize logging
setup_logging()

def main():
    """Test error handling and monitoring"""
    logger = logging.getLogger(__name__)
    
    # Test error handling
    @handle_errors(default_return="Error occurred")
    def test_function():
        raise ValueError("Test error")
    
    result = test_function()
    print(f"Error handling test: {result}")
    
    # Test performance monitoring
    @performance_monitor.time_execution("test_function")
    def slow_function():
        time.sleep(0.1)
        return "Success"
    
    result = slow_function()
    print(f"Performance test: {result}")
    
    # Test data validation
    test_data = pd.DataFrame({
        'timestamp': ['2024-01-01', '2024-01-02'],
        'route': ['501', '504'],
        'delay_minutes': [5, -2]  # One negative delay
    })
    
    validation = data_validator.validate_delay_data(test_data)
    print(f"Data validation: {validation}")
    
    # Print summaries
    print(f"Error summary: {error_handler.get_error_summary()}")
    print(f"Performance summary: {performance_monitor.get_performance_summary()}")

if __name__ == "__main__":
    main()

