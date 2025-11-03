#!/bin/bash

# Startup script for ParagonAI Backend

echo "Starting ParagonAI Backend..."

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "MongoDB is not running. Starting MongoDB..."
    # Try to start MongoDB (adjust for your system)
    if command -v brew > /dev/null; then
        brew services start mongodb-community 2>/dev/null || mongod --fork --logpath /tmp/mongod.log
    elif command -v systemctl > /dev/null; then
        sudo systemctl start mongod
    else
        echo "Please start MongoDB manually"
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please update .env with your credentials"
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Run the application
echo "Starting FastAPI server..."
python main.py

