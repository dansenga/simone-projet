"""
API FastAPI améliorée avec support WebSocket pour la traduction en temps réel.

Fonctionnalités :
- WebSocket pour streaming audio bidirectionnel
- Endpoints REST pour traduction classique
- Interface web moderne servie statiquement
- Support multilingue (FR ↔ EN)

Projet académique et professionnel - SIMONE v2.0
"""

import asyncio
import base64
import json
import logging
import os
import uuid
from typing import Optional, List

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.translation import translate_text, translate_text_custom
from backend.realtime import get_translator, remove_translator, RealtimeTranslator
from backend import storage

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application FastAPI
app = FastAPI(
    title="SIMONE - Traduction en Temps Réel",
    description="Application de traduction vocale en temps réel avec IA",
    version="2.0.0"
)

# CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques du frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ============== Modèles Pydantic ==============

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "fr"
    target_lang: str = "en"


class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str


class HistoryItem(BaseModel):
    id: int
    audio_path: str
    timestamp: str
    detected_lang: Optional[str] = None
    has_docx: bool
    has_pdf: bool


# ============== Endpoints REST ==============

@app.get("/")
async def root():
    """Page principale - Interface de traduction en temps réel."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>SIMONE - Traduction en Temps Réel</h1><p>Frontend non trouvé.</p>")


@app.get("/health")
async def health_check():
    """Vérification de l'état du serveur."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "features": ["realtime", "websocket", "translation", "transcription"]
    }


@app.post("/api/translate", response_model=TranslateResponse)
async def translate_text_endpoint(request: TranslateRequest):
    """Traduit un texte de la langue source vers la langue cible."""
    try:
        translated = translate_text(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        return TranslateResponse(
            original_text=request.text,
            translated_text=translated,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        logger.exception("Erreur de traduction")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/history", response_model=List[HistoryItem])
async def get_history():
    """Récupère l'historique des traductions."""
    try:
        rows = storage.get_all()
        items = []
        for row in rows:
            id_, audio_path, timestamp, detected_lang, _, _, docx_path, pdf_path = row
            items.append(HistoryItem(
                id=id_,
                audio_path=audio_path or "",
                timestamp=str(timestamp),
                detected_lang=detected_lang,
                has_docx=bool(docx_path),
                has_pdf=bool(pdf_path)
            ))
        return items
    except Exception as e:
        logger.exception("Erreur lecture historique")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/languages")
async def get_supported_languages():
    """Retourne les langues supportées pour la traduction."""
    return {
        "languages": [
            {"code": "fr", "name": "Français", "flag": "🇫🇷"},
            {"code": "en", "name": "English", "flag": "🇬🇧"},
            {"code": "es", "name": "Español", "flag": "🇪🇸"},
            {"code": "de", "name": "Deutsch", "flag": "🇩🇪"},
            {"code": "it", "name": "Italiano", "flag": "🇮🇹"},
            {"code": "pt", "name": "Português", "flag": "🇵🇹"},
            {"code": "nl", "name": "Nederlands", "flag": "🇳🇱"},
            {"code": "ru", "name": "Русский", "flag": "🇷🇺"},
            {"code": "zh", "name": "中文", "flag": "🇨🇳"},
            {"code": "ja", "name": "日本語", "flag": "🇯🇵"},
            {"code": "ar", "name": "العربية", "flag": "🇸🇦"},
        ]
    }


# ============== WebSocket pour Temps Réel ==============

class ConnectionManager:
    """Gestionnaire de connexions WebSocket."""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Client connecté: {session_id}")
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        remove_translator(session_id)
        logger.info(f"Client déconnecté: {session_id}")
    
    async def send_json(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)


manager = ConnectionManager()


@app.websocket("/ws/realtime/{session_id}")
async def websocket_realtime(websocket: WebSocket, session_id: str):
    """WebSocket pour la traduction en temps réel.
    
    Protocole:
    - Client envoie: {"type": "audio", "data": "<base64>", "source": "fr", "target": "en"}
    - Client envoie: {"type": "config", "source": "fr", "target": "en"}
    - Client envoie: {"type": "stop"} pour arrêter et obtenir le résultat final
    - Serveur répond: {"type": "result", "transcription": "...", "translation": "..."}
    - Serveur répond: {"type": "status", "message": "..."}
    - Serveur répond: {"type": "error", "message": "..."}
    """
    await manager.connect(websocket, session_id)
    
    # Créer un traducteur pour cette session
    translator = get_translator(session_id)
    
    try:
        while True:
            # Recevoir les données du client
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "")
            
            if msg_type == "config":
                # Configuration des langues
                source = message.get("source", "fr")
                target = message.get("target", "en")
                translator.set_languages(source, target)
                await manager.send_json(session_id, {
                    "type": "status",
                    "message": f"Configuration: {source} → {target}"
                })
                
            elif msg_type == "audio":
                # Réception d'un chunk audio
                audio_b64 = message.get("data", "")
                source = message.get("source", translator.source_lang)
                target = message.get("target", translator.target_lang)
                
                # Mettre à jour les langues si nécessaire
                translator.set_languages(source, target)
                
                # Décoder et ajouter au buffer
                try:
                    audio_bytes = base64.b64decode(audio_b64)
                    translator.add_audio_chunk(audio_bytes)
                except Exception as e:
                    logger.error(f"Erreur décodage audio: {e}")
                    
            elif msg_type == "process":
                # Traiter le buffer audio actuel
                await manager.send_json(session_id, {
                    "type": "status",
                    "message": "Traitement en cours..."
                })
                
                result = await translator.process_audio()
                
                if result and "error" not in result:
                    await manager.send_json(session_id, {
                        "type": "result",
                        "transcription": result["transcription"],
                        "translation": result["translation"],
                        "source_lang": result["source_lang"],
                        "target_lang": result["target_lang"]
                    })
                    # Vider le buffer après traitement réussi
                    translator.clear_buffer()
                elif result and "error" in result:
                    await manager.send_json(session_id, {
                        "type": "error",
                        "message": result["error"]
                    })
                else:
                    await manager.send_json(session_id, {
                        "type": "status",
                        "message": "Pas assez d'audio (minimum 2 secondes)"
                    })
                    
            elif msg_type == "stop":
                # Arrêter l'enregistrement et traiter
                result = await translator.process_audio()
                
                if result and "error" not in result:
                    await manager.send_json(session_id, {
                        "type": "final",
                        "transcription": result["transcription"],
                        "translation": result["translation"],
                        "source_lang": result["source_lang"],
                        "target_lang": result["target_lang"]
                    })
                
                translator.clear_buffer()
                
            elif msg_type == "clear":
                # Vider le buffer
                translator.clear_buffer()
                await manager.send_json(session_id, {
                    "type": "status",
                    "message": "Buffer vidé"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.exception(f"Erreur WebSocket: {e}")
        manager.disconnect(session_id)


# ============== Point d'entrée ==============

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Démarrage du serveur SIMONE sur le port {port}")
    
    uvicorn.run(
        "api_v2:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
