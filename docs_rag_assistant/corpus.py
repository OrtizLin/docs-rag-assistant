"""Load the indexed corpus: one Markdown file per topic.
Each file starts with a Title: line and a Source: line, then a short
original summary written for this project. The corpus is NOT a copy
of Apple documentation: it paraphrases the topic in our own words
and points at the official docs for the full text. That keeps the
sample small, checkable, and safe to publish.
"""
from __future__ import annotations
from pathlib import Path

def load_corpus(corpus_dir):
    docs = []
    for path in sorted(Path(corpus_dir).glob("*.md")):
        text = path.read_text()
        title, source, body = path.stem, "", text
        lines = text.splitlines()
        if lines and lines[0].startswith("Title:"):
            title = lines[0][6:].strip()
        if len(lines) > 1 and lines[1].startswith("Source:"):
            source = lines[1][7:].strip()
            body = "\n".join(lines[2:]).strip()
        docs.append({"id": path.stem, "title": title, "source": source, "text": body, "path": str(path)})
    return docs
