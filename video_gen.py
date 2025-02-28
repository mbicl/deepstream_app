import cv2
import sys

def resize_video(input_path, output_path, width=544, height=960):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        sys.exit(1)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 output
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        resized_frame = cv2.resize(frame, (width, height))
        out.write(resized_frame)
    
    cap.release()
    out.release()
    print(f"Video resized and saved to {output_path}")

if __name__ == "__main__":
    input_video = "video.mp4"   # Change this to your input file
    output_video = "generated.mp4" # Change this to your output file
    resize_video(input_video, output_video)