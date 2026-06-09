import fitz
import pytesseract
import pandas as pd
from PIL import Image
import os
import re

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pdf_path = r"C:\Users\Hello\Downloads\HDFC_Statement.pdf"
output_csv = "hdfc.csv"

all_rows = []

# Open PDF
pdf = fitz.open(pdf_path)

for page_num in range(len(pdf)):

    page = pdf[page_num]

    # Convert PDF page to image
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))

    image_path = f"page_{page_num + 1}.png"

    pix.save(image_path)

    print(f"Processing {image_path}")

    # OCR extraction
    text = pytesseract.image_to_string(
        Image.open(image_path)
    )

    # Save OCR output for debugging
    with open(
        f"page_{page_num + 1}.txt",
        "w",
        encoding="utf-8"
    ) as f:
        f.write(text)

    lines = text.split("\n")

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # Split on multiple spaces/tabs
        row = re.split(r"\s{2,}|\t", line)

        all_rows.append(row)

# Create CSV
if all_rows:

    max_cols = max(len(row) for row in all_rows)

    for row in all_rows:
        while len(row) < max_cols:
            row.append("")

    columns = [
        f"Column_{i+1}"
        for i in range(max_cols)
    ]

    df = pd.DataFrame(
        all_rows,
        columns=columns
    )

    df.to_csv(
        output_csv,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"\nCSV created: {output_csv}")

else:
    print("No data extracted")