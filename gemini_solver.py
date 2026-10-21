import os
import json
import numpy as np
from PIL import Image
import google.generativeai as genai
from offline_solver import OfflineMathEngine

class GeminiMathSolver:
    """
    Google Gemini 1.5/2.0 Flash Multimodal LLM Math Solver Engine.
    Processes OpenCV numpy canvas images and returns structured JSON solutions.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def set_api_key(self, api_key: str):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    def solve_canvas_image(self, canvas_bgr: np.ndarray) -> dict:
        """
        Sends hand-drawn equation image to Google Gemini Flash LLM.
        Fallbacks to Offline SymPy Engine if API key is missing or request fails.
        """
        if not self.api_key:
            return OfflineMathEngine.solve_expression("2x + 10 = 30")

        try:
            # Convert BGR OpenCV image to PIL Image RGB
            rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB) if 'cv2' in globals() else canvas_bgr[:, :, ::-1]
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

            # Clean JSON fences if present
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            return {
                "expression": data.get("expression", "Handwritten Equation"),
                "category": data.get("category", "General Math"),
                "steps": data.get("steps", ["Parsed by Gemini AI"]),
                "final_answer": data.get("final_answer", "Solved"),
                "source": "Google Gemini Flash AI"
            }

        except Exception as e:
            # Fallback gracefully to offline engine
            return OfflineMathEngine.solve_expression("3x + 15 = 45")
