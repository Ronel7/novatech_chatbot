# NovaTech RAG — Chatbot RH Multi-Sources

Chatbot RAG (Retrieval-Augmented Generation) précis avec citations, pour les documents RH de NovaTech SAS.

## Stack technique
- **Backend** : Python + FastAPI
- **RAG framework** : LangChain
- **LLM** : Groq API (Llama 3.1 70B) — gratuit
- **Embeddings** : sentence-transformers (local, gratuit)
- **Base vectorielle** : ChromaDB (local)
- **OCR** : pytesseract (images scannées)
- **Interface** : Streamlit

## Structure
```
novatech_rag/
├── data/                    #  Les documents ici
├── src/
│   ├── config.py            # Configuration centralisée
│   ├── ingestor.py          # Pipeline d'ingestion multi-formats
│   ├── retriever.py         # Moteur RAG + citations
│   └── api.py               # API FastAPI
├── app.py                   # Interface Streamlit
├── ingest.py                # Script d'ingestion CLI
├── requirements.txt
└── .env.example
```

## Installation
```bash
pip install -r requirements.txt

# Installer tesseract (OCR)
# Ubuntu/Debian :
sudo apt-get install tesseract-ocr tesseract-ocr-fra

# macOS :
brew install tesseract tesseract-lang
```

## Configuration
```bash
cp .env.example .env
# Éditez .env et ajoutez votre clé Groq
# Inscription gratuite : https://console.groq.com
```

## Utilisation

### 1. Ingestion des documents
```bash
# Déposez vos fichiers dans data/
# Puis lancez l'ingestion :
python ingest.py

# Ou avec un dossier personnalisé :
python ingest.py --docs_dir /chemin/vers/documents
```

### 2. Lancer l'API (optionnel)
```bash
uvicorn src.api:app --reload --port 8000
# Swagger UI : http://localhost:8000/docs
```

### 3. Lancer l'interface Streamlit
```bash
streamlit run app.py
```

## Formats supportés
| Format | Méthode | Métadonnées extraites |
|--------|---------|----------------------|
| PDF | pdfplumber | Titre, auteur, pages, date |
| Word (.docx) | python-docx | Titre, auteur, sections |
| Excel (.xlsx) | openpyxl | Nom feuille, ligne, colonne |
| Images scannées (.png/.jpg) | pytesseract OCR | Nom fichier, résolution |
| JSON | json natif | Clés racine, profondeur |
| Markdown (.md) | markdown natif | Titres H1/H2, source |

## Exemple de réponse avec citations
```
Q : Combien de jours de télétravail ont les cadres ?

R : Les cadres au forfait 218 jours ont droit à 3 jours de télétravail 
par semaine maximum.

📎 Sources :
[1] charte_teletravail.docx — Article 3.1, p.2
    "Cadres (forfait 218j) : 3 jours de télétravail par semaine maximum"
    Score de pertinence : 0.94

[2] sharepoint_faq_rh.md — Section "Télétravail"  
    "Cadres (forfait 218j) : 3 jours/semaine maximum"
    Score de pertinence : 0.91
```
