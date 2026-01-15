#!/bin/bash

echo "================================================"
echo " Agentic AI Enterprise - Startup Script"
echo "================================================"
echo ""

# Activate virtual environment or create it
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing dependencies..."
    pip install -r requirement.txt
else
    source venv/bin/activate
fi

echo ""
echo "================================================"
echo "Starting Services..."
echo "================================================"
echo ""

# Start Flask API in background
echo "Starting Flask API server on http://localhost:5000"
python api.py &
FLASK_PID=$!

# Wait for Flask to start
sleep 3

# Start Streamlit app
echo "Starting Streamlit app on http://localhost:8501"
streamlit run app.py

# Cleanup on exit
trap "kill $FLASK_PID" EXIT
