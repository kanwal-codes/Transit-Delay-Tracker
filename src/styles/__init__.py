import streamlit as st
import os

class CSSLoader:
    """Load all local CSS styles into Streamlit"""

    def __init__(self):
        self.base = os.path.dirname(__file__)

    def load_all_styles(self):
        for css in ["main.css", "components.css", "themes.css", "transit.css"]:
            f = os.path.join(self.base, css)
            if os.path.exists(f):
                with open(f) as fh:
                    st.markdown(f"<style>{fh.read()}</style>", unsafe_allow_html=True)
