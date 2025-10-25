import streamlit as st
import os

class CSSLoader:
    """Loads CSS files from styles directory"""

    def __init__(self):
        self.path = os.path.dirname(__file__)

    def load_all_styles(self):
        for css in ["main.css", "components.css", "themes.css", "transit.css"]:
            f = os.path.join(self.path, css)
            if os.path.exists(f):
                with open(f) as c:
                    st.markdown(f"<style>{c.read()}</style>", unsafe_allow_html=True)
