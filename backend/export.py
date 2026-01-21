"""
Outils d'export pour les transcriptions : DOCX et PDF.

Fonctions :
- `export_to_docx(text, out_path)` : écrit le texte dans un fichier Word
- `export_to_pdf(text, out_path)`  : écrit le texte dans un PDF simple

Ces fonctions sont simples et visent un usage local / POC. Pour un rendu
professionnel, améliorer le wrapping, les styles et la gestion des pages.
"""

import os
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def export_to_docx(text: str, out_path: str) -> str:
    """Export simple vers DOCX.

    Chaque paragraphe est séparé par un saut de ligne dans `text`.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc = Document()
    for line in text.split('\n'):
        doc.add_paragraph(line)
    doc.save(out_path)
    return out_path


def export_to_pdf(text: str, out_path: str) -> str:
    """Export simple vers PDF en utilisant reportlab.

    Implémentation basique : wrapping naïf à 90 caractères.
    """
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    y = height - 50
    for paragraph in text.split('\n'):
        lines = []
        # simple découpage de 90 caractères pour éviter le débordement
        while len(paragraph) > 90:
            lines.append(paragraph[:90])
            paragraph = paragraph[90:]
        lines.append(paragraph)
        for ln in lines:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(40, y, ln)
            y -= 14
        y -= 8
    c.save()
    return out_path
