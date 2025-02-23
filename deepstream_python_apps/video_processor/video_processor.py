import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import numpy as np
import time

def on_end_of_stream(bus, message, loop,start_time):
    """
    Called when EOS (End of Stream) message is posted on the bus.
    """
    end_time = time.time()
    print("Readed End of Stream")
    print(f"Total time: {end_time - start_time}")
def on_new_sample(sink):
    """Callback triggered when a new sample is ready from appsink."""
    sample = sink.emit("pull-sample")
    if not sample:
        return Gst.FlowReturn.ERROR

    # Get the buffer from the sample
    buf = sample.get_buffer()
    caps = sample.get_caps()

    # Map the buffer data (i.e., get the actual bytes of the frame)
    result, map_info = buf.map(Gst.MapFlags.READ)
    if not result:
        return Gst.FlowReturn.ERROR
    
    # Get the frame dimensions
    width = caps.get_structure(0).get_value("width")
    height = caps.get_structure(0).get_value("height")
    print(f"Width: {width}, Height: {height}")

    try:
        frame_data = map_info.data
        # Since we've requested 'video/x-raw, format=RGBA' or 'RGB',
        # we can interpret it as an 8-bit array
        frame = np.frombuffer(frame_data, dtype=np.uint8)
        print("Raw frame shape:", frame.shape)
        
        # You can reshape based on width/height if needed
        # e.g. frame = frame.reshape((height, width, 4))  # if RGBA
    finally:
        buf.unmap(map_info)

    return Gst.FlowReturn.OK

def main():
    Gst.init(None)

    # 
    # Pipeline Explanation:
    #   1. filesrc reads the MP4 file
    #   2. qtdemux extracts the video stream
    #   3. h264parse ensures we have a proper H.264 stream
    #   4. nvv4l2decoder uses NVDEC hardware decoding
    #   5. nvvideoconvert converts from NVMM memory to standard CPU memory
    #   6. video/x-raw, format=RGBA (or RGB) ensures we have raw 8-bit frames
    #   7. appsink pulls frames into this Python code
    #
    pipeline_str = (
        "filesrc location=/app/sample_720p.mp4 ! "
        "qtdemux ! "
        "h264parse ! "
        "nvv4l2decoder ! "
        "nvvideoconvert ! "
        "video/x-raw,format=RGBA ! "
        "appsink name=mysink emit-signals=true sync=false"
    )

    pipeline = Gst.parse_launch(pipeline_str)

    # Grab appsink element by name
    sink = pipeline.get_by_name("mysink")
    # Connect the callback for new samples
    sink.connect("new-sample", on_new_sample)

    # Start playing
    pipeline.set_state(Gst.State.PLAYING)

    #Record the start time now that the pipeline is playing
    start_time = time.time()
    # Create a main loop
    loop = GLib.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", on_end_of_stream, loop, start_time)

    try:
        loop.run()
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)

if __name__ == "__main__":
    main()
