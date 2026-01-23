"""
Module de traduction en temps réel via WebSocket.

Ce module gère :
- La réception de chunks audio depuis le navigateur
- La transcription avec Whisper
- La traduction avec Marian
- L'envoi des résultats en temps réel

Architecture pour usage académique et professionnel.
"""

import asyncio
import base64
import io
import logging
import os
import tempfile
import wave
from typing import Optional

import numpy as np

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paramètres audio
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio


class RealtimeTranslator:
    """Classe de traduction en temps réel.
    
    Gère le buffer audio, la transcription et la traduction.
    Optimisée pour une latence minimale.
    """
    
    def __init__(self, source_lang: str = "fr", target_lang: str = "en"):
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.audio_buffer = np.array([], dtype=np.float32)
        self.whisper_model = None
        self.translator = None
        self.is_processing = False
        self.min_audio_length = SAMPLE_RATE * 2  # 2 secondes minimum
        self.max_audio_length = SAMPLE_RATE * 10  # 10 secondes maximum
        
    def _load_models(self):
        """Charge les modèles de façon paresseuse."""
        if self.whisper_model is None:
            from backend.speech_to_text import get_whisper_model
            logger.info("Chargement du modèle Whisper...")
            self.whisper_model = get_whisper_model()
            
        if self.translator is None:
            from backend.translation import Translator
            logger.info(f"Chargement du traducteur {self.source_lang} → {self.target_lang}...")
            self.translator = Translator(self.source_lang, self.target_lang)
    
    def set_languages(self, source: str, target: str):
        """Change les langues source et cible."""
        if source != self.source_lang or target != self.target_lang:
            self.source_lang = source
            self.target_lang = target
            # Recharger le traducteur avec les nouvelles langues
            from backend.translation import Translator
            self.translator = Translator(source, target)
            logger.info(f"Langues mises à jour: {source} → {target}")
    
    def add_audio_chunk(self, audio_data: bytes) -> None:
        """Ajoute un chunk audio au buffer.
        
        Args:
            audio_data: Données audio en bytes (PCM 16-bit, mono, 16kHz)
        """
        # Convertir bytes en numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_np])
        
        # Limiter la taille du buffer
        if len(self.audio_buffer) > self.max_audio_length:
            self.audio_buffer = self.audio_buffer[-self.max_audio_length:]
    
    def clear_buffer(self):
        """Vide le buffer audio."""
        self.audio_buffer = np.array([], dtype=np.float32)
    
    async def process_audio(self) -> Optional[dict]:
        """Traite le buffer audio actuel.
        
        Returns:
            dict avec 'transcription', 'translation', 'source_lang', 'target_lang'
            ou None si pas assez d'audio
        """
        if len(self.audio_buffer) < self.min_audio_length:
            return None
            
        if self.is_processing:
            return None
            
        self.is_processing = True
        
        try:
            # Charger les modèles si nécessaire
            self._load_models()
            
            # Copier le buffer actuel
            audio_to_process = self.audio_buffer.copy()
            
            # Transcription avec Whisper
            logger.info(f"Transcription de {len(audio_to_process) / SAMPLE_RATE:.1f}s d'audio...")
            result = self.whisper_model.transcribe(
                audio_to_process,
                language=self.source_lang,
                fp16=False
            )
            transcription = result.get("text", "").strip()
            
            if not transcription:
                return None
            
            # Traduction
            logger.info(f"Traduction: '{transcription[:50]}...'")
            translation = self.translator.translate(transcription)
            
            return {
                "transcription": transcription,
                "translation": translation,
                "source_lang": self.source_lang,
                "target_lang": self.target_lang
            }
            
        except Exception as e:
            logger.exception("Erreur lors du traitement audio")
            return {"error": str(e)}
            
        finally:
            self.is_processing = False


# Instance globale pour le WebSocket
_realtime_translators: dict[str, RealtimeTranslator] = {}


def get_translator(session_id: str, source_lang: str = "fr", target_lang: str = "en") -> RealtimeTranslator:
    """Récupère ou crée un traducteur pour une session."""
    if session_id not in _realtime_translators:
        _realtime_translators[session_id] = RealtimeTranslator(source_lang, target_lang)
    else:
        _realtime_translators[session_id].set_languages(source_lang, target_lang)
    return _realtime_translators[session_id]


def remove_translator(session_id: str):
    """Supprime un traducteur de session."""
    if session_id in _realtime_translators:
        del _realtime_translators[session_id]
