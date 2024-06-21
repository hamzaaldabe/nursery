import asyncio
import websockets
import cv2
import numpy as np
import json

async def video_stream(websocket, path):
    cap = cv2.VideoCapture(0)  # Adjust the device index if necessary

    if not cap.isOpened():
        print("Error: Unable to open video capture")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        await websocket.send(json.dumps({"type": "video", "data": frame_bytes.hex()}))

start_server = websockets.serve(video_stream, "0.0.0.0", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

