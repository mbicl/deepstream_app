#!/bin/bash

# Output file name
OUTPUT_FILE="output.mp4"

# Run GStreamer pipeline
gst-launch-1.0 videotestsrc num-buffers=300 ! \
    videoconvert ! \
    nvvideoconvert ! \
    nvv4l2h264enc ! \
    h264parse ! \
    mp4mux ! \
    filesink location=$OUTPUT_FILE