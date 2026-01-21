"""
Module de traduction utilisant les modèles Marian (Helsinki-NLP).

Le module expose `translate_text` comme fonction simple pour traduire
un texte d'une langue source vers une langue cible. Les modèles sont
mis en cache par paire (source,target) pour éviter de recharger.
"""

import logging
import os
from typing import Dict, Tuple

from transformers import MarianMTModel, MarianTokenizer

# Temps de téléchargement raisonnable pour HF hub
os.environ.setdefault("HF_HUB_DOWNLOAD_TIMEOUT", "120")


class Translator:
    """Wrapper autour d'un modèle Marian pour une paire de langues.

    - Caching simple par paire (source_lang, target_lang)
    - Chargement paresseux dans `__init__`
    - Pour usage local/POC ; en prod, privilégier un service dédié.
    """

    _cache: Dict[Tuple[str, str], "Translator"] = {}

    def __new__(cls, source_lang: str = "en", target_lang: str = "fr"):
        key = (source_lang, target_lang)
        if key in cls._cache:
            return cls._cache[key]
        inst = super().__new__(cls)
        cls._cache[key] = inst
        return inst

    def __init__(self, source_lang: str = "en", target_lang: str = "fr"):
        # Eviter de réinitialiser si déjà construit
        if hasattr(self, "initialized") and self.initialized:
            return
        self.initialized = False
        self.source_lang = source_lang
        self.target_lang = target_lang
        model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        logging.info("Chargement du modèle de traduction %s", model_name)
        try:
            self.tokenizer = MarianTokenizer.from_pretrained(model_name)
            self.model = MarianMTModel.from_pretrained(model_name)
        except Exception:
            logging.exception("Echec du chargement du modèle %s", model_name)
            raise
        self.initialized = True

    def translate(self, text: str, max_length: int = 512) -> str:
        """Traduit `text` et retourne la chaîne traduite.

        `max_length` protège contre des sorties trop longues.
        """
        if not text:
            return ""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True)
        outputs = self.model.generate(**inputs, max_length=max_length, num_beams=4)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)



def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Fonction utilitaire utilisée par la pipeline.

    Lève une exception en cas d'erreur de chargement/traduction.
    """
    try:
        translator = Translator(source_lang=source_lang, target_lang=target_lang)
        return translator.translate(text)
    except Exception:
        logging.exception("La traduction a échoué pour %s -> %s", source_lang, target_lang)
        raise
