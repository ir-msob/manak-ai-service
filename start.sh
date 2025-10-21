#!/bin/bash

# مسیر docker-compose.yml
COMPOSE_FILE="./docker-compose.yml"
docker stop milvus elasticsearch minio etcd
docker rm milvus elasticsearch minio etcd

echo "Starting docker compose file ..."
docker-compose -f $COMPOSE_FILE up -d

echo "Docker compose file started successfully!"

