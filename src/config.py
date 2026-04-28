"""Configuration centralisée — chargée depuis .env"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Chemins
BASE_DIR      = Path(__file__).parent.parent
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", BASE_DIR / "data"))
CHROMA_PATH   = Path(os.getenv("CHROMA_DB_PATH", BASE_DIR / "chroma_db"))

# LLM
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Embeddings
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")

# ChromaDB
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "novatech_rh")

# Chunking
CHUNK_SIZE    = int(os.getenv("CHUNK_SIZE", 900))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))

# Retrieval
TOP_K_RETRIEVAL      = int(os.getenv("TOP_K_RETRIEVAL", 8))
TOP_K_FINAL          = int(os.getenv("TOP_K_FINAL", 4))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.35))

# API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))

# Extensions supportées
SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".xlsx", ".xls",
    ".png", ".jpg", ".jpeg", ".tiff",
    ".json", ".md", ".txt"
}
