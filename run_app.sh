#!/bin/bash
# File: run_app.sh
# MapleMover - Easy app launcher

echo "🚀 Starting MapleMover..."
echo "📍 Location: $(pwd)"
echo "🐍 Activating virtual environment..."

# Activate virtual environment
source venv/bin/activate

echo "🌐 Starting Streamlit app on port 8501..."
echo "👉 Open your browser to: http://localhost:8501"
echo ""

# Run the app
python -m streamlit run app.py



