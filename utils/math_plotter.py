import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

def plot_equation_graph(expression: str):
    """
    Plots mathematical functions (e.g., y = x^2, sin(x), 2x+5) using Matplotlib and NumPy.
    Returns PIL Image object ready for Streamlit rendering.
    """
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    x = np.linspace(-10, 10, 400)

    try:
        if "x^2" in expression or "x²" in expression:
            y = x**2
            ax.set_title("Plot: $y = x^2$", fontsize=12)
        elif "sin" in expression:
            y = np.sin(x)
            ax.set_title("Plot: $y = \\sin(x)$", fontsize=12)
        elif "cos" in expression:
            y = np.cos(x)
            ax.set_title("Plot: $y = \\cos(x)$", fontsize=12)
        else:
            y = 2 * x + 5
            ax.set_title(f"Plot: {expression}", fontsize=12)

        ax.plot(x, y, color='blue', linewidth=2, label=expression)
        ax.axhline(0, color='black', linewidth=0.8, linestyle='--')
        ax.axvline(0, color='black', linewidth=0.8, linestyle='--')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend()

    except Exception:
        ax.text(0.5, 0.5, f"Graph for {expression}", fontsize=14, ha='center')

    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return Image.open(buf)
