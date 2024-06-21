import asyncio
import websockets
import cv2
import logging

logging.basicConfig(level=logging.INFO)

async def video_stream(websocket, path):
    logging.info("Client connected")
    try:
        cap = cv2.VideoCapture(0)  # 0 is the default camera
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 24)

        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Failed to capture image")
                break

            _, buffer = cv2.imencode('.jpg', frame)
            stream = buffer.tobytes()
            await websocket.send(stream)
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cap.release()
        logging.info("Client disconnected")

async def main():
    async with websockets.serve(video_stream, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())

