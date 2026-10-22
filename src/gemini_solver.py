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

# Default Public Key Fallback placeholder / Env Key
DEFAULT_GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

class GeminiMathSolver:
    """
    Google Gemini 1.5/2.0 Flash Multimodal LLM Math Solver Engine.
    Processes canvas & problem images and returns structured JSON solutions for ALL math problems.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or DEFAULT_GEMINI_KEY
        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                pass

    def set_api_key(self, api_key: str):
        if api_key and len(api_key.strip()) > 0:
            self.api_key = api_key.strip()
            if HAS_GEMINI:
                try:
                    genai.configure(api_key=self.api_key)
                except Exception:
                    pass

    def solve_canvas_image(self, canvas_bgr: np.ndarray, pil_image: Image.Image = None) -> dict:
        """
        Sends hand-drawn or photographed equation image to Google Gemini Flash LLM.
        Fallbacks to Offline Symbolic Engine if API key is missing or request fails.
        """
        if not HAS_GEMINI or not self.api_key:
            return OfflineMathEngine.solve_image_or_text(image=pil_image)

        try:
            if pil_image is None:
                if HAS_CV2:
                    rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
                else:
                    rgb_img = canvas_bgr[:, :, ::-1] if len(canvas_bgr.shape) == 3 else canvas_bgr
                pil_image = Image.fromarray(rgb_img)

            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = """
            You are an elite AI Mathematician and Professor. Analyze this image containing a mathematical problem, equation, handwritten drawing, or multiple-choice question (MCQ).

            1. Extract the exact handwritten or printed expression/equation/question accurately.
            2. Categorize the problem (e.g. Algebra, Calculus, Trigonometry, Surds, Fractions, Geometry, Physics, MCQ).
            3. Provide a clear, rigorous, step-by-step breakdown explaining how to solve it logically.
            4. Provide the final simplified answer (and if it's an MCQ, state the correct Option like '1/2 (Option B)').

            Return strictly valid JSON with this exact schema (no markdown blocks, pure JSON):
            {
              "expression": "5 / (√2 + 1)",
              "category": "Surds & Rationalization",
              "steps": [
                "Step 1: Rationalize the denominator by multiplying top and bottom by conjugate (√2 - 1)",
                "Step 2: Numerator = 5 * (√2 - 1) = 5√2 - 5",
                "Step 3: Denominator = (√2 + 1)(√2 - 1) = 2 - 1 = 1",
                "Step 4: Result = 5√2 - 5"
              ],
              "final_answer": "5√2 - 5  (Option B)"
            }
            """

            response = model.generate_content([prompt, pil_image])
            raw_text = response.text.strip()

            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            return {
                "expression": data.get("expression", "Handwritten / Printed Equation"),
                "category": data.get("category", "General Math"),
                "steps": data.get("steps", ["Parsed by Gemini AI"]),
                "final_answer": data.get("final_answer", "Solved"),
                "source": "Google Gemini 1.5 Flash AI"
            }

        except Exception:
            return OfflineMathEngine.solve_image_or_text(image=pil_image)
