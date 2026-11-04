"""Local TF-IDF retrieval. Same stable interface as Project 1:
retrieve_top(documents, query, top_k) -> list of (doc, score).
A model embedding can replace this function later, using the same
evaluation in eval/run_eval.py to prove it is better.
"""
from __future__ import annotations
import math, re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "of", "to", "in", "on", "for", "with",
    "how", "what", "is", "are", "was", "were", "do", "does", "did",
    "i", "you", "my", "can", "could", "should", "when", "where", "why",
    "build", "create", "make", "app", "use", "using", "used", "get",
}

def _tokens(text):
    return [t for t in re.findall(r"[a-z0-9_]+", text.lower()) if t not in STOPWORDS]

def retrieve_top(documents, query, top_k=3):
    docs = list(documents)
    if not docs or not query.strip():
        return []
    qtokens = _tokens(query)
    if not qtokens:
        return []
    # document frequency
    df = Counter()
    doc_tokens = []
    for d in docs:
        toks = _tokens(d.get("text", "") + " " + d.get("title", ""))
        doc_tokens.append(Counter(toks))
        for t in set(toks):
            df[t] += 1
    n = len(docs)
    scored = []
    for d, counts in zip(docs, doc_tokens):
        total = sum(counts.values()) or 1
        score = 0.0
        for t in qtokens:
            if counts.get(t):
                idf = math.log((n + 1) / (df[t] + 1)) + 1.0
                score += (counts[t] / total) * idf
        scored.append((d, score))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]
