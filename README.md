# 🎤 SIMONE v2.0

**Système Intelligent de Médiation et d'Optimisation pour la Navigation et l'Échange**

> 🚀 Application de traduction vocale en temps réel avec Intelligence Artificielle

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

## 📋 Table des Matières

- [✨ Fonctionnalités](#-fonctionnalités)
- [🎬 Démo](#-démo)
- [🛠️ Technologies](#️-technologies)
- [📦 Installation](#-installation)
- [🚀 Utilisation](#-utilisation)
- [📁 Structure du Projet](#-structure-du-projet)
- [📚 Documentation](#-documentation)
- [🤝 Contribution](#-contribution)

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| 🎤 **Capture Vocale** | Enregistrement audio directement depuis le navigateur |
| 📝 **Transcription IA** | Conversion parole-texte avec OpenAI Whisper |
| 🌍 **Traduction Neuronale** | Traduction automatique avec Helsinki-NLP Marian |
| 🔊 **Synthèse Vocale** | Écoute de la traduction (Text-to-Speech) |
| ⚡ **Temps Réel** | Communication WebSocket pour résultats instantanés |
| 📄 **Export** | Sauvegarde en PDF/DOCX + Historique SQLite |

### 🌐 Langues Supportées

| Langue | Code |
|--------|------|
| 🇫🇷 Français | `fr` |
| 🇬🇧 English | `en` |
| 🇪🇸 Español | `es` |
| 🇩🇪 Deutsch | `de` |
| 🇮🇹 Italiano | `it` |
| 🇵🇹 Português | `pt` |

---

## 🎬 Démo

### Interface Web

```
┌─────────────────────────────────────────────────────────────┐
│  🎤 SIMONE - Traduction en Temps Réel                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🇫🇷 Français    ⟷    🇬🇧 English                          │
│                                                             │
│   ┌─────────────┐         ┌─────────────┐                  │
│   │ Bonjour,    │   🎙️   │ Hello,      │                  │
│   │ comment     │         │ how are     │                  │
│   │ allez-vous? │         │ you?        │                  │
│   └─────────────┘         └─────────────┘                  │
│                                                             │
│              [🔊 Écouter]  [📋 Copier]                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies

### Backend
- **Python 3.10+** - Langage principal
- **FastAPI** - Framework web asynchrone
- **Uvicorn** - Serveur ASGI
- **SQLite** - Base de données

### Intelligence Artificielle
- **OpenAI Whisper** - Reconnaissance vocale (ASR)
- **Helsinki-NLP Marian** - Traduction neuronale (NMT)
- **PyTorch** - Framework deep learning
- **Transformers** - Bibliothèque Hugging Face

### Frontend
- **HTML5 / CSS3 / JavaScript**
- **Web Audio API** - Capture microphone
- **WebSocket** - Communication temps réel
- **Web Speech API** - Synthèse vocale

---

## 📦 Installation

### Prérequis

- Python 3.10 ou supérieur
- FFmpeg (pour le traitement audio)
- 8 Go RAM minimum (16 Go recommandé)

### Étapes

```bash
# 1. Cloner le repository
git clone https://github.com/dansenga/simone-projet.git
cd simone-projet

# 2. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/macOS
# ou: venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Installer FFmpeg (si non installé)
# Ubuntu/Debian
sudo apt install ffmpeg
# macOS
brew install ffmpeg
# Windows (via chocolatey)
choco install ffmpeg
```

---

## 🚀 Utilisation

### Lancer l'Application Web (Recommandé)

```bash
# Démarrer le serveur
python api_v2.py

# Ouvrir dans le navigateur
# http://localhost:8000
```

### Mode CLI (Version Legacy)

```bash
# Définir le modèle Whisper (optionnel)
export WHISPER_MODEL=tiny  # tiny, base, small, medium, large

# Lancer le script CLI
python app.py
```

### API REST

```bash
# Test de santé
curl http://localhost:8000/health

# Traduction de texte
curl -X POST http://localhost:8000/api/translate \
  -H "Content-Type: application/json" \
  -d '{"text": "Bonjour le monde", "source_lang": "fr", "target_lang": "en"}'
```

---

## 📁 Structure du Projet

```
simone-projet/
│
├── 📄 api_v2.py              # 🚀 Serveur FastAPI principal
├── 📄 api.py                 # API version legacy
├── 📄 app.py                 # Application CLI
├── 📄 requirements.txt       # Dépendances Python
├── 📄 README.md              # Ce fichier
├── 📄 DOCUMENTATION.md       # Documentation complète
│
├── 📁 backend/               # Logique métier
│   ├── 📄 realtime.py       # Traduction temps réel (WebSocket)
│   ├── 📄 speech_to_text.py # Transcription (Whisper)
│   ├── 📄 translation.py    # Traduction (Marian)
│   ├── 📄 pipeline.py       # Orchestration
│   ├── 📄 storage.py        # Base de données SQLite
│   └── 📄 export.py         # Export PDF/DOCX
│
├── 📁 frontend/              # Interface web
│   ├── 📄 index.html        # Page principale
│   ├── 📄 app.js            # Logique JavaScript
│   └── 📄 styles.css        # Styles CSS
│
├── 📁 Presentation/          # Présentation du projet
│   ├── 📄 index.html        # Slides HTML
│   ├── 📄 styles.css        # Styles
│   └── 📄 script.js         # Navigation
│
├── 📁 data/                  # Données (créé automatiquement)
│   └── 📄 history.db        # Historique SQLite
│
└── 📁 outputs/               # Fichiers exportés
```

---

## 📚 Documentation

Une documentation complète est disponible dans le fichier [DOCUMENTATION.md](DOCUMENTATION.md) :

- 🏗️ Architecture technique
- 🔧 Configuration détaillée
- 📖 Explication du code
- 🔌 API REST & WebSocket
- 🔄 Flux de données
- 🐛 Dépannage

### Présentation

Une présentation interactive est disponible dans le dossier `Presentation/` :

```bash
# Ouvrir la présentation dans le navigateur
firefox Presentation/index.html
# ou
google-chrome Presentation/index.html
```

---

## ⚙️ Configuration

### Variables d'Environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `WHISPER_MODEL` | Modèle Whisper (tiny/base/small/medium/large) | `tiny` |
| `HOST` | Adresse du serveur | `0.0.0.0` |
| `PORT` | Port du serveur | `8000` |

### Modèles Whisper

| Modèle | RAM | Précision | Vitesse |
|--------|-----|-----------|---------|
| `tiny` | ~1 Go | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| `base` | ~1 Go | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| `small` | ~2 Go | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| `medium` | ~5 Go | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| `large` | ~10 Go | ⭐⭐⭐⭐⭐ | ⭐ |

---

## 🤝 Contribution

Les contributions sont les bienvenues ! 

1. Fork le projet
2. Créer une branche (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -m 'Ajout nouvelle fonctionnalité'`)
4. Push la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 🙏 Remerciements

- [OpenAI](https://openai.com) pour Whisper
- [Helsinki-NLP](https://huggingface.co/Helsinki-NLP) pour les modèles Marian
- [FastAPI](https://fastapi.tiangolo.com) pour le framework web
- [Hugging Face](https://huggingface.co) pour Transformers

---

<p align="center">
  <strong>🎤 SIMONE v2.0</strong><br>
  <em>Projet Académique & Professionnel — Janvier 2026</em>
</p>


