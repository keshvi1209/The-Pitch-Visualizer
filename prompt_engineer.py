"""
Prompt Engineering Service
Uses Gemini (Google) or Claude (Anthropic) to transform plain text segments into
rich, visually descriptive image-generation prompts.
"""

import os
from typing import Optional

try:
    from google import genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import anthropic
    HAS_CLAUDE = True
except ImportError:
    HAS_CLAUDE = False


STYLE_PRESETS = {
    "cinematic": "cinematic photography, dramatic lighting, film grain, anamorphic lens, 8K",
    "digital art": "vibrant digital illustration, concept art, clean lines, professional, trending on ArtStation",
    "watercolor": "delicate watercolor painting, soft washes, artistic, painterly, warm tones",
    "flat design": "modern flat design illustration, bold colors, minimal shadows, clean geometric shapes",
    "noir": "black and white noir photography, high contrast, dramatic shadows, moody atmosphere",
    "isometric": "isometric 3D illustration, clean render, soft shadows, pastel colors, tech aesthetic",
    "anime": "anime style illustration, vibrant colors, expressive, detailed background, studio quality",
    "photorealistic": "photorealistic render, DSLR, sharp focus, natural lighting, high detail, 4K",
}


def engineer_prompt(text_segment: str, style: str = "cinematic", panel_index: int = 0, total_panels: int = 1) -> str:
    """
    Use Gemini or Claude to transform a text segment into a rich image generation prompt.

    Args:
        text_segment: The narrative sentence/segment
        style: Visual style key from STYLE_PRESETS
        panel_index: Position in the storyboard (for narrative context)
        total_panels: Total number of panels

    Returns:
        Enhanced image generation prompt string
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if not gemini_key and not anthropic_key:
        return _fallback_prompt(text_segment, style)

    style_suffix = STYLE_PRESETS.get(style, style)
    panel_position = _panel_position_hint(panel_index, total_panels)

    system_prompt = """You are an expert storyboard artist and AI image prompt engineer.
Your job is to transform narrative text into highly detailed, visually compelling image generation prompts.

Rules:
- Return ONLY the image prompt — no explanation, no quotes, no preamble
- Make it richly visual: describe scene, lighting, composition, mood, and focal point
- Keep it under 90 words
- Do NOT include brand names, logos, or real people
- Focus on visual storytelling — what would a camera capture?"""

    user_prompt = f"""Transform this text into a vivid image generation prompt.

Text: "{text_segment}"
Panel position: {panel_position}
Visual style: {style_suffix}

The prompt should describe exactly what would appear in this storyboard panel.
End with: {style_suffix}"""

    if gemini_key and HAS_GEMINI:
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_prompt,
                ),
            )
            raw = response.text.strip()
            return raw.strip('"\'')
        except Exception as e:
            print(f"[PromptEngineer] Gemini API error: {e}")
            # Fall through to Claude if configured, else fallback
            pass

    if anthropic_key and HAS_CLAUDE:
        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = message.content[0].text.strip()
            return raw.strip('"\'')
        except Exception as e:
            print(f"[PromptEngineer] Claude API error: {e}")

    return _fallback_prompt(text_segment, style)


def _panel_position_hint(index: int, total: int) -> str:
    if total <= 1:
        return "standalone scene"
    ratio = index / (total - 1)
    if ratio < 0.25:
        return "opening scene — establish setting and context"
    elif ratio < 0.5:
        return "rising action — tension or challenge building"
    elif ratio < 0.75:
        return "climax or turning point"
    else:
        return "resolution — positive outcome or conclusion"


def _fallback_prompt(text: str, style: str) -> str:
    """Simple fallback when API is unavailable."""
    style_suffix = STYLE_PRESETS.get(style, style)
    cleaned = text.replace('"', "").strip()
    return f"A visual scene depicting: {cleaned}. Highly detailed, professional composition, {style_suffix}"
