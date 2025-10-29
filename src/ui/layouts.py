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
        """Render Homepage-style header with logo - exact match"""
        st.markdown(
            '<div style="margin-top: -5rem; margin-bottom: 0; padding: 0;">', 
            unsafe_allow_html=True
        )
        st.markdown("""
        <style>
        /* Remove Streamlit's default padding/margin from top */
        .stApp > header,
        .stApp > div[data-testid="stHeader"] {
            display: none !important;
        }
        /* Remove padding from main content */
        .stApp > div[data-testid="stApp"] {
            padding-top: 0 !important;
        }
        /* Remove extra space from markdown blocks */
        div[data-testid="stMarkdownContainer"]:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="position: sticky; top: 0; z-index: 50; 
                    backdrop-filter: blur(12px);
                    border-bottom: 1px solid #e7e0ec;
                    background: rgba(255, 255, 255, 0.8);
                    margin-top: -2rem;">
            <div style="max-width: 1280px; margin: 0 auto; padding: 0.5rem 1.5rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="display: flex; align-items: center; justify-center; 
                                width: 3rem; height: 3rem; 
                                border-radius: 16px; 
                                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                                background: #6750a4;">
                        <span style="font-size: 1.5rem;">📍</span>
                    </div>
                    <div>
                        <h1 style="margin: 0; font-size: 1.5rem; line-height: 1.5;
                                   color: #1c1b1f; font-weight: 700;">
                            Maple Mover
                        </h1>
                        <p style="margin: 0; font-size: 0.875rem; line-height: 1.25;
                                  color: #49454f;">
                            Canadian Transit
                        </p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
