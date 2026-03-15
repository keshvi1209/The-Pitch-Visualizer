# 🎬 Pitch Visualizer — Narrative to Storyboard

> Transform any sales narrative or customer success story into a multi-panel visual storyboard using AI — panel by panel, in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square)
![Gemini](https://img.shields.io/badge/Gemini-2.5--flash-blue?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange?style=flat-square)
![FLUX](https://img.shields.io/badge/HuggingFace-FLUX.1--schnell-yellow?style=flat-square)

---

## 📖 Overview

**Pitch Visualizer** ingests a block of narrative text (e.g., a customer success story or sales pitch), deconstructs it into logical scenes, uses **Google's Gemini 2.5 Flash** (or Anthropic's Claude as fallback) to engineer richly descriptive image prompts for each scene, and then generates unique images via **HuggingFace's Inference API (FLUX.1-schnell)** — with optional support for OpenAI DALL-E 3 and Stability AI SDXL.

The result is a coherent, multi-panel visual storyboard — streamed live to the browser panel by panel using **Server-Sent Events (SSE)**.

### Key Capabilities

| Feature | Implementation |
|---------|---------------|
| Narrative segmentation | NLTK `punkt` tokenizer + smart merge/split logic |
| LLM prompt engineering | Google `gemini-2.5-flash` (primary), Anthropic `claude-3-5-sonnet` (fallback) |
| Image generation | HuggingFace FLUX.1-schnell (default), OpenAI DALL-E 3, Stability AI SDXL |
| Provider fallback | OpenAI/Stability failures automatically fall back to HuggingFace |
| Real-time streaming | Server-Sent Events (SSE) — panels stream as they're generated |
| 8 visual styles | Cinematic, Digital Art, Watercolor, Flat Design, Noir, Isometric, Anime, Photorealistic |
| Graceful degradation | Styled SVG placeholders rendered locally if no image API token is configured |

---

## 🚀 Setup and Execution

### 1. Prerequisites
- Python 3.10 or higher
- `pip` package manager

### 2. Clone the Repository
```bash
git clone https://github.com/keshvi1209/The-Pitch-Visualizer.git
cd The-Pitch-Visualizer
```

### 3. Create a Virtual Environment and Install Dependencies

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

> **Note:** NLTK's `punkt` tokenizer data is downloaded automatically on the first run.

### 4. API Key Management

Create a `.env` file in the project root (you can copy `.env.example` if it exists):

```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Open `.env` and fill in the keys you want to use:

```env
# --- Prompt Engineering (at least one required) ---
GEMINI_API_KEY=your_gemini_key_here        # Primary LLM for prompt engineering
ANTHROPIC_API_KEY=your_anthropic_key_here  # Fallback LLM (Claude Sonnet)

# --- Image Generation (at least one recommended) ---
HF_TOKEN=your_huggingface_token_here       # Free — FLUX.1-schnell via HuggingFace
OPENAI_API_KEY=your_openai_key_here        # DALL-E 3 (falls back to HuggingFace on billing errors)
STABILITY_API_KEY=your_stability_key_here  # Stability AI SDXL (falls back to HuggingFace on failure)
```

#### Where to get each key

| Key | Provider | Link |
|-----|----------|------|
| `GEMINI_API_KEY` | Google AI Studio | [aistudio.google.com](https://aistudio.google.com/) |
| `ANTHROPIC_API_KEY` | Anthropic Console | [console.anthropic.com](https://console.anthropic.com/) |
| `HF_TOKEN` | HuggingFace (free) | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| `OPENAI_API_KEY` | OpenAI Platform | [platform.openai.com](https://platform.openai.com/) |
| `STABILITY_API_KEY` | Stability AI | [platform.stability.ai](https://platform.stability.ai/) |

> **Minimum setup:** Only `GEMINI_API_KEY` + `HF_TOKEN` are needed for a fully functional experience at no cost.

### 5. Run the App

```bash
python app.py
```

Open your browser and navigate to **`http://localhost:5000`**.
Paste any narrative text, choose a visual style and image provider, and click **Generate**.

### 6. Health Check

To verify all keys are loaded correctly:
```
GET http://localhost:5000/health
```
Returns a JSON object showing which API keys are present and whether the template was found.

---

## 🧠 Design Choices & Prompt Engineering Methodology

### Why Use an LLM for Prompt Engineering?

Feeding raw narrative text directly to an image generation model produces overly literal and visually poor results. A sentence like:

> *"The team was overwhelmed with manual tasks"*

…gives a generic, muddled image. Instead, Pitch Visualizer uses **Gemini 2.5 Flash** as an expert storyboard artist to rewrite it as:

> *"A dimly-lit open-plan office at dusk, stacks of paper overflowing across desks, three exhausted employees illuminated by harsh monitor glow, claustrophobic atmosphere, cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K"*

This intermediate step dramatically improves both visual quality and narrative relevance.

### Position-Aware Narrative Pacing

The prompt engineer receives the panel's position within the full storyboard and injects a structural hint to guide the LLM:

| Position | Hint injected |
|----------|--------------|
| First 25% | *"Opening scene — establish setting and context"* |
| 25–50% | *"Rising action — tension or challenge building"* |
| 50–75% | *"Climax or turning point"* |
| Final 25% | *"Resolution — positive outcome or conclusion"* |

This ensures the visual narrative follows the natural arc of the source text — opening, conflict, climax, resolution — making the storyboard feel like a coherent story rather than isolated images.

### Visual Consistency via Style Anchoring

Generating multiple images from different prompts risks producing a visually incoherent storyboard. To address this, every engineered prompt is suffixed with the same **style anchor** chosen by the user (e.g., `cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K`). By ending every prompt identically, the image model is constrained to a single aesthetic universe across all panels.

### LLM Fallback Chain

```
GEMINI_API_KEY present?  ──yes──▶  Gemini 2.5 Flash (via google-genai)
        │ (fail / missing)
        ▼
ANTHROPIC_API_KEY present?  ──yes──▶  Claude 3.5 Sonnet
        │ (fail / missing)
        ▼
  Rule-based fallback prompt (no API required)
```

### Image Provider Fallback Chain

```
Provider selected by user (openai / stability / huggingface)
        │
        ▼ (on billing error, auth error, or exception)
  HuggingFace FLUX.1-schnell  ──(no HF_TOKEN)──▶  SVG placeholder
```

This means the app **never crashes** — it degrades gracefully at every step.

### Smart Text Segmentation (NLTK)

Text segmentation uses NLTK's `punkt` sentence tokenizer with a custom post-processing pass:

- **Short-sentence merging**: sentences under 8 words are merged with the next sentence to avoid trivially short panels.
- **Minimum panels**: the storyboard always has at least 3 panels; long single-sentence inputs are split by word count.
- **Maximum panels**: segments are merged to stay within 6 panels, preventing overly fragmented storyboards.

---

## 🎨 Visual Style Options

Select a style in the UI before generating. Each style appends a different aesthetic suffix to every prompt:

| Style | Best For | Suffix Keywords |
|-------|----------|-----------------|
| **Cinematic** | B2B, enterprise pitches | film grain, anamorphic lens, dramatic lighting, 8K |
| **Digital Art** | Tech products, startups | concept art, clean lines, ArtStation aesthetic |
| **Watercolor** | Non-profits, storytelling | soft washes, painterly, warm tones |
| **Flat Design** | SaaS, mobile apps | bold colors, minimal shadows, geometric shapes |
| **Noir** | Mystery, high-stakes drama | black & white, high contrast, moody shadows |
| **Isometric** | Infrastructure, tech platforms | 3D illustration, pastel colors, clean render |
| **Anime** | Consumer products, gaming | vibrant colors, expressive, studio quality |
| **Photorealistic** | Real-world scenarios | DSLR, natural lighting, sharp focus, 4K |

---

## 🗂️ Project Structure

```
pitch-visualiser/
├── app.py                # Flask server, SSE streaming endpoint
├── text_segmenter.py     # NLTK-based narrative segmentation
├── prompt_engineer.py    # Gemini/Claude prompt engineering + style presets
├── image_generator.py    # HuggingFace / OpenAI / Stability AI image generation
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Single-page frontend (SSE consumer)
└── .env                  # API keys (not committed)
```

---

## 📄 License

MIT License.
