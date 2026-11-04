from __future__ import annotations
import argparse, json
from pathlib import Path
from .agent import answer_question

def main():
    parser = argparse.ArgumentParser(description="Docs RAG assistant (cite, or say you don't know)")
    parser.add_argument("--question", required=True, help="Question about iOS / Swift / Xcode")
    parser.add_argument("--corpus-dir", default="docs/corpus", help="Corpus directory")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true", default=True, help="Retrieved passages only, offline")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Use the LLM path")
    parser.add_argument("--out-json", default="")
    args = parser.parse_args()
    try:
        result = answer_question(args.question, args.corpus_dir, top_k=args.top_k, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)
    print(f"Question: {result['question']}\n")
    print(result["answer"])
    print(f"\nCitations: {result['citations'] if result['citations'] else 'none (abstained)' }")
    if args.out_json:
        Path(args.out_json).write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\nWrote {args.out_json}")

if __name__ == "__main__":
    main()
