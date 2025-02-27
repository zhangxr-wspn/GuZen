import mediapipe as mp


class HandTracker:
    def __init__(self):
        self.hands = mp.solutions.hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)

    def detect_hands(self, rgb_frame):
        return self.hands.process(rgb_frame)

