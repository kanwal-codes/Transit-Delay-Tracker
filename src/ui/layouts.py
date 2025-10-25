import streamlit as st
from src.config.settings import Settings
from src.styles import CSSLoader

class LayoutComponents:
    def __init__(self):
        self.css_loader = CSSLoader()

    def setup_page(self):
        st.set_page_config(
            page_title=Settings.PAGE_TITLE,
            page_icon=Settings.PAGE_ICON,
            layout=Settings.PAGE_LAYOUT,
            initial_sidebar_state=Settings.SIDEBAR_STATE
        )
        self.css_loader.load_all_styles()

    def render_header(self):
        st.markdown(
            "<h1 style='text-align:center'>🚌🍁 Maple Mover</h1>"
            "<p style='text-align:center'>Find your perfect TTC route</p>",
            unsafe_allow_html=True
        )
