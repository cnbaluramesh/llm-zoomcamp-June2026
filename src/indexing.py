"""Embed chunks with OpenAI and store vectors back into SQLite."""
import json
import sqlite3
import sys
from pathlib import Path

from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_PATH, EMBED_MODEL, OPENAI_API_KEY  # noqa: E402


def embed_texts(texts: list[str], batch: int = 512) -> list[list[float]]:
    client = OpenAI(api_key=OPENAI_API_KEY)
    vecs = []
    for i in range(0, len(texts), batch):
        resp = client.embeddings.create(input=texts[i : i + batch], model=EMBED_MODEL)
        vecs.extend([d.embedding for d in resp.data])
        print(f"embedded {min(i + batch, len(texts))}/{len(texts)}")
    return vecs


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT rowid, text FROM chunks").fetchall()
    texts = [r[1] for r in rows]
    print(f"embedding {len(texts)} chunks")
    vectors = embed_texts(texts)
    conn.execute("ALTER TABLE chunks ADD COLUMN embedding TEXT")
    for (rowid, _), vec in zip(rows, vectors):
        conn.execute("UPDATE chunks SET embedding = ? WHERE rowid = ?", (json.dumps(vec), rowid))
    conn.commit()
    conn.close()
    print("done")


if __name__ == "__main__":
    main()
