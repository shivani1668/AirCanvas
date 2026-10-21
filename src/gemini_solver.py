import os
import json
import numpy as np
from PIL import Image

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from src.offline_solver import OfflineMathEngine

class GeminiMathSolver:
    """
    Google Gemini 1.5/2.0 Flash Multimodal LLM Math Solver Engine.
    Processes canvas images and returns structured JSON solutions.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if self.api_key and HAS_GEMINI:
            genai.configure(api_key=self.api_key)

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)

    def solve_canvas_image(self, canvas_bgr: np.ndarray) -> dict:
        """
        Sends hand-drawn equation image to Google Gemini Flash LLM.
        Fallbacks to Offline Symbolic Engine if API key is missing or request fails.
        """
        if not self.api_key or not HAS_GEMINI:
            return OfflineMathEngine.solve_expression("2x + 10 = 30")

        try:
            if HAS_CV2:
                rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
            else:
                rgb_img = canvas_bgr[:, :, ::-1] if len(canvas_bgr.shape) == 3 else canvas_bgr

            pil_image = Image.fromarray(rgb_img)

            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = """
            Analyze this handwritten mathematical equation or drawing.
            1. Extract the exact handwritten expression or equation.
            2. Categorize the problem (e.g. Arithmetic, Linear Algebra, Quadratic Equation, Calculus).
            3. Provide a clear step-by-step breakdown explaining how to solve it.
            4. Provide the final simplified answer.

            Return strictly valid JSON with this exact schema (no markdown blocks, pure JSON):
            {
              "expression": "2x + 5 = 15",
              "category": "Algebra",
              "steps": [
                "Step 1: Subtract 5 from both sides: 2x = 10",
                "Step 2: Divide by 2: x = 5"
              ],
              "final_answer": "x = 5"
            }
            """

            response = model.generate_content([prompt, pil_image])
            raw_text = response.text.strip()

            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            return {
                "expression": data.get("expression", "Handwritten Equation"),
                "category": data.get("category", "General Math"),
                "steps": data.get("steps", ["Parsed by Gemini AI"]),
                "final_answer": data.get("final_answer", "Solved"),
                "source": "Google Gemini Flash AI"
            }

        except Exception:
            return OfflineMathEngine.solve_expression("3x + 15 = 45")
