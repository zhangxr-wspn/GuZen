import cv2
from config import (
    STRING_COLORS, STRING_THICKNESS, SOUND_FILES_A, SOUND_FILES_B,
    RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1,
    RECT_WIDTH_MODE_2, RECT_HEIGHT_COMPRESSED_MODE_2,
    RECT_COUNT_MODE_2, VERTICAL_SPACING_REDUCTION, VERTICAL_SPACING_OFFSET)
from utils import extract_pitch


class RectangleManager:
    def draw_mode_1(self, frame, frame_width, frame_height):
        rectangles = self.get_rectangles_mode_1(frame_width, frame_height)
        self.draw_rectangles_and_strings(frame, rectangles, STRING_COLORS, STRING_THICKNESS, SOUND_FILES_A, mode=1)
        return frame

    def draw_mode_2(self, frame, frame_width, frame_height):
        rectangles = self.get_rectangles_mode_2(frame_width, frame_height)
        self.draw_rectangles_and_strings(frame, rectangles, STRING_COLORS, STRING_THICKNESS, SOUND_FILES_B, mode=2)
        return frame

    def get_rectangles_mode_1(self, frame_width, frame_height):
        # Mode 1 rectangle logic

        return [
            # Left side
            ((0, 0), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((0, RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((0, 2 * RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((0, 3 * RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            # Right side
            ((frame_width - RECT_WIDTH_MODE_1, 0), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((frame_width - RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((frame_width - RECT_WIDTH_MODE_1, 2 * RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
            ((frame_width - RECT_WIDTH_MODE_1, 3 * RECT_HEIGHT_MODE_1), (RECT_WIDTH_MODE_1, RECT_HEIGHT_MODE_1)),
        ]

    def get_rectangles_mode_2(self, frame_width, frame_height):
        # Mode 2 rectangle logic (compressed height, closer spacing)
        rectangles = []
        for i in range(RECT_COUNT_MODE_2):
            y_position = i * (frame_height // RECT_COUNT_MODE_2) - i * VERTICAL_SPACING_REDUCTION + VERTICAL_SPACING_OFFSET
            rectangles.append(((0, y_position), (RECT_WIDTH_MODE_2, RECT_HEIGHT_COMPRESSED_MODE_2)))
        return rectangles

    def draw_rectangles_and_strings(self, frame, rectangles, string_colors, string_thickness, sound_files, mode):
        for idx, ((x, y), (w, h)) in enumerate(rectangles):
            if mode == 2:
                # Fill rectangle with color in Mode 2
                rectangle_color = string_colors[idx]
                cv2.rectangle(frame, (x, y), (x + w, y + h), rectangle_color, -1)  # -1 fills the rectangle
            elif mode == 1:
                # In Mode 1, just draw the borders
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)

            # Extract pitch and center it
            pitch_text = extract_pitch(sound_files[idx])
            text_size = cv2.getTextSize(pitch_text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2

            text_color = string_colors[idx] if mode == 1 else (255, 255, 255)
            cv2.putText(frame, pitch_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 2, text_color, 3, cv2.LINE_AA)

            # Draw strings
            if mode == 1:
                if idx < 4:  # Left-side rectangles
                    line_x = x + w - 3
                else:  # Right-side rectangles
                    line_x = x + 3
            elif mode == 2:
                line_x = x + w - 3

            cv2.line(frame, (line_x, y), (line_x, y + h), string_colors[idx], string_thickness)

