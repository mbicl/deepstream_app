import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstBase', '1.0')
from gi.repository import Gst, GLib, GObject, GstBase
import numpy as np

# Initialize GStreamer
Gst.init(None)
class NumpySrc(GstBase.BaseSrc):
    __gstmetadata__ = ('NumpySrc', 'Source', 'Generates video frames from a numpy array', 'Author')
    __gsttemplates__ = Gst.PadTemplate.new('src', Gst.PadDirection.SRC, Gst.PadPresence.ALWAYS, Gst.Caps.from_string('video/x-raw,format=RGB,width=320,height=240,framerate=30/1'))

    def __init__(self):
        super(NumpySrc, self).__init__()
        self.set_live(True)
        self.frame_count = 0
        
        self.width = 320
        self.height = 240
        self.fps = 30
        self.format = 'RGB'

    def do_start(self):
        self.frame_count = 0
        return True

    def do_stop(self):
        print("Frame count:", self.frame_count)
        return True

    def do_fill(self, offset, length, buf):
        

        frame = np.full((self.height, self.width, 3), 0, dtype=np.uint8)
        data = frame.tobytes()

        buf.set_size(len(data))
        buf.fill(0, data)

        self.frame_count += 1
        return Gst.FlowReturn.OK

GObject.type_register(NumpySrc)
Gst.Element.register(None, 'numpy_src', 0, NumpySrc)



def main(image_path):
    # gst-launch-1.0 videotestsrc num-buffers=1 ! videoconvert ! jpegenc ! filesink location=frame.jpg
    # - Generate a single frame of synthetic video
    # - Convert the video format to JPEG
    # - Save the JPEG frame to a file
    # Create the empty pipeline
    pipeline = Gst.Pipeline.new("Custom-Pipeline")
    
    # Create the elements
    source = Gst.ElementFactory.make("numpy_src", "source")

    videoconvert = Gst.ElementFactory.make("videoconvert", "video-convert")
    jpegenc = Gst.ElementFactory.make("jpegenc", "jpeg-enc")
    sink = Gst.ElementFactory.make("filesink", "sink")

    # Add elements to the pipeline
    print("Adding elements to pipeline")
    pipeline.add(source)
    pipeline.add(videoconvert)
    pipeline.add(jpegenc)
    pipeline.add(sink)

    # Configure the elements
    source.set_property("num-buffers", 1) # Generate a single frame
    sink.set_property("location", image_path) # Save the frame to the specified image path


    # Link the elements together
    print("Linking elements together")
    if not source.link(videoconvert):
        print("ERROR: Could not link source to videoconvert")
    if not videoconvert.link(jpegenc):
        print("ERROR: Could not link videoconvert to jpegenc")
    if not jpegenc.link(sink):
        print("ERROR: Could not link jpegenc to sink")

    # Wait until the pipeline finishes
    print("Running pipeline")
    pipeline.set_state(Gst.State.PLAYING)
    bus = pipeline.get_bus()
    msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)
    pipeline.set_state(Gst.State.NULL)
    print("Pipeline run complete")
    

if __name__ == "__main__":
    if not sys.argv[1:]:
        print("Usage: python3 save_image.py <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    main(image_path)