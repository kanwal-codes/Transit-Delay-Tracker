"""
Transit Components - Now includes Toronto-only message display
"""
import streamlit as st
import pandas as pd
import plotly.express as px

class TransitComponents:
    def render_transit_results(self, data):
        opts = data.get("transit_options", [])
        if not opts:
            st.info("No nearby TTC transit found yet.")
            return

        for o in opts:
            route_name = o.get("route_name", "Unknown route")
            station_name = o.get("station_name", "Unknown station")
            closest = o.get("closest_arrival", "—")
            st.markdown(f"**🚍 {route_name}** at *{station_name}* → next in {closest} min")

    def render_map(self, lat: float, lon: float, data):
        if lat is None or lon is None:
            st.warning("Map not available yet — still detecting your location.")
            return

        points = [{"Label": "📍 Your Location", "Lat": lat, "Lon": lon, "ColorGroup": "You"}]

        for o in data.get("transit_options", []):
            station_label = o.get("station_name", "Station")
            points.append({
                "Label": station_label,
                "Lat": lat,
                "Lon": lon,
                "ColorGroup": "Stations"
            })

        df = pd.DataFrame(points)
        if df.empty:
            st.warning("No map data available yet.")
            return

        fig = px.scatter_mapbox(
            df,
            lat="Lat",
            lon="Lon",
            hover_name="Label",
            color="ColorGroup",
            zoom=12,
            height=420
        )
        fig.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)

    def render_info_message(self, message: str):
        st.info(f"ℹ️ {message}")

    def render_error_message(self, message: str):
        st.error(f"❌ {message}")
