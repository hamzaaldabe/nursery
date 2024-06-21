import asyncio
from aiortc import RTCPeerConnection, VideoStreamTrack
from picamera2 import Picamera2, Preview
from av import VideoFrame
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CameraVideoTrack(VideoStreamTrack):
    def __init__(self, camera):
        super().__init__()
        self.camera = camera

    async def recv(self):
        logger.debug('Capturing video frame')
        frame = VideoFrame.from_ndarray(self.camera.capture_array(), format="rgb24")
        frame.pts = time.time_ns() // 1000
        frame.time_base = 1_000_000
        return frame

async def run_sender():
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
    picam2.start()
    logger.info("Camera started with preview configuration")

    pc = RTCPeerConnection()

    video_track = CameraVideoTrack(picam2)
    pc.addTrack(video_track)
    logger.info("Video track added to PeerConnection")

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            logger.info("ICE connection failed, PC closed")

    # Keep the event loop running to maintain the WebRTC connection and camera stream
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(run_sender())
