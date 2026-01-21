import os
import logging
import argparse
from backend.pipeline import audio_to_translated_text
from backend import storage
from backend.speech_to_text import real_time_transcription


# Application CLI minimale
# - Liste l'historique des transcriptions enregistrées
# - Puis exécute la pipeline sur le fichier audio de démonstration


def list_history():
    """Affiche l'historique des transcriptions (SQLite) de façon lisible."""
    try:
        rows = storage.get_all()
    except Exception:
        logging.exception("Impossible de lire l'historique")
        rows = []

    if not rows:
        print("Aucun historique trouvé.")
        return

    print("\n=== HISTORIQUE DES TRANSCRIPTIONS ===")
    for row in rows:
        id_, audio_path, timestamp, detected_lang, original_text, translated_text, docx_path, pdf_path = row
        print(f"[{id_}] {timestamp} — {audio_path} (lang détectée: {detected_lang})")
        snippet = (original_text or "").replace('\n', ' ')[:200]
        print(f"    Extrait: {snippet}")
        if docx_path:
            print(f"    DOCX: {docx_path}")
        if pdf_path:
            print(f"    PDF: {pdf_path}")



def parse_args():
    parser = argparse.ArgumentParser(description="SIMONE - Transcription & Traduction")
    parser.add_argument("--mic", action="store_true", help="Activer la transcription en temps réel depuis le micro")
    parser.add_argument("--max-duration", type=int, default=600, help="Durée max en secondes pour l'enregistrement micro (par défaut 600s)")
    parser.add_argument("--audio", type=str, default="audio/samples/test2.mp3", help="Chemin du fichier audio à traiter (mode fichier)")
    parser.add_argument("--source", type=str, default=None, help="Code langue source (ex: fr, en). Si non fourni: détection automatique")
    parser.add_argument("--target", type=str, default="fr", help="Code langue cible pour la traduction (par défaut: fr)")
    return parser.parse_args()


def main():
    """Point d'entrée principal pour la traduction audio."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    args = parse_args()

    if args.mic:
        # Mode micro: possibilité de limite de durée; on utilise RecordingSession pour contrôle
        try:
            from backend.speech_to_text import RecordingSession
            session = RecordingSession(max_seconds=args.max_duration, language=args.source)
            print(f"Démarrage du micro (max {args.max_duration}s). Appuyez sur Ctrl+C pour arrêter.")
            session.start()
            try:
                # on attend que l'utilisateur interrompt
                while session.is_recording():
                    import time as _t
                    _t.sleep(0.5)
            except KeyboardInterrupt:
                print("\nArrêt manuel demandé...")
                session.stop()

            result = session.get_result()
            if result:
                print("\n=== TRANSCRIPTION (session micro) ===")
                print(result.get('text', ''))
                print("Langue détectée:", result.get('language'))
        except Exception as e:
            logging.exception("Erreur en mode micro: %s", e)
        return

    # Mode fichier: lister l'historique puis exécuter la pipeline
    list_history()

    audio_path = args.audio
    if not os.path.exists(audio_path):
        logging.error("Fichier introuvable: %s", audio_path)
        return

    try:
        result = audio_to_translated_text(audio_path=audio_path, source_lang=args.source, target_lang=args.target)
        print("\n=== TEXTE ORIGINAL (transcrit) ===")
        print(result.get("original_text", ""))
        print("\n=== LANGUE DÉTECTÉE ===")
        print(result.get("detected_source", "unknown"))
        print("\n=== TEXTE TRADUIT ===")
        print(result.get("translated_text", ""))
    except Exception as e:
        logging.exception("Erreur lors de la traduction: %s", e)


if __name__ == "__main__":
    main()
