import os
import json
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

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
    if HAS_STREAMLIT:
        try:
            if "GEMINI_API_KEY" in st.secrets:
                return st.secrets["GEMINI_API_KEY"]
        except Exception:
            pass
    return os.getenv("GEMINI_API_KEY", "")

def enhance_math_image(pil_img: Image.Image) -> Image.Image:
    """
    Enhances contrast and sharpness of mathematical image for crystal-clear OCR.
    """
    try:
        # Convert to RGB
        img = pil_img.convert('RGB')
        # Increase contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        # Increase sharpness
        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(1.8)
        return img
    except Exception:
        return pil_img

class GeminiMathSolver:
    """
    Google Gemini 1.5/2.0 Flash Multimodal LLM Math Solver Engine.
    High-Precision Vision Prompting & Double-Checked Verification.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or get_secret_key()
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

        try:
            if pil_image is None:
                if HAS_CV2:
                    rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
                else:
                    rgb_img = canvas_bgr[:, :, ::-1] if len(canvas_bgr.shape) == 3 else canvas_bgr
                pil_image = Image.fromarray(rgb_img)

            # Enhance image for high precision OCR
            enhanced_image = enhance_math_image(pil_image)

            model = genai.GenerativeModel('gemini-1.5-flash')

            prompt = """
            You are a World-Class AI Mathematics Professor and Vision Expert.
            Examine this image containing a mathematical problem, equation, handwritten drawing, or multiple-choice question (MCQ).

            CRITICAL INSTRUCTIONS:
            1. Transcribe EVERY single number, symbol, square root (√), fraction line, exponent, and variable EXACTLY as shown in the image.
            2. Double-check your OCR reading against the image before solving.
            3. Show a complete, rigorous, step-by-step mathematical proof/calculation.
            4. Verify your final calculated result algebraically.
            5. If multiple-choice options (A, B, C, D) are visible in the image, match your calculated answer to the exact Option letter (e.g. '5√2 - 5 (Option B)').

            Output strictly in VALID JSON format with NO markdown code fences or conversational intro:
            {
              "expression": "Exact Math Problem / Equation Transcribed From Image",
              "category": "Algebra / Calculus / Surds & Rationalization / Geometry / MCQ",
              "steps": [
                "Step 1: ...",
                "Step 2: ...",
                "Step 3: ..."
              ],
              "final_answer": "Exact Simplified Result (Option X if applicable)"
            }
            """

            response = model.generate_content([prompt, enhanced_image])
            raw_text = response.text.strip()

            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)

            return {
                "expression": data.get("expression", "Transcribed Problem"),
                "category": data.get("category", "Mathematics"),
                "steps": data.get("steps", ["Parsed by Gemini AI"]),
                "final_answer": data.get("final_answer", "Solved"),
                "source": "Google Gemini 1.5 Flash AI"
            }

        except Exception as e:
            return OfflineMathEngine.solve_image_or_text(image=pil_image)
