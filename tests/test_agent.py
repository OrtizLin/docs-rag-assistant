import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docs_rag_assistant.agent import answer_question
from docs_rag_assistant.retrieval import retrieve_top

CORPUS = str(Path(__file__).resolve().parent.parent / "docs" / "corpus")

def test_in_scope_returns_citation():
    r = answer_question("What is @State and @Binding in SwiftUI?", CORPUS, dry_run=True)
    assert not r["abstained"]
    assert "swiftui-state-binding" in r["citations"]

def test_out_of_scope_abstains():
    r = answer_question("How do I build an Android app with Jetpack Compose?", CORPUS, dry_run=True)
    assert r["abstained"]
    assert r["citations"] == []

def test_retrieval_top_is_stable():
    docs = [{"id": "a", "title": "SwiftUI state", "text": "State Binding view"}]
    top = retrieve_top(docs, "SwiftUI Binding", top_k=1)
    assert top and top[0][0]["id"] == "a" and top[0][1] > 0
