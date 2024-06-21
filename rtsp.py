import cv2
import subprocess

def gstreamer_pipeline(
    capture_width=640,
    capture_height=480,
    framerate=30,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            capture_width,
            capture_height,
        )
    )

def main():
    pipeline = gstreamer_pipeline()
    cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

    if not cap.isOpened():
        print("Error: Unable to open camera")
        return

    # GStreamer pipeline for RTSP server with video and audio
    gst_str = (
        "appsrc ! videoconvert ! x264enc tune=zerolatency bitrate=500 speed-preset=superfast ! rtph264pay config-interval=1 pt=96 ! "
        "udpsink host=127.0.0.1 port=5000 sync=false async=false "
        "alsasrc device=hw:1,0 ! audio/x-raw,rate=44100,channels=1 ! audioconvert ! audioresample ! "
        "opusenc ! rtpopuspay ! udpsink host=127.0.0.1 port=5001"
    )

    process = subprocess.Popen(gst_str, shell=True, stdin=subprocess.PIPE)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        process.stdin.write(frame.tobytes())

    cap.release()
    process.stdin.close()
    process.wait()

if __name__ == "__main__":
    main()
