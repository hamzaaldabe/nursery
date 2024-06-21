import pyaudio
import wave

# Audio recording parameters
FORMAT = pyaudio.paInt16  # 16-bit resolution
CHANNELS = 1              # Mono audio
RATE = 44100              # 44.1kHz sampling rate
CHUNK = 1024              # 1024 samples per frame
RECORD_SECONDS = 5        # Record duration
WAVE_OUTPUT_FILENAME = "recorded.wav"  # Output file name

# Create an interface to PortAudio
audio = pyaudio.PyAudio()

# Open a stream with the audio recording parameters
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("Recording...")

# Initialize an array to store frames of audio data
frames = []

# Loop through stream and append audio chunks to frames array
for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)

print("Finished recording.")

# Stop and close the stream
stream.stop_stream()
stream.close()

# Terminate the PortAudio interface
audio.terminate()

# Save the recorded audio as a WAV file
with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))

print(f"Audio recorded and saved as {WAVE_OUTPUT_FILENAME}")
