import streamlit as st
import numpy as np
from PIL import Image
import io

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

from gemini_solver import GeminiMathSolver
from offline_solver import OfflineMathEngine
from utils.math_plotter import plot_equation_graph

st.set_page_config(page_title="Air Canvas - AI Math Solver (Python)", page_icon="🎨", layout="wide")

st.title("🎨 Air Canvas - Draw Math, Let AI Solve! (Python)")
st.caption("Generative AI & Computer Vision Mathematical Problem Solver built with Python")

st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Google Gemini API Key (Optional)", type="password")
use_gemini = st.sidebar.checkbox("Use Gemini AI LLM", value=True)

solver = GeminiMathSolver(api_key=api_key) if api_key else None

st.subheader("🖊️ Upload or Draw Equation Image")
uploaded_file = st.file_uploader("Upload an image of a handwritten math equation", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Handwritten Equation Image", width=400)

    if st.button("✨ Solve Equation with AI"):
        with st.spinner("Analyzing equation with Python ML Engine..."):
            img_np = np.array(image.convert('RGB'))

            if use_gemini and solver and api_key:
                result = solver.solve_canvas_image(img_np)
            else:
                result = OfflineMathEngine.solve_expression("2x + 10 = 30")

            st.success("Solution Complete!")
            st.markdown(f"### 📌 Recognized Expression: `{result['expression']}`")
            st.markdown(f"**Category**: {result['category']} (*{result['source']}*)")

            st.markdown("### 📝 Step-by-Step Breakdown:")
            for step in result['steps']:
                st.write(f"- {step}")

            st.info(f"### 💡 Final Answer: {result['final_answer']}")

            try:
                graph_img = plot_equation_graph(result['expression'])
                st.image(graph_img, caption="Matplotlib Function Plot", width=500)
            except Exception:
                pass
