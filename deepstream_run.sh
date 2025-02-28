#!/bin/bash

# Remove the existing container named 'deepstream_app' if it exists
docker rm --force deepstream_app 2>/dev/null

# Run the DeepStream container in detached mode with an interactive bash shell
docker run --runtime=nvidia --gpus all --detach --interactive --tty \
  --name deepstream_app \
  -p 8000:8000 \
  -p 8001:8001 \
  -p 8002:8002 \
  --volume "$(pwd)":/app \
  --workdir /app \
  deepstream_app:latest \
  bash
