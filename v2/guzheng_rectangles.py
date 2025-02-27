# guzheng_rectangles.py
from guzheng_config import RECT_WIDTH_MODE_2, RECT_HEIGHT_COMPRESSED_MODE_2, RECT_COUNT_MODE_2, VERTICAL_SPACING_REDUCTION


def get_rectangles_mode_1(frame_width, rect_width, rect_height):
    """
    Returns the list of rectangles for Mode 1.
    """
    return [
        # Left side
        ((0, 0), (rect_width, rect_height)),
        ((0, rect_height), (rect_width, rect_height)),
        ((0, 2 * rect_height), (rect_width, rect_height)),
        ((0, 3 * rect_height), (rect_width, rect_height)),
        # Right side
        ((frame_width - rect_width, 0), (rect_width, rect_height)),
        ((frame_width - rect_width, rect_height), (rect_width, rect_height)),
        ((frame_width - rect_width, 2 * rect_height), (rect_width, rect_height)),
        ((frame_width - rect_width, 3 * rect_height), (rect_width, rect_height)),
    ]


def get_rectangles_mode_2(frame_width, frame_height):
    """
    Returns the list of rectangles for Mode 2 with compressed height, and closer spacing between them.
    """
    rectangles = []
    y_offset = 0  # Starting y position

    for i in range(RECT_COUNT_MODE_2):
        # Keep the first rectangle's position unchanged
        if i == 0:
            y_position = 0
        else:
            # For subsequent rectangles, reduce the spacing
            y_position = i * (frame_height // RECT_COUNT_MODE_2) - i * VERTICAL_SPACING_REDUCTION

        # Append the rectangle (x, y, width, height)
        rectangles.append(((0, y_position), (RECT_WIDTH_MODE_2, RECT_HEIGHT_COMPRESSED_MODE_2)))

    return rectangles