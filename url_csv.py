import pdfplumber
import pandas as pd

pdf_path = r"C:\Users\Hello\Downloads\renewal_application.pdf"
output_csv = "renewal.csv"

all_rows = []

with pdfplumber.open(pdf_path) as pdf:
    for page in pdf.pages:
        table = page.extract_table()

        if table:
            if not all_rows:
                all_rows.extend(table)
            else:
                all_rows.extend(table[1:])

if all_rows:
    df = pd.DataFrame(all_rows[1:], columns=all_rows[0])
    df.to_csv(output_csv, index=False)

    print(f"CSV file created successfully: {output_csv}")
else:
    print("No table found in PDF")