#!/bin/bash

# مسیر docker-compose.yml
COMPOSE_FILE="./docker-compose.yml"

echo "Starting docker compose file ..."
docker-compose -f $COMPOSE_FILE up -d

echo "Docker compose file started successfully!"

