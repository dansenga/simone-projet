import sqlite3
import os
from typing import Optional, Dict

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'history.db')


def init_db(db_path: Optional[str] = None):
    """Initialise la base de données si nécessaire.

    Crée le dossier `data/` à la racine du projet et la table `transcripts`.
    """
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        '''
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
        '''
    )
    conn.commit()
    conn.close()


def save_record(record: Dict[str, str], db_path: Optional[str] = None) -> int:
    """Enregistre un enregistrement de transcription/traduction.

    record keys: audio_path, detected_lang, original_text, translated_text, docx_path, pdf_path
    Returns the inserted row id.
    """
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        '''
        INSERT INTO transcripts (audio_path, detected_lang, original_text, translated_text, docx_path, pdf_path)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            record.get('audio_path'),
            record.get('detected_lang'),
            record.get('original_text'),
            record.get('translated_text'),
            record.get('docx_path'),
            record.get('pdf_path'),
        )
    )
    conn.commit()
    rowid = cur.lastrowid
    conn.close()
    return rowid


def get_all(db_path: Optional[str] = None):
    path = db_path or DB_PATH
    if not os.path.exists(path):
        return []
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute('SELECT id, audio_path, timestamp, detected_lang, original_text, translated_text, docx_path, pdf_path FROM transcripts ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows
