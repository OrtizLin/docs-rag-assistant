"""Answer loop: retrieve -> (dry-run passages | LLM draft) -> validate.
Abstention is a first-class outcome, not a failure: if the best
retrieval score is below threshold, the answer is "I don't know"
instead of a hallucinated answer with fake citations.
"""
from __future__ import annotations
import os
from .corpus import load_corpus
from .prompts import PROMPT_VERSION, SYSTEM_PROMPT
from .retrieval import retrieve_top, EmbeddingRetriever

ABSTAIN_THRESHOLD = 0.10
# Embedding cosine scores run much higher than TF-IDF scores, so the
# embedding path needs its own, higher abstain threshold. Set from
# real scores measured 2026-11-05 (gemini-embedding-001, 12 docs):
# out-of-scope top scores were 0.6029 (Android) and 0.5474 (WPF);
# the lowest in-scope top score was 0.6168 (a SwiftData paraphrase).
# 0.61 sits between them, but the gap is only 0.014, so this
# threshold is FRAGILE: a new out-of-scope question could score
# above it, or a new paraphrase below it. It works on the measured
# 26 questions; it is not a robust separator. If abstention
# misfires on new questions, the fix is a better separator
# (e.g. a margin between top-1 and top-2, or a second check),
# not quietly moving this number to fit one question.
EMBEDDING_ABSTAIN_THRESHOLD = 0.61
ABSTAIN_TEXT = "I don't know based on the indexed docs. No indexed passage answers this question."

_RETRIEVER_CACHE = {}

def _get_embedding_retriever(docs, corpus_dir):
    """One EmbeddingRetriever per (corpus, model, endpoint) per process.
    Document vectors are computed once and reused for every question
    in the same run; only the query is embedded per question. Without
    this, eval/held-out re-embedded all 12 documents for every case
    and hit the free-tier rate limit (HTTP 429, 2026-11-05)."""
    key = (
        str(corpus_dir),
        os.environ.get("EMBEDDING_MODEL", "text-embedding-3-small"),
        os.environ.get("EMBEDDING_BASE_URL", "https://api.openai.com/v1"),
    )
    if key not in _RETRIEVER_CACHE:
        _RETRIEVER_CACHE[key] = EmbeddingRetriever(docs)
    return _RETRIEVER_CACHE[key]

def _pick_retriever(docs, corpus_dir, retriever=None):
    """Default policy (switched 2026-11-05, same rule as Project 1):
    embedding won the comparison (original 12/12 both, paraphrase
    embedding 12/12 vs TF-IDF 9/12) and the embedding abstain
    threshold was set from real out-of-scope scores (0.61; see
    EMBEDDING_ABSTAIN_THRESHOLD). So: embedding when an embedding
    key is set, otherwise TF-IDF offline fallback.
    RETRIEVER=embedding forces embedding (clear error with no key);
    RETRIEVER=tfidf forces TF-IDF. Returns (name, ranked_fn, threshold).
    """
    choice = retriever or os.environ.get("RETRIEVER", "")
    if choice == "tfidf":
        return "tfidf", lambda q, k: retrieve_top(docs, q, top_k=k), ABSTAIN_THRESHOLD
    if choice == "embedding":
        return "embedding", _get_embedding_retriever(docs, corpus_dir).retrieve_top, EMBEDDING_ABSTAIN_THRESHOLD
    if os.environ.get("EMBEDDING_API_KEY") or os.environ.get("LLM_API_KEY"):
        return "embedding", _get_embedding_retriever(docs, corpus_dir).retrieve_top, EMBEDDING_ABSTAIN_THRESHOLD
    return "tfidf", lambda q, k: retrieve_top(docs, q, top_k=k), ABSTAIN_THRESHOLD

def answer_question(question, corpus_dir, top_k=3, dry_run=True, retriever=None):
    docs = load_corpus(corpus_dir)
    retriever_name, ranked_fn, threshold = _pick_retriever(docs, corpus_dir, retriever)
    ranked = ranked_fn(question, top_k)
    if not ranked or ranked[0][1] < threshold:
        return {
            "question": question, "answer": ABSTAIN_TEXT, "citations": [],
            "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
            "abstained": True, "prompt_version": PROMPT_VERSION, "retriever": retriever_name,
        }
    retrieved = [d for d, _ in ranked]
    if dry_run:
        parts = []
        for d in retrieved:
            parts.append(f"[{d['id']}] {d['title']}: {d['text']}")
        return {
            "question": question,
            "answer": "Retrieved passages (dry-run, not a generated summary):\n\n" + "\n\n".join(parts),
            "citations": [d["id"] for d in retrieved],
            "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
            "abstained": False, "prompt_version": PROMPT_VERSION, "retriever": retriever_name,
        }
    from .llm import complete_answer
    passages = "\n\n".join(f"[{d['id']}] {d['title']}: {d['text']}" for d in retrieved)
    user_prompt = f"Question: {question}\n\nRetrieved passages:\n{passages}"
    parsed = complete_answer(SYSTEM_PROMPT, user_prompt)
    allowed = {d["id"] for d in retrieved}
    citations = [c for c in parsed["citations"] if c in allowed]
    if not parsed["answer"].strip() or not citations:
        return {
            "question": question, "answer": ABSTAIN_TEXT, "citations": [],
            "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
            "abstained": True, "prompt_version": PROMPT_VERSION, "retriever": retriever_name,
        }
    return {
        "question": question, "answer": parsed["answer"], "citations": citations,
        "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
        "abstained": False, "prompt_version": PROMPT_VERSION, "retriever": retriever_name,
    }
