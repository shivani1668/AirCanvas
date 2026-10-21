import sys
import os

# Check if running in headless Streamlit environment or if Tkinter/OpenCV GUI is unavailable
try:
    import _tkinter
    import tkinter as tk
    import cv2
    HAS_DESKTOP_GUI = True
except Exception:
    HAS_DESKTOP_GUI = False

if not HAS_DESKTOP_GUI or "STREAMLIT_SERVER_PORT" in os.environ:
    # Streamlit Web Environment Fallback
    import app_streamlit
else:
    from tkinter import ttk, messagebox, scrolledtext
    import numpy as np
    from PIL import Image, ImageTk

    from air_canvas import AirCanvasDetector
    from gemini_solver import GeminiMathSolver
    from offline_solver import OfflineMathEngine
    from utils.image_processing import preprocess_canvas_for_ai
    from utils.math_plotter import plot_equation_graph

    class AirCanvasMLApp:
        """
        Air Canvas - AI Powered Mathematical Solver Application (Python & Machine Learning Stack).
        Uses OpenCV, MediaPipe, Google Gemini API, SymPy, NumPy, and Matplotlib.
        """

        def __init__(self, root):
            self.root = root
            self.root.title("Air Canvas - AI Math Solver (Python & ML)")
            self.root.geometry("1280x800")
            self.root.configure(bg="#1e1e2e")

            self.air_detector = AirCanvasDetector(width=800, height=500)
            self.gemini_solver = GeminiMathSolver()

            self.drawing = False
            self.last_x, self.last_y = None, None
            self.current_color = (0, 0, 0)
            self.brush_size = 6
            self.is_eraser = False

            self.mouse_canvas = np.ones((500, 800, 3), dtype=np.uint8) * 255
            self.cap = cv2.VideoCapture(0)

            self._setup_ui()
            self.root.after(10, self._update_camera_loop)

        def _setup_ui(self):
            title_frame = tk.Frame(self.root, bg="#11111b", height=60)
            title_frame.pack(fill=tk.X, side=tk.TOP)

            title_label = tk.Label(
                title_frame,
                text="🎨 Air Canvas - Draw Math, Let AI Solve!",
                font=("Helvetica", 18, "bold"),
                fg="#cba6f7",
                bg="#11111b"
            )
            title_label.pack(side=tk.LEFT, padx=20, pady=10)

            api_frame = tk.Frame(title_frame, bg="#11111b")
            api_frame.pack(side=tk.RIGHT, padx=20)

            tk.Label(api_frame, text="Gemini API Key:", fg="#a6adc8", bg="#11111b", font=("Helvetica", 10)).pack(side=tk.LEFT, padx=5)
            self.api_key_entry = tk.Entry(api_frame, show="*", width=20, font=("Helvetica", 10))
            self.api_key_entry.pack(side=tk.LEFT, padx=5)

            save_key_btn = tk.Button(api_frame, text="Save Key", bg="#89b4fa", fg="#11111b", command=self._save_api_key, font=("Helvetica", 9, "bold"))
            save_key_btn.pack(side=tk.LEFT, padx=5)

            main_frame = tk.Frame(self.root, bg="#1e1e2e")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            left_panel = tk.Frame(main_frame, bg="#1e1e2e")
            left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            self.notebook = ttk.Notebook(left_panel)
            self.notebook.pack(fill=tk.BOTH, expand=True)

            self.tab_mouse = tk.Frame(self.notebook, bg="#181825")
            self.notebook.add(self.tab_mouse, text="🖊️ Drawing Canvas")

            self.cv_canvas = tk.Canvas(self.tab_mouse, width=800, height=500, bg="white", cursor="cross")
            self.cv_canvas.pack(padx=10, pady=10)
            self.cv_canvas.bind("<Button-1>", self._start_drawing)
            self.cv_canvas.bind("<B1-Motion>", self._draw_stroke)
            self.cv_canvas.bind("<ButtonRelease-1>", self._stop_drawing)

            self.tab_air = tk.Frame(self.notebook, bg="#181825")
            self.notebook.add(self.tab_air, text="📹 Air Gesture Camera")

            self.video_label = tk.Label(self.tab_air, bg="black")
            self.video_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            toolbar = tk.Frame(left_panel, bg="#313244", padding=8)
            toolbar.pack(fill=tk.X, pady=5)

            colors = [
                ("Black", (0, 0, 0), "#000000"),
                ("Red", (0, 0, 255), "#e64553"),
                ("Blue", (255, 0, 0), "#1e66f5"),
                ("Green", (0, 180, 0), "#40a02b"),
                ("Purple", (128, 0, 128), "#8839ef")
            ]

            for name, bgr, hex_code in colors:
                btn = tk.Button(
                    toolbar,
                    text=name,
                    bg=hex_code,
                    fg="white" if name != "Black" else "white",
                    command=lambda c=bgr: self._set_color(c),
                    width=6
                )
                btn.pack(side=tk.LEFT, padx=3)

            eraser_btn = tk.Button(toolbar, text="Eraser", bg="#fe640b", fg="white", command=self._enable_eraser, width=6)
            eraser_btn.pack(side=tk.LEFT, padx=5)

            clear_btn = tk.Button(toolbar, text="Clear Canvas", bg="#d20f39", fg="white", command=self._clear_canvas, width=10)
            clear_btn.pack(side=tk.LEFT, padx=5)

            tk.Label(toolbar, text="Size:", fg="white", bg="#313244").pack(side=tk.LEFT, padx=(10, 2))
            self.size_scale = tk.Scale(toolbar, from_=2, to=30, orient=tk.HORIZONTAL, bg="#313244", fg="white", highlightthickness=0)
            self.size_scale.set(6)
            self.size_scale.pack(side=tk.LEFT, padx=5)

            solve_btn = tk.Button(
                left_panel,
                text="✨ Solve Equation (AI / ML)",
                font=("Helvetica", 14, "bold"),
                bg="#a6e3a1",
                fg="#11111b",
                command=self._solve_equation_action,
                pady=8
            )
            solve_btn.pack(fill=tk.X, pady=8)

            right_panel = tk.Frame(main_frame, bg="#181825", width=420)
            right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

            tk.Label(right_panel, text="📐 AI Solution & Explanation", font=("Helvetica", 12, "bold"), fg="#cba6f7", bg="#181825").pack(anchor="w", pady=5)

            self.solution_text = scrolledtext.ScrolledText(
                right_panel,
                wrap=tk.WORD,
                width=45,
                height=16,
                font=("Consolas", 10),
                bg="#11111b",
                fg="#a6adc8"
            )
            self.solution_text.pack(fill=tk.BOTH, expand=True, pady=5)
            self.solution_text.insert(tk.END, "Draw a math equation on the canvas and click 'Solve Equation (AI)'!\n")

            tk.Label(right_panel, text="📊 Function Graph Visualizer", font=("Helvetica", 11, "bold"), fg="#89b4fa", bg="#181825").pack(anchor="w", pady=(10, 2))
            self.graph_label = tk.Label(right_panel, bg="#11111b", text="Graph preview will appear here", fg="#6c7086")
            self.graph_label.pack(fill=tk.BOTH, expand=True, pady=5)

        def _start_drawing(self, event):
            self.drawing = True
            self.last_x, self.last_y = event.x, event.y

        def _draw_stroke(self, event):
            if self.drawing:
                color_hex = "#FFFFFF" if self.is_eraser else f"#{self.current_color[2]:02x}{self.current_color[1]:02x}{self.current_color[0]:02x}"
                size = self.size_scale.get() if not self.is_eraser else self.size_scale.get() * 4

                self.cv_canvas.create_line(
                    self.last_x, self.last_y, event.x, event.y,
                    fill=color_hex,
                    width=size,
                    capstyle=tk.ROUND,
                    smooth=True
                )

                cv2.line(
                    self.mouse_canvas,
                    (self.last_x, self.last_y),
                    (event.x, event.y),
                    (255, 255, 255) if self.is_eraser else self.current_color,
                    size
                )

                self.last_x, self.last_y = event.x, event.y

        def _stop_drawing(self, event):
            self.drawing = False
            self.last_x, self.last_y = None, None

        def _set_color(self, bgr):
            self.current_color = bgr
            self.is_eraser = False
            self.air_detector.set_brush_color(bgr)

        def _enable_eraser(self):
            self.is_eraser = True

        def _clear_canvas(self):
            self.cv_canvas.delete("all")
            self.mouse_canvas = np.ones((500, 800, 3), dtype=np.uint8) * 255
            self.air_detector.clear_canvas()

        def _save_api_key(self):
            key = self.api_key_entry.get().strip()
            if key:
                self.gemini_solver.set_api_key(key)
                messagebox.showinfo("Saved", "Gemini API Key configured successfully!")

        def _update_camera_loop(self):
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.resize(frame, (800, 500))
                    processed_frame, mode = self.air_detector.process_frame(frame)

                    rgb_img = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                    pil_img = Image.fromarray(rgb_img)
                    imgtk = ImageTk.PhotoImage(image=pil_img)

                    self.video_label.imgtk = imgtk
                    self.video_label.configure(image=imgtk)

            self.root.after(30, self._update_camera_loop)

        def _solve_equation_action(self):
            current_tab = self.notebook.index(self.notebook.select())

            if current_tab == 0:
                canvas_to_solve = self.mouse_canvas
            else:
                canvas_to_solve = self.air_detector.canvas

            self.solution_text.delete(1.0, tk.END)
            self.solution_text.insert(tk.END, "Analyzing mathematical equation with AI...\n\n")

            result = self.gemini_solver.solve_canvas_image(canvas_to_solve)

            output = f"📌 RECOGNIZED EXPRESSION:\n  {result['expression']}\n\n"
            output += f"🏷️ CATEGORY:\n  {result['category']} ({result['source']})\n\n"
            output += f"📝 STEP-BY-STEP SOLUTION:\n"
            for step in result['steps']:
                output += f"  • {step}\n"
            output += f"\n💡 FINAL ANSWER:\n  {result['final_answer']}\n"

            self.solution_text.delete(1.0, tk.END)
            self.solution_text.insert(tk.END, output)

            try:
                graph_img = plot_equation_graph(result['expression'])
                graph_rgb = cv2.cvtColor(graph_img, cv2.COLOR_BGR2RGB)
                pil_graph = Image.fromarray(graph_rgb).resize((380, 240))
                graph_tk = ImageTk.PhotoImage(image=pil_graph)
                self.graph_label.configure(image=graph_tk, text="")
                self.graph_label.image = graph_tk
            except Exception:
                pass

        def __del__(self):
            if hasattr(self, 'cap') and self.cap.isOpened():
                self.cap.release()

    if __name__ == "__main__":
        root = tk.Tk()
        app = AirCanvasMLApp(root)
        root.mainloop()
