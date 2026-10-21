import cv2
import numpy as np

def preprocess_canvas_for_ai(canvas: np.ndarray) -> np.ndarray:
    """
    Preprocesses drawing canvas to high-contrast black-on-white image for Gemini AI.
    """
    # Convert BGR to Grayscale if needed
    if len(canvas.shape) == 3:
        gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    else:
        gray = canvas.copy()

    # Invert drawing (if strokes are white on black, invert to black on white)
    inverted = cv2.bitwise_not(gray)

    # Thresholding for sharp stroke edges
    _, thresh = cv2.threshold(inverted, 200, 255, cv2.THRESH_BINARY)
    return thresh

def combine_frame_and_canvas(frame: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    """
    Blends real-time camera feed with Air Canvas drawing strokes using OpenCV.
    """
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray_canvas, 20, 255, cv2.THRESH_BINARY_INV)

    # Convert mask to 3 channels
    mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    # Combine webcam background with canvas strokes
    combined = cv2.bitwise_and(frame, mask_3d)
    combined = cv2.bitwise_or(combined, canvas)
    return combined
