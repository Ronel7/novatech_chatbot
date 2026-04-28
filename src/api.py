"""
API FastAPI — NovaTech RAG
Endpoints : /ask, /ingest, /stats, /health
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import shutil
import tempfile
from pathlib import Path

from src.retriever import NovaTechRAG, RAGResponse
from src.ingestor import ingest_documents
from src.config import DOCUMENTS_DIR

app = FastAPI(
    title="NovaTech RAG API",
    description="Chatbot RH multi-sources avec citations précises — NovaTech SAS",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singleton RAG (chargé une seule fois)
rag = NovaTechRAG()


# ─── Schémas ────────────────────────────────

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000,
                          example="Combien de jours de télétravail ont les cadres ?")

class SourceResponse(BaseModel):
    index: int
    source_file: str
    source_type: str
    excerpt: str
    relevance_score: float
    page: Optional[int] = None
    section: Optional[str] = None
    sheet_name: Optional[str] = None
    author: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    sources: List[SourceResponse]
    has_answer: bool
    confidence: str
    chunks_used: int
    query: str


# ─── Endpoints ──────────────────────────────

@app.get("/health")
def health():
    """Vérifie que l'API est opérationnelle."""
    return {"status": "ok", "model": "NovaTech RAG v1.0"}


@app.post("/ask", response_model=AskResponse)
def ask(request: QuestionRequest):
    """
    Pose une question au chatbot RAG.
    
    Retourne la réponse avec les sources citées, le score de confiance
    et les extraits des documents utilisés.
    """
    try:
        result: RAGResponse = rag.ask(request.question)
        return AskResponse(
            answer=result.answer,
            sources=[
                SourceResponse(
                    index=s.index,
                    source_file=s.source_file,
                    source_type=s.source_type,
                    excerpt=s.excerpt,
                    relevance_score=s.relevance_score,
                    page=s.page,
                    section=s.section,
                    sheet_name=s.sheet_name,
                    author=s.author,
                )
                for s in result.sources
            ],
            has_answer=result.has_answer,
            confidence=result.confidence,
            chunks_used=result.chunks_used,
            query=result.query,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")


@app.get("/stats")
def stats():
    """Statistiques de la base vectorielle."""
    try:
        return rag.get_collection_stats()
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/ingest")
def ingest(background_tasks: BackgroundTasks, reset: bool = False):
    """
    Déclenche l'ingestion des documents dans data/documents/.
    
    - reset=false : ingère uniquement les nouveaux fichiers
    - reset=true : vide la base et réingère tout
    """
    def run_ingest():
        ingest_documents(docs_dir=Path(DOCUMENTS_DIR), reset=reset)

    background_tasks.add_task(run_ingest)
    return {
        "status": "ingestion démarrée en arrière-plan",
        "reset": reset,
        "docs_dir": str(DOCUMENTS_DIR),
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload et ingère un document à la volée.
    Formats supportés : PDF, DOCX, XLSX, PNG, JPG, JSON, MD.
    """
    allowed = {".pdf", ".docx", ".xlsx", ".png", ".jpg", ".json", ".md", ".txt"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporté : {suffix}. Formats acceptés : {', '.join(allowed)}"
        )

    # Sauvegarde temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    # Copie vers le dossier documents avec le nom d'origine
    dest = Path(DOCUMENTS_DIR) / file.filename
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(tmp_path, dest)
    tmp_path.unlink()

    # Ingestion immédiate
    from src.ingestor import parse_file, chunk_documents, get_embeddings
    from langchain_chroma import Chroma

    docs = parse_file(dest)
    if not docs:
        raise HTTPException(status_code=422, detail="Impossible d'extraire du texte de ce fichier.")

    chunks = chunk_documents(docs)
    embeddings = get_embeddings()
    vs = Chroma(
        collection_name="novatech_rh",
        embedding_function=embeddings,
        persist_directory=str(Path("./chroma_db")),
    )
    texts = [c.page_content for c in chunks]
    metadatas = [c.metadata for c in chunks]
    ids = [c.metadata["chunk_id"] for c in chunks]
    vs.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks_created": len(chunks),
        "message": f"'{file.filename}' ingéré avec succès ({len(chunks)} chunks)."
    }

from fastapi.responses import StreamingResponse

@app.post("/ask-stream")
async def ask_stream(request: QuestionRequest):
    # On vérifie si la question est vide ou trop courte (politesse)
    # Si c'est une question normale, on lance le stream
    return StreamingResponse(
        rag.stream_ask(request.question),
        media_type="text/event-stream"
    )
