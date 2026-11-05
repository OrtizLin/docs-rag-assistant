"""Score the held-out set (eval/heldout_cases.json).
Same scoring as eval/run_eval.py: top-1 must match expected_doc
for in-scope questions, abstention for out-of-scope ones.
Held-out rules (same as Project 1): these cases were written
after the development set and were never used for tuning. Run
once and report as-is; do not change code, rules, or prompts to
make a failing held-out case pass, and do not merge held-out
cases into the development set, or the held-out score stops
meaning anything. This score is separate from the 14/14
development score.
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from docs_rag_assistant.agent import answer_question

def main():
    root = Path(__file__).resolve().parent.parent
    cases = json.loads((root / "eval" / "heldout_cases.json").read_text())
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
    print(f"Held-out: {passed}/{len(cases)} (separate from the development score)")
    raise SystemExit(0 if passed == len(cases) else 1)

if __name__ == "__main__":
    main()
