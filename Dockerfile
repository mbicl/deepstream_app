# Use NVIDIA DeepStream 7.1 GC Triton development image
FROM nvcr.io/nvidia/deepstream:7.1-gc-triton-devel

# Set working directory
WORKDIR /app

# Run the script to build Python bindings
RUN /bin/bash -c "/opt/nvidia/deepstream/deepstream-7.1/user_deepstream_python_apps_install.sh --build-bindings"

# Check Python bindings
# RUN python3 -c "import pyds"

# Set the entrypoint

CMD [ "/bin/bash" ]
