import os
import wave
import pyaudio
from pydub import AudioSegment

# Directories
source_directory = '/home/hamza/Desktop/hamza/ayahpi/nursery/baby_cry_detection/data/301 - Crying baby'
destination_directory = '/home/hamza/Desktop/hamza/ayahpi/nursery/baby_cry_detection/data/aug_crying'

# Initialize PyAudio
p = pyaudio.PyAudio()


def play_and_record(file_path, output_path):
    # Convert the file to 32-bit PCM format using pydub
    audio = AudioSegment.from_file(file_path)
    pcm_audio = audio.set_frame_rate(44100).set_channels(1).set_sample_width(4)  # 32-bit PCM
    pcm_path = file_path + '_pcm.wav'
    pcm_audio.export(pcm_path, format='wav')

    # Open the converted PCM wav file
    wf = wave.open(pcm_path, 'rb')

    # Set up the stream
    stream = p.open(format=pyaudio.paInt32,
                    channels=1,
                    rate=44100,
                    output=True,
                    input=True,
                    frames_per_buffer=1024)

    frames = []

    # Play and record the stream
    data = wf.readframes(1024)
    while data:
        stream.write(data)
        frames.append(stream.read(1024))
        data = wf.readframes(1024)

    # Stop the stream
    stream.stop_stream()
    stream.close()

    # Save the recorded audio
    wf_output = wave.open(output_path, 'wb')
    wf_output.setnchannels(1)
    wf_output.setsampwidth(p.get_sample_size(pyaudio.paInt32))
    wf_output.setframerate(44100)
    wf_output.writeframes(b''.join(frames))
    wf_output.close()

    # Close the wav file
    wf.close()

    # Remove the temporary PCM file
    os.remove(pcm_path)


def main():
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    for filename in os.listdir(source_directory):
        if filename.endswith(".wav"):
            print(f"Filename: {filename}")
            source_path = os.path.join(source_directory, filename)
            destination_path = os.path.join(destination_directory, filename)
            play_and_record(source_path, destination_path)

    # Terminate PyAudio
    p.terminate()


if __name__ == "__main__":
    main()
