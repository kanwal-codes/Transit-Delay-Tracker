"""
Streamlit Cloud Entry Point
This file is required by Streamlit Cloud to find your app
"""
import sys
import os
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now we can import from src
import app

# Run the main app
if __name__ == "__main__":
    app.MapleMoverApp().run()

