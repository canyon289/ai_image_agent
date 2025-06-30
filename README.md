# Welcome!

In this workshop, we'll dig into the image capabilities of the Gemma series.

We'll
- 🧾 Extract structured information from images (e.g. OCR on receipts)
- 🖼️ Classify and count objects using LLMs
- ⚙️ Route behavior based on image content
- 🚦 Prototype image-to-action workflows (e.g. “if dog, then…”)

All running **locally** using **Gemma 3 models** through **Ollama** — with no cloud dependencies and no unnecessary complexity.


This workshop was inspired in part by a talk given by **Ravin Kumar** during [Hugo Bowne-Anderson's course, *Building LLM-Powered Applications for Data Scientists and Software Engineers*](https://maven.com/s/course/d56067f338).

Next cohort starts July 8 and use code `LLM10` for 10% off (valid until July 5, 2025)!

---

## 🛠 What You'll Build

The workshop is divided into three progressive phases:

---

### ✅ Phase 0: Get started with image workflows locally

You'll start by setting up a simple but complete local application:
- Connect to a local Gemma 3 model using Ollama.
- Send basic prompts and receive responses.
- Build a basic Gradio UI to interact with the model that takes in images


---

### ✅ Phase 1: Various image capabilities of Gemma

After a basic prompting we'll show various image capabilities

- Object recognition
- Counting
- OCR

---

### ✅ Phase 2: Connect everything together with GradIO

Finally, you'll move from hardcoded tool lists to a dynamic system:
- Add all this to GradIO
- Make the image input seamless for users
- Use the LLM to provide routed responses

---

## 🚀 Getting Started

To run this workshop locally, you'll need **Ollama** and a working **Python 3.9+ environment**.

---

### 1. Install Ollama

Download and install Ollama from [https://ollama.com/](https://ollama.com/).

Then pull the required models:

```bash
ollama pull gemma3:4b-it-qat
ollama pull gemma3:12b-it-qat  # optional if your machine can handle it
ollama pull gemma3:27b-it-qat  # optional if your machine can handle it

```

---

### 2. Set up your Python environment

We recommend using `uv` for managing dependencies.

```bash
pip install uv
uv venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

Install dependencies:

```bash
uv pip install -r requirements.txt
```

---

### 3. Running the Materials

- **Notebooks** are located in the `notebooks/` folder.
- **Gradio apps** and other small scripts are in the `apps/` folder.

Start with `notebooks/1-ai-app-mvp.ipynb` and work through them in order.

---

## ⚡ Quick Note on Hardware

- You should have at least **16GB of RAM** to run Gemma 3 4B models comfortably.
- 12B models may require **32GB+** of RAM or a machine with unified memory.
- Model downloads can be large (~10–20GB).

Running locally is part of the hands-on experience:  
You'll encounter real-world constraints — and learn how to work with them.

---

Ready to build your first agent? Let's go. 🚀
