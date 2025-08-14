#!/bin/bash

# Docker copy script to copy model files from running container to local app/model
# Usage: ./docker-cp.sh [container_name]

# Default container name (from docker-compose)
CONTAINER_NAME=${1:-"phdata-api-1"}

# Source and destination paths
CONTAINER_PATH="/src/app/model"
LOCAL_PATH="app/model"

echo "Copying files from container '$CONTAINER_NAME'..."
echo "Source: $CONTAINER_NAME:$CONTAINER_PATH"
echo "Destination: $LOCAL_PATH"

# Create local directory if it doesn't exist
mkdir -p "$LOCAL_PATH"

# Copy all files from container model directory
docker cp "$CONTAINER_NAME:$CONTAINER_PATH/." "$LOCAL_PATH/"

echo "Files copied successfully!"
echo "Contents of $LOCAL_PATH:"
ls -la "$LOCAL_PATH"
