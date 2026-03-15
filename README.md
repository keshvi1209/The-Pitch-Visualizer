# 🎬 Pitch Visualizer — Narrative to Storyboard

> Transform any sales narrative or customer success story into a multi-panel visual storyboard using AI — panel by panel, in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-blue?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange?style=flat-square)
![FLUX](https://img.shields.io/badge/HuggingFace-FLUX.1--schnell-yellow?style=flat-square)

---

## 📖 Overview

**Pitch Visualizer** ingests a block of narrative text (e.g., a customer success story), deconstructs it into logical scenes, uses **Google's Gemini** (or Anthropic's Claude) to engineer richly descriptive image prompts for each scene, and then generates unique images via **HuggingFace's Inference API (FLUX.1-schnell)**. 

The result is a coherent, downloadable visual storyboard — streamed to the browser panel by panel using Server-Sent Events (SSE).

### Key Capabilities

| Feature | Implementation |
|---------|---------------|
| Narrative segmentation | NLTK sentence tokenizer + smart merge/split logic |
| LLM prompt engineering | Google `gemini-2.5-flash` natively, with fallback to Claude |
| Image generation | HuggingFace Inference API — FLUX.1-schnell (free tier) |
| Real-time streaming | Server-Sent Events (SSE) — panels appear as they're generated |
| 8 visual styles | Cinematic, Digital Art, Watercolor, Flat Design, Noir, Isometric, Anime, Photorealistic |
| Graceful fallback | Styled SVG placeholders if no image generation token is provided |

---

## 🚀 Setup and Execution

### 1. Requirements
Ensure you have Python 3.10+ installed on your system.

### 2. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/pitch-visualizer.git
cd pitch-visualizer
```

### 3. Install dependencies
It's highly recommended to use a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

*(Note: NLTK's `punkt` tokenizer will automatically be downloaded on the first run).*

### 4. API Key Management
The system requires specific API keys to function end-to-end. Copy the environment template:
```bash
cp .env.example .env
```

Open `.env` and configure your keys:

- **GEMINI_API_KEY**: (Primary) Used for transforming your text into visually descriptive prompts. Get it from [Google AI Studio](https://aistudio.google.com/).
- **ANTHROPIC_API_KEY**: (Fallback) If you prefer to use Claude for prompt engineering. Get it from [Anthropic Console](https://console.anthropic.com/).
- **HF_TOKEN**: Required to generate actual images using HuggingFace. Without this, the app will gracefully fall back to generating visually styled SVG placeholders. Get a free token at [HuggingFace Settings](https://huggingface.co/settings/tokens).

### 5. Execution

Start the Flask server:
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`. You can begin pasting narratives immediately!

---

## 🧠 Design Choices & Prompt Engineering Methodology

### Why use an LLM for Prompt Engineering?
Feeding a direct sentence like *"The team was overwhelmed with manual tasks"* to an image generation model usually produces overly literal, generic, or poorly structured images.

Pitch Visualizer leverages **Gemini 2.5 Flash** (via the `google-genai` SDK) to act as an expert storyboard artist. It transforms the text into something like:
> *"A dimly-lit open-plan office at dusk, stacks of paper overflowing across desks, three exhausted employees illuminated by harsh monitor glow, environment feels claustrophobic and pressured..."*

This dramatically improves the visual quality and relevance of the generated imagery.

### Position-Aware Narrative Context
The prompt engineering is context-aware based on the text segment's position in the overall story. The engineer injects specific hints:

- **Panel 1** → "Opening scene — establish setting and context"
- **Mid Panels** → "Rising action — tension or challenge building"
- **Climax Panels** → "Climax or turning point"
- **Final Panel** → "Resolution — positive outcome or conclusion"

This guarantees that the visual narrative progresses logically and matches the structural pacing of the story text.

### Visual Consistency Through Style Anchoring
Achieving visual consistency across multiple uniquely generated AI images is notoriously difficult. Pitch Visualizer addresses this by enforcing a **global style anchor**. 

Every engineered prompt concludes with a specific user-selected suffix (e.g., `cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K`). This restricts the image generator to a specific aesthetic universe across all panels, ensuring the storyboard feels cohesive.

### Smart Segmentation (NLTK)
The text segmentation utilizes NLTK's `punkt` tokenizer for natural sentence splitting. To prevent awkwardly short panels, it employs a custom merge pass: any sentence under 8 words is merged with the following sentence. It also ensures the storyboard has a minimum of 3 panels, artificially splitting longer segments if necessary by word count, and merges segments to remain under the maximum defined threshold (6 panels).

---

## 🎨 Visual Style Options

You can select a visual style directly in the UI. Options include:
- **Cinematic**: Film-grain, anamorphic, dramatic lighting (Best for B2B)
- **Digital Art**: Clean concept art, ArtStation aesthetic
- **Watercolor**: Soft, painterly, warm tones
- **Flat Design**: Bold, minimal, geometric shapes (Best for tech/SaaS)
- **Noir**: High-contrast black & white photography
- **Isometric**: 3D tech illustration
- **Anime**: Expressive, vibrant studio quality
- **Photorealistic**: DSLR-quality render, sharp focus

## 📄 License
MIT License.