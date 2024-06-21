# rtsp_server.py
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class RTSPServer:
    def __init__(self):
        Gst.init(None)
        self.server = GstRtspServer.RTSPServer()
        self.factory = GstRtspServer.RTSPMediaFactory()
        self.factory.set_launch(
            "( udpsrc port=5000 caps=\"application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96 \" ! "
            "rtph264depay ! h264parse ! rtph264pay name=pay0 pt=96 udpsrc port=5001 caps=\"application/x-rtp, media=(string)audio, clock-rate=(int)48000, encoding-name=(string)OPUS, payload=(int)97 \" ! "
            "rtpopusdepay ! opusparse ! rtpopuspay name=pay1 pt=97 )"
        )
        self.factory.set_shared(True)
        self.server.get_mount_points().add_factory("/test", self.factory)
        self.server.attach(None)

    def run(self):
        loop = GLib.MainLoop()
        loop.run()

if __name__ == "__main__":
    server = RTSPServer()
    server.run()
