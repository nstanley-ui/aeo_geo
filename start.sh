#!/bin/bash

# MOJO AEO GEO CHECKER Start Script
# This script starts both the backend and frontend servers

set -e  # Exit on error

echo "======================================================================"
echo "MOJO AEO GEO CHECKER"
echo "======================================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Install Python dependencies if needed
echo "📦 Checking Python dependencies..."
pip3 install -r requirements.txt --quiet

# Install Node dependencies if needed
if [ ! -d "ui/node_modules" ]; then
    echo "📦 Installing Node dependencies..."
    cd ui
    npm install
    cd ..
fi

echo ""
echo "🚀 Starting Backend Server on http://localhost:8000"
echo "🎨 Starting Frontend Server on http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to handle cleanup
cleanup() {
    echo ""
    echo "👋 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start backend in background
python3 server.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
cd ui
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
