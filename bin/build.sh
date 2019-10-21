#!/bin/bash

script="$0"
FOLDER="$(dirname $script)"

TOKEN=$1

source $FOLDER/shared.sh
PROJECT_ROOT="$(abspath $FOLDER/..)"

echo "Building Docker image now..."

docker build --build-arg GITHUB_TOKEN="$TOKEN" \
             -f $PROJECT_ROOT/Dockerfile \
             -t $IMAGE_NAME \
             $PROJECT_ROOT