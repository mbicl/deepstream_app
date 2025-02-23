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

    # Create the empty pipeline
    pipeline = Gst.Pipeline.new("Custom-Pipeline")

    # Create the elements
    source = Gst.ElementFactory.make("videotestsrc", "source")
    videoconvert = Gst.ElementFactory.make("videoconvert", "video-convert")
    nvvideoconvert = Gst.ElementFactory.make("nvvideoconvert", "nvvideo-convert")
    encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
    parse = Gst.ElementFactory.make("h264parse", "parse")
    mux = Gst.ElementFactory.make("mp4mux", "mux")
    sink = Gst.ElementFactory.make("filesink", "sink")
    
    # Add elements to the pipeline
    pipeline.add(source)
    pipeline.add(videoconvert)
    pipeline.add(nvvideoconvert)
    pipeline.add(encoder)
    pipeline.add(parse)
    pipeline.add(mux)
    pipeline.add(sink)

    # Link the elements together
    source.link(videoconvert)
    videoconvert.link(nvvideoconvert)
    nvvideoconvert.link(encoder)
    encoder.link(parse)
    parse.link(mux)
    mux.link(sink)

    # Set elements properties
    source.set_property("num-buffers", 300)
    sink.set_property("location", "output.mp4")

    # Start playing
    pipeline.set_state(Gst.State.PLAYING)
    
    print("Pipeline is running, saving file to output.mp4...")

    # Wait until an error or End-Of-Stream (EOS) message is received
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(
        Gst.CLOCK_TIME_NONE,
        Gst.MessageType.ERROR | Gst.MessageType.EOS
    )

    # Clean up
    pipeline.set_state(Gst.State.NULL)

    if msg:
        error, debug = msg.parse_error()
        print("Error: %s: %s" % (error, debug))
    else:
        print("End-of-stream")

    

    
       

if __name__ == "__main__":
    main()
