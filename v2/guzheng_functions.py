# utils.py
import cv2
import pygame
import time
import random


# Initialize pygame for sound
def initialize_pygame():
    pygame.mixer.init()
    pygame.mixer.set_num_channels(128)  # Allow more simultaneous sounds


# Load audio files
def load_sounds(sound_files):
    return [pygame.mixer.Sound(file) for file in sound_files]


# Extract the pitch from the file name
def extract_pitch(file_name):
    return file_name.split('/')[-1].replace('.wav', '')


# Play sound function
def play_sound(rect_index, sounds):
    sounds[rect_index].play()


# Draw rectangles, strings, and pitch text
def draw_rectangles_and_strings(frame, rectangles, string_colors, string_thickness, sound_files, mode):
    for idx, ((x, y), (w, h)) in enumerate(rectangles):
        if mode == 2:
            # In Mode 2, fill the rectangle with its corresponding string color
            rectangle_color = string_colors[idx]
            cv2.rectangle(frame, (x, y), (x + w, y + h), rectangle_color, -1)  # -1 fills the rectangle with color

        elif mode == 1:
            # In Mode 1, draw the rectangle borders without filling
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)  # Green borders for Mode 1

        # Extract the pitch and center it in the rectangle (applies to both modes)
        pitch_text = extract_pitch(sound_files[idx])
        text_size = cv2.getTextSize(pitch_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2

        # In Mode 1, the text color should match the string color
        text_color = string_colors[idx] if mode == 1 else (255, 255, 255)  # String color in Mode 1, white in Mode 2
        cv2.putText(frame, pitch_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, text_color, 3, cv2.LINE_AA)

        # Draw strings on the right edge of the left-side rectangles and the left edge of the right-side rectangles
        if mode == 1:
            if idx < 4:  # Left-side rectangles
                line_x = x + w - 3  # Right edge of left-side rectangles
            else:  # Right-side rectangles
                line_x = x + 3  # Left edge of right-side rectangles
        elif mode == 2:
            line_x = x + w - 3  # In Mode 2, strings are always on the right edge

        # Draw the string with the corresponding color and thickness
        cv2.line(frame, (line_x, y), (line_x, y + h), string_colors[idx], string_thickness)


# Function to display the current mode at the bottom-right of the screen
def display_mode_text(frame, mode, frame_width, frame_height):
    mode_text = f"Mode {mode}"

    # Calculate the position for bottom-right corner
    text_size = cv2.getTextSize(mode_text, cv2.FONT_HERSHEY_SIMPLEX, 3, 6)[0]
    text_x = frame_width - text_size[0] - 20  # 20px padding from the right
    text_y = frame_height - 20  # 20px padding from the bottom

    # Draw the mode text at the bottom-right corner
    cv2.putText(frame, mode_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6, cv2.LINE_AA)


# Function to generate a random color
def generate_random_color():
    """
    Generates a random color in BGR format.
    :return: A color tuple (B, G, R) with random values for each component.
    """
    b = random.randint(0, 255)
    g = random.randint(0, 255)
    r = random.randint(0, 255)
    return (b, g, r)

# Function to smoothly transition between two colors
def interpolate_colors(color_start, color_end, t):
    """
    Interpolates between two colors based on a factor t (0.0 to 1.0).
    :param color_start: The starting color as a (B, G, R) tuple.
    :param color_end: The target color as a (B, G, R) tuple.
    :param t: A value between 0.0 and 1.0 representing the interpolation factor.
    :return: A color tuple (B, G, R) with the interpolated color.
    """
    b = int(color_start[0] + (color_end[0] - color_start[0]) * t)
    g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
    r = int(color_start[2] + (color_end[2] - color_start[2]) * t)
    return (b, g, r)

# Initialize variables to store the current color, target color, and time
electro_start_time = None
last_color_change_time = 0
current_color = (255, 255, 0)  # Default yellow before triggering
target_color = generate_random_color()  # First random target color
transition_duration = 2.0  # Duration of each color transition in seconds

# Function to handle the smooth color transition for the electro trigger circle
def draw_smooth_transition_electro_circle(frame, circle_center_x, circle_center_y, circle_radius, electro_triggered):
    global electro_start_time, last_color_change_time, current_color, target_color

    if electro_triggered:
        # Initialize the start time if not set
        if electro_start_time is None:
            electro_start_time = time.time()

        # Get the current time
        current_time = time.time()

        # Calculate the time since the last color change
        time_since_last_change = current_time - last_color_change_time

        # If the transition is complete, generate a new target color
        if time_since_last_change > transition_duration:
            last_color_change_time = current_time
            current_color = target_color  # Set current color to the completed target color
            target_color = generate_random_color()  # Generate a new random target color
            time_since_last_change = 0  # Reset time since last change

        # Calculate the interpolation factor (0.0 to 1.0)
        t = min(time_since_last_change / transition_duration, 1.0)

        # Interpolate between the current color and the target color
        interpolated_color = interpolate_colors(current_color, target_color, t)

        # Draw the circle with the interpolated color
        cv2.circle(frame, (circle_center_x, circle_center_y), circle_radius, interpolated_color, 20)

    else:
        # If not triggered, draw the circle in yellow (non-random)
        electro_start_time = None  # Reset the start time
        current_color = (255, 255, 0)  # Default yellow
        target_color = generate_random_color()  # Prepare a random color for next trigger
        cv2.circle(frame, (circle_center_x, circle_center_y), circle_radius, current_color, 20)  # Yellow

