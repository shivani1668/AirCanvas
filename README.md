# 🌌 Air Canvas - Next-Generation AI & Computer Vision Mathematical Solver 🎨🐍

> *An advanced, interactive Multimodal Generative AI and 3D Hand-Tracking Computer Vision platform that converts handwritten, photographed, or typed mathematical questions into step-by-step educational proofs with clean typography and real-time function visualization.*

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app)
[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Google Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini%20Flash-purple.svg)](https://aistudio.google.com/)
[![MediaPipe](https://img.shields.io/badge/Computer%20Vision-MediaPipe-green.svg)](https://mediapipe.dev/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Headless-red.svg)](https://opencv.org/)
[![SymPy](https://img.shields.io/badge/Symbolic%20Math-SymPy-orange.svg)](https://www.sympy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📌 Table of Contents

- [Executive Summary & Vision](#-executive-summary--vision)
- [Live Web Application](#-live-web-application)
- [System Architecture & Workflow](#-system-architecture--workflow)
- [Key Features & Capability Breakdown](#-key-features--capability-breakdown)
- [Mathematical Engine & AI Integration](#-mathematical-engine--ai-integration)
- [Repository Structure](#-repository-structure)
- [Prerequisites & System Drivers](#-prerequisites--system-drivers)
- [Installation & Local Setup](#-installation--local-setup)
- [API Key Configuration](#-api-key-configuration)
- [Usage Walkthrough & Examples](#-usage-walkthrough--examples)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [License & Credits](#-license--credits)

---

## 🚀 Executive Summary & Vision

**Air Canvas** is an open-source, full-stack Machine Learning and Computer Vision educational web and desktop application designed to bridge the gap between complex mathematical expressions and student understanding. By combining **Google Gemini Multimodal Generative Vision Models** (`gemini-3.8-flash`, `gemini-2.5-flash`), **MediaPipe 3D Hand Gesture Tracking**, and the **SymPy Symbolic Mathematics Engine**, Air Canvas provides instant, step-by-step explanations for handwritten equations, uploaded images, or typed mathematical problems.

Whether solving multi-variable calculus integrals ($\int \cos(2x) \, dx$), surd rationalizations ($\frac{5}{\sqrt{2}+1}$), exponent simplifications ($\sqrt{3^9 + 3^9 + 3^9}$), or competitive examination MCQs, Air Canvas formats solutions into clean, legible typography with dedicated mathematical calculation cards prefixing each step with a double arrow **`⇒`**.

---

## 🌐 Live Web Application

The web application is deployed on **Streamlit Cloud** and accessible 24/7 globally:

👉 **Live URL**: [https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app](https://aircanvas-j69cqyxw6krbgayddgmnee.streamlit.app)

---

## 🏗️ System Architecture & Workflow

```text
                                  +---------------------------------------+
                                  |            USER INPUT MODALITIES      |
                                  | 1. Image Upload (PNG/JPG/JPEG)        |
                                  | 2. Mobile Camera Snap (Camera Input)  |
                                  | 3. Typed Question + Symbol Keyboard   |
                                  | 4. Desktop Air Canvas Gesture Draw    |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +-------------------+-------------------+
                                  |       IMAGE / TEXT PREPROCESSING      |
                                  | - Contrast Enhancement (1.4x)         |
                                  | - Sharpening & Thresholding           |
                                  | - Implicit Multiplication Parsing     |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +-------------------+-------------------+
                                  |        CORE SOLVER ROUTING ENGINE     |
                                  |                                       |
                                  |  [ Gemini AI API Key Available? ]      |
                                  |        /                     \        |
                                  |      YES                      NO      |
                                  |      /                         \      |
                                  v                                 v     |
                  +---------------+---------------+   +-------------+---------------+
                  |  GOOGLE GEMINI FLASH VISION   |   |   OFFLINE SYMPY MATH ENGINE   |
                  |  - gemini-3.8-flash           |   |   - Symbolic Differentiation  |
                  |  - gemini-2.5-flash           |   |   - Indefinite & Definite ∫   |
                  |  - gemini-2.0-flash           |   |   - Equation Balancing        |
                  +---------------+---------------+   +-------------+---------------+
                                  |                                 |
                                  +----------------+----------------+
                                                   |
                                                   v
                                  +----------------+----------------+
                                  |    LATEX TO PLAIN MATH PARSER   |
                                  | - Convert \frac{A}{B} -> (A) / (B)|
                                  | - Convert \sqrt{X} -> √(X)      |
                                  | - Convert \implies -> ⇒         |
                                  +----------------+----------------+
                                                   |
                                                   v
                                  +----------------+----------------+
                                  |      STREAMLIT UI PRESENTATION   |
                                  | - Centered Title & Branding     |
                                  | - Step-by-Step Breakdown        |
                                  | - Times New Roman Bold Cards    |
                                  | - Matplotlib Graph Visualizer   |
                                  +---------------------------------+
```

---

## ✨ Key Features & Capability Breakdown

### 1. 🤖 Multimodal AI Vision & OCR Engine
- **Direct Gemini Flash Integration**: Uses Google's latest multimodal models (`gemini-3.8-flash`, `gemini-2.5-flash`) for real-time Optical Character Recognition (OCR) and mathematical reasoning directly from images.
- **Image Enhancement Pipeline**: Integrates `PIL.ImageEnhance.Contrast` to boost low-contrast smartphone photos, making fine superscripts, fractional bars, and root symbols clearly legible.

### 2. 🔣 Interactive Math Symbol Virtual Keyboard
- **Top Text Input Area**: Places the question text box at the very top of the tab for immediate typing.
- **Quick-Insert Symbol Palette**: Provides dedicated buttons placed directly below the text box for complex mathematical symbols:
  - Square Roots: `√`
  - Exponents / Powers: `x²` (`^2`)
  - Division & Fractions: `/`
  - Plus-Minus: `±`
  - Derivatives: `d/dx`
  - Integrals: `∫` (Indefinite) & `∫_a^b` (Definite)
  - Differentials: `dx`, `dy`
  - Constants & Greek Symbols: `π`, `θ`, `∞`, `≠`
- **Default Placeholder**: Features an intuitive default text area with `placeholder="Type question here..."` for quick typing.

### 3. ✍️ Clean Mathematical Typography & Formatting
- **Standardized Text Explanations**: Regular step explanations use clean, modern UI fonts.
- **Dedicated Math Calculation Cards**: Mathematical equations and calculations appear on a new line directly below explanations inside a **larger, bold Times New Roman + Symbol font card** prefixed with a right double arrow **`⇒`**.
- **LaTeX Sanitization**: Automatically strips raw LaTeX commands (`\frac{A}{B}`, `\sqrt{X}`, `\implies`) into clean, human-readable slash fractions `(A) / (B)` and root symbols `√X`.

### 4. 📱 Mobile Camera & Air Canvas Drawing Modes
- **Mobile Camera Snap**: Native browser camera capture (`st.camera_input`) with an explicit **📷 Enable Camera** toggle switch (OFF by default to conserve bandwidth and battery).
- **Desktop Gesture Canvas**: Computer vision hand tracking module using **MediaPipe** (3D hand landmarks) and **OpenCV** for drawing equations in the air with index finger movements.

### 5. 🌗 Dynamic Theme Engine (Dark Mode & Light Mode)
- Single-click toggle switch in the left sidebar (**`🌙 Dark Mode / ☀️ Light Mode`**).
- Dynamically updates both the main application container and the left sidebar background synchronously:
  - **Dark Mode**: Solid black `#000000` with high-contrast `#ffffff` text and dark card overlays.
  - **Light Mode**: Crisp `#f8fafc` background with clean white cards and dark text.

### 6. 🧹 Streamlined 2-Option Navigation
- **`🏠 Home`**: Hero header, central header card (*Made with 💝 by Shivani*), input tabs (Upload Image, Open Camera, Type Question), step-by-step AI proof cards, category grid, and recent solution history.
- **`⚙️ Settings & Login`**: User account authentication, profile manager, and Gemini AI API connection status badge (`🟢 Gemini AI Connected`).

---

## 🧮 Mathematical Engine & AI Integration

The system employs a dual-engine architecture:

1. **Primary AI Engine (`src/gemini_solver.py`)**:
   Sends the visual image tensor or typed mathematical text string directly to Google Gemini Flash API (`models/gemini-3.8-flash`). The model receives structured prompt instructions mandating step-by-step pedagogical breakdown, LaTeX-free output, and JSON schema formatting.

2. **Fallback Symbolic Engine (`src/offline_solver.py`)**:
   Runs 100% locally without external API calls using Python's **SymPy** library. Handles symbolic calculus (`sp.diff`, `sp.integrate`), algebraic equation solving (`sp.solve`), and expression simplification (`sp.simplify`).

---

## 📂 Repository Structure

```text
AirCanvas/
├── app.py                     # Main Streamlit Web Application Entry Point
├── main.py                    # Desktop Tkinter & OpenCV App (with Streamlit fallback)
├── requirements.txt           # Python Package Dependencies
├── packages.txt               # Linux System Packages (libgl1, libglib2.0-0)
├── README.md                  # Comprehensive Project Documentation
│
├── .streamlit/
│   └── config.toml            # Streamlit Server Configuration (10MB Upload Limit)
│
├── src/                       # 🧠 Core Processing Modules
│   ├── __init__.py            # Package Init
│   ├── air_canvas.py          # MediaPipe 3D Hand Tracking Engine
│   ├── gemini_solver.py       # Google Gemini AI Vision/Text Integration & LaTeX Cleaner
│   └── offline_solver.py      # SymPy General Symbolic Mathematics Engine
│
└── utils/                     # 🛠️ Helper Utilities
    ├── image_processing.py    # OpenCV Image Thresholding & Preprocessing
    └── math_plotter.py        # Matplotlib Function Graph Plotter Engine
```

---

## 📋 Prerequisites & System Drivers

- **Python Version**: Python 3.9, 3.10, or 3.11 (Recommended: Python 3.11).
- **System Graphics Drivers (Linux/Cloud Deployment)**:
  - `libgl1` (OpenGL driver for OpenCV)
  - `libglib2.0-0` (System runtime library)

---

## 📥 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/shivani1668/AirCanvas.git
cd AirCanvas
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Streamlit Web Application
```bash
streamlit run app.py
```

### 5. Run Desktop OpenCV Camera App (Optional)
```bash
python main.py
```

---

## 🔑 API Key Configuration

To enable live Multimodal AI image recognition and LLM reasoning:

1. Obtain a 100% free Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Configure your key using any of the following methods:
   - **Method A (Sidebar)**: Paste your key directly into the **Gemini API Key** field in the left sidebar.
   - **Method B (Streamlit Secrets)**: Create a file `.streamlit/secrets.toml`:
     ```toml
     GEMINI_API_KEY = "your_actual_gemini_api_key_here"
     ```
   - **Method C (Environment Variable)**:
     ```bash
     export GEMINI_API_KEY="your_actual_gemini_api_key_here"
     ```

---

## 💡 Usage Walkthrough & Examples

### Example 1: Calculus Integration (`∫ cos(2x) dx`)
1. Open the **`⌨️ Type Question`** tab on the homepage.
2. Type `∫ cos(2x) dx` into the text box at the top (or click **`∫ (Integral)`** from the keyboard below).
3. Click **`✨ SOLVE TYPED QUESTION WITH AI`**.
4. **Result**:
   - **Step 1**: Identify integral $\int \cos(2x) \, dx$.
   - **Step 2**: Apply u-substitution: Let $u = 2x \implies du = 2 \, dx \implies dx = \frac{du}{2}$.
   - **Step 3**: Substitute $\int \cos(u) \frac{du}{2} = \frac{1}{2} \sin(u) + C$.
   - **Final Answer Card**: `⇒ sin(2x) / 2 + C`

### Example 2: Surd Rationalization ($\frac{5}{\sqrt{2}+1}$)
1. Upload an image of $\frac{5}{\sqrt{2}+1}$ or type it into the text box.
2. Click **Solve Math Problem**.
3. **Result**:
   - **Step 1**: Multiply numerator and denominator by conjugate $(\sqrt{2}-1)$.
   - **Step 2**: $5(\sqrt{2}-1) / ((\sqrt{2}+1)(\sqrt{2}-1)) = 5\sqrt{2}-5 / (2-1)$.
   - **Final Answer Card**: `⇒ 5√2 - 5`

---

## ❓ Troubleshooting & FAQ

| Problem | Cause | Resolution |
| :--- | :--- | :--- |
| `ImportError: libGL.so.1` on Linux | Missing OpenGL driver | Ensure `packages.txt` includes `libgl1` and `libglib2.0-0`. |
| `API Key Missing` Warning | Gemini API Key not detected | Paste your API key in the sidebar or set `GEMINI_API_KEY` in Streamlit Secrets. |
| Camera Input Disabled | Default state for performance | Toggle the **📷 Enable Camera** switch on the camera tab. |
| Large Image Upload Fail | Exceeds Streamlit default limit | Configured `maxUploadSize = 10` in `.streamlit/config.toml`. |

---

## 📜 License & Credits

Designed & Developed with 💝 by **Shivani**.

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

*Special thanks to Google AI Studio, MediaPipe, OpenCV, SymPy, and Streamlit communities.*
