# main.py
import cv2
import mediapipe as mp
import time
from guzheng_config import SOUND_FILES_A, SOUND_FILES_B, STRING_COLORS, SOUND_COOLDOWN, STRING_THICKNESS, RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1, RECT_COUNT_MODE_2
from guzheng_functions import initialize_pygame, load_sounds, draw_smooth_transition_electro_circle, draw_rectangles_and_strings, play_sound, display_mode_text
from guzheng_rectangles import get_rectangles_mode_1, get_rectangles_mode_2  # Import the rectangle utility functions


# Gesture detection and sound playback logic
def detect_gesture_and_play_sound(result, frame, rectangles, frame_width, frame_height, sounds, last_sound_time, mode,
                                  electro_triggered=False):
    fingertip_detected = False
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Draw hand skeleton
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS,
                mp.solutions.drawing_utils.DrawingSpec(color=(0, 255, 0), thickness=4, circle_radius=2),
                mp.solutions.drawing_utils.DrawingSpec(color=(255, 0, 0), thickness=6, circle_radius=8)
            )

            fingertip_x = int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width)
            fingertip_y = int(
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height)

            # Draw a thicker circle on the fingertip for visibility
            cv2.circle(frame, (fingertip_x, fingertip_y), 15, (255, 0, 0), -1)

            # Only trigger electro sound in Mode 2
            if mode == 2 and not electro_triggered and fingertip_x > (frame_width * 0.75) and fingertip_y < (
                    frame_height * 0.25):
                play_sound(9, sounds)  # Electro sound is last in SOUND_FILES_B
                electro_triggered = True

            # Check if the fingertip is inside any of the rectangles
            for idx, ((x, y), (w, h)) in enumerate(rectangles):
                if x < fingertip_x < x + w and y < fingertip_y < y + h:
                    current_time = time.time()
                    if current_time - last_sound_time[idx] > SOUND_COOLDOWN:
                        play_sound(idx, sounds)
                        last_sound_time[idx] = current_time
                    fingertip_detected = True

    return fingertip_detected, electro_triggered


# Mode 1 logic
def mode_1_logic(frame, result, sounds, sound_files, rectangles, last_sound_time, frame_width, frame_height):
    # Draw the rectangles, strings, and pitch text for Mode 1
    draw_rectangles_and_strings(frame, rectangles, STRING_COLORS, STRING_THICKNESS, sound_files, mode=1)

    # Display the current mode at the bottom-right corner
    display_mode_text(frame, mode=1, frame_width=frame_width, frame_height=frame_height)

    # Detect gesture and play sound for Mode 1
    detect_gesture_and_play_sound(result, frame, rectangles, frame_width, frame_height, sounds, last_sound_time, mode=1)
    return frame


# Mode 2: Logic with 9 rectangles on the left side and electro trigger
def mode_2_logic(frame, result, sounds, sound_files, last_sound_time, frame_width, frame_height, electro_triggered):
    # Get the compressed rectangles for Mode 2
    rectangles = get_rectangles_mode_2(frame_width, frame_height)

    # Draw the rectangles and strings (now updated for Mode 2 with color filling)
    draw_rectangles_and_strings(frame, rectangles, STRING_COLORS[:RECT_COUNT_MODE_2], STRING_THICKNESS,
                                sound_files[:RECT_COUNT_MODE_2], mode=2)

    # Display the current mode at the bottom-right corner
    display_mode_text(frame, mode=2, frame_width=frame_width, frame_height=frame_height)

    # Define the circle area for the electro sound trigger (top-right)
    circle_center_x = int(frame_width * 0.85)  # X-coordinate (85% of the screen width)
    circle_center_y = int(frame_height * 0.2)  # Y-coordinate (20% of the screen height)
    circle_radius = 150  # Radius of the circle

    # Draw the smooth color transitioning electro trigger circle
    draw_smooth_transition_electro_circle(frame, circle_center_x, circle_center_y, circle_radius, electro_triggered)

    # Detect gesture and play sound for 9 rectangles
    fingertip_detected, electro_triggered = detect_gesture_and_play_sound(result, frame, rectangles, frame_width, frame_height, sounds, last_sound_time, mode=2, electro_triggered=electro_triggered)

    # Check if the hand is inside the circle area to trigger the electro sound
    if result.multi_hand_landmarks and not electro_triggered:
        for hand_landmarks in result.multi_hand_landmarks:
            fingertip_x = int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width)
            fingertip_y = int(hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height)

            # Calculate distance from the fingertip to the center of the circle
            distance_to_circle = ((fingertip_x - circle_center_x) ** 2 + (fingertip_y - circle_center_y) ** 2) ** 0.5

            # Trigger the electro sound when the fingertip is inside the circle
            if distance_to_circle <= circle_radius:
                play_sound(9, sounds)  # Electro sound is last in SOUND_FILES_B
                electro_triggered = True  # Ensure it's triggered only once
                break  # Stop checking after the sound is triggered

    return frame, electro_triggered


# Main loop
def run_guzheng_simulation():
    # Initialize resources
    initialize_pygame()
    sounds_mode_1 = load_sounds(SOUND_FILES_A)
    sounds_mode_2 = load_sounds(SOUND_FILES_B)

    last_sound_time = [0] * 9  # Adjusted for 9 rectangles in mode 2
    electro_triggered = False  # Electro sound should be triggered only once per mode switch

    mode = 1  # Start with Mode 1

    # Initialize MediaPipe for hand detection
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    cap = cv2.VideoCapture(0)

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    rect_height_mode_1 = RECT_HEIGHT_MODE_1
    rect_width_mode_1 = RECT_WIDTH_MODE_1
    rectangles_mode_1 = get_rectangles_mode_1(frame_width, rect_width_mode_1, rect_height_mode_1)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        # Draw based on the current mode
        if mode == 1:
            frame = mode_1_logic(frame, result, sounds_mode_1, SOUND_FILES_A, rectangles_mode_1, last_sound_time,
                                 frame_width, frame_height)
        elif mode == 2:
            frame, electro_triggered = mode_2_logic(frame, result, sounds_mode_2, SOUND_FILES_B, last_sound_time, frame_width, frame_height, electro_triggered)


        # Show the frame
        cv2.imshow('Virtual Guzheng - CCOM', frame)

        # Handle key events
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord(' '):  # Switch mode when space is pressed
            if mode == 1:
                mode = 2
                paragraph_text = "Mode 2"
                electro_triggered = False  # Reset electro trigger when switching to Mode 2
            else:
                mode = 1
                paragraph_text = "Mode 1"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_guzheng_simulation()
