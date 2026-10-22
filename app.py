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

# Page Config
st.set_page_config(
    page_title="Air Canvas - AI Math Solver",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state["history"] = []

# Custom Glassmorphism Dark Theme Styling
st.markdown("""
<style>
    /* Dark Theme Core */
    .stApp {
        background-color: #0c0d1a !important;
        color: #f5e0dc !important;
    }

    /* Global Sans-Serif Font */
    html, body, p, div, span, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }

    /* Hero Section Header */
    .hero-title {
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #ffffff 0%, #89b4fa 50%, #cba6f7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1.25rem !important;
        color: #a6adc8 !important;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero-badge {
        background: rgba(137, 180, 250, 0.15);
        color: #89b4fa;
        border: 1px solid rgba(137, 180, 250, 0.3);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 12px;
    }

    /* Glass Cards */
    .glass-card {
        background: rgba(22, 24, 46, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .solve-category-card {
        background: rgba(30, 32, 64, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        transition: all 0.3s ease;
    }

    /* Times New Roman + Symbol Typography ONLY for Math Expressions & Cards */
    .step-explanation {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #f5e0dc !important;
        margin-top: 12px !important;
    }

    .math-card {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.45rem !important;
        font-weight: bold !important;
        background-color: #181825 !important;
        color: #a6e3a1 !important;
        padding: 12px 20px !important;
        border-radius: 10px !important;
        margin-top: 6px !important;
        margin-bottom: 14px !important;
        border-left: 5px solid #89b4fa !important;
        letter-spacing: 0.5px !important;
        display: block !important;
    }

    .final-answer-box {
        font-family: 'Times New Roman', 'Times', 'Cambria Math', 'Symbol', serif !important;
        font-size: 1.65rem !important;
        font-weight: bold !important;
        background-color: #1e1e2e !important;
        color: #89b4fa !important;
        padding: 18px 24px !important;
        border-radius: 14px !important;
        border: 2px solid #89b4fa !important;
        margin-top: 18px !important;
        box-shadow: 0 4px 20px rgba(137, 180, 250, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Check Gemini AI Key in Secrets
has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

# SIDEBAR NAVIGATION (Matching User Design Specs)
st.sidebar.markdown("## 🌌 Air Canvas")
st.sidebar.caption("AI Math Solver")

sidebar_page = st.sidebar.radio(
    "Navigation",
    ["🏠 Home / Upload", "📐 Math Tools", "📖 Learning Mode", "📜 Solution History", "📊 Function Graph", "🎯 Practice Quiz", "⚙️ Settings & AI Status"],
    label_visibility="collapsed"
)

st.sidebar.markdown("---")

# Gemini AI Connection Badge
if has_secrets_key:
    st.sidebar.success("🟢 Gemini AI Connected")
else:
    st.sidebar.warning("🟡 Gemini AI Key Optional")

user_api_key = st.sidebar.text_input("Custom Gemini API Key", type="password", help="Get free key at aistudio.google.com")
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

# PAGE 1: HOME / UPLOAD (Matching Screenshot 1)
if sidebar_page == "🏠 Home / Upload":
    st.markdown("<div style='text-align: center;'><span class='hero-badge'>✨ AI-Powered Learning</span></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='hero-title'>Math made simple.</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-subtitle'>Upload a question. Understand every step. Learn at your pace.</p>", unsafe_allow_html=True)

    # Central Upload Area
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    input_mode = st.radio("Choose Input Method", ["🖼️ Upload Image", "📷 Open Camera"], horizontal=True)

    image_to_process = None

    if input_mode == "🖼️ Upload Image":
        uploaded_file = st.file_uploader("Upload a photo of your math problem", type=["png", "jpg", "jpeg"])
        if uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)
    else:
        camera_file = st.camera_input("Snap Math Problem")
        if camera_file is not None:
            image_to_process = Image.open(camera_file)

    st.markdown("</div>", unsafe_allow_html=True)

    # Solution Execution Area
    if image_to_process is not None:
        st.image(image_to_process, caption="Problem Image", use_column_width=True)

        if st.button("✨ Solve Math Problem with Gemini AI", type="primary", use_container_width=True):
            with st.spinner("Analyzing math problem & generating step-by-step AI solution..."):
                img_np = np.array(image_to_process.convert('RGB'))

                result = solver.solve_canvas_image(img_np, pil_image=image_to_process)

                # Save to History
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

                # Optional Graph Plotting (Only if asked in question)
                expr_lower = result['expression'].lower()
                if any(w in expr_lower for w in ["graph", "plot", "sketch", "curve", "draw"]):
                    try:
                        graph_img = plot_equation_graph(result['expression'])
                        st.image(graph_img, caption="Function Graph Visualizer", use_column_width=True)
                    except Exception:
                        pass

    # "What can you solve?" Grid Section
    st.markdown("### What can you solve?")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='solve-category-card'>
            <h3>Σ Algebra</h3>
            <p style='color: #a6adc8;'>Equations, polynomials, and expressions</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='solve-category-card'>
            <h3>📈 Calculus</h3>
            <p style='color: #a6adc8;'>Limits, derivatives, and integrals</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='solve-category-card'>
            <h3>📐 Geometry</h3>
            <p style='color: #a6adc8;'>Shapes, theorems, and proofs</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='solve-category-card'>
            <h3>🧠 Practice</h3>
            <p style='color: #a6adc8;'>Quizzes and step-by-step hints</p>
        </div>
        """, unsafe_allow_html=True)

# PAGE 2: MATH TOOLS
elif sidebar_page == "📐 Math Tools":
    st.title("📐 Math Tools & Calculators")
    st.caption("Quick access to algebra, calculus, geometry, and matrix tools")

    tool_type = st.selectbox("Select Calculator Tool", ["Quadratic Solver", "Calculus Derivative", "Matrix Determinant", "Surd Rationalizer"])

    if tool_type == "Quadratic Solver":
        st.subheader("Quadratic Equation Solver (ax² + bx + c = 0)")
        a = st.number_input("Coefficient a", value=1.0)
        b = st.number_input("Coefficient b", value=-5.0)
        c = st.number_input("Coefficient c", value=6.0)

        if st.button("Solve Quadratic Equation"):
            res = OfflineMathEngine.solve_expression(f"{a}*x^2 + ({b})*x + ({c}) = 0")
            st.markdown(f"### Result: `{res['final_answer']}`")

    elif tool_type == "Calculus Derivative":
        st.subheader("Derivative Calculator d/dx(f(x))")
        func = st.text_input("Function f(x)", value="x^3 + 2*x^2 - 5*x + 7")
        if st.button("Calculate Derivative"):
            res = OfflineMathEngine.solve_expression(f"d/dx({func})")
            st.markdown(f"### Derivative: `{res['final_answer']}`")

# PAGE 3: LEARNING MODE
elif sidebar_page == "📖 Learning Mode":
    st.title("📖 Learning Mode & Hints")
    st.caption("Understand fundamental concepts, formulas, and step-by-step hints")

    st.info("💡 **Hint System Active**: Select a math concept to review formulas before solving problems.")
    concept = st.selectbox("Math Concept", ["Quadratic Formula", "Rationalization", "Exponent Rules", "Differentiation Rules"])

    if concept == "Quadratic Formula":
        st.markdown("""
        ### Quadratic Formula Formula:
        For $ax^2 + bx + c = 0$:
        $$x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$
        - **Discriminant $D = b^2 - 4ac$**:
          - If $D > 0$: 2 real distinct roots.
          - If $D = 0$: 1 repeated real root.
          - If $D < 0$: 2 complex conjugate roots.
        """)

    elif concept == "Rationalization":
        st.markdown("""
        ### Surd Rationalization:
        To rationalize $\\frac{a}{\\sqrt{b} + c}$, multiply numerator & denominator by conjugate $(\\sqrt{b} - c)$:
        $$\\frac{a(\\sqrt{b} - c)}{(\\sqrt{b} + c)(\\sqrt{b} - c)} = \\frac{a(\\sqrt{b} - c)}{b - c^2}$$
        """)

# PAGE 4: SOLUTION HISTORY
elif sidebar_page == "📜 Solution History":
    st.title("📜 Solution History")
    st.caption("Save previous questions and solutions")

    if not st.session_state["history"]:
        st.info("No saved solutions yet. Solve a math problem on the Home tab to see it here!")
    else:
        for idx, item in enumerate(reversed(st.session_state["history"])):
            with st.expander(f"Equation {len(st.session_state['history']) - idx}: {item['expression']}"):
                st.write(f"**Category**: {item['category']}")
                for s in item['steps']:
                    st.write(f"- {s}")
                st.success(f"Final Answer: {item['final_answer']}")

# PAGE 5: FUNCTION GRAPH
elif sidebar_page == "📊 Function Graph":
    st.title("📊 Function Graph Plotter")
    st.caption("Plot mathematical functions dynamically")

    func_expr = st.text_input("Enter Function (e.g. y = x^2 - 4, sin(x), 2*x + 5)", value="x^2 - 4")
    if st.button("Generate Graph"):
        try:
            graph_img = plot_equation_graph(func_expr)
            st.image(graph_img, caption=f"Plot of {func_expr}", use_column_width=True)
        except Exception as e:
            st.error(f"Error plotting graph: {e}")

# PAGE 6: PRACTICE QUIZ
elif sidebar_page == "🎯 Practice Quiz":
    st.title("🎯 Practice Quiz")
    st.caption("Test your mathematical skills with instant feedback")

    st.markdown("### Question 1: Solve $\\frac{5}{\\sqrt{2} + 1}$")
    ans = st.radio("Select Choice:", ["A) 5√2", "B) 5√2 - 5", "C) 2 - √2", "D) √2 - 5"])

    if st.button("Submit Answer"):
        if "B) 5√2 - 5" in ans:
            st.success("🎉 Correct! Option B is the right choice!")
        else:
            st.error("❌ Incorrect. Correct choice is Option B: 5√2 - 5")

# PAGE 7: SETTINGS & AI STATUS
elif sidebar_page == "⚙️ Settings & AI Status":
    st.title("⚙️ Settings & AI Status")
    st.caption("Configure Gemini AI API and app appearance")

    st.markdown("### Gemini AI Connection Status")
    if has_secrets_key:
        st.success("🟢 Google Gemini AI Connected via Cloud Secrets")
    else:
        st.warning("🟡 Gemini Key Not Found in Cloud Secrets (You can paste it below)")

    st.markdown("### Model Selection")
    st.write("Active Model: **gemini-3.8-flash** (`models/gemini-3.8-flash`)")

    st.markdown("---")
    st.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
