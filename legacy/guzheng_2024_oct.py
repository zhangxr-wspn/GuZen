import cv2
import pygame
import mediapipe as mp
import time

# Initialize pygame for sound
pygame.mixer.init()

# Load audio files
sound_files = [
    'A4.wav',  # Top-left corner
    'A3.wav',  # Top-left corner
    'G4.wav',  # Top-right corner
    'B3.wav',  # Top-right corner
    'D4.wav',  # Bottom-left corner
    'D3.wav',  # Bottom-left corner
    'E4.wav',  # Bottom-right corner
    'E3.wav',  # Bottom-right corner
]

sound_files = ['./audio/A/' + s for s in sound_files]
sounds = [pygame.mixer.Sound(file) for file in sound_files]

# Initialize the index for each corner to track the next audio file to play
audio_index = [0, 0, 0, 0]  # One index per corner

# Initialize sound cooldown (in seconds) and last sound play time for each corner/block
sound_cooldown = 2.0
last_sound_time = [0, 0, 0, 0]  # For corners (top-left, top-right, bottom-left, bottom-right)
corner_size = 500  # Size of the corner areas

# Initialize message-related variables
hint_message = ""
message_display_time = 0  # Time in seconds when the message should disappear
message_duration = 2  # Duration in seconds for message visibility
mode = 1  # Default to mode 1
paragraph_text = "Paragraph 1"  # Default paragraph

# Block properties for mode 2
block_size = 400  # Increased block size
block_center_x = None
block_center_y = None
block_last_sound_time = 0  # Track the last time sound was played for the block

# Function to play sound for a specific corner
def play_sound(corner_index):
    sounds[corner_index * 2 + audio_index[corner_index]].play()
    audio_index[corner_index] = (audio_index[corner_index] + 1) % 2

# Function to detect if a point hits the corner regions
def check_gesture_in_corner(x, y, frame_width, frame_height):
    if x < corner_size and y < corner_size:  # Top-left corner
        return 0
    elif x > (frame_width - corner_size) and y < corner_size:  # Top-right corner
        return 1
    elif x < corner_size and y > (frame_height - corner_size):  # Bottom-left corner
        return 2
    elif x > (frame_width - corner_size) and y > (frame_height - corner_size):  # Bottom-right corner
        return 3
    return None

# Initialize MediaPipe for hand detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# OpenCV to capture video from the webcam
cap = cv2.VideoCapture(0)

# Get frame dimensions
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# Main loop for gesture recognition and audio playback
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally (mirror image)
    frame = cv2.flip(frame, 1)

    # Convert the frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe to detect hands
    result = hands.process(rgb_frame)

    # Mode-specific behavior
    if mode == 1 or mode == 3:
        # Mode 1: Current logic with corners
        cv2.rectangle(frame, (0, 0), (corner_size, corner_size), (0, 255, 0), 2)  # Top-left corner
        cv2.rectangle(frame, (frame_width - corner_size, 0), (frame_width, corner_size), (0, 255, 0), 2)  # Top-right corner
        cv2.rectangle(frame, (0, frame_height - corner_size), (corner_size, frame_height), (0, 255, 0), 2)  # Bottom-left corner
        cv2.rectangle(frame, (frame_width - corner_size, frame_height - corner_size), (frame_width, frame_height), (0, 255, 0), 2)  # Bottom-right corner

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                fingertip_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width)
                fingertip_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height)

                cv2.circle(frame, (fingertip_x, fingertip_y), 10, (255, 0, 0), -1)

                corner_index = check_gesture_in_corner(fingertip_x, fingertip_y, frame_width, frame_height)
                if corner_index is not None:
                    current_time = time.time()
                    if current_time - last_sound_time[corner_index] > sound_cooldown:
                        play_sound(corner_index)
                        last_sound_time[corner_index] = current_time

    elif mode == 2:
        # Mode 2: Single block in the center
        block_center_x = frame_width // 2
        block_center_y = frame_height // 2
        cv2.rectangle(frame, (block_center_x - block_size // 2, block_center_y - block_size // 2),
                      (block_center_x + block_size // 2, block_center_y + block_size // 2), (0, 255, 0), 2)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                fingertip_x = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * frame_width)
                fingertip_y = int(hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * frame_height)

                cv2.circle(frame, (fingertip_x, fingertip_y), 10, (255, 0, 0), -1)

                # Check if fingertip is inside the block
                if (block_center_x - block_size // 2 < fingertip_x < block_center_x + block_size // 2) and \
                        (block_center_y - block_size // 2 < fingertip_y < block_center_y + block_size // 2):
                    current_time = time.time()
                    if current_time - block_last_sound_time > sound_cooldown:
                        play_sound(0)  # Play the specific sound for the block
                        block_last_sound_time = current_time

    # Display the paragraph text for the current mode
    cv2.putText(frame, paragraph_text, (frame_width // 2 - 100, frame_height // 2 - 100),
                cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    # Display the frame
    cv2.imshow('Virtual Guzheng - CCOM', frame)

    # Key detection for '1', '2', '3', 'R', and 'q'
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('1'):
        mode = 1
        paragraph_text = "Paragraph 1"
        audio_index = [0, 0, 0, 0]  # Reset audio index
        print("Switched to Mode 1: Corner interaction reset.")
    elif key == ord('2'):
        mode = 2
        paragraph_text = "Paragraph 2"
        print("Switched to Mode 2: Block interaction.")
    elif key == ord('3'):
        mode = 3
        paragraph_text = "Paragraph 3"
        audio_index = [0, 0, 0, 0]  # Reset audio index
        print("Switched to Mode 3: Corner interaction reset.")
    elif key == ord('r'):
        # Reset audio index and display reset message
        audio_index = [0, 0, 0, 0]
        hint_message = "Reset"
        message_display_time = time.time()


# Release the camera and close any open windows
cap.release()
cv2.destroyAllWindows()