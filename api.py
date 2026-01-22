"""Petit serveur FastAPI pour exposer les fonctions de traduction du backend.

- /health : vérification simple
- /translate/standard : utilise les modèles Marian pré-entraînés (backend.translation.translate_text)
- /translate/custom : utilise un modèle finetuné sauvegardé dans un dossier

Ce fichier ne remplace pas app.py (CLI), il offre juste une API web
que ton interface pourra appeler.
"""

import logging
import os
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.translation import translate_text, translate_text_custom
from backend import storage


logging.basicConfig(level=logging.INFO)

app = FastAPI(title="SIMONE Translation API", version="1.0.0")

# Servir les fichiers statiques du frontend (HTML/CSS/JS)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class StandardTranslateRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


class CustomTranslateRequest(BaseModel):
    text: str
    model_dir: Optional[str] = None  # peut être omis si env CUSTOM_TRANSLATION_MODEL_DIR défini


class TranslateResponse(BaseModel):
    translated_text: str


class HistoryItem(BaseModel):
    id: int
    audio_path: str
    timestamp: str
    detected_lang: Optional[str] = None
    has_docx: bool
    has_pdf: bool


class HistoryDetail(BaseModel):
    id: int
    audio_path: str
    timestamp: str
    detected_lang: Optional[str] = None
    original_text: str
    translated_text: str
    docx_path: Optional[str] = None
    pdf_path: Optional[str] = None


@app.get("/health")
def health_check():
    """Endpoint de santé très simple."""

    return {"status": "ok"}


@app.get("/")
def root():
    """Renvoie la page principale du tableau de bord (frontend)."""

    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        return {"message": "Frontend non trouvé. Vérifiez le dossier 'frontend'."}
    return FileResponse(index_path)


@app.get("/history", response_model=List[HistoryItem])
def list_history():
    """Retourne une liste des transcriptions déjà réalisées.

    Utilisé par l'onglet "Historique" de l'interface.
    """

    try:
        rows = storage.get_all()
    except Exception as exc:  # pragma: no cover
        logging.exception("Erreur lors de la lecture de l'historique")
        raise HTTPException(status_code=500, detail=str(exc))

    items: List[HistoryItem] = []
    for row in rows:
        (
            id_,
            audio_path,
            timestamp,
            detected_lang,
            original_text,
            translated_text,
            docx_path,
            pdf_path,
        ) = row
        items.append(
            HistoryItem(
                id=id_,
                audio_path=audio_path,
                timestamp=str(timestamp),
                detected_lang=detected_lang,
                has_docx=bool(docx_path),
                has_pdf=bool(pdf_path),
            )
        )
    return items


@app.get("/history/{record_id}", response_model=HistoryDetail)
def get_history_item(record_id: int):
    """Détail complet d'une entrée d'historique (texte original + traduit)."""

    try:
        rec = storage.get_by_id(record_id)
    except Exception as exc:  # pragma: no cover
        logging.exception("Erreur lors de la lecture de l'élément d'historique")
        raise HTTPException(status_code=500, detail=str(exc))

    if rec is None:
        raise HTTPException(status_code=404, detail="Enregistrement non trouvé")

    return HistoryDetail(**rec)


@app.post("/translate/standard", response_model=TranslateResponse)
def translate_standard(payload: StandardTranslateRequest):
    """Traduction standard via les modèles Marian pré-entraînés."""

    try:
        translated = translate_text(
            text=payload.text,
            source_lang=payload.source_lang,
            target_lang=payload.target_lang,
        )
        return TranslateResponse(translated_text=translated)
    except Exception as exc:  # pragma: no cover - gestion d'erreurs générique
        logging.exception("Erreur pendant la traduction standard")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/translate/custom", response_model=TranslateResponse)
def translate_custom(payload: CustomTranslateRequest):
    """Traduction via ton modèle finetuné (dossier de modèle personnalisé).

    - Si `model_dir` est fourni dans le body, on l'utilise.
    - Sinon, on lit la variable d'environnement CUSTOM_TRANSLATION_MODEL_DIR.
    """

    try:
        translated = translate_text_custom(text=payload.text, model_dir=payload.model_dir)
        return TranslateResponse(translated_text=translated)
    except ValueError as ve:
        # Erreur de configuration (pas de chemin de modèle)
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:  # pragma: no cover
        logging.exception("Erreur pendant la traduction personnalisée")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/export/{record_id}")
def export_record(record_id: int, format: str = "pdf"):
    """Permet de télécharger un export DOCX ou PDF pour un enregistrement.

    - format=pdf ou docx
    - Si le fichier n'existe pas encore, on échoue pour l'instant (la pipeline le crée normalement).
    """

    rec = storage.get_by_id(record_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Enregistrement non trouvé")

    fmt = format.lower()
    if fmt == "pdf":
        path = rec.get("pdf_path")
    elif fmt == "docx":
        path = rec.get("docx_path")
    else:
        raise HTTPException(status_code=400, detail="Format non supporté (utiliser 'pdf' ou 'docx')")

    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Fichier d'export introuvable pour ce format")

    filename = os.path.basename(path)
    return FileResponse(path, filename=filename)


if __name__ == "__main__":
    # Lancement direct : python api.py
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
