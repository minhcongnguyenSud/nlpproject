#!/bin/bash

# AI Newsletter Generator - Docker Setup Script

set -e

echo " AI Newsletter Generator Docker Setup"
echo "======================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "  .env file not found!"
    echo "📋 Creating .env file from template..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo " Created .env file from .env.example"
        echo " Please edit .env and add your MISTRAL_API_KEY"
        echo ""
        echo "To get your Mistral AI API key:"
        echo "1. Go to https://console.mistral.ai/"
        echo "2. Create an account or sign in"
        echo "3. Generate an API key"
        echo "4. Add it to your .env file"
        echo ""
        read -p "Press Enter once you've added your API key to .env..."
    else
        echo " .env.example not found. Please create .env manually with:"
        echo "MISTRAL_API_KEY=your_api_key_here"
        exit 1
    fi
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo " Docker is not running. Please start Docker and try again."
    exit 1
fi

echo " Building Docker containers..."
docker-compose build

echo " Starting services..."
docker-compose up -d

echo ""
echo " Setup complete!"
echo ""
echo "Dashboard: http://localhost:8080"
echo " Newsletters: http://localhost:8081"
echo ""
echo "🔍 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo "  To rebuild: docker-compose build --no-cache"
