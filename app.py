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

if "typed_question" not in st.session_state:
    st.session_state["typed_question"] = "2x + 10 = 30"

# Secrets Check
has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

# Dark / Light Mode Switch Toggle
theme_toggle = st.sidebar.toggle("🌙 Dark Mode / ☀️ Light Mode", value=(st.session_state["theme_mode"] == "Dark"))
st.session_state["theme_mode"] = "Dark" if theme_toggle else "Light"
is_dark = (st.session_state["theme_mode"] == "Dark")

# LEFT SIDEBAR DESIGN
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
    <div style='background: #1976d2; width: 40px; height: 40px; border-radius: 2px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 1.4rem; color: white;'>A</div>
    <div>
        <div style='font-weight: 900; font-size: 1.3rem;'>Air Canvas</div>
        <div style='font-size: 0.8rem; font-weight: bold;'>AI Math Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Simplified 2-Option Sidebar Navigation
sidebar_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "⚙️ Settings & Login"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Gemini AI Status Badge
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

st.sidebar.markdown("<br><div style='font-weight: bold; font-size: 0.85rem;'>Made with 💝 by Shivani</div>", unsafe_allow_html=True)

solver = GeminiMathSolver(api_key=user_api_key if user_api_key else None)

# Dynamic CSS Theme Injection
if is_dark:
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #000000 !important;
            color: #ffffff !important;
        }
        section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #0c0d1a !important;
            color: #ffffff !important;
            border-right: 1px solid #1e2040 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #ffffff !important;
        }
        .hero-main-title { color: #ffffff !important; text-align: center !important; font-size: 3.8rem !important; font-weight: 900 !important; }
        .hero-title { font-size: 3.2rem !important; font-weight: 800 !important; color: #ffffff !important; text-align: center; }
        .hero-subtitle { font-size: 1.2rem !important; color: #b0bec5 !important; text-align: center; font-weight: 600 !important; }
        .glass-card { background-color: #121212 !important; border: 2px solid #2c2c2c !important; border-radius: 2px !important; padding: 24px !important; margin-bottom: 20px !important; }
        .category-card { background-color: #1a1a1a !important; border: 2px solid #333333 !important; border-radius: 2px !important; padding: 20px !important; color: #ffffff !important; }
        .step-explanation { font-size: 1.15rem !important; font-weight: 700 !important; color: #ffffff !important; margin-top: 12px !important; }
        .math-card { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.5rem !important; font-weight: bold !important; background-color: #181818 !important; color: #388e3c !important; padding: 12px 20px !important; border-radius: 2px !important; margin-top: 6px !important; margin-bottom: 14px !important; border-left: 6px solid #1976d2 !important; display: block !important; }
        .final-answer-box { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.7rem !important; font-weight: bold !important; background-color: #0d47a1 !important; color: #ffffff !important; padding: 18px 24px !important; border-radius: 2px !important; border: 2px solid #1976d2 !important; margin-top: 20px !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"] {
            background-color: #f8fafc !important;
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
            background-color: #ffffff !important;
            color: #0f172a !important;
            border-right: 1px solid #cbd5e1 !important;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
            color: #0f172a !important;
        }
        .hero-main-title { color: #1e1b4b !important; text-align: center !important; font-size: 3.8rem !important; font-weight: 900 !important; }
        .hero-title { font-size: 3.2rem !important; font-weight: 800 !important; color: #1e1b4b !important; text-align: center; }
        .hero-subtitle { font-size: 1.2rem !important; color: #475569 !important; text-align: center; font-weight: 600 !important; }
        .glass-card { background-color: #ffffff !important; border: 2px solid #cbd5e1 !important; border-radius: 2px !important; padding: 24px !important; margin-bottom: 20px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important; }
        .category-card { background-color: #ffffff !important; border: 2px solid #cbd5e1 !important; border-radius: 2px !important; padding: 20px !important; color: #0f172a !important; }
        .step-explanation { font-size: 1.15rem !important; font-weight: 700 !important; color: #0f172a !important; margin-top: 12px !important; }
        .math-card { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.5rem !important; font-weight: bold !important; background-color: #f1f5f9 !important; color: #15803d !important; padding: 12px 20px !important; border-radius: 2px !important; margin-top: 6px !important; margin-bottom: 14px !important; border-left: 6px solid #2563eb !important; display: block !important; }
        .final-answer-box { font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important; font-size: 1.7rem !important; font-weight: bold !important; background-color: #eff6ff !important; color: #1d4ed8 !important; padding: 18px 24px !important; border-radius: 2px !important; border: 2px solid #2563eb !important; margin-top: 20px !important; }
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
    st.markdown("""
    <div style='text-align: center; margin-bottom: 16px;'>
        <h1 class='hero-main-title'>🌌 Air Canvas</h1>
        <div style='font-size: 1.25rem; font-weight: 800; color: #1976d2;'>AI Math Solver</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='text-align: center;'><span style='background-color: #1976d2; color: #ffffff; padding: 6px 16px; border-radius: 2px; font-size: 0.85rem; font-weight: 800;'>✨ AI-POWERED LEARNING</span></div>", unsafe_allow_html=True)
    st.markdown("<h2 class='hero-title'>Math made simple.</h2>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Upload, snap, or type a question. Learn at your pace.</p>", unsafe_allow_html=True)

    # Central Box Displaying "Made with 💝 by Shivani"
    st.markdown("""
    <div class='glass-card' style='text-align: center; padding: 18px 24px; margin-bottom: 16px;'>
        <div style='font-size: 1.4rem; font-weight: 900; color: #ffffff;'>✨ Made with 💝 by Shivani</div>
        <div style='font-size: 0.9rem; color: #b0bec5; margin-top: 4px;'>Upload image, snap with camera, or type equation with math symbol keyboard</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    input_tab1, input_tab2, input_tab3 = st.tabs(["🖼️ Upload Image", "📷 Open Camera", "⌨️ Type Question"])

    image_to_process = None
    text_question_to_process = None

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

    with input_tab3:
        st.write("Type or paste your math question / equation:")

        # Math Symbol Keyboard Buttons
        st.markdown("**Math Symbol Keyboard (Click symbol to insert):**")
        sym_col1, sym_col2, sym_col3, sym_col4, sym_col5, sym_col6 = st.columns(6)

        def append_symbol(sym):
            st.session_state["typed_question"] = st.session_state.get("typed_question", "") + " " + sym

        with sym_col1:
            if st.button("√ (Root)"): append_symbol("√")
            if st.button("x² (Power)"): append_symbol("^2")
        with sym_col2:
            if st.button("± (Plus-Minus)"): append_symbol("±")
            if st.button("/ (Fraction)"): append_symbol("/")
        with sym_col3:
            if st.button("d/dx (Diff)"): append_symbol("d/dx(")
            if st.button("∫ (Integral)"): append_symbol("∫")
        with sym_col4:
            if st.button("π (Pi)"): append_symbol("π")
            if st.button("θ (Theta)"): append_symbol("θ")
        with sym_col5:
            if st.button("∞ (Infinity)"): append_symbol("∞")
            if st.button("≤ (Less Equal)"): append_symbol("≤")
        with sym_col6:
            if st.button("≥ (Greater Equal)"): append_symbol("≥")
            if st.button("≠ (Not Equal)"): append_symbol("≠")

        typed_val = st.text_area("Question Text Area", value=st.session_state.get("typed_question", ""), height=100)
        st.session_state["typed_question"] = typed_val

        if st.button("✨ SOLVE TYPED QUESTION WITH AI", type="primary", use_container_width=True):
            text_question_to_process = typed_val

    st.markdown("</div>", unsafe_allow_html=True)

    # Process Image or Typed Question
    if image_to_process is not None or text_question_to_process is not None:
        if image_to_process is not None:
            st.image(image_to_process, caption="Math Question Image", use_column_width=True)

        solve_trigger = False
        if text_question_to_process is not None:
            solve_trigger = True
        else:
            solve_trigger = st.button("✨ SOLVE MATH PROBLEM WITH GEMINI AI", type="primary", use_container_width=True)

        if solve_trigger:
            with st.spinner("Analyzing math problem & generating step-by-step AI solution..."):
                if text_question_to_process is not None:
                    result = OfflineMathEngine.solve_expression(text_question_to_process)
                else:
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
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #ab47bc; font-weight: bold;'>Σ</div><div style='font-weight: 800; font-size: 1.1rem;'>Algebra</div><div style='font-size: 0.85rem;'>Equations and expressions</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #1976d2; font-weight: bold;'>📈</div><div style='font-weight: 800; font-size: 1.1rem;'>Calculus</div><div style='font-size: 0.85rem;'>Limits, derivatives, integrals</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #388e3c; font-weight: bold;'>📐</div><div style='font-weight: 800; font-size: 1.1rem;'>Geometry</div><div style='font-size: 0.85rem;'>Shapes, theorems and proofs</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='category-card'><div style='font-size: 1.8rem; color: #f57c00; font-weight: bold;'>🧠</div><div style='font-weight: 800; font-size: 1.1rem;'>Practice</div><div style='font-size: 0.85rem;'>Quizzes and hints</div></div>", unsafe_allow_html=True)

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
                    <div style='font-weight: 800; font-size: 1rem;'>{item['expression']}</div>
                    <div style='font-size: 0.8rem; color: #1976d2; margin-top: 4px; font-weight: bold;'>{item['category']}</div>
                    <div style='font-size: 0.9rem; font-weight: 900; color: #388e3c; margin-top: 8px;'>Ans: {item['final_answer']}</div>
                </div>
                """, unsafe_allow_html=True)

    # App Footer
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 1.1rem; font-weight: 800; color: #1976d2;'>✨ Made with 💝 by Shivani ✨</div>", unsafe_allow_html=True)

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
