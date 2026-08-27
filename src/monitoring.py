"""Query + feedback logging into SQLite for monitoring."""
import json
import sqlite3
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import DB_PATH  # noqa: E402


def _init(conn: sqlite3.Connection) -> None:
    conn.execute(
        """CREATE TABLE IF NOT EXISTS query_log (
            id TEXT PRIMARY KEY,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            question TEXT,
            rewritten_question TEXT,
            method TEXT,
            answer TEXT,
            latency_s REAL,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            sources TEXT
        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP,
            query_id TEXT,
            rating INTEGER
        )"""
    )
    conn.commit()


def log_query(
    question: str,
    rewritten: str,
    method: str,
    answer: str,
    latency_s: float,
    prompt_tokens: int,
    completion_tokens: int,
    sources: list[dict],
) -> str:
    query_id = uuid.uuid4().hex
    conn = sqlite3.connect(DB_PATH)
    _init(conn)
    conn.execute(
        "INSERT INTO query_log (id, question, rewritten_question, method, answer, latency_s, prompt_tokens, completion_tokens, sources) VALUES (?,?,?,?,?,?,?,?,?)",
        (query_id, question, rewritten, method, answer, latency_s, prompt_tokens, completion_tokens, json.dumps(sources)),
    )
    conn.commit()
    conn.close()
    return query_id


def log_feedback(query_id: str, rating: int) -> None:
    conn = sqlite3.connect(DB_PATH)
    _init(conn)
    conn.execute("INSERT INTO feedback (id, query_id, rating) VALUES (?,?,?)", (uuid.uuid4().hex, query_id, rating))
    conn.commit()
    conn.close()
