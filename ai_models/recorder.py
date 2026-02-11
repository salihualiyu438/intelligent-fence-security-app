import cv2
import time
import os

class VideoRecorder:
    def __init__(self):
        self.recording = False
        self.start_time = None
        self.writer = None
        self.duration = 25  # seconds

        os.makedirs("recordings", exist_ok=True)

    def start(self, frame):
        h, w, _ = frame.shape
        filename = f"recordings/intrusion_{int(time.time())}.avi"

        self.writer = cv2.VideoWriter(
            filename,
            cv2.VideoWriter_fourcc(*'XVID'),
            20,
            (w, h)
        )

        self.start_time = time.time()
        self.recording = True

    def update(self, frame):
        if not self.recording:
            return

        self.writer.write(frame)

        if time.time() - self.start_time >= self.duration:
            self.writer.release()
            self.recording = False
