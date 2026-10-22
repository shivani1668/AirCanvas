import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st
import numpy as np
from PIL import Image

try:
    from src.gemini_solver import GeminiMathSolver
    from src.offline_solver import OfflineMathEngine
except ImportError:
    from gemini_solver import GeminiMathSolver
    from offline_solver import OfflineMathEngine

from utils.math_plotter import plot_equation_graph

st.set_page_config(
    page_title="Air Canvas - AI Math Solver",
    page_icon="🎨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom Styling: Global UI stays in standard Sans-Serif font, while Math Calculation cards use Times New Roman + Symbol font with double arrow ⇒
st.markdown("""
<style>
    .step-explanation {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #f5e0dc !important;
        margin-top: 10px !important;
    }

    .math-card {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.35rem !important;
        font-weight: bold !important;
        background-color: #181825 !important;
        color: #a6e3a1 !important;
        padding: 10px 18px !important;
        border-radius: 8px !important;
        margin-top: 6px !important;
        margin-bottom: 12px !important;
        border-left: 5px solid #89b4fa !important;
        letter-spacing: 0.5px !important;
        display: block !important;
    }

    .final-answer-box {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.55rem !important;
        font-weight: bold !important;
        background-color: #1e1e2e !important;
        color: #89b4fa !important;
        padding: 16px 20px !important;
        border-radius: 12px !important;
        border: 2px solid #89b4fa !important;
        margin-top: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎨 Air Canvas - AI Math Solver")
st.caption("Powered by Google Gemini Flash AI & Universal Math Engine")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration & AI Status")

has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

if has_secrets_key:
    st.sidebar.success("✅ Google Gemini AI Active (Connected via Cloud Secrets)")
else:
    st.sidebar.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")

user_api_key = st.sidebar.text_input("Custom Gemini API Key (Optional)", type="password", help="Leave blank if set in Cloud Secrets")

show_graph_manual = st.sidebar.checkbox("📊 Show Function Graph", value=False)

solver = GeminiMathSolver(api_key=user_api_key if user_api_key else None)

tab1, tab2 = st.tabs(["📷 Mobile Camera", "📁 Upload Image"])

image_to_process = None

with tab1:
    camera_on = st.toggle("📷 Enable Camera", value=False)
    if camera_on:
        st.write("Snap a picture of any math problem or equation:")
        camera_file = st.camera_input("Snap Math Problem")
        if camera_file is not None:
            image_to_process = Image.open(camera_file)
    else:
        st.info("Camera is currently OFF. Toggle 'Enable Camera' above to turn on your phone camera.")

with tab2:
    st.write("Upload an image of any math problem (Algebra, Calculus, MCQs, Geometry):")
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image_to_process = Image.open(uploaded_file)

def render_step_with_larger_math(step_text: str):
    """
    Renders step explanation in regular font, and places the math calculation
    right below it on a new line in a larger, bold Times New Roman + Symbol font card with double arrow ⇒.
    """
    step_str = str(step_text).strip()
    if ":" in step_str:
        parts = step_str.split(":", 1)
        explanation = parts[0].strip()
        calc = parts[1].strip()
        st.markdown(f"<div class='step-explanation'>• {explanation}:</div>", unsafe_allow_html=True)
        if calc:
            # Prefix double arrow symbol ⇒ for math calculations
            display_calc = calc if calc.startswith("⇒") else f"⇒ {calc}"
            st.markdown(f"<div class='math-card'>{display_calc}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='step-explanation'>• {step_str}</div>", unsafe_allow_html=True)

if image_to_process is not None:
    st.image(image_to_process, caption="Math Problem Image", use_column_width=True)

    if st.button("✨ Solve Math Problem with Gemini AI", type="primary", use_container_width=True):
        with st.spinner("Analyzing math problem & generating step-by-step AI solution..."):
            img_np = np.array(image_to_process.convert('RGB'))

            result = solver.solve_canvas_image(img_np, pil_image=image_to_process)

            st.success("Solution Complete!")
            st.markdown(f"### 📌 Recognized Expression:\n`{result['expression']}`")
            st.markdown(f"**Category**: {result['category']} (*{result['source']}*)")

            st.markdown("### 📝 Step-by-Step Breakdown:")
            for step in result['steps']:
                render_step_with_larger_math(step)

            st.markdown(
                f"<div class='final-answer-box'>💡 Final Answer: {result['final_answer']}</div>",
                unsafe_allow_html=True
            )

            expr_lower = result['expression'].lower()
            asked_for_graph = any(w in expr_lower for w in ["graph", "plot", "sketch", "curve", "draw"])

            if asked_for_graph or show_graph_manual:
                try:
                    graph_img = plot_equation_graph(result['expression'])
                    st.image(graph_img, caption="Function Graph Visualizer", use_column_width=True)
                except Exception:
                    pass
