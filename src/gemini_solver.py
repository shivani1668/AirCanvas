import os
import json
import re
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
        img = enhancer.enhance(1.4)
        return img
    except Exception:
        return pil_img

def clean_latex_to_plain_math(text: str) -> str:
    if not text:
        return text

    cleaned = str(text)

    for _ in range(3):
        cleaned = re.sub(r"\\frac\s*\{([^{}]+)\}\s*\{([^{}]+)\}", r"(\1) / (\2)", cleaned)

    cleaned = re.sub(r"\\sqrt\s*\{([^{}]+)\}", r"√(\1)", cleaned)
    cleaned = re.sub(r"\\sqrt", "√", cleaned)

    cleaned = (
        cleaned.replace(r"\implies", "⇒")
        .replace(r"\Rightarrow", "⇒")
        .replace("=>", "⇒")
        .replace("->", "⇒")
        .replace(r"\times", "×")
        .replace(r"\div", "÷")
        .replace(r"\cdot", "*")
        .replace(r"\pm", "±")
        .replace(r"\infty", "∞")
        .replace(r"\pi", "π")
        .replace(r"\theta", "θ")
        .replace(r"\alpha", "α")
        .replace(r"\beta", "β")
        .replace(r"\int", "∫")
        .replace("{", "")
        .replace("}", "")
    )

    return cleaned

class GeminiMathSolver:
    """
    Direct Google Gemini Multimodal Vision & Text AI Model Engine.
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

    def solve_text_question(self, question_text: str) -> dict:
        """
        Sends typed mathematical text directly to Google Gemini Flash LLM for live reasoning and step-by-step resolution.
        """
        if not self.api_key:
            self.api_key = get_secret_key()

        if self.api_key and HAS_GEMINI:
            try:
                genai.configure(api_key=self.api_key)
            except Exception:
                pass

        if not HAS_GEMINI or not self.api_key:
            return OfflineMathEngine.solve_image_or_text(raw_text=question_text)

        prompt = f"""
        You are a World-Class AI Mathematics Professor. Solve this mathematical question/equation step-by-step:

        QUESTION:
        {question_text}

        INSTRUCTIONS:
        1. Transcribe the mathematical problem in clean readable notation (use '∫' for integrals, 'd/dx' for derivatives, '/' for fractions, '√' for square roots).
        2. Perform rigorous step-by-step mathematical calculation / integration / differentiation / algebra.
        3. Provide the final simplified answer clearly.

        Output strictly in VALID JSON format (no markdown blocks, pure JSON):
        {{
          "expression": "{question_text}",
          "category": "Calculus / Algebra / Trigonometry / Arithmetic",
          "steps": [
            "Step 1: ...",
            "Step 2: ...",
            "Step 3: ..."
          ],
          "final_answer": "Final Answer"
        }}
        """

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

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                raw_text = response.text.strip()

                clean_json = raw_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)

                raw_expr = data.get("expression", question_text)
                raw_steps = data.get("steps", ["Solved by Gemini AI"])
                raw_ans = data.get("final_answer", "Solved")

                return {
                    "expression": clean_latex_to_plain_math(raw_expr),
                    "category": data.get("category", "Mathematics"),
                    "steps": [clean_latex_to_plain_math(s) for s in raw_steps],
                    "final_answer": clean_latex_to_plain_math(raw_ans),
                    "source": f"Google Gemini ({model_name})"
                }
            except Exception:
                pass

        return OfflineMathEngine.solve_image_or_text(raw_text=question_text)

    def solve_canvas_image(self, canvas_bgr: np.ndarray, pil_image: Image.Image = None) -> dict:
        """
        Directly sends the uploaded image to Google Gemini Flash AI Vision Model for live analysis.
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

        FORMATTING RULES:
        1. DO NOT use raw LaTeX commands like \\frac{}{} or \\sqrt{}.
        2. Use slash '/' for fractions (e.g. '2√3 / 3' instead of '\\frac{2\\sqrt{3}}{3}').
        3. Use root symbol '√' for square roots (e.g. '√3' instead of '\\sqrt{3}').
        4. Use double arrow symbol '⇒' for step implications (e.g. '2x = 10 ⇒ x = 5').
        5. Show a complete, rigorous, step-by-step mathematical proof and solution.
        6. Provide the final simplified answer (and if it's an MCQ, state the exact Option letter like 'Option B').

        Output strictly in VALID JSON format (no markdown blocks, pure JSON):
        {
          "expression": "<Transcribed Problem From Image in clean math notation>",
          "category": "<Mathematical Category>",
          "steps": [
            "Step 1: ...",
            "Step 2: ...",
            "Step 3: ..."
          ],
          "final_answer": "<Final Answer in clean math notation>"
        }
        """

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

                raw_expr = data.get("expression", "Analyzed Image Problem")
                raw_steps = data.get("steps", ["Parsed directly by Gemini AI"])
                raw_ans = data.get("final_answer", "Solved")

                clean_expr = clean_latex_to_plain_math(raw_expr)
                clean_steps = [clean_latex_to_plain_math(s) for s in raw_steps]
                clean_ans = clean_latex_to_plain_math(raw_ans)

                return {
                    "expression": clean_expr,
                    "category": data.get("category", "Mathematics"),
                    "steps": clean_steps,
                    "final_answer": clean_ans,
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
