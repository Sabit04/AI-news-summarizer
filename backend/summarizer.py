"""Summarization pipeline.

Calls the Hugging Face Inference API with a BART-based summarization model.
Handles long inputs by chunking + batching the chunks into a single request,
then stitching the per-chunk summaries together.

Why chunk: BART has a ~1024 token context window. Feeding it 5000+ character
articles in one shot silently truncates the tail. Chunking preserves the
whole article.

Why batch: sending each chunk as its own HTTP request multiplies latency by
the number of chunks. HF's API accepts a list input and returns one summary
per item in a single round trip.
"""

import os
import requests
from typing import List

HF_MODEL = "facebook/bart-large-cnn"
# HF deprecated api-inference.huggingface.co in 2025 in favor of the
# router.huggingface.co endpoint, which dispatches to whichever provider
# (hf-inference, replicate, together, etc.) is serving the model.
HF_URL = f"https://router.huggingface.co/hf-inference/models/{HF_MODEL}"

# BART's context window is ~1024 tokens. We approximate 1 token ≈ 4 chars and
# keep chunks comfortably under that so the model sees the whole chunk.
CHUNK_SIZE_CHARS = 3200
CHUNK_OVERLAP_CHARS = 200  # small overlap preserves sentence continuity


def _chunk_text(text: str) -> List[str]:
    text = text.strip()
    if len(text) <= CHUNK_SIZE_CHARS:
        return [text]

    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = min(start + CHUNK_SIZE_CHARS, len(text))
        # Prefer breaking at a sentence boundary within the tail ~300 chars.
        if end < len(text):
            window = text[max(end - 300, start):end]
            last_period = window.rfind(". ")
            if last_period > 0:
                end = max(end - 300, start) + last_period + 1
        chunks.append(text[start:end].strip())
        start = max(end - CHUNK_OVERLAP_CHARS, end)
    return [c for c in chunks if c]


def _call_hf(payload: dict, token: str) -> list:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    resp = requests.post(HF_URL, headers=headers, json=payload, timeout=60)
    if resp.status_code == 503:
        # Model is warming up on a cold start. One retry is enough in practice.
        resp = requests.post(HF_URL, headers=headers, json=payload, timeout=90)
    resp.raise_for_status()
    return resp.json()


def summarize(text: str, max_length: int = 150, min_length: int = 40) -> dict:
    token = os.environ.get("HF_API_TOKEN")
    if not token:
        raise RuntimeError("HF_API_TOKEN is not set")

    chunks = _chunk_text(text)

    # Send all chunks as a single batched inference request. HF returns one
    # summary per list item. Constraining max_length curbs hallucination —
    # the model can't invent details beyond the budget it's given.
    payload = {
        "inputs": chunks,
        "parameters": {
            "max_length": max_length,
            "min_length": min_length,
            "do_sample": False,
            "truncation": True,
        },
        "options": {"wait_for_model": True},
    }
    result = _call_hf(payload, token)

    # HF returns either [{summary_text: ...}, ...] for list inputs, or a single
    # dict for a single input depending on version. Normalize.
    if isinstance(result, dict):
        result = [result]
    summaries = [item.get("summary_text", "") for item in result]

    combined = " ".join(s.strip() for s in summaries if s).strip()

    return {
        "summary": combined,
        "chunk_count": len(chunks),
        "input_chars": len(text),
        "model": HF_MODEL,
    }
