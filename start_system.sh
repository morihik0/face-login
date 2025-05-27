#!/bin/bash

# Face Login System - Quick Start Script

echo "🚀 Starting Face Login System..."
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Function to start backend
start_backend() {
    echo "📦 Starting Backend API..."
    cd "$(dirname "$0")"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install backend dependencies
    echo "Installing backend dependencies..."
    pip install -r requirements.txt
    
    # Start Flask app
    echo "Starting Flask API on port 5001..."
    python3 run.py &
    BACKEND_PID=$!
    echo "Backend PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend UI..."
    cd "$(dirname "$0")/frontend"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Start React app
    echo "Starting React app on port 3000..."
    npm start &
    FRONTEND_PID=$!
    echo "Frontend PID: $FRONTEND_PID"
}

# Function to stop all services
stop_all() {
    echo ""
    echo "🛑 Stopping all services..."
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    
    # Kill any remaining processes on ports
    lsof -ti:5001 | xargs kill -9 2>/dev/null
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    
    echo "All services stopped"
    exit 0
}

# Trap Ctrl+C to stop all services
trap stop_all INT

# Start services
start_backend
sleep 5  # Wait for backend to start
start_frontend

echo ""
echo "✅ Face Login System is starting up!"
echo "================================"
echo "Backend API: http://localhost:5001"
echo "Frontend UI: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Keep script running
wait