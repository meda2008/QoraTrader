#!/bin/bash

# Deployment script for QoraTrader Production Environment
set -e  # Exit on any error

echo "Starting QoraTrader production deployment..."

# Check if docker and docker-compose are installed
if ! [ -x "$(command -v docker)" ]; then
  echo "Error: docker is not installed." >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ]; then
  echo "Error: docker-compose is not installed." >&2
  exit 1
fi

# Build and start the services using production docker-compose file
if [ -f "docker/docker-compose.prod.yml" ]; then
    docker-compose -f docker/docker-compose.prod.yml up --build -d
else
    echo "Production docker-compose file not found, using default"
    docker-compose -f docker/docker-compose.yml up --build -d
fi

echo "QoraTrader deployed successfully!"
echo "Services are now running in production mode."