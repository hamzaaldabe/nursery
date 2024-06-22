import os

import pyaudio
import numpy as np
import wave
import time
import subprocess
from flask import Flask, jsonify

app = Flask(__name__)

# Audio recording parameters
FORMAT = pyaudio.paInt32
CHANNELS = 1
RATE = 44100
CHUNK = 1024
DURATION = 5
THRESHOLD = 5000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "recorded.wav"
timestamps = []

# Initialize PyAudio
p = pyaudio.PyAudio()


def record_sound(filename, duration):
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print(f"Recording {duration} seconds of audio...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"Recording saved to {filename}")


def check_for_cry():
    try:
        current_path = os.getcwd()

        # Construct the command with the current path
        command = [
            'python3',
            'baby_cry_detection/rpi_main/make_prediction.py',
        ]

        # Run the command
        result = subprocess.run(command, capture_output=True, text=True, check=True)

        # Clean the output
        output = result.stdout.strip()
        print("Raw Output:", output)
        return int(output[0])
    except subprocess.CalledProcessError as e:
        print(f"Error running detection script: {e}")
        print("Output:", e.stdout)
        print("Error (if any):", e.stderr)
        return 0


@app.route('/timestamps', methods=['GET'])
def get_timestamps():
    response = jsonify(timestamps)
    timestamps = []
    return response


def listen_for_sound():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Listening for sound...")

    try:
        while True:
            data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)
            max_amplitude = np.max(np.abs(data))

            if max_amplitude > THRESHOLD:
                print(f"Sound detected with amplitude {max_amplitude}")
                record_sound(WAVE_OUTPUT_FILENAME, RECORD_SECONDS)
                if check_for_cry() == 1:
                    timestamps.append(time.strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    print("No baby cry detected.")
    except KeyboardInterrupt:
        print("Stopping listening...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    # Start listening in a separate thread or process if needed
    from threading import Thread

    listener_thread = Thread(target=listen_for_sound)
    listener_thread.start()

    # Start the Flask server
    app.run(debug=True, use_reloader=False)
