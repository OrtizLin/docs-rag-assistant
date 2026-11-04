"""Answer loop: retrieve -> (dry-run passages | LLM draft) -> validate.
Abstention is a first-class outcome, not a failure: if the best
retrieval score is below threshold, the answer is "I don't know"
instead of a hallucinated answer with fake citations.
"""
from __future__ import annotations
from .corpus import load_corpus
from .prompts import PROMPT_VERSION, SYSTEM_PROMPT
from .retrieval import retrieve_top

ABSTAIN_THRESHOLD = 0.10
ABSTAIN_TEXT = "I don't know based on the indexed docs. No indexed passage answers this question."

def answer_question(question, corpus_dir, top_k=3, dry_run=True):
    docs = load_corpus(corpus_dir)
    ranked = retrieve_top(docs, question, top_k=top_k)
    if not ranked or ranked[0][1] < ABSTAIN_THRESHOLD:
        return {
            "question": question, "answer": ABSTAIN_TEXT, "citations": [],
            "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
            "abstained": True, "prompt_version": PROMPT_VERSION,
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
            "abstained": False, "prompt_version": PROMPT_VERSION,
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
            "abstained": True, "prompt_version": PROMPT_VERSION,
        }
    return {
        "question": question, "answer": parsed["answer"], "citations": citations,
        "retrieved": [{"id": d["id"], "title": d["title"], "score": round(s, 4)} for d, s in ranked],
        "abstained": False, "prompt_version": PROMPT_VERSION,
    }
