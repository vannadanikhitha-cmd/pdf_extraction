import requests
import base64
import json

IMAGE_PATH = r"C:\Users\Hello\Desktop\pdf_extraction\page_6.png"

OLLAMA_URL = "http://192.168.0.200:11434/api/generate"

# Convert image to base64
with open(IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

prompt = """
You are an expert table extraction engine.

Instructions:
1. Extract ONLY the table data.
2. Identify column headers correctly.
3. Preserve all rows.
4. If a cell is empty, use null.
5. Return ONLY valid JSON.
6. Do not summarize.
7. Do not explain.
8. Do not add markdown.

Output Format Example:

[
  {
    "Date": "01-01-2026",
    "Amount": "1000",
    "Balance": "5000"
  }
]
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

print(result["response"])

with open("table_output.json", "w", encoding="utf-8") as f:
    f.write(result["response"])