#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2019-2023 NVIDIA CORPORATION &
#                        AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
################################################################################

import sys
import gi

gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
import pyds

# Change these class IDs / strings according to your model
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3


# Simple function to handle GStreamer Bus Messages (errors, EOS, state changes).
def bus_call(bus, message, loop):
    msg_type = message.type
    if msg_type == Gst.MessageType.EOS:
        print("End of stream")
        loop.quit()
    elif msg_type == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print("Error: %s: %s" % (err, debug))
        loop.quit()
    return True


# Probe function to extract metadata from the `nvinfer` element
def pgie_src_pad_buffer_probe(pad, info, u_data):
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer")
        return Gst.PadProbeReturn.OK

    # Get batch metadata from gst buffer
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        frame_number = frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta

        # Simple object counter (based on class IDs)
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_ROADSIGN: 0,
        }

        l_obj = frame_meta.obj_meta_list
        while l_obj is not None:
            obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            obj_counter[obj_meta.class_id] += 1
            l_obj = l_obj.next
            # Get bounding box coordinates
            rect_params = obj_meta.rect_params
            left = int(rect_params.left)
            top = int(rect_params.top)
            width = int(rect_params.width)
            height = int(rect_params.height)
            print(
                f"Frame={frame_number}, Object={obj_meta.object_id}, "
                f"Class={obj_meta.class_id}, "
                f"Bounding Box=({left},{top}),({left+width},{top+height})"
            )

        # print(f"Frame={frame_number}, Total Objects={num_rects}, "
        #       f"Vehicle={obj_counter[PGIE_CLASS_ID_VEHICLE]}, "
        #       f"Person={obj_counter[PGIE_CLASS_ID_PERSON]}")

        l_frame = l_frame.next
    return Gst.PadProbeReturn.OK


# Called once decodebin creates a new pad for raw video. We link it to streammux sink.
def cb_newpad(decodebin, decoder_src_pad, data):
    print("In cb_newpad")
    caps = decoder_src_pad.get_current_caps()
    if not caps:
        caps = decoder_src_pad.query_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    print("gstname=", gstname)
    if "video" in gstname:
        streammux = data["streammux"]
        sinkpad = streammux.get_request_pad("sink_0")
        if not sinkpad:
            sys.stderr.write(" Unable to create sink pad for streammux.\n")
        decoder_src_pad.link(sinkpad)


def main(input_uri, pgie_config_path):
    # Standard GStreamer initialization
    Gst.init(None)

    # Create the pipeline
    pipeline = Gst.Pipeline()

    # Create elements
    source = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "converter")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")

    if (
        not pipeline
        or not source
        or not streammux
        or not pgie
        or not nvvidconv
        or not nvosd
        or not sink
    ):
        sys.stderr.write(" Unable to create one of the GStreamer elements.\n")
        sys.exit(1)

    # Set element properties
    source.set_property("uri", input_uri)
    # If input is RTSP, consider enabling 'live-source' for low-latency
    if input_uri.startswith("rtsp://"):
        streammux.set_property("live-source", 1)

    # streammux properties
    streammux.set_property("width", 1920)
    streammux.set_property("height", 1080)
    streammux.set_property("batch-size", 1)
    streammux.set_property("batched-push-timeout", 40000)  # microseconds

    # nvinfer config file
    pgie.set_property("config-file-path", pgie_config_path)

    # Add elements to pipeline
    pipeline.add(source)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)
    pipeline.add(sink)

    # Link elements together. The 'source' (uridecodebin) will link dynamically.
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(sink)

    # Connect decodebin pad-added signal
    source.connect("pad-added", cb_newpad, {"streammux": streammux})

    # Add probe to nvinfer's source pad to examine inference results
    pgie_src_pad = pgie.get_static_pad("src")
    if not pgie_src_pad:
        sys.stderr.write(" Unable to get src pad of nvinfer\n")
    else:
        pgie_src_pad.add_probe(Gst.PadProbeType.BUFFER, pgie_src_pad_buffer_probe, 0)

    # Create an event loop and feed GStreamer bus messages to it
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # Start the pipeline
    print("Starting pipeline...")
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except:
        pass

    # Cleanup
    print("Exiting app...")
    pipeline.set_state(Gst.State.NULL)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.stderr.write(
            f"Usage: {sys.argv[0]} <input_uri> <nvinfer_config_file>\n"
            f"Example: {sys.argv[0]} sample_720p.h264 dstest3_pgie_config.txt\n"
        )
        sys.exit(1)

    input_uri = sys.argv[1]
    pgie_config_path = sys.argv[2]
    main(input_uri, pgie_config_path)
# python3 video_infer.py file:///app/sample_720p.mp4 config_video.txt
# python3 deepstream_test_3.py -i "rtsp://192.168.0.242:554/user=admin&password=&channel=1&stream=0.sdp?" --pgie nvinfer -c config_infer_primary_peoplenet.txt
# python3 video_infer.py "rtsp://192.168.0.242:554/user=admin&password=&channel=1&stream=0.sdp?" config_video.txt
