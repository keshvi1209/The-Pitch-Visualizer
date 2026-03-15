"""
Image Generation Service
Calls HuggingFace Inference API to generate images from prompts.
Supports FLUX.1-schnell (free tier) with fallback to placeholder SVG.
"""

import os
import base64
import time
from io import BytesIO
from typing import Optional

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"), override=True)


# Model options (ordered by quality/speed tradeoff)
HF_MODELS = {
    "flux-schnell": "black-forest-labs/FLUX.1-schnell",
    "sdxl": "stabilityai/stable-diffusion-xl-base-1.0",
    "sd21": "stabilityai/stable-diffusion-2-1",
}

DEFAULT_MODEL = "flux-schnell"


def generate_image(prompt: str, width: int = 768, height: int = 512) -> str:
    """
    Generate an image from a prompt using HuggingFace Inference API.

    Args:
        prompt: The image generation prompt
        width: Image width in pixels
        height: Image height in pixels

    Returns:
        Base64 data URI string (data:image/png;base64,...)
        Falls back to SVG placeholder on failure.
    """
    hf_token = os.getenv("HF_TOKEN")
    print("[ImageGen] HF_TOKEN found:", bool(hf_token))
    print("[ImageGen] HF_TOKEN found:", hf_token)

    if not hf_token:
        print("[ImageGen] No HF_TOKEN found — using placeholder")
        return _placeholder_svg(prompt)

    # Try primary model, then fallbacks
    model_key = os.getenv("HF_MODEL", DEFAULT_MODEL)
    model_id = HF_MODELS.get(model_key, HF_MODELS[DEFAULT_MODEL])

    for attempt, mid in enumerate([model_id] + [v for k, v in HF_MODELS.items() if v != model_id]):
        try:
            result = _call_hf_api(prompt, mid, hf_token, width, height)
            if result:
                return result
        except Exception as e:
            print(f"[ImageGen] Model {mid} failed (attempt {attempt + 1}): {e}")
            if attempt < 2:
                time.sleep(2)

    # print("[ImageGen] All models failed — using placeholder")
    # return _placeholder_svg(prompt)


def _call_hf_api(prompt: str, model_id: str, token: str, width: int, height: int) -> Optional[str]:
    """Call HuggingFace Inference API directly via requests."""
    import requests

    url = f"https://router.huggingface.co/hf-inference/models/{model_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": width,
            "height": height,
            "num_inference_steps": 4 if "schnell" in model_id.lower() else 25,
            "guidance_scale": 0.0 if "schnell" in model_id.lower() else 7.5,
        },
        "options": {"wait_for_model": True},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)

    if response.status_code == 200:
        content_type = response.headers.get("content-type", "")
        if "image" in content_type:
            img_bytes = response.content
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            ext = "png" if "png" in content_type else "jpeg"
            return f"data:image/{ext};base64,{b64}"
        else:
            # Sometimes returns JSON with base64
            data = response.json()
            if isinstance(data, list) and data and "generated_image" in data[0]:
                return f"data:image/png;base64,{data[0]['generated_image']}"
    elif response.status_code == 503:
        # Model loading — wait and retry
        estimated_time = response.json().get("estimated_time", 20)
        wait = min(float(estimated_time), 30)
        print(f"[ImageGen] Model loading, waiting {wait:.0f}s...")
        time.sleep(wait)
        # One more try
        response2 = requests.post(url, headers=headers, json=payload, timeout=120)
        if response2.status_code == 200:
            b64 = base64.b64encode(response2.content).decode("utf-8")
            return f"data:image/png;base64,{b64}"
    else:
        print(f"[ImageGen] HTTP {response.status_code}: {response.text[:200]}")

    return None


def _placeholder_svg(prompt: str) -> str:
    """
    Generate a stylised SVG placeholder when image generation is unavailable.
    Shows a film-strip style panel with the prompt text.
    """
    # Truncate prompt for display
    display = prompt[:180] + "..." if len(prompt) > 180 else prompt
    display = display.replace('"', "'").replace("<", "&lt;").replace(">", "&gt;")

    # Generate a deterministic gradient color from prompt hash
    h = abs(hash(prompt)) % 360
    h2 = (h + 40) % 360

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="768" height="512" viewBox="0 0 768 512">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:hsl({h},50%,18%)" />
      <stop offset="100%" style="stop-color:hsl({h2},50%,10%)" />
    </linearGradient>
    <filter id="noise">
      <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch"/>
      <feColorMatrix type="saturate" values="0"/>
      <feBlend in="SourceGraphic" mode="overlay" result="blend"/>
      <feComposite in="blend" in2="SourceGraphic" operator="in"/>
    </filter>
  </defs>
  <rect width="768" height="512" fill="url(#bg)"/>
  <rect width="768" height="512" fill="url(#bg)" filter="url(#noise)" opacity="0.15"/>

  <!-- Film strip perforations -->
  {"".join(f'<rect x="{x}" y="12" width="18" height="28" rx="3" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>' for x in range(20, 750, 50))}
  {"".join(f'<rect x="{x}" y="472" width="18" height="28" rx="3" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1.5"/>' for x in range(20, 750, 50))}

  <!-- Center icon (Image representation) -->
  <circle cx="384" cy="220" r="48" fill="none" stroke="rgba(255,255,255,0.2)" stroke-width="2"/>
  <rect x="360" y="204" width="48" height="32" rx="4" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
  <circle cx="372" cy="214" r="3" fill="rgba(255,255,255,0.3)"/>
  <path d="M360 236 L376 218 L386 228 L394 220 L408 232" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>

  <!-- Label -->
  <text x="384" y="300" font-family="monospace" font-size="11" fill="rgba(255,255,255,0.4)" text-anchor="middle">IMAGE GENERATION PREVIEW</text>
  <text x="384" y="320" font-family="monospace" font-size="11" fill="rgba(255,255,255,0.25)" text-anchor="middle">Add HF_TOKEN to .env to generate real images</text>

  <!-- Prompt preview -->
  <rect x="60" y="345" width="648" height="80" rx="8" fill="rgba(0,0,0,0.35)"/>
  <text x="384" y="368" font-family="monospace" font-size="10" fill="rgba(255,255,255,0.5)" text-anchor="middle">PROMPT</text>
  <foreignObject x="75" y="375" width="618" height="45">
    <div xmlns="http://www.w3.org/1999/xhtml" style="color:rgba(255,255,255,0.7);font-family:monospace;font-size:11px;word-wrap:break-word;line-height:1.4">{display}</div>
  </foreignObject>
</svg>"""

    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"
