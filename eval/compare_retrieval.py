"""Compare TF-IDF vs model-embedding retrieval, top-1 accuracy.
Two query sets, both written BEFORE any embedding scores were seen:
- original: the 12 in-scope questions from eval/cases.json
- paraphrase: 12 rewordings, one per document, deliberately avoiding
  the document's distinctive keywords (e.g. no @State/@Binding,
  no Task/cancellation, no Sendable, no provisioning).
Also prints the top score of each retriever on the 2 out-of-scope
questions: embedding cosine scores run much higher than TF-IDF, so
the embedding abstain threshold must be set from those numbers,
not guessed. An embedding that cannot abstain out-of-scope must
not become the default, however well it does on paraphrases.

Win rule (same as Project 1): embedding becomes the default only
if it beats TF-IDF on paraphrases without losing on originals.
A tie keeps TF-IDF as the default. To switch, edit
docs_rag_assistant/agent.py _pick_retriever after the numbers
are in, and update README.md. Never fake the comparison: with
no key set, the embedding run prints "skipped (no key set)".
"""
import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docs_rag_assistant.corpus import load_corpus
from docs_rag_assistant.retrieval import retrieve_top, EmbeddingRetriever

PARAPHRASE = [
    ("a child screen needs to change a value owned by its parent without owning it itself", "swiftui-state-binding"),
    ("stopping a background job cooperatively when the user leaves the screen", "swift-concurrency"),
    ("the compiler cannot find a library I imported even though the code looks right", "xcode-no-such-module"),
    ("moving between screens in a stack and passing data to the next screen", "swiftui-navigation"),
    ("my app must talk to a server over plain HTTP for testing, how do I allow just that one address", "app-transport-security"),
    ("storing objects in a local database and listing only the ones matching a filter", "swiftdata-model"),
    ("scrolling through thousands of rows feels slow and stutters", "swiftui-list-performance"),
    ("the build fails because the identity proving who made the app does not match the allowed list", "xcode-code-signing"),
    ("sending a finished build to testers first, then to the store for review", "app-store-submission"),
    ("I added a field to my stored objects and old users' data must still open", "core-data-migration"),
    ("the compiler now complains when two tasks touch the same variable at once", "swift-6-strict-concurrency"),
    ("finding which part of my app uses the most processor time while it runs", "xcode-instruments-debugging"),
]

def score(retrieve_fn, queries):
    correct = 0
    for query, expected in queries:
        top = retrieve_fn(query, 1)
        ok = bool(top) and top[0][0]["id"] == expected
        correct += ok
        print(f"  {'PASS' if ok else 'FAIL'}: {query[:55]} (top={top[0][0]['id'] if top else None} score={top[0][1]:.4f} expected={expected})")
    return correct

def main():
    root = Path(__file__).resolve().parent.parent
    docs = load_corpus(str(root / "docs" / "corpus"))
    cases = json.loads((root / "eval" / "cases.json").read_text())
    original = [(c["question"], c["expected_doc"]) for c in cases if not c.get("must_abstain")]
    out_of_scope = [c["question"] for c in cases if c.get("must_abstain")]

    print("TF-IDF original:")
    tfidf_orig = score(lambda q, k: retrieve_top(docs, q, top_k=k), original)
    print("TF-IDF paraphrase:")
    tfidf_para = score(lambda q, k: retrieve_top(docs, q, top_k=k), PARAPHRASE)
    print(f"TF-IDF original top-1: {tfidf_orig}/{len(original)}")
    print(f"TF-IDF paraphrase top-1: {tfidf_para}/{len(PARAPHRASE)}")
    print("TF-IDF out-of-scope top scores:")
    for q in out_of_scope:
        top = retrieve_top(docs, q, top_k=1)
        print(f"  {top[0][1]:.4f}  {q[:60]}")

    if not (os.environ.get("EMBEDDING_API_KEY") or os.environ.get("LLM_API_KEY")):
        print("Embedding: skipped (no key set)")
        print("Summary: TF-IDF %d/%d original, %d/%d paraphrase; Embedding skipped" % (tfidf_orig, len(original), tfidf_para, len(PARAPHRASE)))
        return
    try:
        retriever = EmbeddingRetriever(docs)
    except RuntimeError as exc:
        print(f"Embedding: error: {exc}")
        return
    print("Embedding original:")
    emb_orig = score(retriever.retrieve_top, original)
    print("Embedding paraphrase:")
    emb_para = score(retriever.retrieve_top, PARAPHRASE)
    print(f"Embedding original top-1: {emb_orig}/{len(original)}")
    print(f"Embedding paraphrase top-1: {emb_para}/{len(PARAPHRASE)}")
    print("Embedding out-of-scope top scores:")
    for q in out_of_scope:
        top = retriever.retrieve_top(q, 1)
        print(f"  {top[0][1]:.4f}  {q[:60]}")
    if emb_para > tfidf_para and emb_orig >= tfidf_orig:
        print("Verdict: embedding BEATS TF-IDF on paraphrases without losing on originals -> switch default to embedding (after setting the embedding abstain threshold from the out-of-scope scores above).")
    elif emb_para == tfidf_para and emb_orig >= tfidf_orig:
        print("Verdict: embedding TIES TF-IDF -> keep TF-IDF as default.")
    else:
        print("Verdict: embedding does NOT beat TF-IDF -> keep TF-IDF as default.")
    print("Summary: TF-IDF %d/%d original, %d/%d paraphrase; Embedding %d/%d original, %d/%d paraphrase" % (tfidf_orig, len(original), tfidf_para, len(PARAPHRASE), emb_orig, len(original), emb_para, len(PARAPHRASE)))

if __name__ == "__main__":
    main()
