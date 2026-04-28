"""
Moteur RAG — Retrieval + Génération avec citations obligatoires.
Utilise Groq (Llama 3.1 70B) + ChromaDB + reranking par score.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Optional, Generator
from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import (
    GROQ_API_KEY, GROQ_MODEL, EMBEDDING_MODEL,
    CHROMA_PATH, CHROMA_COLLECTION,
    TOP_K_RETRIEVAL, TOP_K_FINAL, SIMILARITY_THRESHOLD,
)

# ─────────────────────────────────────────────
# Structures de données
# ─────────────────────────────────────────────

@dataclass
class Source:
    """Une source citée dans la réponse."""
    index: int
    source_file: str
    source_type: str
    chunk_context: str
    excerpt: str          # Extrait du chunk (100 premiers mots)
    relevance_score: float
    page: Optional[int] = None
    section: Optional[str] = None
    sheet_name: Optional[str] = None
    author: Optional[str] = None

    def format_label(self) -> str:
        """Étiquette courte pour affichage dans l'UI."""
        label = self.source_file
        if self.page:
            label += f", page {self.page}"
        elif self.section:
            label += f" — {self.section}"
        elif self.sheet_name:
            label += f" — feuille '{self.sheet_name}'"
        return label


@dataclass
class RAGResponse:
    """Réponse complète avec réponse textuelle et sources citées."""
    answer: str
    sources: List[Source] = field(default_factory=list)
    has_answer: bool = True
    confidence: str = "high"   # high / medium / low / none
    query: str = ""
    chunks_retrieved: int = 0
    chunks_used: int = 0


# ─────────────────────────────────────────────
# Prompt système
# ─────────────────────────────────────────────
SYSTEM_PROMPT = """Tu es l'assistant RH interne de NovaTech SAS. 

RÈGLES ABSOLUES :
1. Si l'utilisateur te salue ou fait des formules de politesse de base, réponds poliment en te présentant de manière concise (sans chercher dans les documents).
2. Pour toutes les questions informatives ou métiers, base-toi EXCLUSIVEMENT sur les documents fournis.
3. Pour CHAQUE information factuelle que tu donnes, tu dois citer la source avec ce format précis : [SOURCE_1], [SOURCE_2], etc.
4. Si l'information n'est pas dans le contexte, dis : "Je n'ai pas cette information dans les documents disponibles."
5. Sois précis et professionnel.

FORMAT DE RÉPONSE :
- Pas de blabla inutile.
- Langue : Français."""


def build_context(chunks: List[tuple[Document, float]]) -> str:
    """Construit le contexte textuel à injecter dans le prompt."""
    context_parts = []
    for i, (doc, score) in enumerate(chunks, 1):
        meta = doc.metadata
        label = meta.get("source", "document inconnu")
        ctx   = meta.get("chunk_context", "")
        if meta.get("page"):
            label += f" (page {meta['page']})"
        elif meta.get("section"):
            label += f" — section '{meta['section']}'"
        elif meta.get("sheet_name"):
            label += f" — feuille '{meta['sheet_name']}'"

        context_parts.append(
            f"[SOURCE_{i}] {label}\n"
            f"Contexte : {ctx}\n"
            f"Pertinence : {score:.2f}\n"
            f"---\n{doc.page_content}\n"
        )
    return "\n\n".join(context_parts)


# ─────────────────────────────────────────────
# Classe principale RAG
# ─────────────────────────────────────────────

class NovaTechRAG:
    """Pipeline RAG complet pour NovaTech SAS."""

    def __init__(self):
        self._embeddings = None
        self._vectorstore = None
        self._llm = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
        return self._embeddings

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            if not Path(CHROMA_PATH).exists():
                raise RuntimeError(
                    "❌ Base vectorielle introuvable. "
                    "Lancez d'abord : python ingest.py"
                )
            self._vectorstore = Chroma(
                collection_name=CHROMA_COLLECTION,
                embedding_function=self.embeddings,
                persist_directory=str(CHROMA_PATH),
            )
        return self._vectorstore

    @property
    def llm(self):
        if self._llm is None:
            if not GROQ_API_KEY:
                raise RuntimeError("❌ GROQ_API_KEY manquante.")
            self._llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model=GROQ_MODEL,
                temperature=0.1,
                max_tokens=2048,
            )
        return self._llm

    def retrieve(self, query: str) -> List[tuple[Document, float]]:
        """Récupère et filtre les chunks les plus pertinents."""
        results = self.vectorstore.similarity_search_with_relevance_scores(
            query, k=TOP_K_RETRIEVAL
        )
        filtered = [(d, s) for d, s in results if s >= SIMILARITY_THRESHOLD]
        reranked = sorted(
            filtered,
            key=lambda x: x[1] * (1 + min(len(x[0].page_content) / 2000, 0.2)),
            reverse=True
        )
        # Déduplication
        seen, deduped = set(), []
        for doc, score in reranked:
            key = f"{doc.metadata.get('source')}_{doc.metadata.get('page')}_{doc.metadata.get('section')}"
            if key not in seen:
                seen.add(key)
                deduped.append((doc, score))
        return deduped[:TOP_K_FINAL]

    def stream_ask(self, query: str) -> Generator[str, None, None]:
        """Générateur pour le streaming de la réponse dans l'interface."""
        chunks = self.retrieve(query)
        if not chunks:
            yield "Je n'ai trouvé aucun document pertinent pour répondre à cette question."
            return

        context = build_context(chunks)
        user_message = (
            f"Contexte documentaire ({len(chunks)} source(s)) :\n\n{context}\n\n"
            f"---\nQuestion : {query}\n\n"
            f"Rappel : cite les sources avec [SOURCE_1], [SOURCE_2]... pour chaque fait."
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_message),
        ]

        for chunk in self.llm.stream(messages):
            yield chunk.content

    def ask(self, query: str) -> RAGResponse:
        """Méthode synchrone pour obtenir la réponse complète et les objets sources."""
        query = query.strip()
        
        # Intercepteur politesse
        if query.lower() in ["bonjour", "salut", "hello", "coucou", "hey", "bonsoir"] or len(query) < 4:
            return RAGResponse(
                answer="Bonjour ! Je suis l'assistant RH de NovaTech. Comment puis-je vous aider ?",
                sources=[], confidence="high", query=query
            )

        chunks = self.retrieve(query)
        if not chunks:
            return RAGResponse(answer="Information non trouvée.", has_answer=False, confidence="none")

        # Génération complète
        context = build_context(chunks)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Contexte :\n{context}\n\nQuestion : {query}")
        ]
        response = self.llm.invoke(messages)
        answer = self.clean_citations(response.content)

        # Construction des sources
        sources = []
        for i, (doc, score) in enumerate(chunks, 1):
            excerpt = " ".join(doc.page_content.split()[:120]) + "..."
            sources.append(Source(
                index=i,
                source_file=doc.metadata.get("source", "inconnu"),
                source_type=doc.metadata.get("source_type", "inconnu"),
                chunk_context=doc.metadata.get("chunk_context", ""),
                excerpt=excerpt,
                relevance_score=round(score, 3),
                page=doc.metadata.get("page"),
                section=doc.metadata.get("section") or doc.metadata.get("json_key"),
                sheet_name=doc.metadata.get("sheet_name"),
                author=doc.metadata.get("author"),
            ))

        avg_score = sum(s.relevance_score for s in sources) / len(sources)
        confidence = "high" if avg_score >= 0.75 else "medium" if avg_score >= 0.55 else "low"
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            confidence=confidence,
            query=query,
            chunks_used=len(chunks)
        )

    def clean_citations(self, text: str) -> str:
        """Nettoie et formate les citations [SOURCE_X]."""
        text = re.sub(r'\s+\[', ' [', text)
        def replace_double_citations(match):
            nums = re.findall(r'\d+', match.group(0))
            unique_nums = sorted(list(set(nums)), key=int)
            return " [" + "], [".join(unique_nums) + "]"
        text = re.sub(r'(\s*\[\d+\](?:,\s*\[\d+\])*)', replace_double_citations, text)
        return text

    def get_collection_stats(self) -> dict:
        """Statistiques de la base vectorielle."""
        try:
            data = self.vectorstore.get(include=["metadatas"])
            metadatas = data["metadatas"]
            sources = {}
            for m in metadatas:
                s = m.get("source", "inconnu")
                sources[s] = sources.get(s, 0) + 1
            return {
                "total_chunks": len(metadatas),
                "total_documents": len(sources),
                "documents": sources,
            }
        except Exception as e:
            return {"error": str(e), "total_chunks": 0, "total_documents": 0}