"""
Streamlit Cloud Entry Point
This file is required by Streamlit Cloud to find your app
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main app
if __name__ == "__main__":
    from app import MapleMoverApp
    app = MapleMoverApp()
    app.run()

