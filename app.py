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

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

# Check Gemini AI Key in Secrets
has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

# LEFT SIDEBAR DESIGN (Clean 2-Option Layout)
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 20px;'>
    <div style='background: linear-gradient(135deg, #7c3aed, #4f46e5); width: 38px; height: 38px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.3rem; color: white;'>A</div>
    <div>
        <div style='font-weight: 800; font-size: 1.2rem;'>Air Canvas</div>
        <div style='font-size: 0.75rem; color: #818cf8;'>AI Math Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dark / Light Mode Switch Toggle in Sidebar
theme_toggle = st.sidebar.toggle("🌙 Dark Mode / ☀️ Light Mode", value=(st.session_state["theme_mode"] == "Dark"))
st.session_state["theme_mode"] = "Dark" if theme_toggle else "Light"
is_dark = (st.session_state["theme_mode"] == "Dark")

# Simplified 2-Option Sidebar Navigation
sidebar_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "⚙️ Settings & Login"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Bottom Sidebar Gemini AI Status Badge
if has_secrets_key:
    st.sidebar.markdown("""
    <div style='background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px; border-radius: 12px; display: flex; align-items: center; gap: 10px;'>
        <div style='width: 10px; height: 10px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;'></div>
        <div>
            <div style='font-size: 0.85rem; font-weight: 700;'>Gemini AI</div>
            <div style='font-size: 0.72rem; color: #10b981;'>Connected</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style='background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px;'>
        <div style='font-size: 0.85rem; font-weight: 700; color: #f59e0b;'>🟡 Gemini AI Key Optional</div>
        <div style='font-size: 0.72rem;'>Paste key below if needed</div>
    </div>
    """, unsafe_allow_html=True)

user_api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Free key at aistudio.google.com")
show_graph_manual = st.sidebar.checkbox("📊 Show Function Graph", value=False)

solver = GeminiMathSolver(api_key=user_api_key if user_api_key else None)

# Dynamic CSS Theme Injection (Dark vs Light Mode)
if is_dark:
    st.markdown("""
    <style>
        .stApp { background: radial-gradient(circle at 50% 20%, #15103a 0%, #080716 60%, #04030a 100%) !important; color: #ffffff !important; }
        header[data-testid="stHeader"] { background: transparent !important; }
        .hero-title { font-size: 3.5rem !important; font-weight: 800 !important; background: linear-gradient(135deg, #ffffff 0%, #818cf8 60%, #c084fc 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
        .hero-subtitle { font-size: 1.15rem !important; color: #94a3b8 !important; text-align: center; }
        .glass-card { background: rgba(18, 17, 43, 0.65) !important; backdrop-filter: blur(16px); border: 1px solid rgba(139, 92, 246, 0.25); border-radius: 20px; padding: 24px; margin-bottom: 20px; }
        .category-card { background: rgba(20, 20, 48, 0.6) !important; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 16px; padding: 20px; }
        .step-explanation { font-size: 1.1rem !important; font-weight: 600 !important; color: #f1f5f9 !important; margin-top: 10px !important; }
        .math-card { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.45rem !important; font-weight: bold !important; background-color: #12132a !important; color: #4ade80 !important; padding: 12px 20px !important; border-radius: 10px !important; margin-top: 6px !important; margin-bottom: 12px !important; border-left: 5px solid #818cf8 !important; display: block !important; }
        .final-answer-box { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.65rem !important; font-weight: bold !important; background-color: #171836 !important; color: #818cf8 !important; padding: 18px 24px !important; border-radius: 14px !important; border: 2px solid #818cf8 !important; margin-top: 18px !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background: #f8fafc !important; color: #0f172a !important; }
        header[data-testid="stHeader"] { background: #ffffff !important; }
        .hero-title { font-size: 3.5rem !important; font-weight: 800 !important; color: #1e1b4b !important; text-align: center; }
        .hero-subtitle { font-size: 1.15rem !important; color: #475569 !important; text-align: center; }
        .glass-card { background: #ffffff !important; border: 1px solid #e2e8f0; border-radius: 20px; padding: 24px; margin-bottom: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }
        .category-card { background: #ffffff !important; border: 1px solid #cbd5e1; border-radius: 16px; padding: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); }
        .step-explanation { font-size: 1.1rem !important; font-weight: 600 !important; color: #1e293b !important; margin-top: 10px !important; }
        .math-card { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.45rem !important; font-weight: bold !important; background-color: #f1f5f9 !important; color: #15803d !important; padding: 12px 20px !important; border-radius: 10px !important; margin-top: 6px !important; margin-bottom: 12px !important; border-left: 5px solid #3b82f6 !important; display: block !important; }
        .final-answer-box { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.65rem !important; font-weight: bold !important; background-color: #eff6ff !important; color: #1d4ed8 !important; padding: 18px 24px !important; border-radius: 14px !important; border: 2px solid #3b82f6 !important; margin-top: 18px !important; }
    </style>
    """, unsafe_allow_html=True)

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

# OPTION 1: HOME PAGE
if sidebar_page == "🏠 Home":
    st.markdown("<div style='text-align: center;'><span style='background: rgba(139, 92, 246, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); padding: 6px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>✨ AI-Powered Learning</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Math made simple.</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Upload a question. Understand every step. Learn at your pace.</p>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
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

    st.markdown("</div>", unsafe_allow_html=True)

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

    # "What can you solve?" Grid
    st.markdown("### What can you solve?")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("<div class='category-card'><div style='font-size: 1.6rem; color: #c084fc;'>Σ</div><div style='font-weight: 700; font-size: 1.05rem;'>Algebra</div><div style='font-size: 0.8rem;'>Equations and expressions</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='category-card'><div style='font-size: 1.6rem; color: #60a5fa;'>📈</div><div style='font-weight: 700; font-size: 1.05rem;'>Calculus</div><div style='font-size: 0.8rem;'>Limits, derivatives, integrals</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='category-card'><div style='font-size: 1.6rem; color: #4ade80;'>📐</div><div style='font-weight: 700; font-size: 1.05rem;'>Geometry</div><div style='font-size: 0.8rem;'>Shapes, theorems and proofs</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='category-card'><div style='font-size: 1.6rem; color: #f472b6;'>🧠</div><div style='font-weight: 700; font-size: 1.05rem;'>Practice</div><div style='font-size: 0.8rem;'>Quizzes and hints</div></div>", unsafe_allow_html=True)

    # "Recent Solutions" Section
    st.markdown("### Recent Solutions")
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

# OPTION 2: SETTINGS & LOGIN PAGE
elif sidebar_page == "⚙️ Settings & Login":
    st.title("⚙️ Settings & Login Account")
    st.caption("Manage your profile, Gemini AI Key, and app settings")

    # Login / Account Section
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 User Account & Profile")

    if "logged_in_user" not in st.session_state:
        st.session_state["logged_in_user"] = None

    if st.session_state["logged_in_user"] is None:
        user_email = st.text_input("Email / Username", value="student@aircanvas.ai")
        user_pass = st.text_input("Password", type="password", value="••••••••")
        if st.button("🔐 Login / Sign Up", type="primary"):
            st.session_state["logged_in_user"] = user_email
            st.success(f"Welcome back, {user_email}!")
            st.experimental_rerun()
    else:
        st.success(f"Logged in as: **{st.session_state['logged_in_user']}**")
        if st.button("Logout"):
            st.session_state["logged_in_user"] = None
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Gemini AI Status Section
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Gemini AI Connection Status")
    if has_secrets_key:
        st.success("🟢 Google Gemini AI Active (Connected via Cloud Secrets)")
    else:
        st.warning("🟡 Gemini Key Not Found in Cloud Secrets (Paste key in sidebar)")

    st.write("Active AI Model: **gemini-3.8-flash** (`models/gemini-3.8-flash`)")
    st.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("</div>", unsafe_allow_html=True)
