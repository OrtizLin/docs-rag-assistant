"""Embedding retriever plumbing tests. The stub embedder proves the
ranking code works; it says nothing about real model quality, which
is measured by eval/compare_retrieval.py on a real key.
"""
import math, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docs_rag_assistant.retrieval import EmbeddingRetriever
from docs_rag_assistant.embeddings import parse_embeddings_response

DOCS = [
    {"id": "a", "title": "SwiftUI state", "text": "State Binding view"},
    {"id": "b", "title": "Android compose", "text": "Jetpack Compose activity"},
]

def _stub(texts):
    # a -> [1, 0], b -> [0, 1]; a query about SwiftUI state maps to [1, 0]
    vecs = []
    for t in texts:
        vecs.append([1.0, 0.0] if "SwiftUI" in t or "State" in t else [0.0, 1.0])
    return vecs

def test_embedding_retriever_ranks_by_cosine():
    r = EmbeddingRetriever(DOCS, embed=_stub)
    top = r.retrieve_top("SwiftUI State", top_k=1)
    assert top and top[0][0]["id"] == "a" and top[0][1] > 0.9

def test_parse_embeddings_response_orders_by_index():
    body = {"data": [
        {"index": 1, "embedding": [0.0, 1.0]},
        {"index": 0, "embedding": [1.0, 0.0]},
    ]}
    vecs = parse_embeddings_response(body)
    assert vecs == [[1.0, 0.0], [0.0, 1.0]]

def test_parse_embeddings_response_rejects_empty_vector():
    try:
        parse_embeddings_response({"data": [{"index": 0, "embedding": []}]})
    except RuntimeError:
        return
    raise AssertionError("empty vector should raise RuntimeError")

def test_document_vectors_embedded_once_per_process(monkeypatch):
    """Regression test for the 2026-11-05 HTTP 429: answer_question used
    to re-embed all documents on every question, so a 14-case eval
    made 14 document-embedding calls. Two questions in one process
    must embed the documents exactly once (plus one query embed each).
    """
    import docs_rag_assistant.agent as agent_mod
    import docs_rag_assistant.embeddings as emb_mod
    calls = []
    def counting_embed(texts):
        calls.append(len(texts))
        return [[1.0, 0.0] if ("State" in t or "state" in t.lower()) else [0.0, 1.0] for t in texts]
    monkeypatch.setattr(emb_mod, "embed_texts", counting_embed)
    monkeypatch.setenv("EMBEDDING_API_KEY", "dummy")
    monkeypatch.setenv("EMBEDDING_MODEL", "test-model")
    agent_mod._RETRIEVER_CACHE.clear()
    corpus = str(Path(__file__).resolve().parent.parent / "docs" / "corpus")
    agent_mod.answer_question("What is @State and @Binding in SwiftUI?", corpus, dry_run=True)
    agent_mod.answer_question("What is @State and @Binding in SwiftUI?", corpus, dry_run=True)
    doc_embeds = [c for c in calls if c > 1]
    assert doc_embeds == [12], f"documents embedded {len(doc_embeds)} times, calls={calls}"
    assert len(calls) == 3, f"expected 1 doc embed + 2 query embeds, got {calls}"
