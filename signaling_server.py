import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
from flask import Flask
from flask_socketio import SocketIO, emit
import eventlet
import logging

eventlet.monkey_patch()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet')
pcs = {}

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('offer')
def on_offer(data):
    logger.info('Received offer: %s', data)
    pc = RTCPeerConnection()
    pc_id = data['id']
    pcs[pc_id] = pc

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        logger.info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            del pcs[pc_id]
            logger.info("ICE connection failed, PC closed and discarded")

    @pc.on("track")
    def on_track(track):
        logger.info("Track %s received", track.kind)

    offer = RTCSessionDescription(sdp=data['sdp'], type=data['type'])

    async def run():
        logger.debug('Setting remote description')
        await pc.setRemoteDescription(offer)
        logger.debug('Creating answer')
        answer = await pc.createAnswer()
        logger.debug('Setting local description')
        await pc.setLocalDescription(answer)
        emit('answer', {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type, 'id': pc_id})
        logger.info('Sent answer: %s', {'sdp': pc.localDescription.sdp, 'type': pc.localDescription.type})

    asyncio.ensure_future(run())

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    logger.info('Received ICE candidate: %s', data)
    pc_id = data['id']
    candidate = RTCIceCandidate(sdpMid=data['sdpMid'], sdpMLineIndex=data['sdpMLineIndex'], candidate=data['candidate'])
    pc = pcs.get(pc_id)
    if pc:
        pc.addIceCandidate(candidate)
        logger.debug('Added ICE candidate to PeerConnection')

@app.route('/')
def index():
    return 'WebRTC Signaling Server is running.'

if __name__ == '__main__':
    logger.info('Starting WebRTC signaling server...')
    socketio.run(app, host='0.0.0.0', port=5000)
