#!/bin/bash
# Quick start script

echo "🚀 Starting Text-to-SQL Agent Backend"
echo ""

# Check if virtual environment exists
if [ ! -d .venv ]; then
    echo "🔧 Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Check if data directory exists
if [ ! -d data ]; then
    echo "📁 Creating data directory..."
    mkdir -p data
fi

# Initialize databases if they don't exist
if [ ! -f data/history.db ]; then
    echo "🔧 Initializing databases..."
    python -m app.database.init_db
fi

echo ""
echo "✅ Starting server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""

# Start server
uvicorn app.main:app --reload --port 8000
