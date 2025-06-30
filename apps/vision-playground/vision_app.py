import gradio as gr
import base64
import requests
import json
import os

def analyze_image(prompt, image_path):
    if image_path is None or not os.path.exists(image_path):
        return "Please upload a valid image."

    with open(image_path, 'rb') as image_file:
        image_bytes = image_file.read()
        image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    payload = {
        "model": "llava",
        "prompt": prompt,
        "images": [image_b64],
        "stream": False
    }

    response = requests.post(
        "http://localhost:11434/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    if response.ok:
        return response.json().get("response", "[No response]")
    else:
        return f"Error: {response.status_code} - {response.text}"

gr.Interface(
    fn=analyze_image,
    inputs=[
        gr.Textbox(label="Prompt", placeholder="What’s happening in this image?"),
        gr.Image(type="filepath", label="Upload Image")
    ],
    outputs="text",
    title="LLaVA Vision Model (Local via Ollama)",
    theme="default"
).launch()
