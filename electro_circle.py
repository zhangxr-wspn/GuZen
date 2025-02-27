import cv2
import time
import random

class ElectroCircle:
    def __init__(self, center_x, center_y, radius, transition_duration=1.0):
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.current_color = (255, 255, 0)  # Default yellow
        self.target_color = self.generate_random_color()  # First random color
        self.transition_duration = transition_duration
        self.last_color_change_time = 0
        self.electro_start_time = None

    def generate_random_color(self):
        """Generate a random color in BGR format."""
        return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

    def interpolate_colors(self, color_start, color_end, t):
        """Interpolate between two colors based on factor t (0.0 to 1.0)."""
        b = int(color_start[0] + (color_end[0] - color_start[0]) * t)
        g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
        r = int(color_start[2] + (color_end[2] - color_start[2]) * t)
        return b, g, r

    def draw_smooth_transition(self, frame, electro_triggered):
        current_time = time.time()

        # If the circle is triggered, transition between random colors
        if electro_triggered:
            if self.electro_start_time is None:
                self.electro_start_time = current_time

            time_since_last_change = current_time - self.last_color_change_time

            if time_since_last_change > self.transition_duration:
                self.last_color_change_time = current_time
                self.current_color = self.target_color
                self.target_color = self.generate_random_color()
                time_since_last_change = 0

            t = min(time_since_last_change / self.transition_duration, 1.0)
            interpolated_color = self.interpolate_colors(self.current_color, self.target_color, t)
            cv2.circle(frame, (self.center_x, self.center_y), self.radius, interpolated_color, 20)

        else:
            # If not triggered, keep the circle yellow
            self.electro_start_time = None  # Reset the timer
            self.current_color = (255, 255, 0)  # Default yellow
            self.target_color = self.generate_random_color()
            cv2.circle(frame, (self.center_x, self.center_y), self.radius, self.current_color, 20)
