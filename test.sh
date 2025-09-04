#!/bin/bash

# A simple script to manage the local test environment

if [ "$1" == "up" ]; then
    docker-compose up --build -d

elif [ "$1" == "down" ]; then
    docker-compose down

elif [ "$1" == "logs" ]; then
    docker-compose logs -f api-core

else
    echo "Usage: ./test.sh [up|down|logs]"
fi
