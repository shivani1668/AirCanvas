import sys
import os
import json
import numpy as np
from PIL import Image

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import streamlit as st

try:
    from src.gemini_solver import GeminiMathSolver
    from src.offline_solver import OfflineMathEngine
except ImportError:
    from gemini_solver import GeminiMathSolver
    from offline_solver import OfflineMathEngine

from utils.math_plotter import plot_equation_graph

st.set_page_config(
    page_title="Air Canvas - AI Math Solver",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "history" not in st.session_state:
    st.session_state["history"] = []

# Pixel-Perfect Dark Space Glassmorphism Styling matching User Mockup Screenshot
st.markdown("""
<style>
    /* Dark Space Background */
    .stApp {
        background: radial-gradient(circle at 50% 20%, #15103a 0%, #080716 60%, #04030a 100%) !important;
        color: #ffffff !important;
    }

    /* Hide Default Streamlit Header/Footer Padding */
    header[data-testid="stHeader"] { background: transparent !important; }
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }

    /* Custom Top Navigation Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 24px;
        margin-bottom: 20px;
    }

    .nav-links {
        display: flex;
        gap: 28px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #a0a5cb;
    }

    .nav-item-active {
        color: #ffffff !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #8b5cf6;
        padding-bottom: 4px;
    }

    /* Hero Section Header */
    .hero-badge-container {
        text-align: center;
        margin-top: 10px;
        margin-bottom: 12px;
    }

    .hero-badge {
        background: rgba(139, 92, 246, 0.15);
        color: #c084fc;
        border: 1px solid rgba(192, 132, 252, 0.3);
        padding: 6px 18px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: inline-block;
        box-shadow: 0 0 15px rgba(192, 132, 252, 0.2);
    }

    .hero-title {
        font-size: 3.6rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 0%, #e0e7ff 40%, #818cf8 70%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 8px !important;
        letter-spacing: -0.5px;
    }

    .hero-subtitle {
        font-size: 1.15rem !important;
        color: #94a3b8 !important;
        text-align: center;
        margin-bottom: 28px !important;
    }

    /* Central Upload Glass Box */
    .central-upload-box {
        background: rgba(18, 17, 43, 0.65);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 22px;
        padding: 32px 24px;
        text-align: center;
        max-width: 620px;
        margin: 0 auto 36px auto;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), inset 0 0 20px rgba(139, 92, 246, 0.05);
    }

    /* Category Cards Grid */
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 30px;
        margin-bottom: 16px;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
    }

    .explore-link {
        font-size: 0.9rem;
        color: #818cf8;
        text-decoration: none;
        font-weight: 500;
    }

    .category-card {
        background: rgba(20, 20, 48, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 16px;
        padding: 20px;
        min-height: 120px;
        transition: transform 0.2s ease, border 0.2s ease;
    }

    .category-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(129, 140, 248, 0.4);
    }

    /* Times New Roman + Symbol Typography ONLY for Math Steps & Cards */
    .step-explanation {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #f1f5f9 !important;
        margin-top: 12px !important;
    }

    .math-card {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.45rem !important;
        font-weight: bold !important;
        background-color: #12132a !important;
        color: #4ade80 !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-top: 6px !important;
        margin-bottom: 14px !important;
        border-left: 5px solid #818cf8 !important;
        letter-spacing: 0.5px !important;
        display: block !important;
    }

    .final-answer-box {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.65rem !important;
        font-weight: bold !important;
        background-color: #171836 !important;
        color: #818cf8 !important;
        padding: 18px 24px !important;
        border-radius: 14px !important;
        border: 2px solid #818cf8 !important;
        margin-top: 18px !important;
        box-shadow: 0 4px 25px rgba(129, 140, 248, 0.25);
    }
</style>
""", unsafe_allow_html=True)

# Secrets Check
has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

# LEFT SIDEBAR DESIGN (Matching Mockup Image)
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 20px;'>
    <div style='background: linear-gradient(135deg, #7c3aed, #4f46e5); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.3rem; color: white;'>A</div>
    <div>
        <div style='font-weight: 800; font-size: 1.2rem; color: #ffffff;'>Air Canvas</div>
        <div style='font-size: 0.75rem; color: #818cf8;'>AI Math Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

sidebar_page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home", "📷 Upload / Capture", "🧮 Math Tools", "📖 Learning Mode", "🕒 History", "📊 Graph", "🧠 Practice Quiz", "⚙️ Settings"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Bottom Sidebar Gemini AI Status Badge (Matching Mockup)
if has_secrets_key:
    st.sidebar.markdown("""
    <div style='background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px; border-radius: 12px; display: flex; align-items: center; gap: 10px;'>
        <div style='width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;'></div>
        <div>
            <div style='font-size: 0.85rem; font-weight: 700; color: #ffffff;'>Gemini AI</div>
            <div style='font-size: 0.72rem; color: #10b981;'>Connected</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style='background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;'>
        <div style='font-size: 0.85rem; font-weight: 700; color: #f59e0b;'>🟡 Gemini AI Key Optional</div>
        <div style='font-size: 0.72rem; color: #94a3b8;'>Paste key below if needed</div>
    </div>
    """, unsafe_allow_html=True)

user_api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Free key at aistudio.google.com")
show_graph_manual = st.sidebar.checkbox("📊 Show Function Graph", value=False)

solver = GeminiMathSolver(api_key=user_api_key if user_api_key else None)

def render_step_with_larger_math(step_text: str):
    step_str = str(step_text).strip()
    if ":" in step_str:
        parts = step_str.split(":", 1)
        explanation = parts[0].strip()
        calc = parts[1].strip()
        st.markdown(f"<div class='step-explanation'>• {explanation}:</div>", unsafe_allow_html=True)
        if calc:
            display_calc = calc if calc.startswith("⇒") else f"⇒ {calc}"
            st.markdown(f"<div class='math-card'>{display_calc}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='step-explanation'>• {step_str}</div>", unsafe_allow_html=True)

# TOP NAVIGATION BAR
st.markdown("""
<div class='top-nav'>
    <div class='nav-links'>
        <span class='nav-item-active'>Home</span>
        <span>History</span>
        <span>Math Tools</span>
        <span>Practice</span>
        <span>About</span>
    </div>
    <div style='color: #a0a5cb; font-size: 1.1rem;'>☀️ &nbsp; 👤</div>
</div>
""", unsafe_allow_html=True)

# HERO SECTION & CENTRAL UPLOAD BOX (Matching Screenshot 1)
st.markdown("<div class='hero-badge-container'><span class='hero-badge'>✨ AI-Powered Learning</span></div>", unsafe_allow_html=True)
st.markdown("<h1 class='hero-title'>Math made simple.</h1>", unsafe_allow_html=True)
st.markdown("<p class='hero-subtitle'>Upload a question. Understand every step. Learn at your pace.</p>", unsafe_allow_html=True)

# Central Upload Glass Box
st.markdown("""
<div class='central-upload-box'>
    <div style='font-size: 2.2rem; margin-bottom: 8px;'>☁️</div>
    <div style='font-size: 1.15rem; font-weight: 700; color: #ffffff;'>Upload a photo of your math problem</div>
    <div style='font-size: 0.85rem; color: #64748b; margin: 6px 0 16px 0;'>or</div>
</div>
""", unsafe_allow_html=True)

input_tab1, input_tab2 = st.tabs(["🖼️ Upload Image", "📷 Open Camera"])

image_to_process = None

with input_tab1:
    uploaded_file = st.file_uploader("Choose math image file", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded_file is not None:
        image_to_process = Image.open(uploaded_file)

with input_tab2:
    camera_on = st.toggle("📷 Enable Camera", value=False)
    if camera_on:
        camera_file = st.camera_input("Snap Math Question")
        if camera_file is not None:
            image_to_process = Image.open(camera_file)

# Solution Display Area
if image_to_process is not None:
    st.image(image_to_process, caption="Math Question Image", use_column_width=True)

    if st.button("✨ Solve Math Problem with Gemini AI", type="primary", use_container_width=True):
        with st.spinner("Analyzing math problem & generating step-by-step AI solution..."):
            img_np = np.array(image_to_process.convert('RGB'))
            result = solver.solve_canvas_image(img_np, pil_image=image_to_process)

            st.session_state["history"].append(result)

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

# "What can you solve?" Section (Matching Screenshot 1 Grid)
st.markdown("""
<div class='section-header'>
    <div class='section-title'>What can you solve?</div>
    <a href='#' class='explore-link'>Explore all →</a>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class='category-card'>
        <div style='font-size: 1.6rem; color: #c084fc;'>Σ</div>
        <div style='font-weight: 700; font-size: 1.05rem; margin-top: 6px;'>Algebra</div>
        <div style='font-size: 0.8rem; color: #94a3b8;'>Equations and expressions</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class='category-card'>
        <div style='font-size: 1.6rem; color: #60a5fa;'>📈</div>
        <div style='font-weight: 700; font-size: 1.05rem; margin-top: 6px;'>Calculus</div>
        <div style='font-size: 0.8rem; color: #94a3b8;'>Limits, derivatives and integrals</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class='category-card'>
        <div style='font-size: 1.6rem; color: #4ade80;'>📐</div>
        <div style='font-weight: 700; font-size: 1.05rem; margin-top: 6px;'>Geometry</div>
        <div style='font-size: 0.8rem; color: #94a3b8;'>Shapes, theorems and proofs</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class='category-card'>
        <div style='font-size: 1.6rem; color: #f472b6;'>🧠</div>
        <div style='font-weight: 700; font-size: 1.05rem; margin-top: 6px;'>Practice</div>
        <div style='font-size: 0.8rem; color: #94a3b8;'>Quizzes and step-by-step hints</div>
    </div>
    """, unsafe_allow_html=True)

# "Recent Solutions" Section (Matching Screenshot 1)
st.markdown("""
<div class='section-header'>
    <div class='section-title'>Recent Solutions</div>
    <a href='#' class='explore-link'>View all →</a>
</div>
""", unsafe_allow_html=True)

if not st.session_state["history"]:
    st.info("No recent solutions yet. Upload a math question above to see it here!")
else:
    hist_cols = st.columns(min(4, len(st.session_state["history"])))
    for idx, item in enumerate(reversed(st.session_state["history"][:4])):
        with hist_cols[idx]:
            st.markdown(f"""
            <div class='category-card'>
                <div style='font-weight: 700; font-size: 0.95rem;'>{item['expression']}</div>
                <div style='font-size: 0.78rem; color: #818cf8; margin-top: 4px;'>{item['category']}</div>
                <div style='font-size: 0.85rem; font-weight: bold; color: #4ade80; margin-top: 8px;'>Ans: {item['final_answer']}</div>
            </div>
            """, unsafe_allow_html=True)
