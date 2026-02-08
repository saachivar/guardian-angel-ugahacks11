#!/bin/bash

# Guardian Angel - Receiver Backend Startup Script

echo "🚀 Starting Guardian Angel Receiver Backend..."
echo ""

# Check if requirements are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    echo ""
fi

# Check if main backend is running
echo "🔍 Checking main backend..."
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Main backend is running on port 8000"
else
    echo "⚠️  WARNING: Main backend is not running on port 8000"
    echo "   Please start it in another terminal:"
    echo "   cd ../backend && python3 -m uvicorn main:app --reload --port 8000"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🎯 Starting receiver on port 8001..."
echo "   Access at: http://localhost:8001"
echo "   Health check: http://localhost:8001/health"
echo "   Receive endpoint: http://localhost:8001/receive-fall-detection"
echo ""
echo "📝 Press Ctrl+C to stop"
echo ""

# Start the receiver
python3 -m uvicorn receiver:app --reload --host 0.0.0.0 --port 8001
