#!/bin/bash

# Stop any running containers
echo "Stopping existing Docker containers..."
docker-compose down

# Rebuild the containers with the new changes
echo "Rebuilding containers with new changes..."
docker-compose build --no-cache

# Start the services
echo "Starting services..."
docker-compose up -d

echo ""
echo "==================================================="
echo "🚀 Newsletter Generator is running!"
echo "Access the dashboard at: http://localhost:8080"
echo "View generated newsletters at: http://localhost:8081"
echo "==================================================="
echo ""
echo "To check logs: docker-compose logs -f"
echo "To stop: docker-compose down"
