# utils.py
import cv2
import mediapipe as mp
import pygame
import time


# Initialize pygame for sound
def initialize_pygame():
    pygame.mixer.init()
    pygame.mixer.set_num_channels(128)  # Allow more simultaneous sounds


# Extract the pitch from the file name
def extract_pitch(file_name):
    return file_name.split('/')[-1].replace('.wav', '')


# Play sound function
def play_sound(rect_index, sounds):
    sounds[rect_index].play()


def detect_gesture_and_play_sound(result, frame, rectangles, frame_width, frame_height, sound_manager, last_sound_time, mode, electro_triggered=False):

    # 20241126 skip mode 2
    # 假动作
    if mode == 2:
        return False, electro_triggered

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand skeleton
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=6, circle_radius=8)
            )

            fingertip_x = int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width)
            fingertip_y = int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height)

            # Draw a thicker circle on the fingertip for visibility
            cv2.circle(frame, (fingertip_x, fingertip_y), 15, (255, 0, 0), -1)

            # Check if the fingertip is inside any of the rectangles (one sound per frame)
            for idx, ((x, y), (w, h)) in enumerate(rectangles):
                if x < fingertip_x < x + w and y < fingertip_y < y + h:
                    current_time = time.time()
                    if current_time - last_sound_time[idx] > sound_manager.cooldown:
                        sound_manager.play_sound(idx)  # Use the SoundManager's play_sound method
                        last_sound_time[idx] = current_time
                        return True, electro_triggered  # Exit after one sound triggers

    return False, electro_triggered


# Function to display the current mode at the bottom-right of the screen
def display_mode_text(frame, mode, frame_width, frame_height):
    mode_text = f"Mode {mode}"

    # Calculate the position for bottom-right corner
    text_size = cv2.getTextSize(mode_text, cv2.FONT_HERSHEY_SIMPLEX, 3, 6)[0]
    text_x = frame_width - text_size[0] - 20  # 20px padding from the right
    text_y = frame_height - 20  # 20px padding from the bottom

    # Draw the mode text at the bottom-right corner
    cv2.putText(frame, mode_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6, cv2.LINE_AA)

