"""Split article text into overlapping word-based chunks."""
from config import CHUNK_OVERLAP, CHUNK_TOKENS


def chunk_words(text: str, size: int = CHUNK_TOKENS, overlap: int = CHUNK_OVERLAP) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(1, size - overlap)
    return [" ".join(words[i : i + size]) for i in range(0, len(words), step)]


def chunk_article(article: dict) -> list[dict]:
    chunks = chunk_words(article["text"])
    out = []
    for i, text in enumerate(chunks):
        if len(text.split()) < 30:
            continue
        out.append(
            {
                "doc_title": article["title"],
                "url": article["url"],
                "chunk_id": i,
                "text": text,
            }
        )
    return out
