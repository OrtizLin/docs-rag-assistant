"""Score retrieval + abstention.
Pass = top-1 retrieved doc matches expected_doc for in-scope questions,
and abstention for out-of-scope questions. No partial credit for a
right-looking answer with a wrong citation.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docs_rag_assistant.agent import answer_question

def main():
    root = Path(__file__).resolve().parent.parent
    cases = json.loads((root / "eval" / "cases.json").read_text())
    passed = 0
    for case in cases:
        result = answer_question(case["question"], str(root / "docs" / "corpus"), top_k=3, dry_run=True)
        if case.get("must_abstain"):
            ok = result["abstained"] and not result["citations"]
            detail = f"abstained={result['abstained']}"
        else:
            top = result["retrieved"][0]["id"] if result["retrieved"] else None
            ok = (top == case["expected_doc"]) and not result["abstained"] and case["expected_doc"] in result["citations"]
            detail = f"top={top} expected={case['expected_doc']}"
        print(f"{'PASS' if ok else 'FAIL'}: {case['question'][:60]} ({detail})")
        passed += ok
    print(f"{passed}/{len(cases)} cases passed")
    raise SystemExit(0 if passed == len(cases) else 1)

if __name__ == "__main__":
    main()
