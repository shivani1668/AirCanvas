# 🌌 Air Canvas - AI-Powered Mathematical Solver 🎨🐍

> *"Draw or snap a picture of your math equation & let AI solve it step-by-step!"*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Google Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-purple.svg)](https://aistudio.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌐 Live Web Application

🚀 **Access the Live Web Application here**:
👉 **[https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app](https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app)**

---

## ✨ Features & Highlights

- 🤖 **Multimodal Vision AI Engine**: Powered by **Google Gemini Flash LLM** (`gemini-3.8-flash`, `gemini-2.5-flash`, `gemini-1.5-flash`) for live OCR image analysis, step-by-step mathematical reasoning, and accurate solution generation.
- 🖼️ **Image Preprocessing & Sharpening**: Automatic contrast (1.4x) and sharpness enhancement (`enhance_math_image`) to ensure fine exponents, square roots ($\sqrt{2}$), and division lines are read accurately.
- 🧮 **Universal Mathematical Coverage**:
  - **Algebra & Equations**: Linear equations, quadratic formulas ($ax^2 + bx + c = 0$), polynomial factorization, and variable substitution systems.
  - **Surds & Rationalization**: Rationalizing denominators ($\frac{5}{\sqrt{2}+1} \implies 5\sqrt{2}-5$).
  - **Exponents & Powers**: Simplifying complex radicals ($\sqrt{3^9 + 3^9 + 3^9} = 243$).
  - **Calculus**: Differentiation ($\frac{d}{dx}$), Integration ($\int$), power/chain rules.
  - **Trigonometry**: $\sin(x)$, $\cos(x)$, $\tan(x)$, and fundamental identities.
  - **MCQs**: Multiple-choice questions with automatic option matching (e.g. `Option B`).
- ✍️ **Clean Typography & Double Arrow Symbol (`⇒`)**:
  - Formats step explanations in clean font, and places mathematical calculations on a new line right below in a **larger Times New Roman + Symbol font card** with double arrow **`⇒`**.
  - Converts raw LaTeX commands to readable plain math with slash `/` for fractions and `√` for root symbols.
- 📱 **Mobile & Desktop Camera Modes**:
  - **Mobile Camera Snap**: Direct camera capture (`st.camera_input`) with **📷 Camera ON/OFF** toggle switch.
  - **Desktop Air Canvas Mode**: Real-time 3D finger tracking in the air using **MediaPipe** and **OpenCV**.
- 🌓 **Dark & Light Mode Switch**: Single-click toggle in sidebar switching both sidebar and homepage themes dynamically.
- 🧹 **Clean 2-Option Navigation**:
  - `🏠 Home`: Hero header (**Math made simple.**), Central upload glass card, category grid, recent solution cards history.
  - `⚙️ Settings & Login`: User profile, Gemini AI connection status indicator (`🟢 Gemini AI Connected`), model configuration.

---

## 📂 Repository Directory Structure

```text
AirCanvas/
├── app.py                     # Main Streamlit Web Application
├── main.py                    # Main Desktop Application (Tkinter + OpenCV)
├── requirements.txt           # Python Dependencies (opencv-python-headless, streamlit, sympy, google-generativeai, pillow, matplotlib)
├── packages.txt               # Streamlit Cloud System Packages (libgl1, libglib2.0-0)
├── README.md                  # Documentation
│
├── src/                       # 🧠 Core Source Modules
│   ├── air_canvas.py          # MediaPipe 3D Hand Tracking Engine
│   ├── gemini_solver.py       # Google Gemini Flash Multimodal AI Solver & LaTeX Cleaner
│   └── offline_solver.py      # SymPy Symbolic Math Solver Engine (100% Free Offline)
│
└── utils/                     # 🛠️ Helper Utilities
    ├── image_processing.py    # OpenCV Canvas Image Preprocessing
    └── math_plotter.py        # Matplotlib Function Graph Plotter
```

---

## 🚀 Local Installation & Running

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shivani1668/AirCanvas.git
   cd AirCanvas
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Streamlit Web App**:
   ```bash
   streamlit run app.py
   ```

4. **Run Desktop OpenCV App**:
   ```bash
   python main.py
   ```

---

## 📄 License
Licensed under the [MIT License](LICENSE).
