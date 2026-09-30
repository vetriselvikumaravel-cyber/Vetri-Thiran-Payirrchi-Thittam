import os
from datetime import datetime

from fpdf import FPDF

EXPORTS_DIR = os.path.join("static", "exports")


def _latin(text: str) -> str:
    """FPDF (core fonts) only supports latin-1; replace anything else."""
    return (text or "").encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout: list[dict], title: str = "ComicCraft Comic") -> str:
    """Compile the comic into a multi-page PDF and return its path."""
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Cover page
    pdf.add_page()
    pdf.set_font("Arial", "B", 24)
    pdf.ln(60)
    pdf.multi_cell(0, 14, _latin(title), align="C")

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.multi_cell(0, 10, _latin(f"Panel {panel['panel']}: {panel['title']}"))
        pdf.ln(2)
        img = panel.get("image_path")
        if img and os.path.exists(img):
            pdf.image(img, x=25, w=160)
            pdf.ln(4)
        pdf.set_font("Arial", "I", 11)
        pdf.multi_cell(0, 7, _latin(panel.get("scene", "")))
        pdf.ln(2)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, _latin(panel.get("text", "")))

    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(EXPORTS_DIR, filename)
    pdf.output(path)
    return path.replace("\\", "/")
