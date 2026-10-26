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
    from src.air_canvas import AirCanvasDetector
except ImportError:
    from gemini_solver import GeminiMathSolver
    from offline_solver import OfflineMathEngine
    from air_canvas import AirCanvasDetector

from utils.math_plotter import plot_equation_graph
from utils.image_processing import preprocess_canvas_for_ai

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
    st.session_state["typed_question"] = ""

if "air_detector" not in st.session_state:
    st.session_state["air_detector"] = AirCanvasDetector()

# Secrets Check
has_secrets_key = False
try:
    if "GEMINI_API_KEY" in st.secrets and len(st.secrets["GEMINI_API_KEY"].strip()) > 0:
        has_secrets_key = True
except Exception:
    pass

# Theme mode toggle
theme_toggle = st.sidebar.toggle("🌙 Dark Mode / ☀️ Light Mode", value=(st.session_state["theme_mode"] == "Dark"))
st.session_state["theme_mode"] = "Dark" if theme_toggle else "Light"
is_dark = (st.session_state["theme_mode"] == "Dark")

# SIDEBAR DESIGN MATCHING SCREENSHOT
st.sidebar.markdown("""
<div style='display: flex; align-items: center; gap: 14px; margin-bottom: 24px; padding-top: 10px;'>
    <div style='background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(59,130,246,0.4);'>
        <span style='font-size: 1.5rem;'>🌌</span>
    </div>
    <div>
        <div style='font-weight: 800; font-size: 1.25rem; color: #ffffff; letter-spacing: -0.5px;'>Air Canvas</div>
        <div style='font-size: 0.75rem; font-weight: 600; color: #94a3b8;'>AI Math Solver</div>
    </div>
</div>
""", unsafe_allow_html=True)

sidebar_page = st.sidebar.radio(
    "Navigation Menu",
    ["🏠 Home", "⚙️ Settings & Login"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<br>", unsafe_allow_html=True)

# Gemini AI Connected Status Badge matching screenshot
st.sidebar.markdown("""
<div style='background: linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(5,150,105,0.25) 100%); border: 1.5px solid #059669; padding: 14px 16px; border-radius: 14px; display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(16,185,129,0.1);'>
    <div style='display: flex; align-items: center; gap: 10px;'>
        <div style='width: 8px; height: 8px; border-radius: 50%; background: #10b981; box-shadow: 0 0 10px #10b981;'></div>
        <div>
            <div style='font-size: 0.85rem; font-weight: 700; color: #ffffff;'>Gemini AI</div>
            <div style='font-size: 0.75rem; color: #34d399; font-weight: 600;'>Connected</div>
        </div>
    </div>
    <div style='color: #10b981; font-size: 0.9rem;'>✓</div>
</div>
""", unsafe_allow_html=True)

user_api_key = st.sidebar.text_input("Gemini API Key", type="password", help="Free key at aistudio.google.com")
show_graph_manual = st.sidebar.checkbox("📊 Show Function Graph", value=False)

st.sidebar.markdown("<br><div style='font-weight: 600; font-size: 0.82rem; color: #64748b; text-align: center;'>Made with ❤️ by Shivani</div>", unsafe_allow_html=True)

solver = GeminiMathSolver(api_key=user_api_key if user_api_key else None)

# Advanced CSS with Animations & Exact Screenshot Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    .stApp, [data-testid="stAppViewContainer"] {
        background-color: #07090e !important;
        color: #f8fafc !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }

    section[data-testid="stSidebar"], [data-testid="stSidebar"] > div {
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
        border-right: 1px solid #1a2234 !important;
    }

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 0 15px rgba(59,130,246,0.3); }
        50% { box-shadow: 0 0 30px rgba(139,92,246,0.6); }
        100% { box-shadow: 0 0 15px rgba(59,130,246,0.3); }
    }

    @keyframes floatAnim {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }

    .animated-container {
        animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }

    .hero-banner-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 20px;
        padding: 40px;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        margin-bottom: 30px;
        animation: fadeIn 0.7s ease-out forwards;
    }

    .hero-banner-card::before {
        content: '';
        position: absolute;
        top: -50px;
        right: -50px;
        width: 250px;
        height: 250px;
        background: radial-gradient(circle, rgba(139,92,246,0.25) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 1;
    }

    .category-card-custom {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 24px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: pointer;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .category-card-custom:hover {
        transform: translateY(-5px);
        border-color: #3b82f6;
        box-shadow: 0 12px 30px rgba(59,130,246,0.25);
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    }

    .recent-solutions-box {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 28px;
        margin-top: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: fadeIn 0.8s ease-out forwards;
    }

    .math-card {
        font-family: 'Times New Roman', serif;
        font-size: 1.5rem;
        font-weight: bold;
        background: #0b0f19;
        color: #34d399;
        padding: 14px 22px;
        border-radius: 12px;
        margin-top: 8px;
        margin-bottom: 16px;
        border-left: 5px solid #3b82f6;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
    }

    .final-answer-box {
        font-family: 'Times New Roman', serif;
        font-size: 1.7rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1e3a8a 0%, #312e81 100%);
        color: #ffffff;
        padding: 20px 26px;
        border-radius: 14px;
        border: 1px solid #3b82f6;
        box-shadow: 0 8px 25px rgba(59,130,246,0.3);
        margin-top: 24px;
    }

    /* Custom Gradient Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(59,130,246,0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(139,92,246,0.5) !important;
        opacity: 0.95 !important;
    }
</style>
""", unsafe_allow_html=True)

def render_step_with_larger_math(step_text: str):
    step_str = str(step_text).strip()
    if ":" in step_str:
        parts = step_str.split(":", 1)
        explanation = parts[0].strip()
        calc = parts[1].strip()
        st.markdown(f"<div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 14px;'>• {explanation}:</div>", unsafe_allow_html=True)
        if calc:
            display_calc = calc if calc.startswith("⇒") else f"⇒ {calc}"
            st.markdown(f"<div class='math-card'>{display_calc}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size: 1.15rem; font-weight: 700; color: #f8fafc; margin-top: 14px;'>• {step_str}</div>", unsafe_allow_html=True)

# OPTION 1: HOME PAGE
if sidebar_page == "🏠 Home":

    # Hero Banner matching the screenshot design exactly
    st.markdown("""
    <div class='hero-banner-card animated-container'>
        <div style='display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 30px;'>
            <div style='flex: 1; min-width: 280px; z-index: 2;'>
                <div style='display: flex; align-items: center; gap: 14px; margin-bottom: 18px;'>
                    <div style='background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); width: 56px; height: 56px; border-radius: 16px; display: flex; align-items: center; justify-content: center; box-shadow: 0 8px 25px rgba(59,130,246,0.5);'>
                        <span style='font-size: 1.8rem;'>🌌</span>
                    </div>
                    <div>
                        <h1 style='font-size: 2.4rem; font-weight: 800; color: #ffffff; margin: 0; letter-spacing: -0.5px;'>Air Canvas</h1>
                        <div style='font-size: 1.1rem; font-weight: 700; background: linear-gradient(90deg, #60a5fa, #c084fc); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AI Math Solver</div>
                    </div>
                </div>
                <h2 style='font-size: 1.8rem; font-weight: 800; color: #ffffff; margin-bottom: 10px;'>Snap. Solve. Learn.</h2>
                <p style='font-size: 1rem; color: #94a3b8; line-height: 1.6; margin-bottom: 24px; max-width: 480px;'>
                    Upload, snap, type, or draw your math problem and get instant solutions with step-by-step explanations.
                </p>
            </div>

            <div style='flex: 1; min-width: 280px; display: flex; justify-content: center; align-items: center; z-index: 2;'>
                <div style='background: linear-gradient(135deg, rgba(30,41,59,0.8) 0%, rgba(15,23,42,0.9) 100%); border: 1.5px solid rgba(59,130,246,0.3); border-radius: 20px; padding: 25px; width: 100%; max-width: 380px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); position: relative; animation: floatAnim 4s ease-in-out infinite;'>
                    <div style='position: absolute; top: 12px; right: 15px; font-size: 0.9rem; color: #60a5fa;'>✨ Live AI Math Engine</div>
                    <div style='font-family: "Times New Roman", serif; font-size: 1.4rem; color: #60a5fa; text-align: center; margin: 15px 0; padding: 15px; background: rgba(15,23,42,0.6); border-radius: 12px; border: 1px solid #334155;'>
                        ∫ x² dx = <span style='color: #34d399;'>\u00frac{x³}{3} + C</span>
                    </div>
                    <div style='display: flex; justify-content: space-around; font-size: 1.1rem; color: #94a3b8; margin-top: 10px;'>
                        <span>📐 Triangle</span>
                        <span>π Pi</span>
                        <span>√ Root</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    input_tab1, input_tab2, input_tab3, input_tab4 = st.tabs([
        "🖼️ Upload Image",
        "📷 Open Camera",
        "⌨️ Type Question",
        "🖐️ MediaPipe Live Air Canvas"
    ])

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
        typed_val = st.text_area(
            "Question Text Area",
            value=st.session_state.get("typed_question", ""),
            placeholder="Type question here...",
            label_visibility="collapsed",
            height=100
        )
        st.session_state["typed_question"] = typed_val

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
            if st.button("∫ (Integral)"): append_symbol("∫ ")
        with sym_col4:
            if st.button("∫_a^b (Definite)"): append_symbol("∫_a^b ")
            if st.button("dx (Differential)"): append_symbol("dx")
        with sym_col5:
            if st.button("π (Pi)"): append_symbol("π")
            if st.button("θ (Theta)"): append_symbol("θ")
        with sym_col6:
            if st.button("∞ (Infinity)"): append_symbol("∞")
            if st.button("≠ (Not Equal)"): append_symbol("≠")

        if st.button("✨ SOLVE TYPED QUESTION WITH AI", type="primary", use_container_width=True):
            text_question_to_process = typed_val

    with input_tab4:
        st.markdown("### 🖐️ Real-Time Live Webcam Air Canvas")
        st.write("Turn ON camera & drawing to see yourself and draw colored lines in the air. Turn OFF to completely close the camera!")

        air_canvas_html = """
        <!DOCTYPE html>
        <html>
        <head>
          <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
          <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
          <script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
          <style>
            body { margin: 0; background: #000; color: #fff; font-family: system-ui, sans-serif; text-align: center; }
            #canvas_container { position: relative; width: 640px; height: 480px; margin: 0 auto; border: 2px solid #3b82f6; border-radius: 12px; overflow: hidden; background: #0f172a; box-shadow: 0 10px 30px rgba(59,130,246,0.3); }
            #webcam_video { position: absolute; left: 0; top: 0; width: 640px; height: 480px; transform: scaleX(-1); object-fit: cover; z-index: 1; display: none !important; }
            #drawing_canvas { position: absolute; left: 0; top: 0; width: 640px; height: 480px; transform: scaleX(-1); z-index: 2; }
            #hand_canvas { position: absolute; left: 0; top: 0; width: 640px; height: 480px; transform: scaleX(-1); z-index: 3; }
            .btn-box { margin-top: 15px; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px; }
            button { background: #3b82f6; color: white; border: none; padding: 10px 18px; font-weight: bold; cursor: pointer; border-radius: 8px; font-size: 0.95rem; transition: 0.2s; }
            button:hover { background: #2563eb; transform: translateY(-1px); }
            .toggle-btn-on { background: #059669 !important; }
            .toggle-btn-off { background: #dc2626 !important; }
            #status { margin-top: 12px; font-size: 1.05rem; font-weight: bold; color: #f87171; }
          </style>
        </head>
        <body>
          <div id="canvas_container">
            <video id="webcam_video" width="640" height="480" autoplay playsinline></video>
            <canvas id="drawing_canvas" width="640" height="480"></canvas>
            <canvas id="hand_canvas" width="640" height="480"></canvas>
          </div>
          <div class="btn-box">
            <button id="draw_toggle_btn" class="toggle-btn-off" onclick="toggleDrawing()">📹 Air Camera & Drawing: OFF</button>
            <button onclick="clearAirCanvas()">🧹 Clear Canvas</button>
            <button onclick="changeColor('#38bdf8')">🩵 Cyan</button>
            <button onclick="changeColor('#34d399')">💚 Green</button>
            <button onclick="changeColor('#f87171')">❤️ Red</button>
            <button onclick="changeColor('#facc15')">💛 Yellow</button>
          </div>
          <div id="status">🛑 Camera & Air Drawing Turned OFF (Click button above to start)</div>

          <script>
            const video = document.getElementById('webcam_video');
            const drawCanvas = document.getElementById('drawing_canvas');
            const drawCtx = drawCanvas.getContext('2d');
            const handCanvas = document.getElementById('hand_canvas');
            const handCtx = handCanvas.getContext('2d');
            const statusDiv = document.getElementById('status');
            const drawToggleBtn = document.getElementById('draw_toggle_btn');

            let isDrawingEnabled = false;
            let currentColor = '#38bdf8';
            let prevX = 0, prevY = 0;
            let camera = null;

            drawCtx.lineWidth = 8;
            drawCtx.lineCap = 'round';

            function stopWebcamStream() {
              if (camera) {
                try { camera.stop(); } catch(e){}
              }
              if (video && video.srcObject) {
                try {
                  video.srcObject.getTracks().forEach(track => track.stop());
                } catch(e){}
              }
            }

            function toggleDrawing() {
              isDrawingEnabled = !isDrawingEnabled;
              if (isDrawingEnabled) {
                drawToggleBtn.innerText = "📹 Air Camera & Drawing: ON";
                drawToggleBtn.className = "toggle-btn-on";
                video.style.display = "block";
                if (!camera) {
                  camera = new Camera(video, {
                    onFrame: async () => {
                      if (isDrawingEnabled) {
                        await hands.send({image: video});
                      }
                    },
                    width: 640,
                    height: 480
                  });
                }
                camera.start();
                statusDiv.innerText = "🔍 Camera & Air Drawing Started";
                statusDiv.style.color = "#34d399";
              } else {
                drawToggleBtn.innerText = "📹 Air Camera & Drawing: OFF";
                drawToggleBtn.className = "toggle-btn-off";
                stopWebcamStream();
                video.style.display = "none";
                handCtx.clearRect(0, 0, handCanvas.width, handCanvas.height);
                statusDiv.innerText = "🛑 Camera & Air Drawing Turned OFF";
                statusDiv.style.color = "#f87171";
                prevX = 0; prevY = 0;
              }
            }

            function clearAirCanvas() {
              drawCtx.clearRect(0, 0, drawCanvas.width, drawCanvas.height);
              prevX = 0; prevY = 0;
            }

            function changeColor(col) {
              currentColor = col;
            }

            window.addEventListener('beforeunload', stopWebcamStream);
            window.addEventListener('unload', stopWebcamStream);
            document.addEventListener('visibilitychange', () => {
              if (document.hidden) stopWebcamStream();
            });

            function onResults(results) {
              handCtx.clearRect(0, 0, handCanvas.width, handCanvas.height);

              if (isDrawingEnabled && results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                const landmarks = results.multiHandLandmarks[0];
                drawConnectors(handCtx, landmarks, HAND_CONNECTIONS, {color: '#34d399', lineWidth: 3});
                drawLandmarks(handCtx, landmarks, {color: '#ffffff', lineWidth: 2, radius: 4});

                const ix = landmarks[8].x * handCanvas.width;
                const iy = landmarks[8].y * handCanvas.height;

                const indexUp = landmarks[8].y < landmarks[6].y;
                const middleUp = landmarks[12].y < landmarks[10].y;

                if (indexUp && !middleUp) {
                  statusDiv.innerText = "✍️ DRAWING MODE ACTIVE (Index Finger Active)";
                  statusDiv.style.color = "#38bdf8";
                  drawCtx.strokeStyle = currentColor;
                  if (prevX === 0 && prevY === 0) {
                    prevX = ix; prevY = iy;
                  }
                  drawCtx.beginPath();
                  drawCtx.moveTo(prevX, prevY);
                  drawCtx.lineTo(ix, iy);
                  drawCtx.stroke();
                  prevX = ix; prevY = iy;
                } else {
                  statusDiv.innerText = "✌️ HOVER MODE (Raise 1 Index Finger to Draw)";
                  statusDiv.style.color = "#ffb74d";
                  prevX = 0; prevY = 0;
                }
              } else if (!isDrawingEnabled) {
                statusDiv.innerText = "🛑 Camera & Air Drawing Turned OFF";
                statusDiv.style.color = "#f87171";
                prevX = 0; prevY = 0;
              } else {
                statusDiv.innerText = "🖐️ Place hand in front of camera";
                statusDiv.style.color = "#94a3b8";
                prevX = 0; prevY = 0;
              }
            }

            const hands = new Hands({locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`});
            hands.setOptions({
              maxNumHands: 1,
              modelComplexity: 1,
              minDetectionConfidence: 0.7,
              minTrackingConfidence: 0.7
            });
            hands.onResults(onResults);
          </script>
        </body>
        </html>
        """
        st.components.v1.html(air_canvas_html, height=620)

        st.markdown("---")
        st.write("📷 **Snap & Solve Air Canvas Drawing**:")
        air_snap = st.file_uploader("Upload or Snap Air Canvas Drawing to Solve", type=["png", "jpg", "jpeg"], key="air_snap_file")
        if air_snap is not None:
            image_to_process = Image.open(air_snap)

    # Process Image or Typed Question
    if image_to_process is not None or text_question_to_process is not None:
        if image_to_process is not None and sidebar_page == "🏠 Home":
            st.image(image_to_process, caption="Math Question Image", use_column_width=True)

        solve_trigger = False
        if text_question_to_process is not None:
            solve_trigger = True
        else:
            solve_trigger = st.button("✨ SOLVE MATH PROBLEM WITH GEMINI AI", type="primary", use_container_width=True)

        if solve_trigger:
            with st.spinner("Analyzing math problem & generating step-by-step AI solution..."):
                if text_question_to_process is not None:
                    result = solver.solve_text_question(text_question_to_process)
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

    # "What can you solve?" Grid matching screenshot exactly
    st.markdown("""
    <div style='margin-top: 40px; margin-bottom: 20px;'>
        <div style='font-size: 1.4rem; font-weight: 800; color: #ffffff; display: flex; align-items: center; gap: 10px;'>
            <span>✨</span> What can you solve?
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class='category-card-custom'>
            <div style='background: rgba(147, 51, 234, 0.15); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; border: 1px solid rgba(147, 51, 234, 0.3);'>
                <span style='font-size: 1.3rem; color: #c084fc; font-weight: bold;'>Σ</span>
            </div>
            <div style='font-weight: 800; font-size: 1.15rem; color: #ffffff; margin-bottom: 6px;'>Algebra</div>
            <div style='font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 20px;'>Equations and expressions</div>
            <div style='color: #60a5fa; font-weight: 700; font-size: 0.9rem;'>→</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='category-card-custom'>
            <div style='background: rgba(59, 130, 246, 0.15); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; border: 1px solid rgba(59, 130, 246, 0.3);'>
                <span style='font-size: 1.3rem; color: #60a5fa; font-weight: bold;'>📈</span>
            </div>
            <div style='font-weight: 800; font-size: 1.15rem; color: #ffffff; margin-bottom: 6px;'>Calculus</div>
            <div style='font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 20px;'>Limits, derivatives, integrals</div>
            <div style='color: #60a5fa; font-weight: 700; font-size: 0.9rem;'>→</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class='category-card-custom'>
            <div style='background: rgba(16, 185, 129, 0.15); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; border: 1px solid rgba(16, 185, 129, 0.3);'>
                <span style='font-size: 1.3rem; color: #34d399; font-weight: bold;'>📐</span>
            </div>
            <div style='font-weight: 800; font-size: 1.15rem; color: #ffffff; margin-bottom: 6px;'>Geometry</div>
            <div style='font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 20px;'>Shapes, theorems and proofs</div>
            <div style='color: #60a5fa; font-weight: 700; font-size: 0.9rem;'>→</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div class='category-card-custom'>
            <div style='background: rgba(236, 72, 153, 0.15); width: 44px; height: 44px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-bottom: 16px; border: 1px solid rgba(236, 72, 153, 0.3);'>
                <span style='font-size: 1.3rem; color: #f472b6; font-weight: bold;'>🧠</span>
            </div>
            <div style='font-weight: 800; font-size: 1.15rem; color: #ffffff; margin-bottom: 6px;'>Practice</div>
            <div style='font-size: 0.85rem; color: #94a3b8; line-height: 1.5; margin-bottom: 20px;'>Quizzes and hints</div>
            <div style='color: #60a5fa; font-weight: 700; font-size: 0.9rem;'>→</div>
        </div>
        """, unsafe_allow_html=True)

    # "Recent Solutions" Section matching screenshot
    st.markdown("""
    <div class='recent-solutions-box'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;'>
            <div style='display: flex; align-items: center; gap: 10px; font-weight: 800; font-size: 1.2rem; color: #ffffff;'>
                <span>🕒</span> Recent Solutions
            </div>
            <div style='color: #60a5fa; font-size: 0.9rem; font-weight: 700; cursor: pointer;'>View All →</div>
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state["history"]:
        st.markdown("""
        <div style='text-align: center; padding: 40px 20px;'>
            <div style='font-size: 2.2rem; margin-bottom: 12px;'>✨ π ✨</div>
            <div style='font-weight: 700; font-size: 1.05rem; color: #ffffff; margin-bottom: 6px;'>No recent solutions yet.</div>
            <div style='font-size: 0.85rem; color: #94a3b8;'>Upload a math question above to see it here!</div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        hist_cols = st.columns(min(4, len(st.session_state["history"])))
        for idx, item in enumerate(reversed(st.session_state["history"][:4])):
            with hist_cols[idx]:
                st.markdown(f"""
                <div style='background: #0b0f19; border: 1px solid #1e293b; border-radius: 12px; padding: 16px;'>
                    <div style='font-weight: 800; font-size: 1rem; color: #ffffff;'>{item['expression']}</div>
                    <div style='font-size: 0.8rem; color: #60a5fa; margin-top: 4px; font-weight: bold;'>{item['category']}</div>
                    <div style='font-size: 0.9rem; font-weight: 900; color: #34d399; margin-top: 8px;'>Ans: {item['final_answer']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Footer matching screenshot
    st.markdown("---")
    st.markdown("<div style='text-align: center; font-size: 0.9rem; font-weight: 700; color: #64748b; padding-bottom: 20px;'>✨ Made with ❤️ by Shivani ✨</div>", unsafe_allow_html=True)

# OPTION 2: SETTINGS & LOGIN PAGE
elif sidebar_page == "⚙️ Settings & Login":
    st.title("⚙️ Settings & Login Account")
    st.caption("Manage your profile, Gemini AI Key, and app settings")

    st.markdown("<div class='recent-solutions-box'>", unsafe_allow_html=True)
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

    st.markdown("<div class='recent-solutions-box' style='margin-top: 20px;'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Gemini AI Connection Status")
    if has_secrets_key:
        st.success("🟢 Google Gemini AI Connected via Cloud Secrets")
    else:
        st.warning("🟡 Gemini Key Not Found in Cloud Secrets (Paste key in sidebar)")

    st.write("Active AI Model: **gemini-3.8-flash** (`models/gemini-3.8-flash`)")
    st.markdown("[Get Free Gemini API Key from Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.markdown("</div>", unsafe_allow_html=True)
