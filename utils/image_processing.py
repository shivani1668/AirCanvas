import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

def preprocess_canvas_for_ai(canvas: np.ndarray) -> np.ndarray:
    """
    Preprocesses drawing canvas to high-contrast black-on-white image for Gemini AI.
    """
    if HAS_CV2:
        if len(canvas.shape) == 3:
            gray = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        else:
            gray = canvas.copy()

        inverted = cv2.bitwise_not(gray)
        _, thresh = cv2.threshold(inverted, 200, 255, cv2.THRESH_BINARY)
        return thresh
    else:
        # NumPy fallback when cv2 is not available
        if len(canvas.shape) == 3:
            gray = np.mean(canvas, axis=2).astype(np.uint8)
        else:
            gray = canvas.copy()
        return 255 - gray

def combine_frame_and_canvas(frame: np.ndarray, canvas: np.ndarray) -> np.ndarray:
    """
    Blends real-time camera feed with Air Canvas drawing strokes using OpenCV or NumPy.
    """
    if HAS_CV2:
        gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray_canvas, 10, 255, cv2.THRESH_BINARY_INV)
        mask_3d = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        combined = cv2.bitwise_and(frame, mask_3d)
        combined = cv2.bitwise_or(combined, canvas)
        return combined
    else:
        return np.maximum(frame, canvas)
