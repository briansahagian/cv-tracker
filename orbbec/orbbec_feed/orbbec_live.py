"""
Live RGB-D feed for the Orbbec Astra via OpenNI2.

Usage:
    python orbbec_live.py             # live window (color | depth), q/ESC to quit
    python orbbec_live.py --snapshot  # grab a few frames, save snapshot.png, exit
"""
import os
import sys
import numpy as np
import cv2
from openni import openni2, _openni2 as c_api

REDIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openni2", "sdk", "libs")

WIDTH, HEIGHT, FPS = 640, 480, 30
DEPTH_MAX_MM = 5000  # depth beyond this clamps to the far end of the colormap


def try_set_mode(stream, pixel_format):
    """Set 640x480@30 if the device offers it; otherwise keep the default mode."""
    try:
        stream.set_video_mode(c_api.OniVideoMode(
            pixelFormat=pixel_format, resolutionX=WIDTH, resolutionY=HEIGHT, fps=FPS))
    except Exception as e:
        print(f"  (using default video mode; {WIDTH}x{HEIGHT}@{FPS} not set: {e})")


def open_streams():
    openni2.initialize(REDIST)
    dev = openni2.Device.open_any()
    info = dev.get_device_info()
    name = info.name.decode() if isinstance(info.name, bytes) else info.name
    print(f"Connected: {name} ({info.vendor.decode() if isinstance(info.vendor, bytes) else info.vendor})")

    depth = dev.create_depth_stream()
    color = dev.create_color_stream()
    try_set_mode(depth, c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_1_MM)
    try_set_mode(color, c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888)

    # align depth onto the color camera and time-sync the two streams
    try:
        dev.set_image_registration_mode(c_api.OniImageRegistrationMode.ONI_IMAGE_REGISTRATION_DEPTH_TO_COLOR)
        dev.set_depth_color_sync_enabled(True)
    except Exception as e:
        print(f"  (registration/sync not enabled: {e})")

    depth.start()
    color.start()
    return dev, depth, color


def read_color(color):
    f = color.read_frame()
    rgb = np.frombuffer(f.get_buffer_as_uint8(), dtype=np.uint8).reshape(f.height, f.width, 3)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def read_depth(depth):
    f = depth.read_frame()
    d = np.frombuffer(f.get_buffer_as_uint16(), dtype=np.uint16).reshape(f.height, f.width)
    return d


def colorize_depth(d):
    clamped = np.clip(d, 0, DEPTH_MAX_MM).astype(np.float32)
    vis = (clamped / DEPTH_MAX_MM * 255).astype(np.uint8)
    vis = cv2.applyColorMap(vis, cv2.COLORMAP_JET)
    vis[d == 0] = (0, 0, 0)  # no-data pixels black
    return vis


def compose(color_bgr, depth_bgr):
    h = min(color_bgr.shape[0], depth_bgr.shape[0])
    def fit(img):
        scale = h / img.shape[0]
        return cv2.resize(img, (int(img.shape[1] * scale), h))
    return np.hstack([fit(color_bgr), fit(depth_bgr)])


def main():
    snapshot = "--snapshot" in sys.argv
    dev, depth, color = open_streams()
    try:
        if snapshot:
            # discard a few warm-up frames, then save
            for _ in range(10):
                c = read_color(color)
                d = read_depth(depth)
            out = compose(c, colorize_depth(d))
            nz = d[d > 0]
            print(f"depth frame {d.shape}: valid={nz.size} "
                  f"min={nz.min() if nz.size else 0}mm max={nz.max() if nz.size else 0}mm")
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshot.png")
            cv2.imwrite(path, out)
            print("saved", path)
            return

        print("Live feed running. Press q or ESC in the window to quit.")
        win = "Orbbec Astra  -  Color | Depth"
        cv2.namedWindow(win, cv2.WINDOW_NORMAL)
        while True:
            frame = compose(read_color(color), colorize_depth(read_depth(depth)))
            cv2.imshow(win, frame)
            k = cv2.waitKey(1) & 0xFF
            if k in (ord('q'), 27) or cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                break
        cv2.destroyAllWindows()
    finally:
        depth.stop()
        color.stop()
        dev.close()
        openni2.unload()


if __name__ == "__main__":
    main()
