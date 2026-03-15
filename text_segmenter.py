"""
Text Segmentation Service
Splits narrative text into logical scenes/segments using NLTK sentence tokenizer.
Falls back to period-based splitting if NLTK is unavailable.
"""

from typing import List
import re


def segment_text(text: str, max_segments: int = 6) -> List[str]:
    """
    Segment input narrative into logical scenes.
    Uses NLTK punkt tokenizer with fallback to regex splitting.

    Args:
        text: Input narrative paragraph
        max_segments: Cap on number of panels (default 6)

    Returns:
        List of text segments (at least 3)
    """
    text = text.strip()
    if not text:
        return []

    sentences = _tokenize(text)

    # Merge very short sentences (< 8 words) with the next one
    merged = []
    buffer = ""
    for sent in sentences:
        if buffer:
            combined = buffer + " " + sent
            if len(buffer.split()) < 8:
                buffer = combined
            else:
                merged.append(buffer.strip())
                buffer = sent
        else:
            buffer = sent
    if buffer:
        merged.append(buffer.strip())

    sentences = [s for s in merged if s]

    # Ensure at least 3 segments
    if len(sentences) < 3:
        sentences = _force_split(text, 3)

    # Cap at max_segments
    if len(sentences) > max_segments:
        sentences = _merge_to_limit(sentences, max_segments)

    return sentences


def _tokenize(text: str) -> List[str]:
    """Try NLTK first, fall back to regex."""
    try:
        import nltk
        try:
            tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
        except LookupError:
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
            tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
        return tokenizer.tokenize(text)
    except Exception:
        # Fallback: split on sentence-ending punctuation
        raw = re.split(r"(?<=[.!?])\s+", text)
        return [s.strip() for s in raw if s.strip()]


def _force_split(text: str, n: int) -> List[str]:
    """Split text into n roughly equal parts by word count."""
    words = text.split()
    size = max(1, len(words) // n)
    parts = []
    for i in range(0, len(words), size):
        chunk = " ".join(words[i : i + size])
        if chunk:
            parts.append(chunk)
    return parts[:n] if len(parts) >= n else parts


def _merge_to_limit(sentences: List[str], limit: int) -> List[str]:
    """Merge adjacent sentences to stay within limit."""
    while len(sentences) > limit:
        # Find the two shortest adjacent sentences and merge them
        min_len = float("inf")
        min_idx = 0
        for i in range(len(sentences) - 1):
            combined_len = len(sentences[i]) + len(sentences[i + 1])
            if combined_len < min_len:
                min_len = combined_len
                min_idx = i
        sentences[min_idx] = sentences[min_idx] + " " + sentences[min_idx + 1]
        sentences.pop(min_idx + 1)
    return sentences
