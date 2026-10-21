# Air Canvas - AI-Powered Mathematical Solver (Python & ML Stack) 🎨🐍

> *"Draw your equations in the air or on screen, let AI & Computer Vision solve them!"*

**Air Canvas** is a Generative AI & Computer Vision Python application built using **OpenCV**, **MediaPipe**, **Google Gemini API**, **SymPy**, **NumPy**, and **Matplotlib**.

---

## 🌟 Tech Stack & Features

- 🐍 **Language**: Python 3.9+
- 👁️ **Computer Vision & Hand Tracking**: OpenCV & MediaPipe Hands for real-time 3D finger tracking and gesture drawing in the air.
- 🤖 **Generative AI & LLMs**: Google Gemini 1.5/2.0 Flash Multimodal Vision API for reading handwritten mathematical equations and generating step-by-step solutions.
- 🧮 **Offline Symbolic Math Engine**: SymPy & NumPy for 100% free, offline solving of arithmetic, linear/quadratic equations, and calculus differentiation.
- 📊 **Mathematical Graph Visualization**: Matplotlib for plotting functions ($y = x^2$, $\sin(x)$, linear functions) dynamically.
- 💻 **GUI Interface**: Tkinter dashboard with mouse/stylus drawing canvas, webcam gesture air mode, brush controls, eraser, and solution viewer.

---

## 📁 Repository Structure

```
ML_project/
├── main.py                  # Main Python Application Entry Point (Tkinter + OpenCV + Gemini AI)
├── air_canvas.py            # Computer Vision & MediaPipe Air Gesture Tracker
├── gemini_solver.py         # Google Gemini Multimodal AI Math Solver
├── offline_solver.py        # Free On-Device Symbolic Math Engine (SymPy)
├── utils/
│   ├── image_processing.py  # OpenCV Canvas preprocessing & thresholding
│   └── math_plotter.py      # Matplotlib function graph plotting
├── requirements.txt         # Python dependencies
└── README.md                # Documentation
```

---

## 🚀 How to Run (Python)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python main.py
   ```

3. **(Optional) Configure Gemini API Key**:
   - Enter your free Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey) in the top-right field of the application.
   - If no key is provided, the application automatically uses the built-in **SymPy Offline Math Engine**.
