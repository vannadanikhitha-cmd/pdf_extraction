import requests
import base64
import json

IMAGE_PATH = r"C:\Users\Hello\Desktop\pdf_extraction\page_1.png"

OLLAMA_URL = "http://192.168.0.200:11434/api/generate"

# Convert image to base64
with open(IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")
prompt = """
Extract the table from this image.

Instructions:
1. Detect whether the FIRST ROW of the table contains column names.
2. If the first row contains labels instead of transaction values, treat it as the header row.
3. Use those header names exactly as JSON keys.
4. Do NOT use generic names like Column1, Column2, etc.
5. Every subsequent row must become a JSON object.
6. Preserve multiline cell values as a single value.
7. If a cell is empty, return an empty string.
8. Return only valid JSON.
Output format:

{
  "headers": [],
  "rows": []
}
"""

payload = {
    "model": "qwen3-vl",
    "prompt": prompt,
    "images": [image_base64],
    "stream": False
}

response = requests.post(
    OLLAMA_URL,
    json=payload,
    timeout=1800
)

result = response.json()

# Convert model response string to JSON
table_data = json.loads(result["response"])

print("TYPE:", type(table_data))
print("DATA:", table_data)
#data_rows = table_data["rows"]

json_output = []

for row in data_rows:

    record = {}

    for i in range(len(headers)):

        header = headers[i]

        if i < len(row):
            record[header] = row[i]
        else:
            record[header] = ""

    json_output.append(record)

# Save final JSON
with open("table_output.json", "w", encoding="utf-8") as f:

    json.dump(
        json_output,
        f,
        indent=4,
        ensure_ascii=False
    )

print("JSON saved successfully")