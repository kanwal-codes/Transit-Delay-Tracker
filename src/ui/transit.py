"""
Transit Components - Now includes Toronto-only message display
"""
import streamlit as st
import pandas as pd
import plotly.express as px

class TransitComponents:
    def render_featured_routes(self):
        """Render landing page with featured route cards"""
        st.markdown("""
        <div style="padding: 3rem 1.5rem;">
            <div style="max-width: 1152px; margin: 0 auto; text-align: center; margin-bottom: 3rem;">
                <h2 style="font-size: 2.25rem; color: #1c1b1f; font-weight: 700; margin: 0 0 0.75rem 0;">
                    Popular Routes
                </h2>
                <p style="font-size: 1.125rem; color: #49454f; margin: 0;">
                    Quick access to frequently used transit routes
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Featured routes matching Homepage design
        featured_routes = [
            {
                "route_number": "504",
                "route_name": "King Streetcar",
                "station_name": "King St West At Yonge St",
                "location": "King Station",
                "arrival_times": [
                    {"label": "2 min", "is_primary": True},
                    {"label": "13 mins"},
                    {"label": "27 mins"},
                ]
            },
            {
                "route_number": "95",
                "route_name": "York Mills",
                "station_name": "York Mills Station",
                "location": "York Mills Terminal",
                "arrival_times": [
                    {"label": "5 min", "is_primary": True},
                    {"label": "18 mins"},
                    {"label": "35 mins"},
                ]
            },
            {
                "route_number": "320",
                "route_name": "Yonge Express",
                "station_name": "Yonge St At Bloor St",
                "location": "Bloor-Yonge Station",
                "arrival_times": [
                    {"label": "1 min", "is_primary": True},
                    {"label": "8 mins"},
                    {"label": "15 mins"},
                ]
            },
        ]
        
        # Display in grid layout (3 columns on large screens)
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
        
        for idx, route in enumerate(featured_routes):
            with cols[idx]:
                self._render_featured_card(route)
    
    def _render_featured_card(self, route_data):
        """Render a single featured route card"""
        route_number = route_data.get("route_number", "?")
        route_name = route_data.get("route_name", "Route")
        station_name = route_data.get("station_name", "Station")
        location = route_data.get("location", "Location")
        arrival_times = route_data.get("arrival_times", [])
        
        # Build card HTML using same structure as TransitCard
        card_html = '<div style="width: 100%; max-width: 28rem; margin: 0 auto; background: linear-gradient(to bottom, #ffffff, rgba(251, 245, 255, 0.3)); border-radius: 28px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1); overflow: hidden; border: 0;">'
        
        card_html += '<div style="padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem;">'
        
        # Route Number
        card_html += '<div style="text-align: center;">'
        card_html += '<div style="display: inline-flex; align-items: center; justify-content: center; border-radius: 32px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1); padding: 1.5rem 2rem; background: #eaddff;">'
        card_html += f'<span style="font-size: 4.5rem; font-weight: 700; color: #21005d; line-height: 1;">{route_number}</span>'
        card_html += '</div></div>'
        
        # Route Name
        card_html += '<div style="text-align: center; background: #e8def8; color: #1d192b; padding: 0.75rem 1rem; border-radius: 20px; font-size: 1.125rem; line-height: 1.75;">'
        card_html += f'<span>{route_name}</span>'
        card_html += '</div>'
        
        # Arrival Times
        card_html += '<div style="background: #e7e0ec; border-radius: 24px; padding: 1.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);">'
        
        for idx, time in enumerate(arrival_times):
            time_label = time.get("label", "")
            is_primary = time.get("is_primary", False)
            
            card_html += '<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 1rem;">'
            
            if is_primary:
                card_html += '<div style="background: #ffd8e4; color: #31111d; padding: 0.75rem 1.5rem; border-radius: 16px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);">'
                card_html += f'<span style="font-size: 1.5rem; font-weight: 600;">{time_label}</span>'
            else:
                card_html += '<div style="padding: 0.5rem 1.5rem; border-radius: 12px;">'
                card_html += f'<span style="font-size: 1.125rem; color: #49454f;">{time_label}</span>'
            
            card_html += '</div>'
            
            if idx < len(arrival_times) - 1:
                card_html += '<span style="font-size: 1.5rem; color: #49454f; opacity: 0.4; margin: 0.5rem 0;">•</span>'
            
            card_html += '</div>'
        
        card_html += '</div>'
        
        # Last Stop
        card_html += '<div style="background: #e8def8; color: #1d192b; padding: 1.25rem; border-radius: 20px; text-align: center; display: flex; flex-direction: column; gap: 0.5rem;">'
        card_html += '<p style="font-size: 0.875rem; line-height: 1.25; opacity: 0.7; margin: 0;">Last stop</p>'
        card_html += f'<p style="font-size: 1.125rem; line-height: 1.75; margin: 0; font-weight: 500;">{station_name}</p>'
        card_html += f'<p style="font-size: 0.875rem; line-height: 1.25; opacity: 0.7; margin: 0;">{location}</p>'
        card_html += '</div>'
        
        card_html += '</div></div>'
        
        st.markdown(card_html, unsafe_allow_html=True)
    
    def render_transit_results(self, data):
        opts = data.get("transit_options", [])
        if not opts:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: #F8FAFC; 
                        border-radius: 12px; border: 2px dashed #CBD5E1; margin: 1rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🚌</div>
                <h3 style="color: #64748B; margin-bottom: 0.5rem;">No Transit Routes Found</h3>
                <p style="color: #94A3B8; font-size: 0.9rem;">Try searching for a different location in Toronto</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Group options by data source for better organization
        real_time_routes = [opt for opt in opts if opt.get("data_source") == "nextbus"]
        mock_routes = [opt for opt in opts if opt.get("data_source") == "mock"]
        
        # Show data source indicator
        if mock_routes and real_time_routes:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FEF3C7, #FDE68A); 
                        padding: 1rem; border-radius: 8px; border-left: 4px solid #F59E0B; 
                        margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">⚠️</span>
                    <span style="color: #92400E; font-weight: 500;">
                        Mixed Data Sources: Some routes show real-time data, others show sample data
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif mock_routes:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FEE2E2, #FECACA); 
                        padding: 1rem; border-radius: 8px; border-left: 4px solid #EF4444; 
                        margin-bottom: 1rem;">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.2rem;">🎭</span>
                    <span style="color: #991B1B; font-weight: 500;">
                        TTC APIs are currently unavailable. Showing sample data.
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif real_time_routes:
            # Info message removed - user doesn't want these displayed
            # st.markdown("""
            # <div style="background: linear-gradient(135deg, #D1FAE5, #A7F3D0); 
            #             padding: 1rem; border-radius: 8px; border-left: 4px solid #10B981; 
            #             margin-bottom: 1rem;">
            #     <div style="display: flex; align-items: center; gap: 0.5rem;">
            #         <span style="font-size: 1.2rem;">✅</span>
            #         <span style="color: #065F46; font-weight: 500;">
            #             Using real-time TTC data from NextBus API
            #         </span>
            #     </div>
            # </div>
            # """, unsafe_allow_html=True)
            pass
        
        # Build ALL cards in one HTML string for horizontal scrolling
        all_cards_html = """
        <style>
        .transit-cards-container {
            display: flex;
            overflow-x: auto;
            gap: 1.5rem;
            padding: 1rem 0;
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
        }
        .transit-cards-container::-webkit-scrollbar {
            height: 8px;
        }
        .transit-cards-container::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 10px;
        }
        .transit-cards-container::-webkit-scrollbar-thumb {
            background: #6750a4;
            border-radius: 10px;
        }
        .transit-cards-container::-webkit-scrollbar-thumb:hover {
            background: #554593;
        }
        .transit-card-wrapper {
            flex: 0 0 auto;
            max-width: 28rem;
            min-width: 26rem;
            height: auto;
        }
        
        .transit-card-wrapper > div {
            height: auto;
        }
        </style>
        <div class="transit-cards-container">
        """
        
        for i, o in enumerate(opts):
            route_name = o.get("route_name", "Unknown route")
            station_name = o.get("station_name", "Unknown station")
            closest = o.get("closest_arrival", "—")
            data_source = o.get("data_source", "unknown")
            next_arrivals = o.get("next_arrivals", [])
            vehicle_locations = o.get('vehicle_locations', [])
            has_live_buses = len(vehicle_locations) > 0
            
            # Determine card styling based on data source
            if data_source == "nextbus":
                card_bg = "linear-gradient(135deg, #F0FDF4, #DCFCE7)"
                border_color = "#22C55E"
                icon = "🚌"
                badge_text = "LIVE"
                badge_color = "#16A34A"
            else:
                card_bg = "linear-gradient(135deg, #FEFBFF, #F3E8FF)"
                border_color = "#A855F7"
                icon = "🎭"
                badge_text = "SAMPLE"
                badge_color = "#9333EA"
            
            # Extract route number (e.g., "504" from "504 - 504-King West")
            route_number = route_name.split(' - ')[0] if ' - ' in route_name else route_name.split()[0]
            
            # Format arrivals - ensure unique times
            arrival_times = []
            seen_minutes = set()  # Track unique minutes to avoid duplicates
            
            # Start with closest arrival if available
            if closest != '—' and closest != 'N/A':
                try:
                    closest_min = int(float(closest))
                    if closest_min > 0 and closest_min not in seen_minutes:
                        arrival_times.append({"label": f"{closest_min} min", "minutes": closest_min})
                        seen_minutes.add(closest_min)
                except:
                    pass
            
            # Add next arrivals (avoid duplicates)
            if next_arrivals:
                for arr in next_arrivals:
                    if len(arrival_times) >= 4:  # Limit to 4 total times
                        break
                    minutes = int(arr.get("minutes", 0))
                    if minutes > 0 and minutes not in seen_minutes:
                        seen_minutes.add(minutes)
                        # Format: "13 min"
                        if minutes < 60:
                            time_str = f"{minutes} min"
                        elif minutes == 60:
                            time_str = "1hr"
                        else:
                            hours = minutes // 60
                            mins = minutes % 60
                            if mins == 0:
                                time_str = f"{hours}hr"
                            else:
                                time_str = f"{hours}hr {mins} min"
                        arrival_times.append({"label": time_str, "minutes": minutes})
            
            # Build card HTML - let it size naturally
            card_html = '<div class="transit-card-wrapper"><div style="background: linear-gradient(to bottom, #ffffff, rgba(251, 245, 255, 0.3)); border-radius: 28px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1); overflow: hidden; border: 0; display: flex; flex-direction: column;">'
            
            # Inner container with proper spacing
            card_html += '<div style="padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem;">'
            
            # 1. Route Number - shadow-md px-8 py-6
            card_html += '<div style="text-align: center;">'
            card_html += '<div style="display: inline-flex; align-items: center; justify-content: center; border-radius: 32px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1); padding: 1.5rem 2rem; background: #eaddff;">'
            card_html += f'<span style="font-size: 4.5rem; font-weight: 700; color: #21005d; line-height: 1;">{route_number}</span>'
            card_html += '</div></div>'
            
            # 2. Route Name - Show only the simple route name, not full details
            # Extract clean route name (e.g., "504-King West" from "504 - 504-King West - 504a King towards Dundas West Station")
            if " - " in route_name:
                parts = route_name.split(" - ")
                if len(parts) >= 2:
                    # Show just the main route name (e.g., "504-King West")
                    clean_route_name = parts[1]
                else:
                    clean_route_name = route_name
            else:
                clean_route_name = route_name
            
            card_html += '<div style="text-align: center; background: #e8def8; color: #1d192b; padding: 0.75rem 1rem; border-radius: 20px; font-size: 1.125rem; line-height: 1.75;">'
            card_html += f'<span>{clean_route_name}</span>'
            card_html += '</div>'
            
            # 3. Arrival Times - Always show 4 times, use "-" if unavailable
            card_html += '<div style="background: #e7e0ec; border-radius: 24px; padding: 1.5rem; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1); min-height: 200px;">'
            
            # Ensure we show exactly 4 times
            times_to_display = arrival_times[:4] if len(arrival_times) >= 4 else arrival_times + [{"label": "-", "is_primary": False}] * (4 - len(arrival_times))
            
            for idx, time_obj in enumerate(times_to_display):
                time_label = time_obj.get("label", "-")
                is_primary = (idx == 0 and time_label != "-")
                
                # Outer wrapper for each time item
                card_html += '<div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 1rem;">'
                
                # Time display div
                if is_primary:
                    card_html += '<div style="background: #ffd8e4; color: #31111d; padding: 0.75rem 1.5rem; border-radius: 16px; box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);">'
                    card_html += f'<span style="font-size: 1.5rem; font-weight: 600;">{time_label}</span>'
                else:
                    card_html += '<div style="padding: 0.5rem 1.5rem; border-radius: 12px;">'
                    card_html += f'<span style="font-size: 1.125rem; color: #49454f;">{time_label}</span>'
                
                card_html += '</div>'
                
                # Bullet AFTER time display
                if idx < len(times_to_display) - 1:
                    card_html += '<span style="font-size: 1.5rem; color: #49454f; opacity: 0.4; margin: 0.5rem 0;">•</span>'
                
                card_html += '</div>'
            
            card_html += '</div>'
            
            # 4. Last Stop - space-y-2 (0.5rem gap)
            # Shows: "Last stop" label + location + station/direction (NOT the route name again)
            card_html += '<div style="background: #e8def8; color: #1d192b; padding: 1.25rem; border-radius: 20px; text-align: center; display: flex; flex-direction: column; gap: 0.5rem;">'
            card_html += '<p style="font-size: 0.875rem; line-height: 1.25; opacity: 0.7; margin: 0;">Last stop</p>'
            card_html += f'<p style="font-size: 1.125rem; line-height: 1.75; margin: 0;">{station_name}</p>'
            # Show direction info only if available, don't repeat route name
            direction_text = ""
            if "towards" in route_name:
                parts = route_name.split("towards")
                if len(parts) > 1:
                    direction_text = parts[-1].strip()
            elif "at " in station_name.lower():
                # Extract station name if available
                direction_text = station_name.split(" - ")[-1] if " - " in station_name else station_name
            else:
                direction_text = "Toronto"
            
            if direction_text:
                card_html += f'<p style="font-size: 0.875rem; line-height: 1.25; opacity: 0.7; margin: 0;">{direction_text}</p>'
            card_html += '</div>'
            
            card_html += '</div></div></div>'
            
            # Append to master HTML string
            all_cards_html += card_html
        
        # Close container and render everything at once
        all_cards_html += "</div>"
        
        # Use components.html to render all cards together (no Streamlit wrappers!)
        import streamlit.components.v1 as components
        # Height set to 950px to show complete cards with extra space
        components.html(all_cards_html, height=950, scrolling=False)

    def render_map(self, lat: float, lon: float, data):
        if lat is None or lon is None:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: #F8FAFC; 
                        border-radius: 12px; border: 2px dashed #CBD5E1; margin: 1rem 0;">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">🗺️</div>
                <h3 style="color: #64748B; margin-bottom: 0.5rem;">Map Loading...</h3>
                <p style="color: #94A3B8; font-size: 0.9rem;">Detecting your location to show nearby transit stations</p>
            </div>
            """, unsafe_allow_html=True)
            return

        # Create enhanced map data
        points = [{
            "Label": "📍 Your Location", 
            "Lat": lat, 
            "Lon": lon, 
            "ColorGroup": "You",
            "Size": 15,
            "Symbol": "circle"
        }]

        # Add station markers with route information
        station_coords = {}  # To avoid duplicate stations
        for o in data.get("transit_options", []):
            station_name = o.get("station_name", "Station")
            route_name = o.get("route_name", "Route")
            data_source = o.get("data_source", "unknown")
            
            # Use approximate station coordinates (in real app, you'd have actual station coords)
            # For now, we'll place them around the user's location
            import random
            station_lat = lat + random.uniform(-0.01, 0.01)
            station_lon = lon + random.uniform(-0.01, 0.01)
            
            if station_name not in station_coords:
                station_coords[station_name] = {
                    "Lat": station_lat,
                    "Lon": station_lon,
                    "Routes": [route_name],
                    "DataSource": data_source
                }
            else:
                station_coords[station_name]["Routes"].append(route_name)

        # Add stations to map
        for station_name, info in station_coords.items():
            routes_text = ", ".join(info["Routes"][:2])  # Show first 2 routes
            if len(info["Routes"]) > 2:
                routes_text += f" (+{len(info['Routes'])-2} more)"
            
            icon = "🚌" if info["DataSource"] == "nextbus" else "🎭"
            points.append({
                "Label": f"{icon} {station_name}<br>Routes: {routes_text}", 
                "Lat": info["Lat"], 
                "Lon": info["Lon"], 
                "ColorGroup": "Stations",
                "Size": 12,
                "Symbol": "square"
            })
        
        # Add live bus locations
        total_vehicles = 0
        for o in data.get("transit_options", []):
            vehicle_locations = o.get('vehicle_locations', [])
            if vehicle_locations:
                route_name = o.get('route_name', 'Unknown')
                for vehicle in vehicle_locations:
                    vehicle_lat = vehicle.get('lat')
                    vehicle_lon = vehicle.get('lon')
                    arrival_min = int(vehicle.get('arrival_minutes', 0))
                    
                    # Only add if coordinates are valid
                    if vehicle_lat and vehicle_lon and vehicle_lat != 0 and vehicle_lon != 0:
                        points.append({
                            "Label": f"🚌 Live Bus<br>{route_name}<br>Arrives in {arrival_min} min", 
                            "Lat": vehicle_lat, 
                            "Lon": vehicle_lon, 
                            "ColorGroup": "Vehicles",
                            "Size": 10,
                            "Symbol": "circle"
                        })
                        total_vehicles += 1
        
        # Info message removed - user doesn't want it displayed
        # if total_vehicles > 0:
        #     st.info(f"🟢 Showing {total_vehicles} live bus locations on map")

        df = pd.DataFrame(points)
        if df.empty:
            st.warning("No map data available yet.")
            return

        # Create enhanced map
        fig = px.scatter_mapbox(
            df,
            lat="Lat",
            lon="Lon",
            hover_name="Label",
            color="ColorGroup",
            size="Size",
            zoom=13,
            height=500,
            color_discrete_map={
                "You": "#EF4444",
                "Stations": "#3B82F6",
                "Vehicles": "#22C55E"
            }
        )
        
        # Enhanced map styling
        fig.update_layout(
            mapbox_style="open-street-map",
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
            hovermode='closest'
        )
        
        # Map header removed - user doesn't want it displayed
        # st.markdown("""
        # <div style="background: linear-gradient(135deg, #F0F9FF, #E0F2FE); 
        #             padding: 1rem; border-radius: 8px; border-left: 4px solid #0EA5E9; 
        #             margin-bottom: 1rem;">
        #     <div style="display: flex; align-items: center; gap: 0.5rem;">
        #         <span style="font-size: 1.2rem;">🗺️</span>
        #         <span style="color: #0C4A6E; font-weight: 500;">
        #             Interactive Map: Your location, nearby TTC stops, and live bus locations
        #         </span>
        #     </div>
        # </div>
        # """, unsafe_allow_html=True)
        
        st.plotly_chart(fig, use_container_width=True)

    def render_info_message(self, message: str):
        st.info(f"ℹ️ {message}")

    def render_error_message(self, message: str):
        st.error(f"❌ {message}")
