import streamlit as st
import cv2
import mediapipe as mp
from config import SOUND_FILES_A, SOUND_FILES_B
from utils import detect_gesture_and_play_sound, display_mode_text
from hand_tracker import HandTracker
from sound_manager_streamlit import SoundManager
from electro_circle import ElectroCircle
from rectangle_manager import RectangleManager
import numpy as np
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer


class GuZen(VideoProcessorBase):
    def __init__(self):

        # Initialize hand tracker, sound manager, and electro circle
        self.hand_tracker = HandTracker()
        self.sound_manager_mode_1 = SoundManager(SOUND_FILES_A)  # Load sounds for Mode 1
        self.sound_manager_mode_2 = SoundManager(SOUND_FILES_B)  # Load sounds for Mode 2

        # Rectangle manager for drawing rectangles
        self.rectangle_manager = RectangleManager()

        # Electro circle setup (top-right area)
        self.electro_circle = ElectroCircle(center_x=0, center_y=0, radius=150)  # Initial placeholder

        # Start with Mode 1
        self.mode = 1
        self.electro_triggered = False

        # Track last time each sound was played
        self.last_sound_time_mode_1 = [0] * len(SOUND_FILES_A)  # For Mode 1
        self.last_sound_time_mode_2 = [0] * len(SOUND_FILES_B)  # For Mode 2

    def recv(self, frame):
        # Use Streamlit's camera input to capture a snapshot
        # Convert the frame to an OpenCV-compatible format
        print('here')
        img = frame.to_ndarray(format="bgr24")

        # Flip the frame horizontally (mirror effect)
        img = cv2.flip(img, 1)
        frame_height, frame_width = img.shape[:2]

        # Convert from BGR to RGB for proper display
        rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Process the frame for hand detection
        result = self.hand_tracker.detect_hands(rgb_frame)

        # Mode 1 Logic
        if self.mode == 1:
            frame = self.rectangle_manager.draw_mode_1(frame, frame_width, frame_height)
            self.detect_and_play_gesture_mode_1(result, frame, frame_width, frame_height)

        # Mode 2 Logic
        elif self.mode == 2:
            frame = self.rectangle_manager.draw_mode_2(frame, frame_width, frame_height)
            # Draw and handle electro circle logic
            self.electro_circle.draw_smooth_transition(frame, electro_triggered=self.electro_triggered)
            self.detect_and_play_gesture_mode_2(result, frame, frame_width, frame_height)

        # **Display the current mode at the bottom-right corner**
        display_mode_text(frame, self.mode, frame_width, frame_height)

            # Show the frame
            # cv2.imshow('Virtual Guzheng - CCOM', frame)

            # Handle key events
            # key = cv2.waitKey(1) & 0xFF
            # if key == ord('q'):
            #     break
            # elif key == ord(' '):
            #     self.switch_mode()

        # cap.release()
        # cv2.destroyAllWindows()

    def switch_mode(self):
        if self.mode == 1:
            # self.mode = 1
            self.mode = 2
            self.electro_triggered = False
        else:
            self.mode = 1

    # Mode 1: Detect and play sound for rectangles
    def detect_and_play_gesture_mode_1(self, result, frame, frame_width, frame_height):
        # Get rectangles for Mode 1
        rectangles = self.rectangle_manager.get_rectangles_mode_1(frame_width, frame_height)

        # Detect gesture and play sound for Mode 1
        fingertip_detected, _ = detect_gesture_and_play_sound(
            result, frame, rectangles, frame_width, frame_height, self.sound_manager_mode_1,
            self.last_sound_time_mode_1, mode=1  # Pass the last_sound_time and mode
        )
        return fingertip_detected

    # Mode 2: Detect and play sound for rectangles and electro trigger
    def detect_and_play_gesture_mode_2(self, result, frame, frame_width, frame_height):
        # Get rectangles for Mode 2
        rectangles = self.rectangle_manager.get_rectangles_mode_2(frame_width, frame_height)

        # Detect gesture and play sound for Mode 2 (for rectangles)
        fingertip_detected, self.electro_triggered = detect_gesture_and_play_sound(
            result, frame, rectangles, frame_width, frame_height, self.sound_manager_mode_2,
            self.last_sound_time_mode_2, mode=2, electro_triggered=self.electro_triggered
            # Pass last_sound_time and mode
        )

        return fingertip_detected


if __name__ == "__main__":
    st.title("Continuous Video Stream Processing with streamlit-webrtc")

    webrtc_streamer(
        key="example",
        video_processor_factory=GuZen,
        media_stream_constraints={"video": True, "audio": False}
    )

