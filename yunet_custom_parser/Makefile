TARGET_LIB = libnvdsinfer_customyunet.so

CXX = g++
CXXFLAGS = -Wall -shared -fPIC -std=c++20 -O2

# DeepStream and TensorRT include paths (adjust paths as necessary)
CUDA_HOME ?= /usr/local/cuda
TRT_INC ?= /usr/include/x86_64-linux-gnu
DS_INC ?= /opt/nvidia/deepstream/deepstream/sources/includes

INCLUDES = -I$(CUDA_HOME)/include -I$(TRT_INC) -I$(DS_INC)
LIBS = -L$(CUDA_HOME)/lib64 -lnvinfer

SRC = yunet_custom_parser.cpp
OBJ = $(SRC:.cpp=.o)

all: $(TARGET_LIB)

$(TARGET_LIB): $(OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LIBS)

%.o: %.cpp
	$(CXX) $(CXXFLAGS) $(INCLUDES) -c $< -o $@

clean:
	rm -f $(OBJ) $(TARGET_LIB)
