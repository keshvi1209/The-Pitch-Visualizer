# 🎬 Pitch Visualizer — Narrative to Storyboard

> Transform any sales narrative or customer success story into a multi-panel visual storyboard using AI — panel by panel, in real time.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=flat-square)
![Claude](https://img.shields.io/badge/Claude-Sonnet-orange?style=flat-square)
![FLUX](https://img.shields.io/badge/HuggingFace-FLUX.1--schnell-yellow?style=flat-square)

---

## 📖 Overview

**Pitch Visualizer** ingests a block of narrative text (e.g., a customer success story), deconstructs it into logical scenes, uses **Claude (Anthropic)** to engineer richly descriptive image prompts for each scene, and then generates unique images via **HuggingFace's free Inference API (FLUX.1-schnell)**. The result is a coherent, downloadable visual storyboard — streamed to the browser panel by panel.

### Key Capabilities

| Feature | Implementation |
|---------|---------------|
| Narrative segmentation | NLTK sentence tokenizer + smart merge/split logic |
| LLM prompt engineering | Claude `claude-sonnet-4-5` — context-aware, position-sensitive |
| Image generation | HuggingFace Inference API — FLUX.1-schnell (free tier) |
| Real-time streaming | Server-Sent Events (SSE) — panels appear as they're generated |
| 8 visual styles | Cinematic, Digital Art, Watercolor, Flat Design, Noir, Isometric, Anime, Photorealistic |
| Export | One-click HTML storyboard export with embedded images |
| Graceful fallback | Styled SVG placeholders if no HF_TOKEN is provided |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/pitch-visualizer.git
cd pitch-visualizer
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# OR
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
ANTHROPIC_API_KEY=sk-ant-...    # https://console.anthropic.com
HF_TOKEN=hf_...                 # https://huggingface.co/settings/tokens
```

> **Getting free API keys:**
> - **Anthropic**: Sign up at [console.anthropic.com](https://console.anthropic.com) — $5 free credit for new accounts
> - **HuggingFace**: Free account at [huggingface.co](https://huggingface.co) — FLUX.1-schnell is on the free tier

### 5. Run the app

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

---

## 🏗️ Architecture

```
pitch-visualizer/
├── app.py                        # Flask app + SSE streaming endpoint
├── services/
│   ├── text_segmenter.py         # NLTK-based narrative segmentation
│   ├── prompt_engineer.py        # Claude-powered prompt refinement
│   └── image_generator.py        # HuggingFace image generation + fallback
├── templates/
│   └── index.html                # Single-page dynamic UI
├── requirements.txt
├── .env.example
└── README.md
```

### Request Flow

```
User types narrative
        │
        ▼
[POST /generate]
        │
        ├─▶ text_segmenter.py
        │      └─ NLTK punkt tokenizer → 3–6 logical scenes
        │
        ├─▶ For each scene:
        │      ├─▶ prompt_engineer.py  →  Claude API  →  Enhanced visual prompt
        │      └─▶ image_generator.py  →  HuggingFace API  →  Base64 image
        │
        └─▶ Stream via SSE → Browser renders panels in real time
```

---

## 🧠 Design Choices & Prompt Engineering Methodology

### Why Claude for Prompt Engineering?

Simply feeding a sentence like *"Their team was overwhelmed with manual tasks"* to an image model produces generic or literal results. Claude transforms this into something like:

> *"A dimly-lit open-plan office at dusk, stacks of paper overflowing across desks, three exhausted employees illuminated by harsh monitor glow, environment feels claustrophobic and pressured, shallow depth of field, cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K"*

This produces dramatically more compelling imagery.

### Position-Aware Prompts

The prompt engineer knows where in the story a segment falls:

| Position | Narrative Arc Hint passed to Claude |
|----------|--------------------------------------|
| Panel 1  | "Opening scene — establish setting and context" |
| Panel 2  | "Rising action — tension or challenge building" |
| Panel 3  | "Climax or turning point" |
| Last     | "Resolution — positive outcome or conclusion" |

This ensures visual narrative progression matches story structure.

### Visual Consistency

Every engineered prompt ends with the **user-selected style suffix** (e.g., `cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K`). This acts as a global style anchor across all panels, producing a coherent visual identity throughout the storyboard — addressing the classic AI art consistency challenge.

### Smart Segmentation

The segmenter uses NLTK's Punkt sentence tokenizer and applies a merge pass: sentences under 8 words are combined with their neighbors to avoid trivially short panels. If fewer than 3 segments result, a word-count-based force-split ensures a minimum of 3 panels.

---

## 🎨 Visual Style Options

| Style | Character |
|-------|-----------|
| **Cinematic** | Film-grain, anamorphic, dramatic lighting — ideal for B2B narratives |
| **Digital Art** | Clean concept art, ArtStation aesthetic |
| **Watercolor** | Soft, painterly — good for lifestyle/wellness brands |
| **Flat Design** | Bold, minimal, geometric — ideal for tech/SaaS |
| **Noir** | High-contrast black & white — moody, premium |
| **Isometric** | 3D tech illustration — perfect for platform/infrastructure stories |
| **Anime** | Expressive, vibrant — consumer/gaming verticals |
| **Photorealistic** | DSLR-quality render — enterprise/documentary feel |

---

## 🔧 Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Optional | — | Gemini API key for prompt engineering (preferred) |
| `ANTHROPIC_API_KEY` | Optional | — | Claude API key for prompt engineering (alternative) |
| `HF_TOKEN` | Optional* | — | HuggingFace token for image generation |
| `HF_MODEL` | No | `flux-schnell` | Model: `flux-schnell`, `sdxl`, `sd21` |
| `FLASK_DEBUG` | No | `1` | Set to `0` in production |
| `PORT` | No | `5000` | Server port |

> *Without `HF_TOKEN`, the app still runs — it shows styled SVG placeholders showing the engineered prompt. Useful for demoing prompt engineering alone.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `flask` | Web framework + SSE response streaming |
| `google-genai` | Gemini API client |
| `anthropic` | Claude API client |
| `requests` | HuggingFace REST API calls |
| `nltk` | Sentence tokenization for narrative segmentation |
| `python-dotenv` | Environment variable management |

---

## 🛠️ Troubleshooting

**"Model is loading" delays (~20–30s)**
HuggingFace free tier cold-starts models. The app handles this automatically with retry logic. First request may take 30–60s.

**"FLUX.1-schnell returns 403"**
Accept the model license at [huggingface.co/black-forest-labs/FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell) while logged in, then try again.

**Images not generating but prompt engineering works**
Check that `HF_TOKEN` is set and has `read` permissions. The app will fall back to SVG placeholders and log the error to the console.

**NLTK `LookupError`**
The app auto-downloads the `punkt` tokenizer on first run. Ensure you have internet access on first launch.

---

## 📄 License

MIT — built for internship challenge submission.
#   T h e - P i t c h - V i s u a l i z e r  
 