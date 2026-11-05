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
2. Retrieve the top passages with TF-IDF (`retrieve_top`), or with
   model embeddings (`EmbeddingRetriever`) when `RETRIEVER=embedding`
   is set. The default is TF-IDF until embedding wins the
   comparison in `eval/compare_retrieval.py` (see below).
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

`eval/cases.json` has 14 cases: 12 in-scope questions where
top-1 retrieval must match the expected document and the
citation must be present, and 2 out-of-scope questions that
must abstain with no citations. The corpus grew from 6 to 12
documents (2026-11-05): SwiftUI List performance, Xcode code
signing, App Store submission, Core Data migration, Swift 6
strict concurrency, and Xcode Instruments debugging.

```bash
python eval/compare_retrieval.py
python eval/run_heldout.py
```

`eval/compare_retrieval.py` compares TF-IDF with model
embeddings on the 12 original questions and 12 paraphrase
questions written before any embedding scores were seen.
Measured 2026-11-05 on a machine with a real key
(gemini-embedding-001): TF-IDF 12/12 original, 9/12
paraphrase; embedding 12/12 original, 12/12 paraphrase.
Embedding won under the win rule, so it is now the default
when a key is set (TF-IDF offline fallback without one).
The full numbers, including every per-query score, are in
`eval/retrieval_comparison.md`. One honest caveat: the
embedding abstain threshold is 0.61, set between the highest
out-of-scope score (0.6029, Android) and the lowest in-scope
score (0.6168, a SwiftData paraphrase), a gap of only 0.014,
so the threshold is fragile on new questions. `eval/run_heldout.py`
scores a separate held-out set of 14 questions (12 in-scope,
2 out-of-scope), never used for tuning. VM first run (TF-IDF):
11/14, with 3 misses that are genuine word-matching failures,
not bugs to tune away: cancelling a download, a local HTTP
address, and saving a record with @Query. Re-run the held-out
set with the embedding default after pushing, to see whether
embedding picks those 3 up.

## What is intentionally not here yet

- The corpus is a small sample of paraphrased summaries, not
  a full index of Apple documentation. Check the official docs
  for the full text; the corpus points at the topic, it does
  not reproduce it. It is now 12 documents, not 6.
- Retrieval defaults to model embeddings
  (`docs_rag_assistant/embeddings.py`, `EmbeddingRetriever`,
  gemini-embedding-001) when a key is set, with TF-IDF as the
  offline fallback without one. The switch was earned by the
  comparison above, not assumed. The embedding abstain
  threshold is 0.61, set from real out-of-scope scores; the
  separation is only 0.014, so treat it as fragile (see
  `eval/retrieval_comparison.md`).
- Document vectors are embedded once per process and reused
  for every question in the same run; only the query is
  embedded per question. Before this fix, every question
  re-embedded all 12 documents, and a 14-case eval run right
  after the comparison run hit the Gemini free-tier rate
  limit (HTTP 429, 2026-11-05). A 429 now produces a clear
  "wait a few minutes" error instead of a raw traceback, and
  the code never retries on its own.
- The held-out set exists (`eval/heldout_cases.json`,
  `eval/run_heldout.py`, 11/14 on the first TF-IDF run).
  It is kept separate from the 14 development cases.
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
