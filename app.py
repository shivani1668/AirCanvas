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

st.title("🎨 Air Canvas - AI Math Solver")
st.caption("Powered by Google Gemini 1.5/2.0 Flash AI & Universal Math Engine")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration & AI Key")
st.sidebar.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
user_api_key = st.sidebar.text_input("Paste Free Gemini API Key Here", type="password", help="Get 100% Free Key from Google AI Studio")

solver = GeminiMathSolver(api_key=user_api_key)

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
                st.write(f"- {step}")

            st.info(f"### 💡 Final Answer: {result['final_answer']}")

            try:
                graph_img = plot_equation_graph(result['expression'])
                st.image(graph_img, caption="Function Graph Visualizer", use_column_width=True)
            except Exception:
                pass
