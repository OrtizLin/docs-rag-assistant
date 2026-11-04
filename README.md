# Docs RAG Assistant

A developer-docs RAG assistant for iOS / Swift / Xcode questions.
It retrieves passages first, answers with citations, and says
"I don't know" when the indexed docs do not answer the question.

This is portfolio project 2 for a Senior AI Agent Development
Engineer role, and a deliberate contrast to Project 1
(PR Review Agent): Project 1 reviews code, this one answers
questions from documents. Both share the same discipline —
retrieve first, validate the output, measure it — but the
retrieval target, the output shape, and the failure mode
(abstention, not a fake citation) are different.

## What it does

1. Load a small corpus of Markdown topics in `docs/corpus/`.
2. Retrieve the top passages with TF-IDF (`retrieve_top`).
3. If the best score is below threshold, abstain clearly
   instead of guessing.
4. In dry-run mode, return the retrieved passages with citations.
5. In LLM mode, ask the model to answer ONLY from those passages,
   then re-validate every citation against the retrieved set.
   An answer with no valid citation becomes an abstention.
6. Never cite a document that was not retrieved.

## Quick start (no API key needed)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m docs_rag_assistant.cli --question "What is @State and @Binding in SwiftUI?"
python -m docs_rag_assistant.cli --question "How do I build an Android app with Jetpack Compose?"
```

The second question must abstain: it is out of scope for this
iOS / Swift corpus, and a confident Android answer would be
a hallucination, not helpfulness.

```bash
# LLM path, key in your shell only, never in chat or a committed file:
export LLM_API_KEY="..."
export LLM_MODEL="gpt-4o-mini"  # or a model you actually have access to
python -m docs_rag_assistant.cli --question "How does Task cancellation work in Swift concurrency?" --no-dry-run
```

For a Google AI Studio key, set `LLM_BASE_URL` to the Gemini
OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai`)
and `LLM_MODEL` to a model available to that key.

## Evaluation, not just a demo

```bash
python eval/run_eval.py
python -m pytest -q
```

`eval/cases.json` has 8 cases: 6 in-scope questions where
top-1 retrieval must match the expected document and the
citation must be present, and 2 out-of-scope questions that
must abstain with no citations.

## What is intentionally not here yet

- The corpus is a small sample of paraphrased summaries, not
  a full index of Apple documentation. Check the official docs
  for the full text; the corpus points at the topic, it does
  not reproduce it.
- Retrieval is local TF-IDF, not a model embedding yet.
  The interface (`retrieve_top`) is what an embedding would
  replace, with this same eval to beat.
- No held-out eval set yet. The 8 cases are the development
  set; keep a separate held-out set before claiming a general
  accuracy number.
- No auto-publishing, no user data collection, no chat history
  stored by this tool.

## Mapping to the target role

| Role requirement | Evidence in this repo |
| --- | --- |
| RAG | Corpus loading, TF-IDF retrieval, citation validation |
| LLM applications | OpenAI-compatible boundary, JSON parsing, re-validation |
| Prompt engineering | Versioned system prompt, answer-only-from-passages rule |
| Tool calling / workflow | CLI, retrieval as a tool step before generation |
| Developer productivity | Answers iOS / Swift / Xcode questions a developer actually asks |
| Coding / testing / CI | Tests, eval, GitHub Actions |
