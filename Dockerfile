# Use NVIDIA DeepStream 7.1 GC Triton development image
FROM nvcr.io/nvidia/deepstream:7.1-gc-triton-devel

# Set working directory
WORKDIR /app
COPY . .

# Run the script to build Python bindings
RUN /bin/bash -c "/opt/nvidia/deepstream/deepstream-7.1/user_deepstream_python_apps_install.sh --build-bindings"

# Check Python bindings
# RUN python3 -c "import pyds"

# install updates and necessary packages
RUN apt update && apt upgrade -y && \
    apt-get install -y \
      libgstreamer1.0-dev \
      libgstreamer-plugins-base1.0-dev \
      libgstreamer-plugins-bad1.0-dev \
      gstreamer1.0-plugins-base \
      gstreamer1.0-plugins-good \
      gstreamer1.0-plugins-bad \
      gstreamer1.0-plugins-ugly \
      gstreamer1.0-libav \
      gstreamer1.0-tools \
      gstreamer1.0-x \
      gstreamer1.0-alsa \
      gstreamer1.0-gl \
      gstreamer1.0-gtk3 \
      gstreamer1.0-qt5 \
      gstreamer1.0-pulseaudio \
      libavcodec58 \
      mjpegtools \
      ffmpeg && \
    apt-get clean
# Set the entrypoint

CMD [ "/bin/bash" ]
