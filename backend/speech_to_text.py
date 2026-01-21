"""
Module de transcription audio.

Ce module fournit :
- `get_whisper_model` : chargement paresseux et mise en cache du modèle Whisper
- `transcribe_audio` : transcrit un fichier audio et retourne le texte et la langue détectée
- `real_time_transcription` : option de transcription depuis le microphone (si `sounddevice` installé)

Les commentaires et messages sont en français pour faciliter la maintenance.
"""

import logging
import os
from typing import Optional

import numpy as np
import queue
import torch

try:
    import whisper
except Exception as e:
    raise ImportError("La bibliothèque 'whisper' est requise : pip install -U openai-whisper") from e

# Dépendances optionnelles pour l'audio en temps réel
try:
    import sounddevice as sd
except Exception:
    sd = None  # si absent, la fonctionnalité temps réel est désactivée

# S'assurer que le binaire ffmpeg fourni par imageio-ffmpeg est disponible
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["PATH"] = os.path.dirname(ffmpeg_exe) + os.pathsep + os.environ.get("PATH", "")
except Exception:
    # si imageio-ffmpeg absent, on espère qu'un ffmpeg système est installé
    pass

# =========================
# CONFIG
# =========================
SAMPLE_RATE = 16000
DURATION = 5  # durée en secondes par chunk pour la transcription temps réel
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Pour machines faibles, limiter le nombre de threads CPU
os.environ.setdefault("OMP_NUM_THREADS", "1")
try:
    torch.set_num_threads(1)
except Exception:
    pass

# Cache du modèle Whisper (chargé paresseusement)
_whisper_model: Optional[whisper.Whisper] = None

# Queue d'audio pour la transcription en temps réel
audio_queue = queue.Queue()


def get_whisper_model(name: str | None = None) -> whisper.Whisper:
    """Charge et met en cache le modèle Whisper.

    - Par défaut (`WHISPER_MODEL` env) le modèle est `tiny` (léger pour CPU).
    - Retourne l'instance mise en cache si déjà chargée.
    """
    global _whisper_model
    if name is None:
        name = os.getenv("WHISPER_MODEL", "tiny")

    if _whisper_model is None:
        logging.info("Chargement du modèle Whisper '%s' sur %s", name, DEVICE)
        _whisper_model = whisper.load_model(name, device=DEVICE)
    return _whisper_model


def transcribe_audio(audio_path: str, language: Optional[str] = None) -> dict:
    """Transcrit un fichier audio et retourne le texte et la langue.

    Args:
        audio_path: chemin vers le fichier audio sur disque
        language: si fourni, force la langue de transcription (ex: 'fr', 'en');
                  sinon Whisper détecte automatiquement la langue.

    Returns:
        dict avec les clés : 'text' (texte transcrit) et 'language' (code langue détecté/forcé)
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Fichier audio introuvable : {audio_path}")

    model = get_whisper_model()

    logging.info("Transcription de %s (lang=%s)", audio_path, language)
    # Si la langue est fournie, on la passe à Whisper pour forcer la transcription
    if language:
        result = model.transcribe(audio_path, language=language, fp16=False)
        detected = language
    else:
        result = model.transcribe(audio_path, fp16=False)
        # Whisper peut retourner la langue détectée dans differentes clés
        detected = result.get("language") or result.get("lang") or None

    return {"text": result.get("text", ""), "language": detected}


# =========================
# AUDIO CALLBACK (pour transcription temps réel)
# =========================
def audio_callback(indata, frames, time, status):
    """Callback appelé par `sounddevice` pour ajouter des données audio en buffer."""
    if status:
        logging.warning(status)
    audio_queue.put(indata.copy())


def real_time_transcription(language: Optional[str] = None):
    """Transcription continue depuis le microphone.

    Remarque: nécessite `sounddevice`. Le code lit des chunks et appelle Whisper pour
    transcrire chaque chunk. Cette fonction est destinée à des usages locaux/POC.
    """
    if sd is None:
        raise RuntimeError("sounddevice est requis pour la transcription en temps réel")

    print("Enregistrement en temps réel... (Ctrl+C pour arrêter)")
    if language:
        print(f"Langue forcée: {language}")
    else:
        print("Détection automatique de la langue (peut varier sur petits segments)")

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
        buffer = np.empty((0, 1), dtype=np.float32)

        while True:
            data = audio_queue.get()
            buffer = np.concatenate((buffer, data))

            if len(buffer) >= SAMPLE_RATE * DURATION:
                audio_chunk = buffer[:SAMPLE_RATE * DURATION]
                buffer = buffer[SAMPLE_RATE * DURATION:]

                audio_chunk = audio_chunk.flatten()
                model = get_whisper_model()
                if language:
                    result = model.transcribe(audio_chunk, language=language, fp16=False)
                else:
                    result = model.transcribe(audio_chunk, fp16=False)
                text = result.get("text", "")
                print("📝 :", text)


class RecordingSession:
    """Contrôle d'une session d'enregistrement local.

    Utilisation:
      s = RecordingSession(max_seconds=300, language=None)
      s.start()            # démarre l'enregistrement en arrière-plan
      s.stop()             # arrête l'enregistrement (depuis UI/bouton)
      result = s.get_result()  # dictionnaire { 'text', 'language' }

    La session arrête automatiquement l'enregistrement si `max_seconds` est atteint.
    """

    def __init__(self, max_seconds: int = 600, language: Optional[str] = None):
        if sd is None:
            raise RuntimeError("sounddevice est requis pour RecordingSession")
        self.max_seconds = int(max_seconds)
        self.language = language
        self._buffer = np.empty((0, 1), dtype=np.float32)
        self._stop_event = False
        self._thread = None
        self._result = None

    def _callback(self, indata, frames, time, status):
        if status:
            logging.warning(status)
        self._buffer = np.concatenate((self._buffer, indata.copy()))

    def _run(self):
        # Enregistre jusqu'à stop ou max_seconds
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=self._callback):
            start = sd.default.device
            start_time = sd.get_stream().time if hasattr(sd, 'get_stream') else None
            # boucle active simple : vérifie la condition de fin
            import time as _time
            elapsed = 0.0
            t0 = _time.time()
            while not self._stop_event and elapsed < self.max_seconds:
                _time.sleep(0.1)
                elapsed = _time.time() - t0

        # Flatten et transcrire
        try:
            audio_np = self._buffer.flatten()
            model = get_whisper_model()
            if self.language:
                res = model.transcribe(audio_np, language=self.language, fp16=False)
                detected = self.language
            else:
                res = model.transcribe(audio_np, fp16=False)
                detected = res.get('language') or res.get('lang') or None
            self._result = {'text': res.get('text', ''), 'language': detected}
        except Exception:
            logging.exception('Erreur durant la transcription de la session')
            self._result = {'text': '', 'language': None}

    def start(self):
        """Démarre l'enregistrement en arrière-plan."""
        if self._thread and self._thread.is_alive():
            raise RuntimeError('Session déjà en cours')
        import threading
        self._stop_event = False
        self._buffer = np.empty((0, 1), dtype=np.float32)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Demande l'arrêt de l'enregistrement; la transcription est lancée ensuite."""
        self._stop_event = True
        if self._thread:
            self._thread.join()

    def is_recording(self) -> bool:
        return self._thread is not None and self._thread.is_alive()

    def get_result(self, wait: bool = True):
        """Récupère le résultat (bloque si `wait=True` et la transcription n'est pas terminée)."""
        if wait and self._thread:
            self._thread.join()
        return self._result


if __name__ == "__main__":
    real_time_transcription()

