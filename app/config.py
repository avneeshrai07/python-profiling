"""Central paths and tunables for the simulated RAG system."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
CACHE_DIR = DATA_DIR / "cache"
SQLITE_PATH = DATA_DIR / "metadata.db"

for _d in (DATA_DIR, PDF_DIR, CACHE_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# "Embedding model" (simulated) dimensions
FEATURE_DIM = int(os.getenv("FEATURE_DIM", 1024))
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 256))
PROJECTION_SEED = 42

# Chunking
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 400))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))

# Dummy corpus
DEFAULT_PDF_COUNT = int(os.getenv("DUMMY_PDF_COUNT", 12))
