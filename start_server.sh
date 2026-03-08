#!/bin/bash
# Quick Start Script for LeRobot Django App

echo "========================================="
echo "  LeRobot Django App - Quick Start"
echo "========================================="
echo ""

# Activate virtual environment
echo "→ Activating virtual environment..."
source .venv/bin/activate

# Check if LeRobot is installed
echo "→ Checking LeRobot installation..."
python -c "import lerobot; print(f'✅ LeRobot version: {lerobot.__version__}')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️  LeRobot not found. Installing..."
    pip install lerobot
fi

# Start Django development server
echo ""
echo "→ Starting Django server..."
echo "→ Open your browser to: http://127.0.0.1:8000"
echo "→ Robot Connection: http://127.0.0.1:8000/connect/"
echo ""
echo "→ API Endpoints:"
echo "   POST http://127.0.0.1:8000/api/robot/connect/"
echo "   GET  http://127.0.0.1:8000/api/robot/status/"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

python manage.py runserver
