import json
import os
import sys
import time

from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request

# Resolve paths relative to THIS file — works regardless of cwd or OS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from image_generator import generate_image
from prompt_engineer import STYLE_PRESETS, engineer_prompt
from text_segmenter import segment_text

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "pitch-visualizer-dev")

TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")


@app.route("/")
def index():
    """Serve HTML directly — no render_template, no TemplateNotFound."""
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    narrative = (data.get("text") or "").strip()
    style = data.get("style", "cinematic")

    if not narrative:
        return jsonify({"error": "No text provided"}), 400

    if style not in STYLE_PRESETS:
        style = "cinematic"

    def event_stream():
        try:
            segments = segment_text(narrative)
            if not segments:
                yield _sse({"type": "error", "message": "Could not segment the input text."})
                return

            yield _sse({"type": "start", "total": len(segments), "style": style})

            for i, segment in enumerate(segments):
                yield _sse({"type": "segment", "index": i, "text": segment})

                enhanced = engineer_prompt(
                    text_segment=segment,
                    style=style,
                    panel_index=i,
                    total_panels=len(segments),
                )
                yield _sse({"type": "prompt", "index": i, "enhanced": enhanced})

                image_data = generate_image(enhanced)
                yield _sse({"type": "image", "index": i, "src": image_data})

            yield _sse({"type": "done"})

        except Exception as e:
            print(f"[/generate] Unhandled error: {e}")
            yield _sse({"type": "error", "message": str(e)})

    return Response(
        event_stream(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "gemini_key": bool(os.getenv("GEMINI_API_KEY")),
        "hf_token": bool(os.getenv("HF_TOKEN")),
        "template_found": os.path.exists(TEMPLATE_PATH),
        "base_dir": BASE_DIR,
    })


def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    print(f"\n Pitch Visualizer")
    print(f"    URL     : http://localhost:{port}")
    print(f"    BASE_DIR: {BASE_DIR}")
    print(f"    Template: {'found' if os.path.exists(TEMPLATE_PATH) else 'MISSING - check templates/index.html'}")
    print(f"    Gemini  : {'set' if os.getenv('GEMINI_API_KEY') else 'missing'}")
    print(f"    HF Token: {'set' if os.getenv('HF_TOKEN') else 'missing (placeholders)'}\n")
    app.run(host="0.0.0.0", port=port, debug=debug, threaded=True)