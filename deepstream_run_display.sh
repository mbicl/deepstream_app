#!/bin/bash

# Remove the existing container named 'deepstream_app' if it exists
docker rm --force mbi_deepstream_app_display 2>/dev/null
# Allow the root user to connect to the X server
xhost +local:root 
# Run the DeepStream container in detached mode with an interactive bash shell
docker run --runtime=nvidia --gpus all --detach --interactive --tty \
  --env DISPLAY=$DISPLAY \
  --volume /tmp/.X11-unix:/tmp/.X11-unix \
  --name mbi_deepstream_app_display \
  -p 9000:9000 \
  --volume "$(pwd)":/app \
  --workdir /app \
  deepstream_app:latest \
  bash
