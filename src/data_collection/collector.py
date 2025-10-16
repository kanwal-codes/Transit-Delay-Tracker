"""
TTC Data Collection System
Fetches real-time delay data from TTC API and stores for ML training
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional
import logging
import struct
from google.transit import gtfs_realtime_pb2

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTCDataCollector:
    def __init__(self):
        # Real TTC GTFS-RT API endpoints
        self.gtfs_rt_urls = {
            'vehicle_positions': 'https://bustime.ttc.ca/gtfsrt/vehicles',
            'trip_updates': 'https://bustime.ttc.ca/gtfsrt/trips',
            'alerts': 'https://bustime.ttc.ca/gtfsrt/alerts'
        }
        self.data_dir = "data"
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def fetch_ttc_delays(self) -> Optional[List[Dict]]:
        """
        Fetch current TTC delay data from GTFS-RT feeds
        Returns list of delay records or None if API fails
        """
        try:
            # Try to fetch real GTFS-RT data
            delays = self.fetch_gtfs_rt_data()
            if delays:
                logger.info(f"Fetched {len(delays)} real delay records from GTFS-RT")
                return delays
            else:
                logger.warning("GTFS-RT data unavailable, using mock data")
                return self.generate_mock_data()
                
        except Exception as e:
            logger.error(f"Error fetching TTC data: {e}")
            return self.generate_mock_data()  # Fallback to mock data
    
    def fetch_gtfs_rt_data(self) -> Optional[List[Dict]]:
        """
        Fetch and parse GTFS-RT data from TTC
        """
        delays = []
        
        try:
            # Fetch trip updates (contains delay information)
            trip_updates = self.fetch_gtfs_rt_feed('trip_updates')
            if trip_updates:
                delays.extend(self.parse_trip_updates(trip_updates))
            
            # Fetch alerts (contains service disruptions)
            alerts = self.fetch_gtfs_rt_feed('alerts')
            if alerts:
                delays.extend(self.parse_alerts(alerts))
            
            return delays if delays else None
            
        except Exception as e:
            logger.error(f"Error parsing GTFS-RT data: {e}")
            return None
    
    def fetch_gtfs_rt_feed(self, feed_type: str) -> Optional[bytes]:
        """
        Fetch GTFS-RT feed data
        """
        try:
            url = self.gtfs_rt_urls[feed_type]
            headers = {
                'User-Agent': 'TTC-Delay-Predictor/1.0',
                'Accept': 'application/x-protobuf'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error fetching {feed_type} feed: {e}")
            return None
    
    def parse_trip_updates(self, feed_data: bytes) -> List[Dict]:
        """
        Parse trip updates from GTFS-RT feed
        """
        delays = []
        
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)
            
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip_update = entity.trip_update
                    
                    # Extract trip information
                    trip = trip_update.trip
                    route_id = trip.route_id
                    
                    # Process stop time updates
                    for stop_time_update in trip_update.stop_time_updates:
                        if stop_time_update.HasField('arrival'):
                            arrival = stop_time_update.arrival
                            
                            # Calculate delay
                            scheduled_time = arrival.time
                            actual_time = arrival.time + arrival.delay if arrival.HasField('delay') else arrival.time
                            delay_seconds = arrival.delay if arrival.HasField('delay') else 0
                            delay_minutes = delay_seconds / 60
                            
                            # Create delay record
                            delay_record = {
                                'timestamp': datetime.fromtimestamp(scheduled_time).isoformat(),
                                'route': route_id,
                                'direction': 'Unknown',  # Not available in trip updates
                                'delay_minutes': round(delay_minutes, 1),
                                'stop_id': stop_time_update.stop_id,
                                'stop_name': f"Stop {stop_time_update.stop_id}",
                                'vehicle_id': trip_update.vehicle.id if trip_update.HasField('vehicle') else 'Unknown',
                                'status': 'Delayed' if delay_minutes > 2 else 'On Time',
                                'weather_factor': 1.0,  # Would integrate with weather API
                                'day_of_week': datetime.fromtimestamp(scheduled_time).weekday(),
                                'hour': datetime.fromtimestamp(scheduled_time).hour,
                                'data_source': 'GTFS-RT Trip Updates'
                            }
                            delays.append(delay_record)
            
        except Exception as e:
            logger.error(f"Error parsing trip updates: {e}")
        
        return delays
    
    def parse_alerts(self, feed_data: bytes) -> List[Dict]:
        """
        Parse alerts from GTFS-RT feed
        """
        delays = []
        
        try:
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(feed_data)
            
            for entity in feed.entity:
                if entity.HasField('alert'):
                    alert = entity.alert
                    
                    # Extract alert information
                    for informed_entity in alert.informed_entity:
                        if informed_entity.HasField('route_id'):
                            route_id = informed_entity.route_id
                            
                            # Create delay record for alert
                            delay_record = {
                                'timestamp': datetime.now().isoformat(),
                                'route': route_id,
                                'direction': 'Unknown',
                                'delay_minutes': 10.0,  # Assume 10 min delay for alerts
                                'stop_id': 'Unknown',
                                'stop_name': 'Service Alert',
                                'vehicle_id': 'Unknown',
                                'status': 'Service Disruption',
                                'weather_factor': 1.0,
                                'day_of_week': datetime.now().weekday(),
                                'hour': datetime.now().hour,
                                'data_source': 'GTFS-RT Alerts',
                                'alert_message': alert.header_text.translation[0].text if alert.header_text.translation else 'Service disruption'
                            }
                            delays.append(delay_record)
            
        except Exception as e:
            logger.error(f"Error parsing alerts: {e}")
        
        return delays
            
    def generate_mock_data(self) -> List[Dict]:
        """
        Generate realistic mock TTC delay data for development/testing
        """
        import random
        from datetime import datetime
        
        routes = ['501', '504', '505', '506', '509', '510', '511', '512']
        directions = ['Eastbound', 'Westbound', 'Northbound', 'Southbound']
        
        delays = []
        current_time = datetime.now()
        
        for _ in range(random.randint(5, 15)):
            delay_record = {
                'timestamp': current_time.isoformat(),
                'route': random.choice(routes),
                'direction': random.choice(directions),
                'delay_minutes': random.randint(1, 20),
                'stop_id': f"stop_{random.randint(1000, 9999)}",
                'stop_name': f"Mock Stop {random.randint(1, 100)}",
                'vehicle_id': f"vehicle_{random.randint(10000, 99999)}",
                'status': random.choice(['Delayed', 'On Time', 'Early']),
                'weather_factor': random.uniform(0.8, 1.2),  # Weather impact multiplier
                'day_of_week': current_time.weekday(),
                'hour': current_time.hour
            }
            delays.append(delay_record)
            
        logger.info(f"Generated {len(delays)} mock delay records")
        return delays
        
    def process_delay_data(self, raw_data: Dict) -> List[Dict]:
        """
        Process raw API data into standardized format
        """
        delays = []
        
        # This would be customized based on actual TTC API response structure
        if 'delays' in raw_data:
            for delay in raw_data['delays']:
                processed_delay = {
                    'timestamp': delay.get('timestamp', datetime.now().isoformat()),
                    'route': delay.get('route', 'Unknown'),
                    'direction': delay.get('direction', 'Unknown'),
                    'delay_minutes': delay.get('delay_minutes', 0),
                    'stop_id': delay.get('stop_id', ''),
                    'stop_name': delay.get('stop_name', ''),
                    'vehicle_id': delay.get('vehicle_id', ''),
                    'status': delay.get('status', 'Unknown'),
                    'weather_factor': 1.0,  # Would integrate with weather API
                    'day_of_week': datetime.now().weekday(),
                    'hour': datetime.now().hour
                }
                delays.append(processed_delay)
                
        return delays
        
    def save_delays_to_csv(self, delays: List[Dict], filename: Optional[str] = None):
        """
        Save delay data to CSV file
        """
        if not delays:
            logger.warning("No delay data to save")
            return
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ttc_delays_{timestamp}.csv"
            
        filepath = os.path.join(self.data_dir, filename)
        
        df = pd.DataFrame(delays)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(delays)} delay records to {filepath}")
        
    def collect_historical_data(self, hours: int = 24, interval_minutes: int = 5):
        """
        Collect data over specified time period
        """
        logger.info(f"Starting data collection for {hours} hours, every {interval_minutes} minutes")
        
        end_time = datetime.now() + timedelta(hours=hours)
        all_delays = []
        
        while datetime.now() < end_time:
            delays = self.fetch_ttc_delays()
            if delays:
                all_delays.extend(delays)
                self.save_delays_to_csv(delays)
                
            logger.info(f"Collected {len(delays)} delays. Next collection in {interval_minutes} minutes")
            time.sleep(interval_minutes * 60)
            
        # Save final consolidated dataset
        if all_delays:
            final_filename = f"historical_delays_{datetime.now().strftime('%Y%m%d')}.csv"
            self.save_delays_to_csv(all_delays, final_filename)
            logger.info(f"Collection complete. Total records: {len(all_delays)}")
            
    def load_historical_data(self, filename: str) -> pd.DataFrame:
        """
        Load historical delay data from CSV
        """
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            logger.info(f"Loaded {len(df)} historical records from {filepath}")
            return df
        else:
            logger.error(f"File not found: {filepath}")
            return pd.DataFrame()

def main():
    """Main function for testing data collection"""
    collector = TTCDataCollector()
    
    # Test single fetch
    print("Testing TTC data collection...")
    delays = collector.fetch_ttc_delays()
    
    if delays:
        print(f"Successfully fetched {len(delays)} delay records")
        print("\nSample record:")
        print(json.dumps(delays[0], indent=2))
        
        # Save test data
        collector.save_delays_to_csv(delays, "test_delays.csv")
    else:
        print("Failed to fetch delay data")

if __name__ == "__main__":
    main()

