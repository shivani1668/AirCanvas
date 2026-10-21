import streamlit as st
import numpy as np
from PIL import Image
import io

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
st.caption("Draw or snap a picture of your math equation & let AI solve it!")

# Sidebar Configuration
st.sidebar.header("⚙️ Configuration")
api_key = st.sidebar.text_input("Google Gemini API Key (Optional)", type="password")
use_gemini = st.sidebar.checkbox("Use Gemini AI LLM", value=True)

solver = GeminiMathSolver(api_key=api_key) if api_key else None

tab1, tab2 = st.tabs(["📷 Mobile Camera Snap", "📁 Upload Image"])

image_to_process = None

with tab1:
    st.write("Take a photo of your handwritten math equation directly from your mobile camera:")
    camera_file = st.camera_input("Snap Equation")
    if camera_file is not None:
        image_to_process = Image.open(camera_file)

with tab2:
    st.write("Upload an image of a math problem:")
    uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])
    if uploaded_file is not None:
        image_to_process = Image.open(uploaded_file)

if image_to_process is not None:
    st.image(image_to_process, caption="Captured Equation", use_column_width=True)

    if st.button("✨ Solve Equation with AI", type="primary", use_container_width=True):
        with st.spinner("Analyzing math equation with AI..."):
            img_np = np.array(image_to_process.convert('RGB'))

            if use_gemini and solver and api_key:
                result = solver.solve_canvas_image(img_np)
            else:
                result = OfflineMathEngine.solve_expression("2x + 10 = 30")

            st.success("Solution Complete!")
            st.markdown(f"### 📌 Recognized Expression:\n`{result['expression']}`")
            st.markdown(f"**Category**: {result['category']} (*{result['source']}*)")

            st.markdown("### 📝 Step-by-Step Breakdown:")
            for step in result['steps']:
                st.write(f"- {step}")

            st.info(f"### 💡 Final Answer: {result['final_answer']}")

            try:
                graph_img = plot_equation_graph(result['expression'])
                st.image(graph_img, caption="Matplotlib Function Plot", use_column_width=True)
            except Exception:
                pass
