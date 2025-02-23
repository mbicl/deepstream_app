import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib

# Initialize GStreamer
Gst.init(None)

def main():
    # Define a pipeline that:
    # - Generates a test video (videotestsrc) with 300 frames.
    # - Converts video format to a common raw format (videoconvert).
    # - Encodes the video with x264enc.
    # - Muxes the encoded stream into an MP4 container (mp4mux).
    # - Writes the output to a file using filesink.
    pipeline_description = (
        "videotestsrc num-buffers=300 ! "
        "videoconvert ! "
        "nvvideoconvert ! "
        "nvv4l2h264enc ! "
        "h264parse ! "
        "mp4mux ! "
        "filesink location=output.mp4"
    )
    
    print("Pipeline:", pipeline_description)
    
    # Create the pipeline from the description string
    pipeline = Gst.parse_launch(pipeline_description)
    
    # Start playing the pipeline
    pipeline.set_state(Gst.State.PLAYING)
    print("Pipeline is running, saving file to output.mp4...")
    
    # Wait until an error or End-Of-Stream (EOS) message is received
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(
        Gst.CLOCK_TIME_NONE,
        Gst.MessageType.ERROR | Gst.MessageType.EOS
    )
    
    # Process the message
    if msg:
        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            print(f"Error: {err}\nDebug Info: {debug}")
        elif msg.type == Gst.MessageType.EOS:
            print("End-Of-Stream reached. File saved as 'output.mp4'.")
    
    # Stop the pipeline and free resources
    pipeline.set_state(Gst.State.NULL)
    print("Pipeline stopped.")

if __name__ == "__main__":
    main()
