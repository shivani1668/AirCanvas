import os
import json
import numpy as np
from PIL import Image, ImageEnhance

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

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

def get_secret_key() -> str:
    key = ""
    if HAS_STREAMLIT:
        try:
            if "GEMINI_API_KEY" in st.secrets:
                key = str(st.secrets["GEMINI_API_KEY"])
        except Exception:
            pass
    if not key:
        key = os.getenv("GEMINI_API_KEY", "")
    return key.strip('"\'' + " \t\r\n")

def enhance_math_image(pil_img: Image.Image) -> Image.Image:
    try:
        img = pil_img.convert('RGB')
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        return img
    except Exception:
        return pil_img

class GeminiMathSolver:
    """
    Google Gemini 1.5/2.0 Flash Multimodal LLM Math Solver Engine.
    High-Precision Vision Prompting & Double-Checked Verification.
    """

    def __init__(self, api_key: str = None):
        self.api_key = (api_key or get_secret_key()).strip('"\'' + " \t\r\n")
        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                pass

    def set_api_key(self, api_key: str):
        if api_key and len(api_key.strip()) > 0:
            self.api_key = api_key.strip('"\'' + " \t\r\n")
            if HAS_GEMINI:
                try:
                    genai.configure(api_key=self.api_key)
                except Exception:
                    pass

    def solve_canvas_image(self, canvas_bgr: np.ndarray, pil_image: Image.Image = None) -> dict:
        """
        Sends hand-drawn or photographed equation image to Google Gemini Flash LLM.
        Applies high-precision vision prompting & step-by-step verification.
        """
        if not self.api_key:
            self.api_key = get_secret_key()

        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                pass

        if not HAS_GEMINI or not self.api_key:
            return OfflineMathEngine.solve_image_or_text(image=pil_image)

        last_error = ""

        if pil_image is None:
            if HAS_CV2:
                rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
            else:
                rgb_img = canvas_bgr[:, :, ::-1] if len(canvas_bgr.shape) == 3 else canvas_bgr
            pil_image = Image.fromarray(rgb_img)

        enhanced_image = enhance_math_image(pil_image)

        prompt = """
        You are a World-Class AI Mathematics Professor and Vision Expert.
        Examine this image containing a mathematical problem, equation, handwritten drawing, or multiple-choice question (MCQ).

        CRITICAL INSTRUCTIONS:
        1. Transcribe EVERY single number, symbol, square root (√), exponent, fraction line, and variable EXACTLY as shown in the image.
        2. Show a complete, rigorous, step-by-step mathematical proof/calculation.
        3. Verify your final calculated result algebraically.
        4. If multiple-choice options (A, B, C, D) are visible in the image, match your calculated answer to the exact Option letter.

        Output strictly in VALID JSON format with NO markdown code fences or conversational intro:
        {
          "expression": "Exact Math Problem Transcribed From Image (e.g. √(3^9 + 3^9 + 3^9))",
          "category": "Algebra / Exponents / Calculus / Surds / Geometry / MCQ",
          "steps": [
            "Step 1: Simplify inside square root -> 3^9 + 3^9 + 3^9 = 3 * 3^9 = 3^(1+9) = 3^10",
            "Step 2: Take square root -> √(3^10) = (3^10)^(1/2) = 3^5",
            "Step 3: Evaluate 3^5 = 243"
          ],
          "final_answer": "3^5 = 243"
        }
        """

        # Try multiple model endpoints in case one is restricted
        models_to_try = ['gemini-1.5-flash', 'gemini-2.0-flash-exp', 'gemini-1.5-pro']

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, enhanced_image])
                raw_text = response.text.strip()

                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)

                return {
                    "expression": data.get("expression", "Transcribed Problem"),
                    "category": data.get("category", "Mathematics"),
                    "steps": data.get("steps", ["Parsed by Gemini AI"]),
                    "final_answer": data.get("final_answer", "Solved"),
                    "source": f"Google Gemini ({model_name})"
                }
            except Exception as e:
                last_error = str(e)

        # If Gemini fails, display error details and fallback
        fallback = OfflineMathEngine.solve_image_or_text(image=pil_image)
        if last_error:
            fallback["source"] = f"Offline Engine (Gemini Note: {last_error[:80]})"
        return fallback
