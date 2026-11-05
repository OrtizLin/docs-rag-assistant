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

def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)

class EmbeddingRetriever:
    """Model-embedding retrieval with the same output shape as TF-IDF:
    retrieve_top(documents, query, top_k) -> list of (doc, score).
    Document vectors are computed once in __init__; the query is
    embedded per call. Query and documents must use the same model.
    """

    def __init__(self, documents, embed=None):
        from .embeddings import embed_texts
        self.docs = list(documents)
        self.embed = embed or embed_texts
        texts = [d.get("title", "") + "\n" + d.get("text", "") for d in self.docs]
        self.vectors = self.embed(texts) if texts else []

    def retrieve_top(self, query, top_k=3):
        if not self.docs or not query.strip():
            return []
        qvec = self.embed([query])[0]
        scored = [(d, _cosine(qvec, v)) for d, v in zip(self.docs, self.vectors)]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

def retrieve_top_embedding(documents, query, embed=None, top_k=3):
    return EmbeddingRetriever(documents, embed=embed).retrieve_top(query, top_k=top_k)

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
