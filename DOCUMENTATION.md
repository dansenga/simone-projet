# 📚 SIMONE v2.0 - Documentation Complète

## Application de Traduction Vocale en Temps Réel avec Intelligence Artificielle

---

# 📑 Table des Matières

1. [Introduction](#1-introduction)
2. [Architecture du Projet](#2-architecture-du-projet)
3. [Technologies Utilisées](#3-technologies-utilisées)
4. [Installation et Configuration](#4-installation-et-configuration)
5. [Structure des Fichiers](#5-structure-des-fichiers)
6. [Backend - Explication du Code](#6-backend---explication-du-code)
7. [Frontend - Explication du Code](#7-frontend---explication-du-code)
8. [API REST et WebSocket](#8-api-rest-et-websocket)
9. [Flux de Données](#9-flux-de-données)
10. [Guide d'Utilisation](#10-guide-dutilisation)
11. [Dépannage](#11-dépannage)
12. [Améliorations Futures](#12-améliorations-futures)
13. [Références](#13-références)

---

# 1. Introduction

## 1.1 Qu'est-ce que SIMONE ?

**SIMONE** (Système Intelligent de Médiation et d'Optimisation pour la Navigation et l'Échange) est une application web de traduction vocale en temps réel. Elle permet de :

- 🎤 **Parler** dans une langue (ex: Français)
- 📝 **Transcrire** automatiquement la parole en texte
- 🌍 **Traduire** le texte dans une autre langue (ex: Anglais)
- 🔊 **Écouter** la traduction via synthèse vocale

## 1.2 Cas d'Utilisation

| Contexte | Description |
|----------|-------------|
| **Académique** | Projet de fin d'études en IA/NLP |
| **Professionnel** | Communication multilingue en entreprise |
| **Voyage** | Traduction instantanée lors de déplacements |
| **Accessibilité** | Aide à la communication pour malentendants |

## 1.3 Fonctionnalités Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    SIMONE v2.0                               │
├─────────────────────────────────────────────────────────────┤
│  ✅ Traduction vocale en temps réel                         │
│  ✅ Support multilingue (FR, EN, ES, DE, IT, PT)            │
│  ✅ Interface web moderne et responsive                      │
│  ✅ WebSocket pour communication bidirectionnelle            │
│  ✅ Synthèse vocale (Text-to-Speech)                         │
│  ✅ Historique des traductions                               │
│  ✅ Export PDF/DOCX                                          │
│  ✅ Mode texte manuel                                        │
└─────────────────────────────────────────────────────────────┘
```

---

# 2. Architecture du Projet

## 2.1 Vue d'Ensemble

```
┌──────────────────────────────────────────────────────────────────┐
│                         NAVIGATEUR WEB                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐   │
│  │  index.html │  │   app.js    │  │      styles.css         │   │
│  │  (Structure)│  │  (Logique)  │  │      (Design)           │   │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘   │
│         │                │                                        │
│         └────────────────┼────────────────────────────────────   │
│                          │                                        │
│                   Web Audio API                                   │
│                   (Capture Micro)                                 │
│                          │                                        │
└──────────────────────────┼────────────────────────────────────────┘
                           │
                    WebSocket / HTTP
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                      SERVEUR PYTHON                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                      api_v2.py                               │ │
│  │                   (FastAPI + WebSocket)                      │ │
│  └─────────────────────────┬───────────────────────────────────┘ │
│                            │                                      │
│  ┌─────────────────────────┴───────────────────────────────────┐ │
│  │                        backend/                              │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │ │
│  │  │ realtime.py  │  │speech_to_text│  │  translation.py  │   │ │
│  │  │ (WebSocket)  │  │   (Whisper)  │  │    (Marian)      │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │ │
│  │  │  storage.py  │  │  export.py   │  │   pipeline.py    │   │ │
│  │  │  (SQLite)    │  │ (PDF/DOCX)   │  │ (Orchestration)  │   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────┐
│                     MODÈLES D'IA                                  │
│  ┌───────────────────────┐  ┌────────────────────────────────┐   │
│  │   OpenAI Whisper      │  │   Helsinki-NLP Marian          │   │
│  │   (Transcription)     │  │   (Traduction)                 │   │
│  │   Voix → Texte        │  │   Texte → Texte traduit        │   │
│  └───────────────────────┘  └────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

## 2.2 Communication Client-Serveur

```
┌─────────────┐                              ┌─────────────┐
│   Client    │                              │   Serveur   │
│  (Browser)  │                              │  (Python)   │
└──────┬──────┘                              └──────┬──────┘
       │                                            │
       │  1. Connexion WebSocket                    │
       │ ────────────────────────────────────────▶  │
       │                                            │
       │  2. Configuration langues {fr → en}        │
       │ ────────────────────────────────────────▶  │
       │                                            │
       │  3. Envoi chunks audio (base64)            │
       │ ────────────────────────────────────────▶  │
       │ ────────────────────────────────────────▶  │
       │ ────────────────────────────────────────▶  │
       │                                            │
       │  4. Demande de traitement                  │
       │ ────────────────────────────────────────▶  │
       │                                            │
       │                    ┌───────────────────────┤
       │                    │ 5. Whisper transcrit  │
       │                    │ 6. Marian traduit     │
       │                    └───────────────────────┤
       │                                            │
       │  7. Résultat {transcription, traduction}   │
       │ ◀────────────────────────────────────────  │
       │                                            │
```

---

# 3. Technologies Utilisées

## 3.1 Backend (Python)

| Technologie | Version | Rôle |
|-------------|---------|------|
| **Python** | 3.10+ | Langage de programmation principal |
| **FastAPI** | 0.110+ | Framework web asynchrone |
| **Uvicorn** | 0.29+ | Serveur ASGI haute performance |
| **OpenAI Whisper** | 20231117+ | Modèle de transcription audio |
| **Transformers** | 4.31+ | Bibliothèque Hugging Face pour les modèles |
| **PyTorch** | 2.0+ | Framework de deep learning |
| **SQLite** | 3.x | Base de données légère |

## 3.2 Frontend (Web)

| Technologie | Rôle |
|-------------|------|
| **HTML5** | Structure de la page |
| **CSS3** | Design et animations |
| **JavaScript ES6+** | Logique interactive |
| **Web Audio API** | Capture du microphone |
| **WebSocket API** | Communication temps réel |
| **Web Speech API** | Synthèse vocale (TTS) |

## 3.3 Modèles d'Intelligence Artificielle

### Whisper (OpenAI)

```
┌────────────────────────────────────────────────────────────┐
│                      WHISPER                                │
├────────────────────────────────────────────────────────────┤
│  Type: Automatic Speech Recognition (ASR)                   │
│  Entrée: Audio (WAV, MP3, FLAC, etc.)                      │
│  Sortie: Texte transcrit + langue détectée                 │
│  Modèles: tiny, base, small, medium, large                 │
│  Langues: 99 langues supportées                            │
└────────────────────────────────────────────────────────────┘
```

### Marian (Helsinki-NLP)

```
┌────────────────────────────────────────────────────────────┐
│                      MARIAN NMT                             │
├────────────────────────────────────────────────────────────┤
│  Type: Neural Machine Translation (NMT)                     │
│  Entrée: Texte en langue source                            │
│  Sortie: Texte traduit en langue cible                     │
│  Architecture: Transformer (encoder-decoder)               │
│  Modèles: opus-mt-{source}-{target}                        │
│  Exemple: Helsinki-NLP/opus-mt-fr-en                       │
└────────────────────────────────────────────────────────────┘
```

---

# 4. Installation et Configuration

## 4.1 Prérequis

- **Système d'exploitation** : Linux, macOS, Windows
- **Python** : Version 3.10 ou supérieure
- **RAM** : Minimum 8 Go (16 Go recommandé)
- **GPU** : Optionnel mais recommandé pour Whisper
- **Navigateur** : Chrome, Firefox, Edge (avec support WebRTC)

## 4.2 Étapes d'Installation

### Étape 1 : Cloner ou créer le projet

```bash
# Créer le dossier du projet
mkdir Sim-one
cd Sim-one
```

### Étape 2 : Créer un environnement virtuel

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Étape 3 : Installer les dépendances

Créer le fichier `requirements.txt` :

```txt
openai-whisper>=20231117
transformers>=4.31.0
torch>=2.0.0
sentencepiece>=0.1.99
numpy>=1.24.0
sounddevice>=0.4.6
imageio-ffmpeg>=0.4.10
python-docx>=0.8.12
reportlab>=4.0.0
fastapi>=0.110.0
uvicorn[standard]>=0.29.0
```

Installer les packages :

```bash
pip install -r requirements.txt
```

### Étape 4 : Installer FFmpeg (requis pour Whisper)

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows (via chocolatey)
choco install ffmpeg
```

### Étape 5 : Lancer l'application

```bash
python api_v2.py
```

### Étape 6 : Accéder à l'interface

Ouvrir dans le navigateur : **http://localhost:8000**

---

# 5. Structure des Fichiers

```
Sim-one/
│
├── 📄 api_v2.py                 # Point d'entrée principal (API FastAPI)
├── 📄 api.py                    # Ancienne API (version 1)
├── 📄 app.py                    # Application CLI
├── 📄 requirements.txt          # Dépendances Python
├── 📄 README.md                 # Documentation rapide
├── 📄 DOCUMENTATION.md          # Cette documentation
│
├── 📁 backend/                  # Logique métier Python
│   ├── 📄 __init__.py          # Initialisation du module
│   ├── 📄 realtime.py          # Traduction temps réel (WebSocket)
│   ├── 📄 speech_to_text.py    # Transcription audio (Whisper)
│   ├── 📄 translation.py       # Traduction texte (Marian)
│   ├── 📄 pipeline.py          # Orchestration des tâches
│   ├── 📄 storage.py           # Gestion base de données SQLite
│   └── 📄 export.py            # Export PDF/DOCX
│
├── 📁 frontend/                 # Interface utilisateur web
│   ├── 📄 index.html           # Page HTML principale
│   ├── 📄 app.js               # Logique JavaScript
│   ├── 📄 styles.css           # Styles CSS
│   └── 📄 styles_v2.css        # Styles CSS (backup)
│
├── 📁 audio/                    # Fichiers audio de test
│   └── 📄 __init__.py
│
├── 📁 data/                     # Données de l'application
│   └── 📄 history.db           # Base SQLite (créée automatiquement)
│
└── 📁 outputs/                  # Fichiers exportés (PDF/DOCX)
```

---

# 6. Backend - Explication du Code

## 6.1 api_v2.py - Serveur Principal

Ce fichier est le **cœur du serveur**. Il expose l'API REST et le WebSocket.

### Imports et Configuration

```python
"""
API FastAPI améliorée avec support WebSocket pour la traduction en temps réel.
"""

import asyncio
import base64
import json
import logging
import os
import uuid
from typing import Optional, List

# FastAPI pour créer l'API REST
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Pydantic pour la validation des données
from pydantic import BaseModel

# Nos modules backend
from backend.translation import translate_text, translate_text_custom
from backend.realtime import get_translator, remove_translator
from backend import storage
```

**Explication :**
- `FastAPI` : Framework web moderne et rapide pour Python
- `WebSocket` : Permet la communication bidirectionnelle en temps réel
- `Pydantic` : Valide automatiquement les données entrantes
- `CORSMiddleware` : Autorise les requêtes depuis d'autres origines

### Création de l'Application

```python
# Création de l'application FastAPI
app = FastAPI(
    title="SIMONE - Traduction en Temps Réel",
    description="Application de traduction vocale en temps réel avec IA",
    version="2.0.0"
)

# Configuration CORS (Cross-Origin Resource Sharing)
# Permet au frontend d'accéder à l'API depuis n'importe quelle origine
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Toutes les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],      # Toutes les méthodes HTTP autorisées
    allow_headers=["*"],      # Tous les headers autorisés
)

# Servir les fichiers statiques (HTML, CSS, JS)
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
```

### Modèles de Données (Pydantic)

```python
class TranslateRequest(BaseModel):
    """Structure d'une requête de traduction."""
    text: str                    # Texte à traduire
    source_lang: str = "fr"      # Langue source (défaut: français)
    target_lang: str = "en"      # Langue cible (défaut: anglais)


class TranslateResponse(BaseModel):
    """Structure de la réponse de traduction."""
    original_text: str           # Texte original
    translated_text: str         # Texte traduit
    source_lang: str             # Langue source utilisée
    target_lang: str             # Langue cible utilisée
```

**Pourquoi Pydantic ?**
- Validation automatique des types
- Documentation auto-générée (Swagger UI)
- Conversion automatique JSON ↔ Objets Python

### Endpoints REST

```python
@app.get("/")
async def root():
    """Page principale - Sert l'interface web."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>SIMONE</h1><p>Frontend non trouvé.</p>")


@app.get("/health")
async def health_check():
    """Vérifie que le serveur fonctionne."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "features": ["realtime", "websocket", "translation"]
    }


@app.post("/api/translate", response_model=TranslateResponse)
async def translate_text_endpoint(request: TranslateRequest):
    """
    Endpoint de traduction de texte.
    
    Exemple de requête:
    POST /api/translate
    {
        "text": "Bonjour le monde",
        "source_lang": "fr",
        "target_lang": "en"
    }
    
    Réponse:
    {
        "original_text": "Bonjour le monde",
        "translated_text": "Hello world",
        "source_lang": "fr",
        "target_lang": "en"
    }
    """
    try:
        # Appel au module de traduction
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
        # En cas d'erreur, renvoyer une erreur HTTP 500
        raise HTTPException(status_code=500, detail=str(e))
```

### WebSocket pour le Temps Réel

```python
class ConnectionManager:
    """Gère les connexions WebSocket actives."""
    
    def __init__(self):
        # Dictionnaire des connexions: session_id → WebSocket
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accepte une nouvelle connexion WebSocket."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        """Supprime une connexion fermée."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        # Nettoyer aussi le traducteur associé
        remove_translator(session_id)
    
    async def send_json(self, session_id: str, data: dict):
        """Envoie des données JSON à un client."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)


# Instance globale du gestionnaire
manager = ConnectionManager()


@app.websocket("/ws/realtime/{session_id}")
async def websocket_realtime(websocket: WebSocket, session_id: str):
    """
    WebSocket pour la traduction en temps réel.
    
    Protocole de communication:
    
    Client → Serveur:
    - {"type": "config", "source": "fr", "target": "en"}
    - {"type": "audio", "data": "<base64>"}
    - {"type": "process"}
    - {"type": "stop"}
    
    Serveur → Client:
    - {"type": "status", "message": "..."}
    - {"type": "result", "transcription": "...", "translation": "..."}
    - {"type": "error", "message": "..."}
    """
    # Accepter la connexion
    await manager.connect(websocket, session_id)
    
    # Créer un traducteur pour cette session
    translator = get_translator(session_id)
    
    try:
        while True:
            # Attendre un message du client
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "")
            
            if msg_type == "config":
                # Configurer les langues
                source = message.get("source", "fr")
                target = message.get("target", "en")
                translator.set_languages(source, target)
                
            elif msg_type == "audio":
                # Recevoir un chunk audio encodé en base64
                audio_b64 = message.get("data", "")
                audio_bytes = base64.b64decode(audio_b64)
                translator.add_audio_chunk(audio_bytes)
                
            elif msg_type == "process":
                # Traiter le buffer audio
                await manager.send_json(session_id, {
                    "type": "status",
                    "message": "Traitement en cours..."
                })
                
                result = await translator.process_audio()
                
                if result and "error" not in result:
                    await manager.send_json(session_id, {
                        "type": "result",
                        "transcription": result["transcription"],
                        "translation": result["translation"]
                    })
                    translator.clear_buffer()
                    
    except WebSocketDisconnect:
        # Client déconnecté
        manager.disconnect(session_id)
```

---

## 6.2 backend/realtime.py - Traduction Temps Réel

Ce module gère le **buffer audio** et coordonne la transcription/traduction.

```python
"""
Module de traduction en temps réel via WebSocket.
"""

import numpy as np
import logging

# Configuration
SAMPLE_RATE = 16000  # 16 kHz (requis par Whisper)

class RealtimeTranslator:
    """
    Classe de traduction en temps réel.
    
    Responsabilités:
    1. Accumuler les chunks audio
    2. Déclencher Whisper pour transcrire
    3. Déclencher Marian pour traduire
    """
    
    def __init__(self, source_lang: str = "fr", target_lang: str = "en"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Buffer pour stocker l'audio
        self.audio_buffer = np.array([], dtype=np.float32)
        
        # Modèles (chargés à la demande)
        self.whisper_model = None
        self.translator = None
        
        # Durées min/max en échantillons
        self.min_audio_length = SAMPLE_RATE * 2   # 2 secondes
        self.max_audio_length = SAMPLE_RATE * 10  # 10 secondes
    
    def _load_models(self):
        """Charge les modèles IA de façon paresseuse (lazy loading)."""
        if self.whisper_model is None:
            from backend.speech_to_text import get_whisper_model
            self.whisper_model = get_whisper_model()
            
        if self.translator is None:
            from backend.translation import Translator
            self.translator = Translator(self.source_lang, self.target_lang)
    
    def add_audio_chunk(self, audio_data: bytes) -> None:
        """
        Ajoute un chunk audio au buffer.
        
        L'audio arrive en PCM 16-bit (Int16) depuis le navigateur.
        On le convertit en Float32 normalisé [-1, 1] pour Whisper.
        """
        # Conversion: bytes → Int16 → Float32 normalisé
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        audio_float = audio_np.astype(np.float32) / 32768.0
        
        # Ajouter au buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_float])
        
        # Limiter la taille du buffer (éviter les débordements mémoire)
        if len(self.audio_buffer) > self.max_audio_length:
            self.audio_buffer = self.audio_buffer[-self.max_audio_length:]
    
    async def process_audio(self):
        """
        Traite le buffer audio actuel.
        
        Étapes:
        1. Vérifier qu'on a assez d'audio
        2. Transcrire avec Whisper
        3. Traduire avec Marian
        4. Retourner le résultat
        """
        # Vérifier la durée minimale
        if len(self.audio_buffer) < self.min_audio_length:
            return None
        
        # Charger les modèles si nécessaire
        self._load_models()
        
        # Copier le buffer (éviter les modifications pendant le traitement)
        audio_to_process = self.audio_buffer.copy()
        
        # Étape 1: Transcription avec Whisper
        result = self.whisper_model.transcribe(
            audio_to_process,
            language=self.source_lang,
            fp16=False  # Désactiver FP16 sur CPU
        )
        transcription = result.get("text", "").strip()
        
        if not transcription:
            return None
        
        # Étape 2: Traduction avec Marian
        translation = self.translator.translate(transcription)
        
        return {
            "transcription": transcription,
            "translation": translation,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang
        }
    
    def clear_buffer(self):
        """Vide le buffer audio après traitement."""
        self.audio_buffer = np.array([], dtype=np.float32)
```

---

## 6.3 backend/speech_to_text.py - Transcription Whisper

```python
"""
Module de transcription audio avec OpenAI Whisper.

Whisper est un modèle de reconnaissance vocale capable de:
- Transcrire de l'audio en texte
- Détecter automatiquement la langue
- Gérer le bruit de fond et les accents
"""

import os
import logging
import torch

try:
    import whisper
except ImportError:
    raise ImportError("Installez whisper: pip install openai-whisper")

# Configuration
SAMPLE_RATE = 16000
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Cache du modèle (singleton)
_whisper_model = None


def get_whisper_model(name: str = None):
    """
    Charge et met en cache le modèle Whisper.
    
    Modèles disponibles (du plus rapide au plus précis):
    - tiny   : 39M paramètres  (~1 Go RAM)
    - base   : 74M paramètres  (~1 Go RAM)
    - small  : 244M paramètres (~2 Go RAM)
    - medium : 769M paramètres (~5 Go RAM)
    - large  : 1550M paramètres (~10 Go RAM)
    
    Le modèle est choisi via la variable d'environnement WHISPER_MODEL.
    Par défaut: "tiny" (rapide, léger, moins précis)
    """
    global _whisper_model
    
    if name is None:
        # Lire depuis l'environnement ou utiliser "tiny"
        name = os.getenv("WHISPER_MODEL", "tiny")
    
    if _whisper_model is None:
        logging.info(f"Chargement de Whisper '{name}' sur {DEVICE}...")
        _whisper_model = whisper.load_model(name, device=DEVICE)
    
    return _whisper_model


def transcribe_audio(audio_path: str, language: str = None) -> dict:
    """
    Transcrit un fichier audio.
    
    Args:
        audio_path: Chemin vers le fichier audio
        language: Code langue (fr, en, etc.) ou None pour détection auto
    
    Returns:
        {
            "text": "Le texte transcrit...",
            "language": "fr"
        }
    
    Exemple:
        result = transcribe_audio("audio.mp3", language="fr")
        print(result["text"])  # "Bonjour tout le monde"
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Fichier introuvable: {audio_path}")
    
    model = get_whisper_model()
    
    # Transcrire
    if language:
        result = model.transcribe(audio_path, language=language, fp16=False)
        detected = language
    else:
        result = model.transcribe(audio_path, fp16=False)
        detected = result.get("language")
    
    return {
        "text": result.get("text", ""),
        "language": detected
    }
```

---

## 6.4 backend/translation.py - Traduction Marian

```python
"""
Module de traduction avec Helsinki-NLP Marian.

Marian est une famille de modèles de traduction neuronale
pré-entraînés sur des corpus parallèles massifs.
"""

import os
import logging
from typing import Dict, Tuple
from transformers import MarianMTModel, MarianTokenizer


class Translator:
    """
    Wrapper pour un modèle de traduction Marian.
    
    Les modèles sont mis en cache par paire de langues
    pour éviter de les recharger à chaque traduction.
    """
    
    # Cache des traducteurs: (source, target) → Translator
    _cache: Dict[Tuple[str, str], "Translator"] = {}
    
    def __new__(cls, source_lang: str = "en", target_lang: str = "fr"):
        """
        Implémentation du pattern Singleton par paire de langues.
        
        Si un traducteur fr→en existe déjà, on le réutilise.
        """
        key = (source_lang, target_lang)
        if key in cls._cache:
            return cls._cache[key]
        
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance
    
    def __init__(self, source_lang: str = "en", target_lang: str = "fr"):
        # Éviter la réinitialisation
        if hasattr(self, "initialized") and self.initialized:
            return
        
        self.source_lang = source_lang
        self.target_lang = target_lang
        
        # Nom du modèle Hugging Face
        # Format: Helsinki-NLP/opus-mt-{source}-{target}
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        
        logging.info(f"Chargement du modèle: {model_name}")
        
        # Charger le tokenizer et le modèle
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        
        self.initialized = True
    
    def translate(self, text: str, max_length: int = 512) -> str:
        """
        Traduit un texte.
        
        Args:
            text: Texte à traduire
            max_length: Longueur maximale de la sortie
        
        Returns:
            Texte traduit
        
        Exemple:
            translator = Translator("fr", "en")
            result = translator.translate("Bonjour le monde")
            print(result)  # "Hello world"
        """
        if not text:
            return ""
        
        # Tokeniser le texte d'entrée
        inputs = self.tokenizer(
            text,
            return_tensors="pt",  # Format PyTorch
            truncation=True       # Tronquer si trop long
        )
        
        # Générer la traduction
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_beams=4           # Beam search pour meilleure qualité
        )
        
        # Décoder le résultat
        translated = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True  # Supprimer les tokens spéciaux
        )
        
        return translated


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Fonction utilitaire pour traduire un texte.
    
    C'est le point d'entrée principal utilisé par l'API.
    """
    translator = Translator(source_lang, target_lang)
    return translator.translate(text)
```

---

## 6.5 backend/storage.py - Base de Données

```python
"""
Module de stockage avec SQLite.

SQLite est une base de données légère stockée dans un fichier.
Idéale pour les applications locales.
"""

import sqlite3
import os
from typing import Optional, Dict, List

# Chemin de la base de données
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.db')


def init_db(db_path: str = None):
    """
    Initialise la base de données.
    
    Crée la table 'transcripts' si elle n'existe pas.
    """
    path = db_path or DB_PATH
    
    # Créer le dossier data/ si nécessaire
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    # Créer la table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transcripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            audio_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            detected_lang TEXT,
            original_text TEXT,
            translated_text TEXT,
            docx_path TEXT,
            pdf_path TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def save_record(record: Dict[str, str]) -> int:
    """
    Enregistre une traduction dans l'historique.
    
    Args:
        record: {
            "audio_path": "chemin/audio.mp3",
            "detected_lang": "fr",
            "original_text": "Bonjour",
            "translated_text": "Hello",
            "docx_path": "outputs/audio.docx",
            "pdf_path": "outputs/audio.pdf"
        }
    
    Returns:
        ID de l'enregistrement créé
    """
    path = DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO transcripts 
        (audio_path, detected_lang, original_text, translated_text, docx_path, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        record.get('audio_path'),
        record.get('detected_lang'),
        record.get('original_text'),
        record.get('translated_text'),
        record.get('docx_path'),
        record.get('pdf_path')
    ))
    
    conn.commit()
    rowid = cursor.lastrowid
    conn.close()
    
    return rowid


def get_all() -> List[tuple]:
    """Récupère tous les enregistrements."""
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, audio_path, timestamp, detected_lang, 
               original_text, translated_text, docx_path, pdf_path 
        FROM transcripts 
        ORDER BY id DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows
```

---

## 6.6 backend/export.py - Export PDF/DOCX

```python
"""
Module d'export vers PDF et DOCX.

Utilise:
- python-docx pour les fichiers Word
- reportlab pour les fichiers PDF
"""

import os
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_to_docx(text: str, out_path: str) -> str:
    """
    Exporte un texte vers un fichier Word (.docx).
    
    Args:
        text: Texte à exporter
        out_path: Chemin du fichier de sortie
    
    Returns:
        Chemin du fichier créé
    """
    # Créer le dossier si nécessaire
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Créer un nouveau document Word
    doc = Document()
    
    # Ajouter chaque paragraphe
    for line in text.split('\n'):
        doc.add_paragraph(line)
    
    # Sauvegarder
    doc.save(out_path)
    
    return out_path


def export_to_pdf(text: str, out_path: str) -> str:
    """
    Exporte un texte vers un fichier PDF.
    
    Args:
        text: Texte à exporter
        out_path: Chemin du fichier de sortie
    
    Returns:
        Chemin du fichier créé
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    # Créer le canvas PDF
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    
    y = height - 50  # Position de départ
    
    for paragraph in text.split('\n'):
        # Découper les longues lignes
        while len(paragraph) > 90:
            c.drawString(40, y, paragraph[:90])
            paragraph = paragraph[90:]
            y -= 14
            
            # Nouvelle page si nécessaire
            if y < 50:
                c.showPage()
                y = height - 50
        
        c.drawString(40, y, paragraph)
        y -= 14
    
    c.save()
    
    return out_path
```

---

# 7. Frontend - Explication du Code

## 7.1 index.html - Structure de la Page

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SIMONE - Traduction en Temps Réel</title>
    
    <!-- Feuille de styles -->
    <link rel="stylesheet" href="/static/styles.css">
    
    <!-- Police Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
    <div id="app">
        <!-- ========== EN-TÊTE ========== -->
        <header class="header">
            <div class="header-content">
                <!-- Logo -->
                <div class="logo">
                    <span class="logo-icon">🎙️</span>
                    <span class="logo-text">SIMONE</span>
                    <span class="logo-version">v2.0</span>
                </div>
                
                <!-- Navigation -->
                <nav class="nav-links">
                    <a href="#" class="nav-link active" data-section="translator">Traducteur</a>
                    <a href="#" class="nav-link" data-section="history">Historique</a>
                    <a href="#" class="nav-link" data-section="about">À propos</a>
                </nav>
            </div>
        </header>

        <!-- ========== CONTENU PRINCIPAL ========== -->
        <main class="main-content">
            
            <!-- Section Traducteur (active par défaut) -->
            <section id="translator" class="section active">
                <div class="translator-container">
                    <h1 class="section-title">Traduction Vocale en Temps Réel</h1>
                    <p class="section-subtitle">Parlez dans votre langue, obtenez la traduction instantanément</p>

                    <!-- Sélecteurs de Langues -->
                    <div class="language-selectors">
                        <!-- Langue Source -->
                        <div class="language-selector">
                            <label for="source-lang">Je parle en</label>
                            <select id="source-lang" class="lang-select">
                                <option value="fr" selected>🇫🇷 Français</option>
                                <option value="en">🇬🇧 English</option>
                                <option value="es">🇪🇸 Español</option>
                                <option value="de">🇩🇪 Deutsch</option>
                            </select>
                        </div>

                        <!-- Bouton Inverser -->
                        <button id="swap-langs" class="swap-button" title="Inverser les langues">
                            <!-- Icône SVG -->
                            <svg width="24" height="24" viewBox="0 0 24 24">
                                <path d="M7 16V4M7 4L3 8M7 4L11 8M17 8V20M17 20L21 16M17 20L13 16"/>
                            </svg>
                        </button>

                        <!-- Langue Cible -->
                        <div class="language-selector">
                            <label for="target-lang">Traduire en</label>
                            <select id="target-lang" class="lang-select">
                                <option value="en" selected>🇬🇧 English</option>
                                <option value="fr">🇫🇷 Français</option>
                                <option value="es">🇪🇸 Español</option>
                                <option value="de">🇩🇪 Deutsch</option>
                            </select>
                        </div>
                    </div>

                    <!-- Zone de Traduction -->
                    <div class="translation-area">
                        
                        <!-- Panneau Source (Transcription) -->
                        <div class="panel source-panel">
                            <div class="panel-header">
                                <span class="panel-title">🎤 Votre voix</span>
                                <span id="source-lang-display" class="lang-badge">Français</span>
                            </div>
                            <div class="panel-content">
                                <div id="transcription-output" class="text-output">
                                    <p class="placeholder">Cliquez sur le microphone pour commencer...</p>
                                </div>
                            </div>
                        </div>

                        <!-- Bouton Microphone Central -->
                        <div class="mic-container">
                            <button id="mic-button" class="mic-button" title="Cliquez pour parler">
                                <div class="mic-icon">
                                    <svg width="48" height="48" viewBox="0 0 24 24">
                                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                                        <line x1="12" y1="19" x2="12" y2="23"/>
                                    </svg>
                                </div>
                                <div class="mic-pulse"></div>
                            </button>
                            <p id="mic-instruction">Appuyez pour parler</p>
                            
                            <!-- Visualiseur Audio -->
                            <div id="audio-visualizer" class="audio-visualizer">
                                <div class="bar"></div>
                                <div class="bar"></div>
                                <div class="bar"></div>
                                <div class="bar"></div>
                                <div class="bar"></div>
                            </div>
                        </div>

                        <!-- Panneau Cible (Traduction) -->
                        <div class="panel target-panel">
                            <div class="panel-header">
                                <span class="panel-title">🌍 Traduction</span>
                                <span id="target-lang-display" class="lang-badge">English</span>
                            </div>
                            <div class="panel-content">
                                <div id="translation-output" class="text-output">
                                    <p class="placeholder">La traduction apparaîtra ici...</p>
                                </div>
                            </div>
                            <div class="panel-footer">
                                <!-- Bouton Écouter -->
                                <button id="speak-translation" class="action-button" disabled>
                                    🔊 Écouter
                                </button>
                                <!-- Bouton Copier -->
                                <button id="copy-translation" class="action-button" disabled>
                                    📋 Copier
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Zone de Texte Manuel -->
                    <div class="manual-input-area">
                        <div class="manual-input-header">
                            <span>Ou tapez votre texte :</span>
                        </div>
                        <div class="manual-input-content">
                            <textarea id="manual-text" placeholder="Entrez votre texte ici..."></textarea>
                            <button id="translate-text" class="translate-button">
                                Traduire →
                            </button>
                        </div>
                    </div>
                </div>
            </section>

            <!-- Section Historique -->
            <section id="history" class="section">
                <!-- Contenu de l'historique -->
            </section>

            <!-- Section À propos -->
            <section id="about" class="section">
                <!-- Informations sur le projet -->
            </section>
        </main>

        <!-- Pied de Page -->
        <footer class="footer">
            <p>SIMONE v2.0 — Projet académique et professionnel</p>
        </footer>

        <!-- Conteneur pour les Notifications Toast -->
        <div id="toast-container" class="toast-container"></div>
    </div>

    <!-- Script JavaScript -->
    <script src="/static/app.js"></script>
</body>
</html>
```

---

## 7.2 app.js - Logique JavaScript

### Configuration et État

```javascript
/**
 * SIMONE v2.0 - Application de traduction vocale en temps réel
 */

// ============== CONFIGURATION ==============
const CONFIG = {
    API_BASE: window.location.origin,           // URL de l'API (même domaine)
    WS_BASE: `ws://${window.location.host}`,    // URL WebSocket
    SAMPLE_RATE: 16000,                         // Fréquence d'échantillonnage (16 kHz)
    BUFFER_SIZE: 4096,                          // Taille du buffer audio
    MIN_RECORDING_TIME: 2000,                   // Durée minimale (2 secondes)
};

// ============== ÉTAT DE L'APPLICATION ==============
const state = {
    isRecording: false,           // Est-ce qu'on enregistre ?
    websocket: null,              // Connexion WebSocket
    sessionId: null,              // ID de session
    mediaStream: null,            // Flux audio du micro
    audioContext: null,           // Contexte Web Audio
    audioProcessor: null,         // Processeur audio
    recordingStartTime: null,     // Heure de début d'enregistrement
    currentTranscription: '',     // Dernière transcription
    currentTranslation: '',       // Dernière traduction
};

// ============== UTILITAIRES DOM ==============
// Fonctions raccourcies pour sélectionner des éléments
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => Array.from(document.querySelectorAll(sel));
```

### Système de Notifications (Toast)

```javascript
/**
 * Affiche une notification toast.
 * 
 * @param {string} message - Le message à afficher
 * @param {string} type - Type: 'info', 'success', 'error'
 * @param {number} duration - Durée en millisecondes
 */
function showToast(message, type = 'info', duration = 3000) {
    const container = $('#toast-container');
    if (!container) return;
    
    // Créer l'élément toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
        <span class="toast-message">${message}</span>
    `;
    
    // Ajouter au conteneur
    container.appendChild(toast);
    
    // Animation d'entrée
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Supprimer après la durée
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, duration);
}
```

### Connexion WebSocket

```javascript
/**
 * Génère un ID de session unique.
 */
function generateSessionId() {
    return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Établit une connexion WebSocket avec le serveur.
 * 
 * Le WebSocket permet une communication bidirectionnelle
 * en temps réel entre le navigateur et le serveur.
 */
function connectWebSocket() {
    // Si déjà connecté, ne rien faire
    if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
        return Promise.resolve();
    }
    
    return new Promise((resolve, reject) => {
        // Générer un nouvel ID de session
        state.sessionId = generateSessionId();
        
        // URL du WebSocket
        const wsUrl = `${CONFIG.WS_BASE}/ws/realtime/${state.sessionId}`;
        console.log('Connexion WebSocket:', wsUrl);
        
        // Créer la connexion
        state.websocket = new WebSocket(wsUrl);
        
        // Événement: Connexion établie
        state.websocket.onopen = () => {
            console.log('WebSocket connecté');
            
            // Envoyer la configuration des langues
            state.websocket.send(JSON.stringify({
                type: 'config',
                source: $('#source-lang').value,
                target: $('#target-lang').value
            }));
            
            resolve();
        };
        
        // Événement: Message reçu du serveur
        state.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
        };
        
        // Événement: Erreur
        state.websocket.onerror = (error) => {
            console.error('Erreur WebSocket:', error);
            showToast('Erreur de connexion au serveur', 'error');
            reject(error);
        };
        
        // Événement: Connexion fermée
        state.websocket.onclose = () => {
            console.log('WebSocket fermé');
            state.websocket = null;
        };
    });
}

/**
 * Traite les messages reçus du serveur.
 */
function handleWebSocketMessage(data) {
    console.log('Message reçu:', data);
    
    switch (data.type) {
        case 'status':
            // Mise à jour du statut
            updateStatus(data.message);
            break;
            
        case 'result':
        case 'final':
            // Afficher le résultat
            displayResult(data);
            break;
            
        case 'error':
            // Afficher l'erreur
            showToast(data.message, 'error');
            break;
    }
}

/**
 * Affiche le résultat de la traduction.
 */
function displayResult(data) {
    // Stocker les résultats
    state.currentTranscription = data.transcription;
    state.currentTranslation = data.translation;
    
    // Mettre à jour l'interface
    $('#transcription-output').innerHTML = `<p class="result-text">${data.transcription}</p>`;
    $('#translation-output').innerHTML = `<p class="result-text">${data.translation}</p>`;
    
    // Activer les boutons
    $('#speak-translation').disabled = false;
    $('#copy-translation').disabled = false;
    
    showToast('Traduction terminée !', 'success');
}
```

### Capture Audio avec Web Audio API

```javascript
/**
 * Initialise la capture audio depuis le microphone.
 * 
 * Utilise l'API Web Audio pour capturer, traiter
 * et envoyer l'audio au serveur.
 */
async function initAudioCapture() {
    try {
        // 1. Demander l'accès au microphone
        state.mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,              // Mono
                sampleRate: CONFIG.SAMPLE_RATE, // 16 kHz
                echoCancellation: true,       // Annulation d'écho
                noiseSuppression: true        // Réduction du bruit
            }
        });
        
        // 2. Créer le contexte audio
        state.audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: CONFIG.SAMPLE_RATE
        });
        
        // 3. Créer la source audio (microphone)
        const source = state.audioContext.createMediaStreamSource(state.mediaStream);
        
        // 4. Créer le processeur audio
        // Le ScriptProcessor nous permet d'accéder aux données brutes
        state.audioProcessor = state.audioContext.createScriptProcessor(
            CONFIG.BUFFER_SIZE,  // Taille du buffer
            1,                   // Canaux d'entrée (mono)
            1                    // Canaux de sortie (mono)
        );
        
        // 5. Traiter chaque buffer audio
        state.audioProcessor.onaudioprocess = (event) => {
            // Ne rien faire si on n'enregistre pas
            if (!state.isRecording) return;
            
            // Récupérer les données audio (Float32Array)
            const inputData = event.inputBuffer.getChannelData(0);
            
            // Convertir Float32 → Int16 (format attendu par le serveur)
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                // Multiplier par 32768 et limiter à [-32768, 32767]
                pcmData[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
            }
            
            // Encoder en Base64 et envoyer via WebSocket
            if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
                // Convertir en base64
                const base64Data = btoa(
                    String.fromCharCode.apply(null, new Uint8Array(pcmData.buffer))
                );
                
                // Envoyer au serveur
                state.websocket.send(JSON.stringify({
                    type: 'audio',
                    data: base64Data,
                    source: $('#source-lang').value,
                    target: $('#target-lang').value
                }));
            }
            
            // Mettre à jour le visualiseur
            updateVisualizer(inputData);
        };
        
        // 6. Connecter les nœuds audio
        source.connect(state.audioProcessor);
        state.audioProcessor.connect(state.audioContext.destination);
        
        return true;
        
    } catch (error) {
        console.error('Erreur d\'accès au microphone:', error);
        showToast('Impossible d\'accéder au microphone', 'error');
        return false;
    }
}

/**
 * Met à jour le visualiseur audio avec les données actuelles.
 */
function updateVisualizer(audioData) {
    const bars = $$('#audio-visualizer .bar');
    if (!bars.length) return;
    
    const chunkSize = Math.floor(audioData.length / bars.length);
    
    bars.forEach((bar, index) => {
        // Calculer la moyenne du volume pour ce segment
        let sum = 0;
        for (let i = 0; i < chunkSize; i++) {
            sum += Math.abs(audioData[index * chunkSize + i]);
        }
        const average = sum / chunkSize;
        
        // Convertir en hauteur (0-100%)
        const height = Math.min(100, average * 500);
        bar.style.height = `${Math.max(5, height)}%`;
    });
}
```

### Contrôle de l'Enregistrement

```javascript
/**
 * Démarre l'enregistrement audio.
 */
async function startRecording() {
    console.log('Démarrage de l\'enregistrement...');
    
    // 1. Se connecter au WebSocket
    try {
        await connectWebSocket();
    } catch (error) {
        showToast('Impossible de se connecter au serveur', 'error');
        return;
    }
    
    // 2. Initialiser la capture audio
    const audioReady = await initAudioCapture();
    if (!audioReady) return;
    
    // 3. Démarrer l'enregistrement
    state.isRecording = true;
    state.recordingStartTime = Date.now();
    
    // 4. Mettre à jour l'interface
    $('#mic-button').classList.add('recording');
    $('#mic-instruction').textContent = 'Parlez maintenant...';
    $('#audio-visualizer').classList.add('active');
    
    showToast('Enregistrement démarré', 'info');
}

/**
 * Arrête l'enregistrement et demande le traitement.
 */
async function stopRecording() {
    console.log('Arrêt de l\'enregistrement...');
    
    // Vérifier la durée minimale
    const duration = Date.now() - state.recordingStartTime;
    if (duration < CONFIG.MIN_RECORDING_TIME) {
        showToast('Parlez au moins 2 secondes', 'error');
        return;
    }
    
    // Arrêter l'enregistrement
    state.isRecording = false;
    
    // Mettre à jour l'interface
    $('#mic-button').classList.remove('recording');
    $('#mic-instruction').textContent = 'Traitement en cours...';
    $('#audio-visualizer').classList.remove('active');
    
    // Demander le traitement au serveur
    if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
        state.websocket.send(JSON.stringify({ type: 'process' }));
    }
    
    // Arrêter le flux audio
    if (state.mediaStream) {
        state.mediaStream.getTracks().forEach(track => track.stop());
        state.mediaStream = null;
    }
    
    // Fermer le contexte audio
    if (state.audioContext) {
        state.audioContext.close();
        state.audioContext = null;
    }
}

/**
 * Initialise le bouton microphone.
 */
function initMicButton() {
    const micButton = $('#mic-button');
    if (!micButton) return;
    
    micButton.addEventListener('click', async () => {
        if (state.isRecording) {
            await stopRecording();
        } else {
            await startRecording();
        }
    });
}
```

### Synthèse Vocale (Text-to-Speech)

```javascript
/**
 * Initialise le bouton d'écoute.
 * 
 * Utilise l'API Web Speech pour lire le texte traduit.
 */
function initTextToSpeech() {
    const speakBtn = $('#speak-translation');
    if (!speakBtn) return;
    
    speakBtn.addEventListener('click', () => {
        if (!state.currentTranslation) return;
        
        // Créer un objet SpeechSynthesisUtterance
        const utterance = new SpeechSynthesisUtterance(state.currentTranslation);
        
        // Configurer la langue
        utterance.lang = $('#target-lang').value;
        utterance.rate = 0.9;  // Vitesse légèrement réduite
        
        // Événements
        utterance.onstart = () => speakBtn.classList.add('speaking');
        utterance.onend = () => speakBtn.classList.remove('speaking');
        
        // Lancer la synthèse vocale
        speechSynthesis.speak(utterance);
    });
}
```

### Initialisation

```javascript
/**
 * Point d'entrée de l'application.
 * 
 * Appelé lorsque le DOM est complètement chargé.
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('SIMONE v2.0 - Initialisation...');
    
    // Initialiser tous les composants
    initNavigation();
    initLanguageSelectors();
    initMicButton();
    initManualTranslation();
    initTextToSpeech();
    initCopyButton();
    
    // Vérifier le support du navigateur
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showToast('Votre navigateur ne supporte pas l\'enregistrement audio', 'error');
        $('#mic-button').disabled = true;
    }
    
    console.log('SIMONE v2.0 - Prêt !');
});
```

---

## 7.3 styles.css - Design CSS

### Variables CSS

```css
/**
 * Variables CSS (Custom Properties)
 * 
 * Permettent de centraliser les couleurs, tailles, etc.
 * et de les réutiliser partout dans le CSS.
 */
:root {
    /* Couleurs principales */
    --primary: #4F46E5;           /* Violet (boutons, liens) */
    --primary-light: #818CF8;     /* Violet clair */
    --primary-dark: #3730A3;      /* Violet foncé */
    --secondary: #10B981;         /* Vert (succès) */
    --danger: #EF4444;            /* Rouge (erreur) */
    
    /* Arrière-plans */
    --bg-main: #F8FAFC;           /* Fond principal (gris clair) */
    --bg-card: #FFFFFF;           /* Fond des cartes (blanc) */
    --bg-dark: #0F172A;           /* Fond sombre (header) */
    
    /* Textes */
    --text-primary: #0F172A;      /* Texte principal (noir) */
    --text-secondary: #475569;    /* Texte secondaire (gris) */
    --text-muted: #94A3B8;        /* Texte atténué (gris clair) */
    
    /* Ombres */
    --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    
    /* Bordures arrondies */
    --radius: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-full: 9999px;        /* Cercle parfait */
    
    /* Transitions */
    --transition: all 0.2s ease;
}
```

### Bouton Microphone

```css
/**
 * Bouton microphone central.
 * 
 * Design circulaire avec effet de pulsation
 * lors de l'enregistrement.
 */
.mic-button {
    width: 120px;
    height: 120px;
    border-radius: 50%;               /* Cercle */
    border: none;
    background: linear-gradient(135deg, var(--primary), var(--primary-dark));
    color: white;
    cursor: pointer;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: var(--transition);
    box-shadow: var(--shadow-lg);
}

/* Effet au survol */
.mic-button:hover {
    transform: scale(1.05);
}

/* État d'enregistrement */
.mic-button.recording {
    background: linear-gradient(135deg, var(--danger), #DC2626);
    animation: pulse 1.5s infinite;
}

/* Animation de pulsation */
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

/* Cercle de pulsation autour du bouton */
.mic-pulse {
    display: none;
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: rgba(239, 68, 68, 0.3);
    animation: ripple 1.5s infinite;
}

.mic-button.recording .mic-pulse {
    display: block;
}

@keyframes ripple {
    0% { transform: scale(1); opacity: 1; }
    100% { transform: scale(1.5); opacity: 0; }
}
```

### Visualiseur Audio

```css
/**
 * Visualiseur audio avec barres animées.
 */
.audio-visualizer {
    display: flex;
    align-items: flex-end;
    justify-content: center;
    gap: 4px;
    height: 40px;
    opacity: 0;                   /* Invisible par défaut */
    transition: var(--transition);
}

/* Visible pendant l'enregistrement */
.audio-visualizer.active {
    opacity: 1;
}

/* Barres individuelles */
.audio-visualizer .bar {
    width: 6px;
    height: 5%;                   /* Hauteur modifiée par JavaScript */
    background: var(--primary);
    border-radius: var(--radius);
    transition: height 0.1s ease;
}
```

---

# 8. API REST et WebSocket

## 8.1 Endpoints REST

| Méthode | Endpoint | Description | Exemple |
|---------|----------|-------------|---------|
| GET | `/` | Page principale | - |
| GET | `/health` | Vérification santé | `{"status": "ok"}` |
| POST | `/api/translate` | Traduire du texte | Voir ci-dessous |
| GET | `/api/history` | Historique | Liste des traductions |
| GET | `/api/languages` | Langues supportées | Liste des langues |

### Exemple: Traduction de Texte

**Requête:**
```http
POST /api/translate
Content-Type: application/json

{
    "text": "Bonjour, comment allez-vous ?",
    "source_lang": "fr",
    "target_lang": "en"
}
```

**Réponse:**
```json
{
    "original_text": "Bonjour, comment allez-vous ?",
    "translated_text": "Hello, how are you?",
    "source_lang": "fr",
    "target_lang": "en"
}
```

## 8.2 Protocole WebSocket

### URL de Connexion

```
ws://localhost:8000/ws/realtime/{session_id}
```

### Messages Client → Serveur

| Type | Payload | Description |
|------|---------|-------------|
| `config` | `{source, target}` | Configurer les langues |
| `audio` | `{data: base64}` | Envoyer un chunk audio |
| `process` | `{}` | Demander le traitement |
| `stop` | `{}` | Arrêter et obtenir le résultat |
| `clear` | `{}` | Vider le buffer |

### Messages Serveur → Client

| Type | Payload | Description |
|------|---------|-------------|
| `status` | `{message}` | Mise à jour du statut |
| `result` | `{transcription, translation}` | Résultat intermédiaire |
| `final` | `{transcription, translation}` | Résultat final |
| `error` | `{message}` | Erreur |

---

# 9. Flux de Données

## 9.1 Traduction Vocale (Temps Réel)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FLUX DE TRADUCTION VOCALE                     │
└─────────────────────────────────────────────────────────────────────┘

 UTILISATEUR          NAVIGATEUR              SERVEUR              MODÈLES IA
     │                    │                      │                     │
     │  1. Clic Micro     │                      │                     │
     │ ─────────────────▶ │                      │                     │
     │                    │                      │                     │
     │                    │  2. getUserMedia()   │                     │
     │                    │  (accès micro)       │                     │
     │                    │                      │                     │
     │                    │  3. WebSocket        │                     │
     │                    │ ───────────────────▶ │                     │
     │                    │                      │                     │
     │  4. Parle          │                      │                     │
     │ ─────────────────▶ │                      │                     │
     │                    │                      │                     │
     │                    │  5. Chunks audio     │                     │
     │                    │  (base64 via WS)     │                     │
     │                    │ ───────────────────▶ │                     │
     │                    │ ───────────────────▶ │                     │
     │                    │ ───────────────────▶ │                     │
     │                    │                      │                     │
     │  6. Clic Stop      │                      │                     │
     │ ─────────────────▶ │                      │                     │
     │                    │                      │                     │
     │                    │  7. "process"        │                     │
     │                    │ ───────────────────▶ │                     │
     │                    │                      │                     │
     │                    │                      │  8. Whisper         │
     │                    │                      │ ──────────────────▶ │
     │                    │                      │                     │
     │                    │                      │  9. Texte transcrit │
     │                    │                      │ ◀────────────────── │
     │                    │                      │                     │
     │                    │                      │  10. Marian         │
     │                    │                      │ ──────────────────▶ │
     │                    │                      │                     │
     │                    │                      │  11. Texte traduit  │
     │                    │                      │ ◀────────────────── │
     │                    │                      │                     │
     │                    │  12. Résultat JSON   │                     │
     │                    │ ◀─────────────────── │                     │
     │                    │                      │                     │
     │  13. Affichage     │                      │                     │
     │ ◀───────────────── │                      │                     │
     │                    │                      │                     │
     ▼                    ▼                      ▼                     ▼
```

## 9.2 Traduction de Texte (API REST)

```
 UTILISATEUR          NAVIGATEUR              SERVEUR              MODÈLE
     │                    │                      │                    │
     │  1. Tape texte     │                      │                    │
     │ ─────────────────▶ │                      │                    │
     │                    │                      │                    │
     │  2. Clic Traduire  │                      │                    │
     │ ─────────────────▶ │                      │                    │
     │                    │                      │                    │
     │                    │  3. POST /api/translate                   │
     │                    │ ───────────────────▶ │                    │
     │                    │                      │                    │
     │                    │                      │  4. Marian         │
     │                    │                      │ ─────────────────▶ │
     │                    │                      │                    │
     │                    │                      │  5. Traduction     │
     │                    │                      │ ◀───────────────── │
     │                    │                      │                    │
     │                    │  6. Réponse JSON     │                    │
     │                    │ ◀─────────────────── │                    │
     │                    │                      │                    │
     │  7. Affichage      │                      │                    │
     │ ◀───────────────── │                      │                    │
     │                    │                      │                    │
```

---

# 10. Guide d'Utilisation

## 10.1 Traduction Vocale

### Étape 1: Sélectionner les Langues

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Je parle en        ⟳        Traduire en              │
│   ┌──────────────┐         ┌──────────────┐            │
│   │ 🇫🇷 Français  ▼│         │ 🇬🇧 English  ▼│            │
│   └──────────────┘         └──────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

- Choisissez votre langue source (celle que vous parlez)
- Choisissez votre langue cible (celle de la traduction)
- Utilisez le bouton ⟳ pour inverser les langues

### Étape 2: Enregistrer Votre Voix

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                      🎤                                  │
│                   (  Micro  )                           │
│                                                         │
│              Appuyez pour parler                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

1. Cliquez sur le bouton microphone
2. Autorisez l'accès au micro si demandé
3. Le bouton devient rouge, parlez maintenant
4. Parlez pendant au moins 2 secondes

### Étape 3: Obtenir la Traduction

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   🎤 Votre voix              🌍 Traduction              │
│   ┌─────────────────┐       ┌─────────────────┐        │
│   │ Bonjour, je     │       │ Hello, I'm      │        │
│   │ m'appelle       │       │ called          │        │
│   │ Marie.          │       │ Marie.          │        │
│   └─────────────────┘       └─────────────────┘        │
│                                                         │
│                     [🔊 Écouter] [📋 Copier]            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

- La transcription apparaît à gauche
- La traduction apparaît à droite
- Cliquez sur "Écouter" pour entendre la traduction
- Cliquez sur "Copier" pour copier le texte

## 10.2 Traduction de Texte

```
┌─────────────────────────────────────────────────────────┐
│  Ou tapez votre texte :                                 │
│  ┌─────────────────────────────────────┐  ┌──────────┐ │
│  │ Bonjour le monde                    │  │ Traduire │ │
│  │                                     │  │    →     │ │
│  └─────────────────────────────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
```

1. Tapez votre texte dans la zone de saisie
2. Cliquez sur "Traduire"
3. Le résultat apparaît dans les panneaux

---

# 11. Dépannage

## 11.1 Problèmes Courants

### Le microphone ne fonctionne pas

**Symptôme:** Message "Impossible d'accéder au microphone"

**Solutions:**
1. Vérifiez que vous utilisez HTTPS ou localhost
2. Autorisez l'accès au micro dans votre navigateur
3. Vérifiez que le micro n'est pas utilisé par une autre application

```
Chrome: chrome://settings/content/microphone
Firefox: about:preferences#privacy → Permissions → Microphone
```

### Erreur de connexion au serveur

**Symptôme:** Message "Erreur de connexion"

**Solutions:**
1. Vérifiez que le serveur Python est lancé:
   ```bash
   python api_v2.py
   ```
2. Vérifiez que le port 8000 n'est pas utilisé:
   ```bash
   lsof -i :8000
   ```
3. Redémarrez le serveur si nécessaire

### Traduction lente

**Symptôme:** Le traitement prend beaucoup de temps

**Solutions:**
1. Utilisez un modèle Whisper plus léger:
   ```bash
   WHISPER_MODEL=tiny python api_v2.py
   ```
2. Si vous avez un GPU, vérifiez qu'il est utilisé:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

### Erreur de traduction

**Symptôme:** Message "Erreur lors de la traduction"

**Solutions:**
1. Vérifiez votre connexion Internet (téléchargement des modèles)
2. Vérifiez que la paire de langues est supportée
3. Consultez les logs du serveur pour plus de détails

## 11.2 Logs de Débogage

Pour activer les logs détaillés:

```python
# Dans api_v2.py
logging.basicConfig(
    level=logging.DEBUG,  # Changer INFO → DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

---

# 12. Améliorations Futures

## 12.1 Fonctionnalités à Ajouter

| Priorité | Fonctionnalité | Description |
|----------|----------------|-------------|
| 🔴 Haute | Streaming continu | Traduction pendant qu'on parle |
| 🔴 Haute | Plus de langues | Chinois, Arabe, Japonais, etc. |
| 🟡 Moyenne | Détection auto langue | Sans sélection manuelle |
| 🟡 Moyenne | Mode conversation | Dialogue bilingue |
| 🟢 Basse | Thèmes personnalisés | Mode sombre, couleurs |
| 🟢 Basse | PWA | Application installable |

## 12.2 Optimisations Techniques

```
┌─────────────────────────────────────────────────────────────────────┐
│                      AMÉLIORATIONS TECHNIQUES                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  🚀 Performance                                                      │
│     • Utiliser faster-whisper (3x plus rapide)                      │
│     • Quantification des modèles (INT8)                             │
│     • Cache Redis pour les traductions fréquentes                   │
│                                                                      │
│  🔒 Sécurité                                                         │
│     • Authentification JWT                                          │
│     • Rate limiting                                                 │
│     • HTTPS obligatoire                                             │
│                                                                      │
│  📈 Scalabilité                                                      │
│     • Docker + Kubernetes                                           │
│     • Load balancing                                                │
│     • Microservices                                                 │
│                                                                      │
│  🧪 Qualité                                                          │
│     • Tests unitaires (pytest)                                      │
│     • Tests d'intégration                                           │
│     • CI/CD (GitHub Actions)                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 13. Références

## 13.1 Documentation Officielle

| Technologie | Lien |
|-------------|------|
| **FastAPI** | https://fastapi.tiangolo.com/ |
| **OpenAI Whisper** | https://github.com/openai/whisper |
| **Hugging Face Transformers** | https://huggingface.co/docs/transformers |
| **Web Audio API** | https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API |
| **WebSocket API** | https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API |

## 13.2 Modèles Helsinki-NLP

| Paire | Modèle Hugging Face |
|-------|---------------------|
| FR → EN | `Helsinki-NLP/opus-mt-fr-en` |
| EN → FR | `Helsinki-NLP/opus-mt-en-fr` |
| ES → EN | `Helsinki-NLP/opus-mt-es-en` |
| DE → EN | `Helsinki-NLP/opus-mt-de-en` |
| IT → EN | `Helsinki-NLP/opus-mt-it-en` |

## 13.3 Ressources d'Apprentissage

- **Python pour l'IA** : https://www.deeplearning.ai/
- **NLP avec Transformers** : https://huggingface.co/learn/nlp-course
- **Web Development** : https://developer.mozilla.org/

---

# 📝 Notes de Version

## v2.0.0 (Janvier 2026)

- ✅ Interface web complètement refaite
- ✅ Traduction vocale en temps réel via WebSocket
- ✅ Capture audio dans le navigateur (Web Audio API)
- ✅ Synthèse vocale de la traduction
- ✅ Support multilingue (FR, EN, ES, DE, IT, PT)
- ✅ Design moderne et responsive

## v1.0.0 (Version initiale)

- CLI pour transcription et traduction
- Export PDF/DOCX
- Historique SQLite

---

# 🙏 Remerciements

Ce projet a été développé dans un cadre académique et professionnel.

**Technologies utilisées avec gratitude :**
- OpenAI pour Whisper
- Hugging Face pour les modèles Transformers
- FastAPI pour le framework web
- La communauté open source

---

**© 2026 SIMONE - Tous droits réservés**

*Documentation rédigée le 22 janvier 2026*
