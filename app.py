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
    page_icon="⬛",
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

# Custom Solid High-Contrast Black & Bold UI Styling (Sharp Square Corners, No Blipping)
st.markdown("""
<style>
    /* Solid Black App Background (No Glow, No Blipping) */
    .stApp {
        background-color: #000000 !important;
        color: #ffffff !important;
    }

    /* Force ALL Buttons, Inputs, Cards, and Elements to SHARP SQUARE SHAPES */
    button, div, [class*="stButton"], [class*="stTextInput"], [class*="stSelectbox"], .glass-card, .category-card, .math-card, .final-answer-box {
        border-radius: 2px !important;
    }

    /* Primary Bold Button Styling (Square & Bold Blue) */
    div.stButton > button {
        background-color: #1976d2 !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        border: 2px solid #1565c0 !important;
        border-radius: 2px !important;
        padding: 12px 24px !important;
        box-shadow: none !important;
        animation: none !important;
        transition: none !important;
    }

    div.stButton > button:hover {
        background-color: #1565c0 !important;
        border-color: #0d47a1 !important;
    }

    /* Header Titles in Bold Solid Colors */
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #ffffff !important;
        text-align: center;
        margin-bottom: 6px !important;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 1.2rem !important;
        color: #b0bec5 !important;
        text-align: center;
        font-weight: 600 !important;
        margin-bottom: 24px !important;
    }

    .hero-badge {
        background-color: #1976d2 !important;
        color: #ffffff !important;
        border: 2px solid #1565c0 !important;
        padding: 6px 16px !important;
        border-radius: 2px !important;
        font-size: 0.85rem !important;
        font-weight: 800 !important;
        display: inline-block;
        box-shadow: none !important;
    }

    /* Square Solid Cards */
    .glass-card {
        background-color: #121212 !important;
        border: 2px solid #2c2c2c !important;
        border-radius: 2px !important;
        padding: 24px !important;
        margin-bottom: 20px !important;
        box-shadow: none !important;
    }

    .category-card {
        background-color: #1a1a1a !important;
        border: 2px solid #333333 !important;
        border-radius: 2px !important;
        padding: 20px !important;
        min-height: 120px !important;
    }

    /* Math Step Calculations in Times New Roman + Bold Green */
    .step-explanation {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        margin-top: 12px !important;
    }

    .math-card {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
        background-color: #181818 !important;
        color: #388e3c !important;
        padding: 12px 20px !important;
        border-radius: 2px !important;
        margin-top: 6px !important;
        margin-bottom: 14px !important;
        border-left: 6px solid #1976d2 !important;
        display: block !important;
    }

    .final-answer-box {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.7rem !important;
        font-weight: bold !important;
        background-color: #0d47a1 !important;
        color: #ffffff !important;
        padding: 18px 24px !important;
        border-radius: 2px !important;
        border: 2px solid #1976d2 !important;
        margin-top: 20px !important;
    }
</style>
""", unsafe_allow_html=True)

# LEFT SIDEBAR DESIGN (Solid Black Square Theme)
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 20px;'>
    <div style='background: #1976d2; width: 40px; height: 40px; border-radius: 2px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.4rem; color: white;'>A</div>
    <div>
        <div style='font-weight: 900; font-size: 1.3rem; color: #ffffff;'>Air Canvas</div>
        <div style='font-size: 0.8rem; color: #64b5f6; font-weight: bold;'>AI Math Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dark / Light Mode Switch Toggle
theme_toggle = st.sidebar.toggle("🌙 Dark Mode / ☀️ Light Mode", value=(st.session_state["theme_mode"] == "Dark"))
st.session_state["theme_mode"] = "Dark" if theme_toggle else "Light"

# Simplified 2-Option Sidebar Navigation
sidebar_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "⚙️ Settings & Login"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Bottom Sidebar Gemini AI Status Badge (Square & Solid)
if has_secrets_key:
    st.sidebar.markdown("""
    <div style='background: #1b5e20; border: 2px solid #2e7d32; padding: 12px; border-radius: 2px; display: flex; align-items: center; gap: 10px;'>
        <div style='width: 12px; height: 12px; border-radius: 2px; background: #4caf50;'></div>
        <div>
            <div style='font-size: 0.9rem; font-weight: 800; color: #ffffff;'>Gemini AI</div>
            <div style='font-size: 0.75rem; color: #81c784; font-weight: bold;'>Connected</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.sidebar.markdown("""
    <div style='background: #e65100; border: 2px solid #f57c00; padding: 12px; border-radius: 2px;'>
        <div style='font-size: 0.9rem; font-weight: 800; color: #ffffff;'>🟡 Gemini AI Key Optional</div>
        <div style='font-size: 0.75rem; color: #ffe0b2;'>Paste key below if needed</div>
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

# OPTION 1: HOME PAGE
if sidebar_page == "🏠 Home":
    st.markdown("<div style='text-align: center;'><span class='hero-badge'>✨ AI-POWERED LEARNING</span></div>", unsafe_allow_html=True)
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

        if st.button("✨ SOLVE MATH PROBLEM WITH GEMINI AI", type="primary", use_container_width=True):
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
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #ab47bc; font-weight: bold;'>Σ</div><div style='font-weight: 800; font-size: 1.1rem; color: #ffffff;'>Algebra</div><div style='font-size: 0.85rem; color: #b0bec5;'>Equations and expressions</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #42a5f5; font-weight: bold;'>📈</div><div style='font-weight: 800; font-size: 1.1rem; color: #ffffff;'>Calculus</div><div style='font-size: 0.85rem; color: #b0bec5;'>Limits, derivatives, integrals</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #66bb6a; font-weight: bold;'>📐</div><div style='font-weight: 800; font-size: 1.1rem; color: #ffffff;'>Geometry</div><div style='font-size: 0.85rem; color: #b0bec5;'>Shapes, theorems and proofs</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #ff7043; font-weight: bold;'>🧠</div><div style='font-weight: 800; font-size: 1.1rem; color: #ffffff;'>Practice</div><div style='font-size: 0.85rem; color: #b0bec5;'>Quizzes and hints</div></div>", unsafe_allow_html=True)

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
                    <div style='font-weight: 800; font-size: 1rem; color: #ffffff;'>{item['expression']}</div>
                    <div style='font-size: 0.8rem; color: #64b5f6; margin-top: 4px; font-weight: bold;'>{item['category']}</div>
                    <div style='font-size: 0.9rem; font-weight: 900; color: #66bb6a; margin-top: 8px;'>Ans: {item['final_answer']}</div>
                </div>
                """, unsafe_allow_html=True)

# OPTION 2: SETTINGS & LOGIN PAGE
elif sidebar_page == "⚙️ Settings & Login":
    st.title("⚙️ Settings & Login Account")
    st.caption("Manage your profile, Gemini AI Key, and app settings")

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 👤 User Account & Profile")

    if "logged_in_user" not in st.session_state:
        st.session_state["logged_in_user"] = None

    if st.session_state["logged_in_user"] is None:
        user_email = st.text_input("Email / Username", value="student@aircanvas.ai")
        user_pass = st.text_input("Password", type="password", value="••••••••")
        if st.button("🔐 LOGIN / SIGN UP"):
            st.session_state["logged_in_user"] = user_email
            st.success(f"Welcome back, {user_email}!")
            st.experimental_rerun()
    else:
        st.success(f"Logged in as: **{st.session_state['logged_in_user']}**")
        if st.button("LOGOUT"):
            st.session_state["logged_in_user"] = None
            st.experimental_rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Gemini AI Connection Status")
    if has_secrets_key:
        st.success("🟢 Google Gemini AI Connected via Cloud Secrets")
    else:
        st.warning("🟡 Gemini Key Not Found in Cloud Secrets (Paste key in sidebar)")

    st.write("Active AI Model: **gemini-3.8-flash** (`models/gemini-3.8-flash`)")
    st.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("</div>", unsafe_allow_html=True)
