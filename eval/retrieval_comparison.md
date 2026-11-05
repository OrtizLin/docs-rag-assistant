# Retrieval comparison (measured 2026-11-05, on the user's machine with a real key)

Model: `gemini-embedding-001` via the Gemini OpenAI-compatible
endpoint (`https://generativelanguage.googleapis.com/v1beta/openai`).
Corpus: 12 documents. Original set: the 12 in-scope questions from
`eval/cases.json`. Paraphrase set: 12 rewordings written before any
embedding scores were seen, avoiding the documents' distinctive
keywords.

| Retriever | Original top-1 | Paraphrase top-1 |
| --- | --- | --- |
| TF-IDF | 12/12 | 9/12 |
| Embedding | 12/12 | 12/12 |

Verdict: embedding BEATS TF-IDF on paraphrases without losing on
originals -> switch default to embedding (after setting the
embedding abstain threshold from the out-of-scope scores below).

## Scores

TF-IDF original top scores: 0.4423, 0.4724, 0.4020, 0.2570, 0.2344,
0.4543, 0.2928, 0.9339, 0.3079, 0.6890, 0.6863, 0.3725 (all top-1
correct). TF-IDF paraphrase: 9/12 correct; the 3 misses were
cancelling a background job, storing objects in a local database,
and a code-signing identity failure.

Embedding original top scores: 0.8818, 0.8245, 0.8737, 0.8303,
0.8280, 0.9093, 0.8591, 0.8578, 0.7849, 0.8634, 0.9300, 0.8491
(lowest 0.7849). Embedding paraphrase top scores: 0.6966, 0.6427,
0.6713, 0.6343, 0.7029, 0.6168, 0.6943, 0.6839, 0.7479, 0.6609,
0.6919, 0.7041 (lowest 0.6168, a SwiftData paraphrase; all top-1
correct).

## Out-of-scope scores and the abstain threshold

| Retriever | Android (Jetpack Compose) | WPF (C#) |
| --- | --- | --- |
| TF-IDF | 0.0000 | 0.0000 |
| Embedding | 0.6029 | 0.5474 |

The embedding abstain threshold is set to **0.61**. It sits between
the highest out-of-scope score (0.6029) and the lowest in-scope
score (0.6168), but the gap is only **0.014**, so the threshold is
fragile: a new out-of-scope question could score above it, or a
new paraphrase below it. It works on the measured 26 questions;
it is not a robust separator. If abstention misfires on new
questions, the fix is a better separator, not quietly moving this
number to fit one question.
