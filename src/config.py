"""Shared configuration for SpaceQuest RAG."""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
CORPUS_DIR = DATA_DIR / "corpus"
INDEX_DIR = DATA_DIR / "index"
EVAL_DIR = DATA_DIR / "eval"
LOGS_DIR = PROJECT_ROOT / "logs"
# dlt's sqlalchemy destination appends the dataset name to the SQLite filename
DB_PATH = DATA_DIR / "knowledge_base__kb.db"

load_dotenv(PROJECT_ROOT / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHUNK_TOKENS = 300
CHUNK_OVERLAP = 50
TOP_K = 5
RRF_K = 60

TOPICS = [
    "Apollo program",
    "Space Shuttle",
    "International Space Station",
    "Hubble Space Telescope",
    "James Webb Space Telescope",
    "Mars rover",
    "Perseverance (rover)",
    "Curiosity (rover)",
    "Voyager program",
    "Cassini–Huygens",
    "New Horizons",
    "Artemis program",
    "SpaceX Dragon 2",
    "Falcon 9",
    "Starship (spacecraft)",
    "Soyuz (spacecraft)",
    "Lunar Gateway",
    "Space telescope",
    "Extravehicular activity",
    "Space suit",
    "Kennedy Space Center",
    "Baikonur Cosmodrome",
    "Sputnik 1",
    "Vostok 1",
    "Mercury-Redstone 3",
    "Gemini program",
    "Skylab",
    "Mir",
    "Boeing Starliner",
    "Dragon (spacecraft)",
]
