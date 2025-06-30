import base64
import json
import requests

image_path = 'example.jpg'
prompt = "What’s happening in this image?"

with open(image_path, 'rb') as f:
    image_bytes = f.read()
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

payload = {
    "model": "llava",
    "prompt": prompt,
    "images": [image_b64],
    "stream": False
}

headers = {"Content-Type": "application/json"}
response = requests.post(
    "http://localhost:11434/api/generate",
    headers=headers,
    data=json.dumps(payload)
)

print(response.json().get('response'))
