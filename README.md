# SIMONE — Transcription et traduction audio

Ce projet est un prototype CLI permettant :
- de transcrire des fichiers audio (Whisper),
- de détecter automatiquement la langue de l'audio,
- de traduire le texte transcrit (Helsinki‑NLP Marian),
- d'enregistrer l'historique des transcriptions et d'exporter en DOCX/PDF.

Installation rapide

1) Créer et activer un environnement virtuel (Windows, cmd) :

```bash
py -3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2) FFmpeg est requis pour décoder les flux audio. Deux options :
- Installer un FFmpeg système (recommandé). Sur Linux : `apt install ffmpeg`.
- Ou installer le paquet Python `imageio-ffmpeg` (fournit un binaire embarqué) :

```bash
pip install imageio-ffmpeg
```

3) Lancer l'application (exemple) :

```bash
set WHISPER_MODEL=tiny
py app.py
```

Fonctionnalités principales

- `app.py` : script d'exemple qui liste d'abord l'historique, puis transcrit et traduit un fichier audio de démonstration.
- `backend/speech_to_text.py` : wrapper pour Whisper, détection automatique de la langue, option temps réel.
- `backend/translation.py` : wrapper pour les modèles Marian (Helsinki‑NLP) avec cache par paire de langues.
- `backend/pipeline.py` : orchestration (transcription → traduction → export → enregistrement historique).
- `backend/storage.py` : base SQLite pour l'historique.
- `backend/export.py` : export DOCX et PDF simples.

Conseils pour une utilisation réelle

- Utilisez `WHISPER_MODEL=tiny` ou `small` sur CPU ; préférez un GPU (Colab, VM) pour `base/medium/large`.
- Pour les très longs fichiers, prévoir un découpage (chunking) et la gestion des segments.
- Pour des besoins de production, envisager :
  - l'utilisation de `faster-whisper` ou d'une API cloud (Google Cloud Speech, Hugging Face Inference),
  - tests automatisés, CI, Docker, gestion des secrets,
  - amélioration des exports DOCX/PDF et interface utilisateur (Web/GUI).

Stockage des résultats

Les transcriptions sont sauvegardées dans `data/history.db` (SQLite) et les exports sont placés dans `outputs/`.


