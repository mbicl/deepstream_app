#!/bin/bash

echo "removing old *.engine files"
rm ./peoplenet/*.engine
rm ./yunet/*.engine

echo "building engines"
trtexec \
    --onnx=./peoplenet/resnet34_peoplenet_int8.onnx --int8 \
    --calib=./peoplenet/resnet34_peoplenet_int8.txt \
    --saveEngine=./peoplenet/resnet34_peoplenet_int8.onnx_b2_gpu0_int8.engine \
    --minShapes="input_1:0":1x3x544x960 \
    --optShapes="input_1:0":2x3x544x960 \
    --maxShapes="input_1:0":2x3x544x960

trtexec \
    --onnx=./yunet/model.onnx \
    --saveEngine=./yunet/model.engine \
    --fp16