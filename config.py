# config.py
# Define sound files
SOUND_FILES_A = [
    'A4.wav',  # Top-left corner
    'G4.wav',  # Second on left
    'D4.wav',  # Third on left
    'E4.wav',  # Bottom-left corner
    'E3.wav',  # Top-right corner
    'D3.wav',  # Second on right
    'B3.wav',  # Third on right
    'A3.wav',  # Bottom-right corner
]

# SOUND_FILES_A = ['./audio/A/' + s for s in SOUND_FILES_A]
SOUND_FILES_A = ['./audio/C/' + s for s in SOUND_FILES_A]


SOUND_FILES_B = [
    '#F4.wav',  # Top 1
    'E4.wav',  # 2
    'D4.wav',  # 3
    'B3.wav',  # 4
    'A3.wav',  # 5
    '#F3.wav',  # 6
    'E3.wav',  # 7
    'D3.wav',  # 8
    'D2.wav',  # 9
    'electro.wav',  # circle

]

SOUND_FILES_B = ['./audio/B/' + s for s in SOUND_FILES_B]

# Define string colors for rectangles
STRING_COLORS = [
    (255, 87, 34),   # Deep Orange
    (255, 193, 7),   # Amber
    (76, 175, 80),   # Green
    (33, 150, 243),  # Blue
    (156, 39, 176),  # Purple
    (0, 188, 212),   # Cyan
    (255, 235, 59),  # Yellow
    (244, 67, 54),   # Red
    (123, 31, 162)   # Deep Purple (For 9th rectangle in mode 2)
]

# Other configuration values
STRING_THICKNESS = 10
SOUND_COOLDOWN = 1.0  # Sound cooldown in seconds
RECT_WIDTH_MODE_1 = 450  # Width of rectangles for Mode 1
RECT_HEIGHT_MODE_1 = 200  # Height of rectangles for Mode 1
RECT_WIDTH_MODE_2 = 1300  # Increase the width of rectangles for Mode 2
RECT_HEIGHT_COMPRESSED_MODE_2 = 60  # Compressed height for rectangles in Mode 2
RECT_COUNT_MODE_2 = 9  # Number of rectangles in Mode 2

# Vertical spacing reduction factor for subsequent rectangles
VERTICAL_SPACING_REDUCTION = 10  # Pixels to reduce the gap between each rectangle
VERTICAL_SPACING_OFFSET = 10  # Pixels to reduce the gap between each rectangle

