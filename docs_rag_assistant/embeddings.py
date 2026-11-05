"""OpenAI-compatible embeddings client, standard library only.
Same contract as Project 1 (pr-review-agent/embeddings.py):
  EMBEDDING_API_KEY  (falls back to LLM_API_KEY if unset)
  EMBEDDING_BASE_URL (default https://api.openai.com/v1)
  EMBEDDING_MODEL    (default text-embedding-3-small)
No key -> clear RuntimeError, no silent fallback.
For a Google AI Studio key, use the Gemini OpenAI-compatible
endpoint (https://generativelanguage.googleapis.com/v1beta/openai)
and EMBEDDING_MODEL=gemini-embedding-001. Do NOT use
text-embedding-004 on the v1beta OpenAI-compatible path: it
returns HTTP 404 for many keys (verified 2026-11-05, Project 1).
"""
from __future__ import annotations
import json, os, urllib.error, urllib.request

def _key():
    return os.environ.get("EMBEDDING_API_KEY") or os.environ.get("LLM_API_KEY") or ""

def embed_texts(texts, timeout=60):
    api_key = _key()
    if not api_key:
        raise RuntimeError(
            "No embedding key set. Set EMBEDDING_API_KEY (or LLM_API_KEY) "
            "in your shell environment, never in chat or a committed file."
        )
    base_url = os.environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small")
    payload = json.dumps({"model": model, "input": list(texts)}).encode()
    request = urllib.request.Request(
        f"{base_url}/embeddings", data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            raise RuntimeError(
                "Embedding API rate limited (HTTP 429: Too Many Requests). "
                "Wait a few minutes before running again, and do not retry "
                "in a loop; the limit is per minute on the free tier."
            ) from exc
        raise RuntimeError(f"Embedding API request failed (HTTP {exc.code}).") from exc
    return parse_embeddings_response(body)

def parse_embeddings_response(body):
    data = body.get("data")
    if not isinstance(data, list) or not data:
        raise RuntimeError("Embeddings response had no data.")
    ordered = sorted(data, key=lambda item: item.get("index", 0))
    vectors = []
    for item in ordered:
        vec = item.get("embedding")
        if not isinstance(vec, list) or not vec:
            raise RuntimeError("Embeddings response contained an empty vector.")
        vectors.append([float(x) for x in vec])
    return vectors
