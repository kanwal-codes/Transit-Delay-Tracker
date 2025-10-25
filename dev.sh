#!/bin/bash
# File: dev.sh
# MapleMover - Development mode with auto-reload

echo "🚀 Starting MapleMover in Development Mode..."
echo "📍 Location: $(pwd)"
echo "🔄 Auto-reload: ENABLED"
echo "🐍 Activating virtual environment..."

# Activate virtual environment
source venv/bin/activate

echo "🌐 Starting Streamlit app with auto-reload..."
echo "👉 Open your browser to: http://localhost:8501"
echo "💡 Save any file to automatically reload the app!"
echo ""

# Run the app with auto-reload
python -m streamlit run src/app.py
