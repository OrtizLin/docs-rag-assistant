"""OpenAI-compatible LLM boundary, standard library only.
Env-only configuration, same contract as Project 1:
  LLM_API_KEY   (required for the LLM path; never in chat or a file)
  LLM_BASE_URL  (default https://api.openai.com/v1)
  LLM_MODEL     (default gpt-4o-mini; set what you actually have access to)
The model must return JSON: {"answer": "...", "citations": ["doc-id", ...]}.
Anything else is rejected, and citations are re-validated by the caller
against the retrieved documents, so the model cannot cite a doc it
was not shown.
"""
from __future__ import annotations
import json, os, urllib.request

def parse_llm_response(text):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("answer"), str):
        return None
    cites = data.get("citations") or []
    if not isinstance(cites, list):
        return None
    return {"answer": data["answer"], "citations": [str(c) for c in cites]}

def complete_answer(system_prompt, user_prompt, timeout=60):
    api_key = os.environ.get("LLM_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY is not set. Set it in your shell environment "
            "(never in chat, never in a committed file) and retry with --no-dry-run."
        )
    base_url = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.environ.get("LLM_MODEL", "gpt-4o-mini")
    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }).encode()
    request = urllib.request.Request(
        f"{base_url}/chat/completions", data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode())
    content = body["choices"][0]["message"]["content"]
    parsed = parse_llm_response(content)
    if parsed is None:
        raise RuntimeError("LLM response was not valid JSON with an answer and citations.")
    return parsed
