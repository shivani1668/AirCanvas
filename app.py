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

# LEFT SIDEBAR DESIGN
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 12px; margin-bottom: 16px;'>
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

# Navigation Menu
sidebar_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "📷 Upload / Capture", "🧮 Math Tools", "📖 Learning Mode", "🕒 History", "📊 Graph", "🧠 Practice Quiz", "⚙️ Settings"],
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
    # Light Mode Theme Styling
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

# PAGE 1 & 2: HOME / UPLOAD & CAPTURE
if sidebar_page in ["🏠 Home", "📷 Upload / Capture"]:
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

# PAGE 3: HISTORY (Main Page History View!)
elif sidebar_page == "🕒 History":
    st.title("🕒 Solution History")
    st.caption("View, review, or delete all previously solved math questions")

    if not st.session_state["history"]:
        st.info("No saved solutions yet. Upload a math question on the Home tab to build your history!")
    else:
        if st.button("🗑️ Clear All History"):
            st.session_state["history"] = []
            st.experimental_rerun()

        for idx, item in enumerate(reversed(st.session_state["history"])):
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown(f"### Question {len(st.session_state['history']) - idx}: `{item['expression']}`")
            st.markdown(f"**Category**: {item['category']} (*{item['source']}*)")

            st.markdown("#### Step-by-Step Breakdown:")
            for s in item['steps']:
                render_step_with_larger_math(s)

            st.markdown(
                f"<div class='final-answer-box'>💡 Final Answer: {item['final_answer']}</div>",
                unsafe_allow_html=True
            )
            st.markdown("</div>", unsafe_allow_html=True)

# PAGE 4: MATH TOOLS
elif sidebar_page == "🧮 Math Tools":
    st.title("🧮 Math Tools & Calculators")
    st.caption("Quick access to algebra, calculus, geometry, and matrix tools")

    tool_type = st.selectbox("Select Calculator Tool", ["Quadratic Solver", "Calculus Derivative", "Surd Rationalizer"])

    if tool_type == "Quadratic Solver":
        st.subheader("Quadratic Equation Solver (ax² + bx + c = 0)")
        a = st.number_input("Coefficient a", value=1.0)
        b = st.number_input("Coefficient b", value=-5.0)
        c = st.number_input("Coefficient c", value=6.0)

        if st.button("Solve Quadratic Equation"):
            res = OfflineMathEngine.solve_expression(f"{a}*x^2 + ({b})*x + ({c}) = 0")
            st.markdown(f"<div class='final-answer-box'>Result: {res['final_answer']}</div>", unsafe_allow_html=True)

    elif tool_type == "Calculus Derivative":
        st.subheader("Derivative Calculator d/dx(f(x))")
        func = st.text_input("Function f(x)", value="x^3 + 2*x^2 - 5*x + 7")
        if st.button("Calculate Derivative"):
            res = OfflineMathEngine.solve_expression(f"d/dx({func})")
            st.markdown(f"<div class='final-answer-box'>Derivative: {res['final_answer']}</div>", unsafe_allow_html=True)

# PAGE 5: LEARNING MODE
elif sidebar_page == "📖 Learning Mode":
    st.title("📖 Learning Mode & Concept Formulas")
    st.caption("Understand fundamental concepts, formulas, and step-by-step hints")

    st.info("💡 **Hint System Active**: Review formulas and step-by-step concepts before solving problems.")
    concept = st.selectbox("Math Concept", ["Quadratic Formula", "Surd Rationalization", "Exponent Rules", "Differentiation Rules"])

    if concept == "Quadratic Formula":
        st.markdown("""
        ### Quadratic Formula:
        For $ax^2 + bx + c = 0$:
        $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
        - **Discriminant $D = b^2 - 4ac$**:
          - $D > 0$: 2 real distinct roots.
          - $D = 0$: 1 repeated real root.
          - $D < 0$: 2 complex conjugate roots.
        """)

    elif concept == "Surd Rationalization":
        st.markdown("""
        ### Surd Rationalization:
        To rationalize $\\frac{a}{\\sqrt{b} + c}$, multiply numerator & denominator by conjugate $(\\sqrt{b} - c)$:
        $$\\frac{a(\\sqrt{b} - c)}{(\\sqrt{b} + c)(\\sqrt{b} - c)} = \\frac{a(\\sqrt{b} - c)}{b - c^2}$$
        """)

# PAGE 6: FUNCTION GRAPH
elif sidebar_page == "📊 Graph":
    st.title("📊 Function Graph Plotter")
    st.caption("Plot mathematical functions dynamically")

    func_expr = st.text_input("Enter Function (e.g. y = x^2 - 4, sin(x), 2*x + 5)", value="x^2 - 4")
    if st.button("Generate Graph"):
        try:
            graph_img = plot_equation_graph(func_expr)
            st.image(graph_img, caption=f"Plot of {func_expr}", use_column_width=True)
        except Exception as e:
            st.error(f"Error plotting graph: {e}")

# PAGE 7: PRACTICE QUIZ
elif sidebar_page == "🧠 Practice Quiz":
    st.title("🧠 Practice Quiz")
    st.caption("Test your mathematical skills with instant feedback")

    st.markdown("### Question 1: Solve $\\frac{5}{\\sqrt{2} + 1}$")
    ans = st.radio("Select Choice:", ["A) 5√2", "B) 5√2 - 5", "C) 2 - √2", "D) √2 - 5"])

    if st.button("Submit Answer"):
        if "B) 5√2 - 5" in ans:
            st.success("🎉 Correct! Option B is the right choice!")
        else:
            st.error("❌ Incorrect. Correct choice is Option B: 5√2 - 5")

# PAGE 8: SETTINGS
elif sidebar_page == "⚙️ Settings":
    st.title("⚙️ Settings & AI Configuration")
    st.caption("Configure Gemini AI API and app appearance")

    st.markdown("### Gemini AI Connection Status")
    if has_secrets_key:
        st.success("🟢 Google Gemini AI Connected via Cloud Secrets")
    else:
        st.warning("🟡 Gemini Key Not Found in Cloud Secrets (You can paste it in the sidebar)")

    st.markdown("### Active Model Endpoint")
    st.write("Active Model: **gemini-3.8-flash** (`models/gemini-3.8-flash`)")

    st.markdown("---")
    st.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
