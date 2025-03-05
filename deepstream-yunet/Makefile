r:
	python3 yunet_test.py -i rtsp://admin:Qwerty12@192.168.0.2 rtsp://admin:Qwerty12@192.168.0.150 --pgie nvinfer -c config_infer_primary_yunet.txt

v:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_yunet.txt

v2:
	python3 yunet_test.py -i file:///app/video.mp4 file:///app/video_3.mp4 --pgie nvinfer -c config_infer_primary_yunet.txt

ds:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_yunet.txt --silent

nd:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_yunet.txt --no-display

nds:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinfer -c config_infer_primary_yunet.txt --no-display --silent

g:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinferserver-grpc -c config_triton_grpc_infer_primary_yunet.txt

h:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinferserver -c config_triton_infer_primary_yunet.txt --no-display

y:
	python3 yunet_test.py -i file:///app/video.mp4 --pgie nvinferserver-grpc -c config_triton_grpc_infer_yunet.txt