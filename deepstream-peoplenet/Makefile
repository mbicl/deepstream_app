r:
	python3 deepstream_test_3.py -i rtsp://admin:Qwerty12@192.168.0.2 rtsp://admin:Qwerty12@192.168.0.150 --pgie nvinfer -c config_infer_primary_peoplenet.txt

v:
	python3 deepstream_test_3.py -i file:///app/video_3.mp4 --pgie nvinfer -c config_infer_primary_peoplenet.txt

v2:
	python3 deepstream_test_3.py -i file:///app/video.mp4 file:///app/video_3.mp4 --pgie nvinfer -c config_infer_primary_peoplenet.txt

ds:
	python3 deepstream_test_3.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_peoplenet.txt --silent

nd:
	python3 deepstream_test_3.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_peoplenet.txt --no-display

nds:
	python3 deepstream_test_3.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_peoplenet.txt --no-display --silent

g:
	python3 deepstream_test_3.py -i file:///app/video.mp4 --pgie nvinferserver-grpc -c config_triton_grpc_infer_primary_peoplenet.txt

h:
	python3 deepstream_test_3.py -i file:///app/video.mp4 --pgie nvinferserver -c config_triton_infer_primary_peoplenet.txt

y:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinferserver-grpc -c config_triton_grpc_infer_yunet.txt