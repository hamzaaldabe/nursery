import asyncio
import websockets
import cv2
import numpy as np
from picamera2 import Picamera2, Preview

async def video_stream(websocket, path):
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(main={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    try:
        while True:
            frame = picam2.capture_array()
            _, buffer = cv2.imencode('.jpg', frame)
            
            await websocket.send(buffer.tobytes())
            
            await asyncio.sleep(0.00001)
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    finally:
        picam2.stop()
        picam2.close()

async def main():
    async with websockets.serve(video_stream, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
