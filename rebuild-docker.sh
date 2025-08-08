#!/bin/bash

# This script creates a fresh build from scratch

echo "Stopping any running containers..."
docker-compose down

echo "Pruning all unused Docker objects to free up space..."
docker system prune -a -f

echo "Rebuilding containers from scratch..."
docker-compose build --no-cache

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
