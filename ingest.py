"""
Script CLI d'ingestion des documents.
Usage : python ingest.py [--docs_dir chemin] [--reset]
"""
import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Ingestion des documents NovaTech dans ChromaDB"
    )
    parser.add_argument(
        "--docs_dir",
        type=str,
        default="data/",
        help="Dossier contenant les documents à ingérer (défaut: data/documents)"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Vide la base vectorielle avant d'ingérer (ré-indexation complète)"
    )
    args = parser.parse_args()

    docs_dir = Path(args.docs_dir)
    if not docs_dir.exists():
        print(f"❌ Dossier introuvable : {docs_dir}")
        sys.exit(1)

    print("=" * 55)
    print("   NovaTech RAG — Pipeline d'ingestion")
    print("=" * 55)
    if args.reset:
        print("⚠️  Mode RESET activé — la base sera vidée\n")

    from src.ingestor import ingest_documents
    stats = ingest_documents(docs_dir=docs_dir, reset=args.reset)

    print("\n" + "=" * 55)
    print("📊 Résumé de l'ingestion :")
    print(f"   Fichiers trouvés    : {stats['files_found']}")
    print(f"   Fichiers traités    : {stats['files_ok']}")
    print(f"   Fichiers ignorés    : {stats['skipped']} (déjà indexés)")
    print(f"   Fichiers en erreur  : {stats['files_error']}")
    print(f"   Chunks créés        : {stats['chunks_total']}")
    print("=" * 55)
    print("\n✅ Prêt. Lancez : streamlit run app.py\n")

if __name__ == "__main__":
    main()
