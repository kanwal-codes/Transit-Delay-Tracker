"""
Main Maple Mover app — restrict TTC routes to Toronto only
"""

import sys
import os
# Add parent directory to path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import structlog
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.api.ttc_client import TTCAPIClient
from src.geocoding.service import GeocodingService
from src.services.location import LocationService
from src.ui.components import UIComponents

logger = structlog.get_logger("maple_mover.app")

class MapleMoverApp:
    def __init__(self):
        self.api = TTCAPIClient()
        self.geo = GeocodingService()
        self.loc = LocationService()
        self.ui = UIComponents()

    def find_transit(self, lat, lon):
        """Find nearby TTC transit stations using NextBus API discovery."""
        # Show loading spinner
        with st.spinner("🔍 Discovering TTC routes and finding nearby intersections..."):
            # Use the new NextBus discovery service
            transit_data = self.api.ttc_service.get_transit_data_for_location(lat, lon)
            
            # Get all vehicle locations for displaying ALL buses on each route
            # Access the underlying NextBus service from UnifiedTTCService
            all_vehicles = self.api.ttc_service.nextbus_service._get_all_vehicle_locations()
            
        if not transit_data:
            return {"transit_options": []}
        
        # Convert new data structure to expected format
        all_opts = []
        
        # Track unique routes to avoid duplicates across stops
        seen_routes = set()
        
        for data in transit_data:
            stop_name = data.get('stop_name', 'Unknown Stop')
            predictions = data.get('predictions', [])
            distance = data.get('distance', 0)
            
            logger.info(f"🔍 Processing {stop_name}: {len(predictions)} predictions")
            
            if predictions:
                # Group predictions by route + direction + vehicle
                # Create unique key: route + direction + first arrival time of that vehicle
                grouped_predictions = {}
                
                for pred in predictions:
                    route_tag = pred.get('route_tag', '')
                    route_title = pred.get('route_title', 'Unknown Route')
                    direction = pred.get('direction', '')
                    vehicle_id = pred.get('vehicle_id', '')
                    minutes = float(pred.get('arrival_minutes', 0))
                    
                    # Create unique key per bus: route + direction
                    # This prevents showing same bus multiple times
                    key = f"{route_tag} - {route_title} {direction}"
                    
                    if key not in grouped_predictions:
                        grouped_predictions[key] = []
                    
                    grouped_predictions[key].append({
                        'minutes': minutes,
                        'vehicle_id': vehicle_id,
                        'vehicle_lat': pred.get('vehicle_lat', 0),
                        'vehicle_lon': pred.get('vehicle_lon', 0)
                    })
                
                # Create one transit option per unique route/direction/bus
                for route_key, pred_list in grouped_predictions.items():
                    # Sort by arrival time
                    pred_list.sort(key=lambda x: x['minutes'])
                    
                    closest_minutes = int(pred_list[0]['minutes']) if pred_list else 0
                    
                    # Show all arrival times for this bus
                    next_arrivals = [{'minutes': int(p['minutes'])} for p in pred_list]
                    
                    # Get vehicle locations for this route (buses coming to this stop)
                    vehicle_coords = []
                    for pred in pred_list:
                        vehicle_lat = pred.get('vehicle_lat', 0)
                        vehicle_lon = pred.get('vehicle_lon', 0)
                        # Only add if coordinates are valid (not 0,0)
                        if vehicle_lat and vehicle_lon and vehicle_lat != 0 and vehicle_lon != 0:
                            vehicle_coords.append({
                                'lat': vehicle_lat,
                                'lon': vehicle_lon,
                                'arrival_minutes': pred['minutes']
                            })
                            logger.debug(f"📍 Adding vehicle at ({vehicle_lat}, {vehicle_lon}) arriving in {pred['minutes']} min")
                    
                    # Also add ALL buses currently running on this route
                    # Extract route tag from key (format: "304 - Route 304 Eastbound")
                    route_tag = route_key.split(' - ')[0]
                    all_route_buses = self.api.ttc_service.nextbus_service.get_all_buses_for_route(route_tag, all_vehicles)
                    
                    # Add all buses on this route to vehicle_coords
                    for bus in all_route_buses:
                        bus_lat = float(bus['lat']) if bus['lat'] else 0
                        bus_lon = float(bus['lon']) if bus['lon'] else 0
                        
                        if bus_lat and bus_lon and bus_lat != 0 and bus_lon != 0:
                            # Check if this bus is already in vehicle_coords (coming to stop)
                            is_already_listed = any(abs(float(v.get('lat', 0)) - bus_lat) < 0.0001 and 
                                                   abs(float(v.get('lon', 0)) - bus_lon) < 0.0001
                                                   for v in vehicle_coords)
                            if not is_already_listed:
                                vehicle_coords.append({
                                    'lat': bus_lat,
                                    'lon': bus_lon,
                                    'arrival_minutes': 999,  # Not coming to this stop
                                    'all_route': True,  # Flag that this is from all-route list
                                    'direction': bus.get('direction', ''),
                                    'speed': bus.get('speed', 0)
                                })
                                logger.info(f"🚌 Route {route_tag}: Adding bus at ({bus_lat}, {bus_lon})")
                    
                    # Only add option if there are actual predictions with valid times
                    if pred_list and closest_minutes > 0:
                        all_opts.append({
                            'route_name': route_key,
                            'station_name': stop_name,
                            'closest_arrival': f"{closest_minutes}",
                            'next_arrivals': next_arrivals,
                            'data_source': data.get('data_source', 'nextbus'),
                            'distance': distance,
                            'stop_id': data.get('stop_id', ''),
                            'vehicle_locations': vehicle_coords
                        })
            
            else:
                # If no predictions but we know the stop exists - show each route that serves it
                routes = data.get('routes', [])
                
                if routes:
                    # Show each route that serves this stop
                    # Use seen_routes to avoid duplicates across different stops
                    for route_tag in routes:
                        route_key = f"Route {route_tag}"  # Simple route name without direction
                        
                        if route_key not in seen_routes:
                            seen_routes.add(route_key)
                            
                            # Get ALL buses on this route even if no predictions
                            all_route_buses = self.api.ttc_service.nextbus_service.get_all_buses_for_route(route_tag, all_vehicles)
                            
                            # Build vehicle coordinates for all route buses
                            vehicle_coords = []
                            for bus in all_route_buses:
                                bus_lat = float(bus['lat']) if bus.get('lat') else 0
                                bus_lon = float(bus['lon']) if bus.get('lon') else 0
                                
                                if bus_lat and bus_lon and bus_lat != 0 and bus_lon != 0:
                                    vehicle_coords.append({
                                        'lat': bus_lat,
                                        'lon': bus_lon,
                                        'arrival_minutes': 999,
                                        'all_route': True,
                                        'direction': bus.get('direction', ''),
                                        'speed': bus.get('speed', 0)
                                    })
                            
                            all_opts.append({
                                'route_name': route_key,
                                'station_name': stop_name,
                                'closest_arrival': '—',
                                'next_arrivals': [],
                                'data_source': data.get('data_source', 'unknown'),
                                'distance': distance,
                                'vehicle_locations': vehicle_coords
                            })
                else:
                    # Fallback if no routes listed
                    all_opts.append({
                        'route_name': 'Route Available',
                        'station_name': stop_name,
                        'closest_arrival': '—',
                        'next_arrivals': [],
                        'data_source': data.get('data_source', 'unknown'),
                        'distance': distance
                    })
        
        logger.info(f"🚀 NextBus service completed: {len(all_opts)} transit options from {len(transit_data)} stops")
        
        return {"transit_options": all_opts}

    def run(self):
        self.ui.setup_page()
        self.ui.render_header()

        # Process location detection FIRST, before rendering search bar
        lat = st.session_state.get("user_lat")
        lon = st.session_state.get("user_lon")
        
        # Auto-detect location on page load (if coordinates in query params)
        if not st.session_state.get("auto_location_processed", False):
            detected_lat, detected_lon, source = self.loc.get_user_location()
            if detected_lat and detected_lon and source == "browser_geolocation":
                # Check if we already have an address for these coordinates
                if not st.session_state.get("search_address"):
                    # Reverse geocode the location to get address
                    with st.spinner("📍 Detecting your location..."):
                        addr = self.geo.reverse_geocode(detected_lat, detected_lon)
                    if addr:
                        st.session_state.search_address = addr
                
                st.session_state.location_source = source
                st.session_state.user_lat = detected_lat
                st.session_state.user_lon = detected_lon
                lat = detected_lat
                lon = detected_lon
                st.session_state.auto_location_processed = True

        # Step 1: show the search bar always (now with address populated)
        address = self.ui.render_search_interface()

        # Step 2: handle search input or location detection
        # Check if user wants to search
        search_requested = address and address.strip()
        location_requested = st.session_state.get("location_requested", False)
        
        # Detect location if requested
        if location_requested:
            detected_lat, detected_lon, source = self.loc.get_user_location()
            if detected_lat and detected_lon:
                with st.spinner("📍 Converting coordinates to address..."):
                    addr = self.geo.reverse_geocode(detected_lat, detected_lon)
                if addr:
                    st.session_state.search_address = addr
                    st.session_state.location_source = source
                    st.session_state.user_lat = detected_lat
                    st.session_state.user_lon = detected_lon
                    lat = detected_lat
                    lon = detected_lon
                st.session_state.location_requested = False
        
        # Handle manual search input
        if search_requested:
            with st.spinner("🔍 Looking up address..."):
                coords = self.geo.geocode_address(address)
            if coords:
                lat, lon = coords
                st.session_state.user_lat = lat
                st.session_state.user_lon = lon
                st.session_state.search_address = address
                st.session_state.location_source = "manual"
            else:
                self.ui.render_error_message("❌ Could not locate that address.")
                return

        # Step 3: Show results OR landing page
        if lat and lon:
            # User has location - show transit results
            # Check Toronto boundaries
            if not self.geo._is_toronto_area(lat, lon):
                self.ui.render_info_message("🗺️ Now only available in Toronto — coming soon to your area!")
                self.ui.render_footer()
                return
            
            # Fetch TTC routes
            data = self.find_transit(lat, lon)
            
            if data["transit_options"]:
                self.ui.render_transit_results(data)
                self.ui.render_map(lat, lon, data)
            else:
                self.ui.render_info_message("No TTC routes found nearby.")
                
            self.ui.render_footer()
        else:
            # No location yet - show landing page with featured routes
            self.ui.render_featured_routes()
            self.ui.render_footer()


if __name__ == "__main__":
    MapleMoverApp().run()
