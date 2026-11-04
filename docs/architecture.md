# Architecture

```
CLI
  -> corpus.py (load Markdown topics)
  -> retrieval.py (TF-IDF, retrieve_top)
  -> agent.py: retrieve -> dry-run passages | LLM draft -> validate citations
  -> answer + citations, or a clear abstention
```

Design choices, and why:

- Retrieval happens before any generation. The model never answers
  from memory alone about a doc topic.
- Citations are validated against the retrieved set. A citation to
  a document that was not retrieved is dropped, and an answer with
  no valid citation becomes an abstention.
- Abstention is measured, not hidden. The eval set includes
  out-of-scope questions that must abstain.
- The corpus is small and paraphrased on purpose. A sample that
  claims to index all of Apple documentation would be dishonest;
  this sample proves the loop, the citations, and the abstention,
  and the same loop scales by adding more corpus files.

Planned next steps:

1. Replace TF-IDF with embeddings; compare on eval/run_eval.py
   before switching.
2. Keep a held-out eval set separate from the development set.
3. Add a larger, licensed or officially linked corpus, with
   per-document source URLs.
