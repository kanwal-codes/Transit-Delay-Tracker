# File: tests/test_api_client.py
"""
Maple Mover - API Client Tests
Basic test suite to demonstrate testing practices
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maple_mover_app import MapleMoverApp


class TestMapleMoverApp:
    """Test suite for MapleMoverApp class"""
    
    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.app = MapleMoverApp()
    
    def test_app_initialization(self):
        """Test that the app initializes correctly"""
        assert self.app is not None
        assert hasattr(self.app, 'base_url')
        assert hasattr(self.app, 'api_timeout')
        assert hasattr(self.app, 'geolocation_handler')
    
    def test_get_user_location_default(self):
        """Test default location fallback"""
        lat, lon, area = self.app.get_user_location()
        assert isinstance(lat, float)
        assert isinstance(lon, float)
        assert isinstance(area, str)
        assert area == "default_location"
    
    def test_get_user_location_manual(self):
        """Test manual location input"""
        test_lat, test_lon = 43.6532, -79.3832
        lat, lon, area = self.app.get_user_location(test_lat, test_lon)
        assert lat == test_lat
        assert lon == test_lon
        assert area == "user_provided"
    
    def test_find_nearest_stations(self):
        """Test station finding logic"""
        test_lat, test_lon = 43.6532, -79.3832
        stations = self.app.find_nearest_stations(test_lat, test_lon)
        
        assert isinstance(stations, list)
        assert len(stations) <= self.app.max_stations
        assert len(stations) > 0
        
        # Check station structure
        for station_uri, station_lat, station_lon, distance in stations:
            assert isinstance(station_uri, str)
            assert isinstance(station_lat, float)
            assert isinstance(station_lon, float)
            assert isinstance(distance, float)
    
    @patch('requests.get')
    def test_fetch_station_data_success(self, mock_get):
        """Test successful API data fetching"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'name': 'Test Station',
            'stops': [
                {
                    'name': 'Test Stop',
                    'uri': 'test_stop_uri',
                    'routes': [
                        {
                            'name': 'Test Route',
                            'uri': 'test_route_uri',
                            'agency': 'TTC',
                            'stop_times': []
                        }
                    ]
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.app.fetch_station_data("test_station")
        
        assert result is not None
        assert result['name'] == 'Test Station'
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_station_data_failure(self, mock_get):
        """Test API failure handling"""
        # Mock API failure
        mock_get.side_effect = Exception("API Error")
        
        result = self.app.fetch_station_data("test_station")
        
        assert result is None
        mock_get.assert_called_once()
    
    def test_extract_transit_options_valid_data(self):
        """Test transit options extraction with valid data"""
        station_data = {
            'name': 'Test Station',
            'stops': [
                {
                    'name': 'Test Stop',
                    'uri': 'test_stop_uri',
                    'routes': [
                        {
                            'name': 'Test Route',
                            'uri': 'test_route_uri',
                            'agency': 'TTC',
                            'stop_times': [
                                {
                                    'departure_time': '12:00:00',
                                    'departure_timestamp': 1234567890,
                                    'shape': 'Test Destination'
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        options = self.app.extract_transit_options(station_data, "Test Station")
        
        assert isinstance(options, list)
        if options:  # If we have options
            option = options[0]
            assert 'route_name' in option
            assert 'stop_name' in option
            assert 'next_arrivals' in option
            assert 'closest_arrival' in option
    
    def test_extract_transit_options_invalid_data(self):
        """Test transit options extraction with invalid data"""
        # Test with None data
        options = self.app.extract_transit_options(None, "Test Station")
        assert options == []
        
        # Test with empty data
        options = self.app.extract_transit_options({}, "Test Station")
        assert options == []
        
        # Test with missing stops key
        options = self.app.extract_transit_options({'name': 'Test'}, "Test Station")
        assert options == []
    
    def test_format_arrival_time(self):
        """Test arrival time formatting"""
        # Test various time scenarios
        assert self.app.format_arrival_time(-5) == "Departed"
        assert self.app.format_arrival_time(0.5) == "Now"
        assert self.app.format_arrival_time(5) == "5 min"
        assert self.app.format_arrival_time(65) == "1h 5m"
    
    def test_known_locations_structure(self):
        """Test that known locations have proper structure"""
        for area, stations in self.app.known_locations.items():
            assert isinstance(area, str)
            assert isinstance(stations, dict)
            
            for station_uri, coords in stations.items():
                assert isinstance(station_uri, str)
                assert isinstance(coords, tuple)
                assert len(coords) == 2
                assert isinstance(coords[0], float)  # lat
                assert isinstance(coords[1], float)  # lon


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])

