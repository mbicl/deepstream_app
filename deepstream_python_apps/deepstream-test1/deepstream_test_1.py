#!/usr/bin/env python3

################################################################################
# SPDX-FileCopyrightText: Copyright (c) 2019-2023 NVIDIA CORPORATION & 
# AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
################################################################################

import sys
import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, Gst

# DeepStream Python modules
# (Adjust the path or imports if your local environment is different)
sys.path.append('../')
import pyds

def bus_call(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t==Gst.MessageType.WARNING:
        err, debug = message.parse_warning()
        sys.stderr.write("Warning: %s: %s\n" % (err, debug))
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True


# Constants (same as original)
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_BATCH_TIMEOUT_USEC = 33000

def osd_sink_pad_buffer_probe(pad, info, u_data):
    """
    Probe function that gets called at the OSD element’s sink pad.
    We read object metadata and draw text overlays.
    """
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return Gst.PadProbeReturn.OK

    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list

    while l_frame is not None:
        try:
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        # Initialize counting of specific classes
        obj_counter = {
            PGIE_CLASS_ID_VEHICLE: 0,
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_BICYCLE: 0,
            PGIE_CLASS_ID_ROADSIGN: 0
        }

        frame_number = frame_meta.frame_num
        num_rects = frame_meta.num_obj_meta
        l_obj = frame_meta.obj_meta_list

        # Iterate over all detected objects
        while l_obj is not None:
            try:
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1

            # Example: change border color
            obj_meta.rect_params.border_color.set(0.0, 0.0, 1.0, 0.8)

            try:
                l_obj = l_obj.next
            except StopIteration:
                break

        # Acquire a display meta object
        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]

        # Prepare text showing counts
        py_nvosd_text_params.display_text = (
            f"Frame Number={frame_number} Number of Objects={num_rects} "
            f"Vehicle_count={obj_counter[PGIE_CLASS_ID_VEHICLE]} "
            f"Person_count={obj_counter[PGIE_CLASS_ID_PERSON]}"
        )

        # Set text placement / style
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)
        py_nvosd_text_params.set_bg_clr = 1
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)

        # Print the OSD text to console just for demonstration
        print(pyds.get_string(py_nvosd_text_params.display_text))

        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def qtdemux_pad_added_cb(demux, pad, h264parser):
    """
    Callback fired when qtdemux adds a new source pad.
    We link that new pad to the h264parser sink pad.
    """
    caps = pad.query_caps(None)
    caps_str = caps.to_string()

    # If it's video, link to the parser
    if caps_str.startswith("video/"):
        sink_pad = h264parser.get_static_pad("sink")
        if sink_pad is None:
            print("Unable to get h264parser sink pad")
            return

        # Attempt linking
        if pad.link(sink_pad) != Gst.PadLinkReturn.OK:
            print("Failed to link demuxer src pad to h264 parser sink pad")
        else:
            print("qtdemux src pad linked to h264parser sink pad")
    else:
        print("qtdemux: pad type is not video, ignoring")


def main(args):
    # Check input arguments
    if len(args) != 2:
        sys.stderr.write(f"usage: {args[0]} <media file or uri>\n")
        sys.exit(1)

    # Initialize GStreamer
    Gst.init(None)
    # We still use platform_info for demonstration, 
    # though it's no longer used for sink selection:

    # Create Pipeline
    print("Creating Pipeline \n")
    pipeline = Gst.Pipeline()
    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")

    print("Creating Source \n")
    source = Gst.ElementFactory.make("filesrc", "file-source")
    if not source:
        sys.stderr.write(" Unable to create Source \n")

    # Create qtdemux
    print("Creating qtdemux\n")
    demux = Gst.ElementFactory.make("qtdemux", "qt-demux")
    if not demux:
        sys.stderr.write(" Unable to create qtdemux \n")

    print("Creating H264Parser \n")
    h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
    if not h264parser:
        sys.stderr.write(" Unable to create h264 parser \n")

    print("Creating Decoder \n")
    decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
    if not decoder:
        sys.stderr.write(" Unable to create Nvv4l2 Decoder \n")

    # nvstreammux
    print("Creating nvstreammux \n")
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    # nvinfer
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")

    # nvvideoconvert (for OSD input)
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    # nvdsosd
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")

    # -------------------------------------------------------------------------
    #  New: Elements to encode and write to file
    # -------------------------------------------------------------------------
    print("Creating H264 Encoder \n")
    encoder = Gst.ElementFactory.make("nvv4l2h264enc", "h264-encoder")
    if not encoder:
        sys.stderr.write(" Unable to create H264 encoder \n")

    print("Creating H264 Parser (for output) \n")
    h264parser_out = Gst.ElementFactory.make("h264parse", "h264-parse-out")
    if not h264parser_out:
        sys.stderr.write(" Unable to create output H264 parser \n")

    print("Creating MP4 Muxer \n")
    mp4mux = Gst.ElementFactory.make("mp4mux", "mp4-mux")
    if not mp4mux:
        sys.stderr.write(" Unable to create mp4 mux \n")

    print("Creating File Sink \n")
    sink = Gst.ElementFactory.make("filesink", "file-sink")
    if not sink:
        sys.stderr.write(" Unable to create file sink \n")
    # Set the output file location
    sink.set_property("location", "deepstream_output.mp4")
    # Usually we want to ensure it doesn't try to sync or wait for clock:
    sink.set_property("sync", 1)
    sink.set_property("async", 0)

    print("Playing file %s \n" % args[1])
    source.set_property("location", args[1])

    # Configs for streammux
    if os.environ.get('USE_NEW_NVSTREAMMUX') != 'yes':
        streammux.set_property("width", 1920)
        streammux.set_property("height", 1080)
        streammux.set_property("batched-push-timeout", MUXER_BATCH_TIMEOUT_USEC)
    streammux.set_property("batch-size", 1)

    # Set pgie config file
    pgie.set_property(
        "config-file-path",
        "/app/deepstream_python_apps/deepstream-test1/dstest1_pgie_config.yml"
    )

    print("Adding elements to Pipeline \n")
    pipeline.add(source)
    pipeline.add(demux)
    pipeline.add(h264parser)
    pipeline.add(decoder)
    pipeline.add(streammux)
    pipeline.add(pgie)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)

    # Add new file-saving elements
    pipeline.add(encoder)
    pipeline.add(h264parser_out)
    pipeline.add(mp4mux)
    pipeline.add(sink)

    print("Linking elements in the Pipeline \n")
    # Link file-source → qtdemux (static link)
    source.link(demux)

    # Dynamically link qtdemux → h264parser (via pad-added signal)
    demux.connect("pad-added", qtdemux_pad_added_cb, h264parser)

    # Now link h264parser → decoder (static link)
    h264parser.link(decoder)

    # Link decoder output to streammux sink_0
    sinkpad = streammux.request_pad_simple("sink_0")
    if not sinkpad:
        sys.stderr.write("Unable to get the sink pad of streammux \n")
    srcpad = decoder.get_static_pad("src")
    if not srcpad:
        sys.stderr.write("Unable to get source pad of decoder \n")
    srcpad.link(sinkpad)

    # Link further downstream:
    # streammux → pgie → nvvideoconvert → nvdsosd → encoder → h264parser_out → mp4mux → filesink
    streammux.link(pgie)
    pgie.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(encoder)
    encoder.link(h264parser_out)
    h264parser_out.link(mp4mux)
    mp4mux.link(sink)

    # Create event loop and handle gstreamer messages
    loop = GLib.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)

    # Add probe to the OSD sink pad, so we can read object metadata
    osdsinkpad = nvosd.get_static_pad("sink")
    if not osdsinkpad:
        sys.stderr.write(" Unable to get sink pad of nvosd \n")
    osdsinkpad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    print("Starting pipeline \n")
    pipeline.set_state(Gst.State.PLAYING)

    try:
        loop.run()
    except:
        pass

    # Cleanup
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
