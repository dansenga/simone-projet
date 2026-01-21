"""
Pipeline principale : orchestration de la transcription et de la traduction.

Cette fonction effectue :
- Transcription (avec détection automatique de la langue si `source_lang` est None)
- Traduction du texte transcrit vers `target_lang`
- Sauvegarde de l'historique dans SQLite et export DOCX/PDF (non bloquant)
"""

import logging
import os
from typing import Dict

from backend.speech_to_text import transcribe_audio
from backend.translation import translate_text
from backend import storage
from backend import export as exporter


def audio_to_translated_text(audio_path: str, source_lang: str | None, target_lang: str) -> Dict[str, str]:
    """Transcrit et traduit un fichier audio.

    Args:
        audio_path: chemin vers le fichier audio
        source_lang: code langue pour forcer la transcription ou None pour détection automatique
        target_lang: langue de sortie (ex: 'fr')

    Retourne un dict contenant `original_text`, `detected_source`, `translated_text`.
    """
    try:
        trans_res = transcribe_audio(audio_path, language=source_lang)
    except Exception:
        logging.exception("Echec de la transcription pour : %s", audio_path)
        raise

    original_text = trans_res.get("text", "")
    detected_source = trans_res.get("language") or source_lang

    # Si la langue détectée est déjà la langue cible, on peut sauter la traduction
    if detected_source and detected_source == target_lang:
        translated_text = original_text
    else:
        try:
            translated_text = translate_text(original_text, detected_source, target_lang)
        except Exception:
            logging.exception("Echec de la traduction de %s vers %s", detected_source, target_lang)
            raise

    # Sauvegarder l'historique et exporter le texte (DOCX/PDF)
    try:
        storage.init_db()
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        out_dir = os.path.join(os.path.dirname(__file__), '..', 'outputs')
        os.makedirs(out_dir, exist_ok=True)
        docx_path = os.path.join(out_dir, f"{base_name}.docx")
        pdf_path = os.path.join(out_dir, f"{base_name}.pdf")
        # Exporter le texte original (on pourrait aussi exporter le texte traduit selon besoin)
        exporter.export_to_docx(original_text, docx_path)
        exporter.export_to_pdf(original_text, pdf_path)
        record = {
            'audio_path': audio_path,
            'detected_lang': detected_source,
            'original_text': original_text,
            'translated_text': translated_text,
            'docx_path': docx_path,
            'pdf_path': pdf_path,
        }
        storage.save_record(record)
    except Exception:
        # Ne bloquer pas la pipeline principale si l'export ou la sauvegarde échoue
        logging.exception("Impossible de sauvegarder/exporter la transcription pour %s", audio_path)

    return {"original_text": original_text, "detected_source": detected_source, "translated_text": translated_text}
