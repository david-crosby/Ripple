#!/bin/zsh

# Quick start script for fundraiser platform backend
# This script sets up and runs the development environment

set -e  # Exit on error

echo "🚀 Starting Fundraiser Platform Backend Setup"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Start MySQL container
echo "📦 Starting MySQL container..."
docker-compose up -d

# Wait for MySQL to be ready
echo "⏳ Waiting for MySQL to be ready..."
sleep 5

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ backend directory not found. Are you in the project root?"
    exit 1
fi

cd backend

# Check if .env exists, if not create from example
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating virtual environment with uv..."
    uv venv
fi

# Activate virtual environment
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install fastapi 'uvicorn[standard]' sqlalchemy pymysql cryptography python-dotenv pydantic pydantic-settings

echo ""
echo "✨ Setup complete! Starting FastAPI server..."
echo ""
echo "Available at:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the server
uvicorn main:app --reload --reload-exclude '.venv/*'