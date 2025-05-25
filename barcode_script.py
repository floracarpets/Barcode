# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from barcode import Code128
from barcode.writer import ImageWriter
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw
import os
import numpy as np
import sys

# === FILES ===
codes_file = "codes_file.txt"
pdf_folder = "labels_pdf"
combined_pdf_name = "labels_combined.pdf"

# === SETTINGS ===
dpi = 300
figsize_inch = (5.91, 3.94)  # 150 x 100 mm
font_pt = 150
arrow_font = 80

# === START ===
os.makedirs(pdf_folder, exist_ok=True)
with open(codes_file, "r", encoding="utf-8") as f:
    codes = [line.strip() for line in f if line.strip()]

combined_pdf = PdfPages(combined_pdf_name)

for code in codes:
    try:
        # === BARCODE ===
        buffer = BytesIO()
        barcode = Code128(code, writer=ImageWriter())
        barcode.write(buffer, {
            "module_height": 35.0,
            "module_width": 0.21,  # 🔧 CHANGED from 0.1 → 0.21 for better scanner readability
            "quiet_zone": 6.5,     # 🔧 CHANGED from 1.0 → 6.5 to match industry standard quiet zone (10x module_width)
            "write_text": False,
            "dpi": dpi
        })
        buffer.seek(0)
        image = Image.open(buffer)

        # === PLOT ===
        fig, ax = plt.subplots(figsize=figsize_inch, dpi=dpi)
        ax.axis('off')

        # === EXPAND AXIS ===
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 2)

        # === BARCODE IMAGE ===
        ax.imshow(image, aspect='auto', extent=[0.05, 0.95, 0.55, 0.95], transform=ax.transAxes)

        # === LARGE TEXT (TRUE VERTICAL STRETCH) ===
        font_path = "/Library/Fonts/Arial.ttf"  # Change path as needed
        font = ImageFont.truetype(font_path, font_pt)
        bbox = font.getbbox(code)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        text_img = Image.new("RGBA", (text_width, text_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(text_img)
        draw.text((-bbox[0], -bbox[1]), code, font=font, fill=(0, 0, 0, 255))

        # Stretch text vertically
        stretch_factor = 2
        stretched_img = text_img.resize((text_width, int(text_height * stretch_factor)))
        stretched_arr = np.array(stretched_img)

        ax.imshow(
            stretched_arr,
            aspect='auto',
            extent=[0.0, 1, 0.1, 0.9],
            zorder=10
        )

        # === ARROWS ===
        ax.text(0.05, 0.7, "↑", fontsize=arrow_font, ha='center', va='center', transform=ax.transAxes)
        ax.text(0.95, 0.7, "↑", fontsize=arrow_font, ha='center', va='center', transform=ax.transAxes)

        # === SAVE ===
        path = os.path.join(pdf_folder, f"{code}.pdf")
        with PdfPages(path) as pdf:
            pdf.savefig(fig, bbox_inches='tight')

        combined_pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ Label generated: {code}")

    except Exception as e:
        print(f"❌ ERROR ({code}): {e}")

# === FINALIZE PDF ===
combined_pdf.close()
print(f"\n📄 Combined PDF ready: {combined_pdf_name}")
print("🎉 Completed. Labels generated with large text.")


# Note:
# python3 -m venv venv
# source venv/bin/activate
# pip install matplotlib python-barcode Pillow numpy
