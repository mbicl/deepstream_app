#!/bin/bash

# Remove the existing container named 'deepstream_app' if it exists
docker rm --force deepstream_app 2>/dev/null

# Run the DeepStream container in detached mode with an interactive bash shell
docker run --runtime=nvidia --gpus all --detach --interactive --tty \
  --name deepstream_app \
  --volume "$(pwd)":/app \
  --workdir /app \
  deepstream_app:latest \
  bash
