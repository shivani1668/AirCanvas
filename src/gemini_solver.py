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
        img = enhancer.enhance(1.4)
        return img
    except Exception:
        return pil_img

class GeminiMathSolver:
    """
    Direct Google Gemini Multimodal Vision AI Model Engine.
    Analyzes uploaded/snapped images directly using Gemini Flash Vision Models.
    Primary Endpoint: gemini-3.8-flash
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
        Directly sends the uploaded image to Google Gemini Flash AI Vision Model for live analysis.
        Primary Model: models/gemini-3.8-flash
        """
        if not self.api_key:
            self.api_key = get_secret_key()

        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                pass

        if not HAS_GEMINI or not self.api_key:
            return {
                "expression": "Gemini API Key Required",
                "category": "Authentication",
                "steps": [
                    "Step 1: Get a 100% Free Gemini API Key from Google AI Studio (aistudio.google.com/app/apikey)",
                    "Step 2: Paste your API key in the left Sidebar or save it in Streamlit Cloud Secrets (GEMINI_API_KEY = \"...\")",
                    "Step 3: Gemini Vision AI will directly analyze and solve your uploaded image live!"
                ],
                "final_answer": "Please enter Gemini API Key to solve live image",
                "source": "AI Key Notice"
            }

        if pil_image is None:
            if HAS_CV2:
                rgb_img = cv2.cvtColor(canvas_bgr, cv2.COLOR_BGR2RGB)
            else:
                rgb_img = canvas_bgr[:, :, ::-1] if len(canvas_bgr.shape) == 3 else canvas_bgr
            pil_image = Image.fromarray(rgb_img)

        enhanced_image = enhance_math_image(pil_image)

        prompt = """
        You are a World-Class AI Mathematics Professor and Multimodal Vision Model.
        Examine this uploaded image directly. Perform live OCR and mathematical analysis.

        INSTRUCTIONS:
        1. Transcribe the mathematical problem, equation, handwritten text, or multiple-choice question (MCQ) directly from this image.
        2. Analyze the structure and mathematical principles required to solve it.
        3. Show a complete, rigorous, step-by-step mathematical proof and solution.
        4. Provide the final simplified answer (and if it's an MCQ, state the exact Option letter like 'Option B').

        Output strictly in VALID JSON format (no markdown blocks, pure JSON):
        {
          "expression": "<Transcribed Problem From Image>",
          "category": "<Mathematical Category>",
          "steps": [
            "Step 1: ...",
            "Step 2: ...",
            "Step 3: ..."
          ],
          "final_answer": "<Final Answer>"
        }
        """

        # Gemini Flash Models (gemini-3.8-flash as primary endpoint)
        models_to_try = [
            'gemini-3.8-flash',
            'models/gemini-3.8-flash',
            'gemini-2.5-flash',
            'models/gemini-2.5-flash',
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-2.0-flash-exp',
            'gemini-2.0-flash'
        ]
        last_error = ""

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, enhanced_image])
                raw_text = response.text.strip()

                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)

                return {
                    "expression": data.get("expression", "Analyzed Image Problem"),
                    "category": data.get("category", "Mathematics"),
                    "steps": data.get("steps", ["Parsed directly by Gemini AI"]),
                    "final_answer": data.get("final_answer", "Solved"),
                    "source": f"Google Gemini ({model_name})"
                }
            except Exception as e:
                last_error = str(e)

        return {
            "expression": "Gemini AI Vision Analysis Error",
            "category": "Error Notice",
            "steps": [
                f"Gemini AI Error: {last_error}",
                "Please verify your Gemini API Key in Google AI Studio or try uploading a clearer image."
            ],
            "final_answer": "API Analysis Error",
            "source": "Gemini AI Error"
        }
