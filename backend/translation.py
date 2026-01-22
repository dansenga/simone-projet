"""
Module de traduction utilisant les modèles Marian (Helsinki-NLP).

Le module expose `translate_text` comme fonction simple pour traduire
un texte d'une langue source vers une langue cible. Les modèles sont
mis en cache par paire (source,target) pour éviter de recharger.
"""

import logging
import os
from typing import Dict, Tuple, Optional

from transformers import MarianMTModel, MarianTokenizer, AutoModelForSeq2SeqLM, AutoTokenizer

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



class CustomTranslator:
    """Wrapper pour un modèle de traduction personnalisé sauvegardé dans un dossier.

    Le modèle est identifié uniquement par le chemin `model_dir` (par exemple un
    modèle Marian finetuné et sauvegardé depuis Colab).
    """

    _cache: Dict[str, "CustomTranslator"] = {}

    def __new__(cls, model_dir: str):
        if model_dir in cls._cache:
            return cls._cache[model_dir]
        inst = super().__new__(cls)
        cls._cache[model_dir] = inst
        return inst

    def __init__(self, model_dir: str):
        if hasattr(self, "initialized") and self.initialized:
            return
        self.initialized = False
        self.model_dir = model_dir
        logging.info("Chargement du modèle de traduction personnalisé depuis %s", model_dir)
        try:
            # AutoModel/AutoTokenizer fonctionnent aussi bien avec un Marian finetuné
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dir)
        except Exception:
            logging.exception("Echec du chargement du modèle personnalisé %s", model_dir)
            raise
        self.initialized = True

    def translate(self, text: str, max_length: int = 512) -> str:
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


def translate_text_custom(text: str, model_dir: Optional[str] = None, max_length: int = 512) -> str:
    """Traduction via un modèle personnalisé sauvegardé dans un dossier.

    - `model_dir` : chemin vers le dossier du modèle finetuné (tokenizer + poids).
      Si non fourni, on lit la variable d'environnement `CUSTOM_TRANSLATION_MODEL_DIR`.
    - Levée d'exception en cas d'échec.
    """
    if model_dir is None:
        model_dir = os.getenv("CUSTOM_TRANSLATION_MODEL_DIR")

    if not model_dir:
        raise ValueError(
            "Aucun chemin de modèle personnalisé fourni (argument model_dir ou env CUSTOM_TRANSLATION_MODEL_DIR)."
        )

    try:
        translator = CustomTranslator(model_dir=model_dir)
        return translator.translate(text, max_length=max_length)
    except Exception:
        logging.exception("La traduction personnalisée a échoué avec le modèle %s", model_dir)
        raise
