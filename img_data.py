import requests
import base64
import json

IMAGE_PATH = r"C:\Users\Hello\Desktop\pdf_extraction\page_2.png"

OLLAMA_URL = "http://192.168.0.200:11434/api/generate"

# Convert image to base64
with open(IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

prompt = """
Extract the table from this image.

Instructions:

1. If a header row exists, identify it and use it as the column names.
2. If no header row exists, infer the table structure from the column alignment.
3. Preserve all rows exactly.
4. Preserve multiline cell values as a single value.
5. If a cell is empty, return an empty string.
6. Return only valid JSON.
7. Do not summarize.
8. Do not explain.
9. Do not add markdown.

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

print(result["response"])

with open("table_output.json", "w", encoding="utf-8") as f:
    f.write(result["response"])