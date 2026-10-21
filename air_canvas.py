import cv2
import numpy as np
import mediapipe as mp

class AirCanvasDetector:
    """
    Real-Time Computer Vision Air Canvas Gesture Tracker powered by MediaPipe & OpenCV.
    Detects hand landmarks and draws lines based on index finger motion in 3D space.
    """

    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        # MediaPipe Hand Tracking Setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        # Canvas State
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.brush_color = (255, 0, 0) # BGR: Blue default
        self.brush_size = 8
        self.eraser_size = 40
        self.prev_x, self.prev_y = 0, 0

    def process_frame(self, frame: np.ndarray, is_drawing_enabled: bool = True):
        frame = cv2.flip(frame, 1)
        h, w, c = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        mode = "Hover"

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                landmarks = hand_landmarks.landmark
                # Index finger tip (8) and Middle finger tip (12)
                ix, iy = int(landmarks[8].x * w), int(landmarks[8].y * h)
                mx, my = int(landmarks[12].x * w), int(landmarks[12].y * h)

                # Check finger states (raised fingers)
                index_up = landmarks[8].y < landmarks[6].y
                middle_up = landmarks[12].y < landmarks[10].y

                if index_up and middle_up:
                    # Hover / Selection Mode (Two fingers up)
                    mode = "Selection / Hover"
                    self.prev_x, self.prev_y = 0, 0
                    cv2.circle(frame, (ix, iy), 12, (0, 255, 255), cv2.FILLED)

                elif index_up and not middle_up and is_drawing_enabled:
                    # Drawing Mode (Only index finger up)
                    mode = "Drawing Mode"
                    cv2.circle(frame, (ix, iy), self.brush_size, self.brush_color, cv2.FILLED)

                    if self.prev_x == 0 and self.prev_y == 0:
                        self.prev_x, self.prev_y = ix, iy

                    # Draw line on canvas array
                    cv2.line(self.canvas, (self.prev_x, self.prev_y), (ix, iy), self.brush_color, self.brush_size)
                    self.prev_x, self.prev_y = ix, iy
                else:
                    self.prev_x, self.prev_y = 0, 0

        # Combine webcam feed and drawing canvas
        gray_canvas = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY_INV)
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        combined = cv2.bitwise_and(frame, mask_3d)
        combined = cv2.bitwise_or(combined, self.canvas)

        return combined, mode

    def clear_canvas(self):
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self.prev_x, self.prev_y = 0, 0

    def set_brush_color(self, color_bgr: tuple):
        self.brush_color = color_bgr

    def set_brush_size(self, size: int):
        self.brush_size = size
