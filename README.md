<div align="center">

# 🎵 TAC MP4 Studio

**Générateur automatique de vidéos musicales réactives**

*Transforme n'importe quel audio en clip visuel professionnel en quelques clics.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1F6FEB?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![Version](https://img.shields.io/badge/Version-1.5.1-7c3aed?style=for-the-badge)](#-roadmap)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

---

## ✦ Accueil

<div align="center">

![TAC MP4 Studio — Page d'accueil](https://i.imgur.com/cHnKviv.png)

*Page d'accueil — interface dark CustomTkinter*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image de pochette. Spectre, fumée, particules, pochette animée, disque vinyle — tout est synchronisé à la musique frame par frame via une analyse audio bas niveau.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel **sans abonnement, sans upload, 100% offline**.

---

## 🎬 Rendus

<div align="center">

![Import musique et pochette](https://i.imgur.com/cRNg6WM.png)

*Import audio et pochette · Drag & Drop ou sélection fichier*

</div>

<div align="center">

![Interface principale](https://i.imgur.com/hVCWmPk.png)

*Éditeur — waveform interactive · preview live · 5 onglets de réglages · presets 1 clic*

</div>

<div align="center">

![Pochette + Vinyle rotatif](https://i.imgur.com/VaMRIP6.png)

*Mode Vinyle — pochette sleeve au premier plan · disque rotatif réactif aux beats*

</div>

<div align="center">

![Panel export](https://i.imgur.com/WldOrGr.png)

*Panel export — CHECK · SHORT · COMPLET · cards cliquables*

</div>

---

## ⚡ Fonctionnalités

### 🎧 Analyse audio réactive
- Extraction frame par frame : **RMS · kick · basse · mids · aigus**
- Oscilloscope temps réel (forme d'onde brute)
- Vectorisé numpy + librosa — ~50× plus rapide qu'une boucle Python

### 📊 10 styles de spectre

| Style | Description |
|---|---|
| **Barres premium** | Barres blanches montantes |
| **Barres néon** | Dégradé rouge→bleu avec halo lumineux |
| **Cercle radial** | Lignes rayonnantes autour de la pochette |
| **Cercle + barres** | Orbe + spectre bas combinés |
| **Symétrie miroir** | Barres haut/bas — idéal 9:16 |
| **Arc plasma** | Demi-cercle coloré avec glow |
| **Onde plasma** | Waveform épaisse + halo + reflet |
| **Waveform miroir** | Forme d'onde symétrique |
| **Oscilloscope** | Forme d'onde brute temps réel |
| **Ligne fine** | Ligne monochrome minimaliste |

Tous les styles supportent la **couleur personnalisée** ou l'extraction automatique depuis la pochette.

### 🎵 Mode Vinyle
- Composition pochette sleeve (premier plan) + disque rotatif (arrière-plan)
- Deux styles : **Image** (pochette visible sur le disque) ou **Noir classique** (sillons + label central)
- Rotation réactive — basses = accélération · kicks = saccades

### 🌫 Effets visuels
- **Fumée** — blobs animés (Légère · Cinématique · Dense)
- **Particules** — réactives aux kicks et aux aigus
- **Fond flottant** — dérive sinusoïdale réactive aux basses
- **Fond dégradé** — color pickers + **couleurs aléatoires vives**
- **Vignette** — masque précalculé

### 🚀 3 modes d'export

```
CHECK   →  15 secondes  ·  1920×1080 horizontal  ·  Aperçu rapide
SHORT   →  1 minute     ·  1080×1920 vertical    ·  Milieu du son  (Reels · TikTok · Shorts)
COMPLET →  Son entier   ·  1920×1080 horizontal  ·  YouTube · SoundCloud
```

Le mode **SHORT** extrait automatiquement 60 secondes centrées sur le milieu de la musique.

---

## 🆕 Historique des mises à jour

### v1.5.1 — Fix & polish
- 🐛 Fix ligne parasite sur la pochette d'album (artefact `rounded_rectangle`)
- 🏠 Page d'accueil redesignée avec fond splitté et pills de features
- 🚀 Panel export redesigné en cards cliquables avec badges colorés
- 🔢 Version visible dans la fenêtre Réglages (⚙)

### v1.5.0 — Update 5 · Couleurs & fond flottant

<div align="center">

![Fond dégradé configurable](https://i.imgur.com/K4p0h4l.png)

</div>

- 🎨 Couleur du spectre personnalisable + extraction auto depuis la pochette
- 🌊 Fond flottant animé (dérive sinusoïdale réactive aux basses)
- 📊 Oscilloscope — 10ème style de spectre (forme d'onde brute)
- ⚫ Vinyle noir classique ou image au choix
- 🎲 Bouton couleurs aléatoires vives pour le dégradé
- ✨ 5 nouveaux presets : Vinyl Classic · Vinyl Gold · Acid Wave · Purple Dream · Midnight Vinyl

### v1.4.0 — Update 4 · Disque vinyle

<div align="center">

![Pochette + Vinyle rotatif](https://i.imgur.com/VaMRIP6.png)

</div>

- 🎵 Composition pochette sleeve + disque vinyle rotatif réactif
- Ombre portée · sillons concentriques · reflet statique · trou de broche

### v1.3.0 — Update 3 · Fond dégradé · Miniatures · Plein écran
- 🎨 Fond dégradé configurable avec color pickers
- 🖼 Miniatures automatiques dans l'historique après chaque export
- ⛶ Mode plein écran preview (F11 ou double-clic)

### v1.2.0 — Update 2 · Waveform · Artiste/Titre · Raccourcis
- 🎚 Waveform globale cliquable pour naviguer dans le son
- ✍ Champs Artiste + Titre séparés avec rendu différencié
- ⌨ Raccourcis clavier : Espace · R · F11 · Échap

### v1.1.0 — Update 1 · Switch format · Drag & Drop
- 🔄 Switch preview 16:9 ↔ 9:16
- 📂 Drag & Drop audio et image
- ⚠️ Vérification FFmpeg au démarrage
- ✅ Validation nom projet avant export

### v1.0.0 — Release initiale
- 9 styles de spectre · fumée · particules · 3 modes export · interface CustomTkinter

---

## 🖥️ Interface

L'éditeur est organisé en **5 onglets** accessibles sans scroll :

| Onglet | Contenu |
|:---:|---|
| ⚡ | Presets intégrés + **Mes presets** (sauvegarde perso) |
| 🎵 | Ambiance · Vinyle · Texte Artiste/Titre |
| 🎨 | Fond photo ou dégradé · Fond flottant |
| 📊 | Style spectre · Taille · Couleur |
| 🚀 | Export · Dossier · Nom projet · CHECK/SHORT/COMPLET |

---

## 🆚 Alternative gratuite à Tuneform

TAC MP4 Studio est une **alternative open source et gratuite à [Tuneform](https://tuneform.com)**.

L'objectif n'est pas de le concurrencer. C'est un outil pensé pour mes propres besoins, que je partage librement.

**Ce que TAC propose :**
- 100% offline — tes fichiers ne quittent pas ton PC
- Gratuit sans limite de durée ni de rendu
- Open source — modifiable à volonté
- Presets sauvegardables personnalisés

**Ce que Tuneform fait mieux :**
- Interface web sans installation
- Plus de templates et d'effets
- Rendu cloud plus rapide sur petites machines

Le projet est développé en **Python** (OpenCV · librosa · CustomTkinter · FFmpeg). Si l'outil devient utile à un plus grand nombre, une migration vers une stack plus performante est possible — mais Python fait le job pour l'instant.

---

## 📦 Installation

### 1. Prérequis

**Python 3.11+** → [python.org](https://www.python.org/downloads/)

**FFmpeg** → [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)

```
→ Télécharger ffmpeg-release-essentials.zip
→ Extraire dans C:\ffmpeg\
→ Ajouter C:\ffmpeg\bin au PATH Windows
→ Vérifier : ffmpeg -version dans un terminal
```

### 2. Installer

```bash
git clone https://github.com/DoktorP3st/tac-mp4-studio.git
cd tac-mp4-studio
pip install -r requirements.txt
python main.py
```

### 3. Dépendances

| Package | Rôle | Obligatoire |
|---|---|---|
| `numpy` | Calculs matriciels | ✅ |
| `opencv-python` | Rendu frame | ✅ |
| `Pillow` | Texte · fonts · compositing | ✅ |
| `librosa` | Analyse audio + waveform | ✅ |
| `soundfile` | Lecture durée audio | ✅ |
| `customtkinter` | Interface modern dark | ✅ |
| `tkinterdnd2` | Drag & Drop | ⚡ Optionnel |

---

## 🖥️ Utilisation

```
1. Lancer python main.py
2. CRÉER → choisir la musique (ou glisser le fichier)
3. Choisir la pochette (ou la glisser)
4. Preset rapide dans l'onglet ⚡ → APPLIQUER
5. Ajuster dans les onglets 🎵 🎨 📊
6. Cliquer sur la waveform pour positionner la preview
7. Espace pour lancer la preview audio synchronisée
8. Onglet 🚀 → nom projet → CHECK / SHORT / COMPLET → GÉNÉRER
```

---

## 🗺️ Roadmap

| Version | Status | Contenu |
|---|---|---|
| **v1.0** | ✅ | Release initiale |
| **v1.1** | ✅ | Switch 16:9↔9:16 · Drag & Drop · FFmpeg check |
| **v1.2** | ✅ | Waveform · Artiste/Titre · Raccourcis clavier |
| **v1.3** | ✅ | Fond dégradé · Miniatures · Plein écran |
| **v1.4** | ✅ | Disque vinyle rotatif |
| **v1.5** | ✅ | Couleur spectre · Fond flottant · Oscilloscope |
| **v1.5.1** | ✅ | Fix glitch pochette · Accueil redesigné · Export cards |
| **v1.6** | 📋 | Format carré 1:1 · Export par lots |

---

## 🎁 Packaging Windows (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "TAC_MP4_Studio" --collect-data librosa main.py
```

Exécutable dans `dist/TAC_MP4_Studio.exe`.

---

## 🏗️ Architecture

```
tac_mp4_studio/
├── main.py
├── app/
│   ├── config.py       ← persistance AppData
│   ├── presets.py      ← 11 presets · 10 styles spectre
│   ├── models.py       ← RenderSettings
│   ├── audio.py        ← analyse librosa vectorisée
│   ├── particles.py    ← FloatingParticle · SmokeBlob
│   ├── renderer.py     ← rendu frame · vinyle · 10 spectres
│   ├── exporter.py     ← pipeline FFmpeg
│   └── ui/
│       └── app.py      ← fenêtre CustomTkinter · 5 onglets
└── requirements.txt
```

---

## 📄 Licence

MIT — libre d'utilisation, modification et distribution.

---

<div align="center">

Fait avec 🎧 par **DoktorP3st**

*Si ce projet t'a servi, une étoile ⭐ c'est toujours apprécié.*

---

### 🌐 Retrouve-nous

| | Canal | Lien |
|:---:|:---|:---|
| 🟣 | **Twitch — DoktorP3st** | [twitch.tv/doktorp3st](https://www.twitch.tv/doktorp3st) |
| 🟣 | **Twitch — Paglorieux** | [twitch.tv/paglorieux](https://www.twitch.tv/paglorieux) |
| 🔴 | **YouTube — TheAuraliaCryia** | [youtube.com/@TheAuraliaCryia](https://www.youtube.com/@TheAuraliaCryia) |
| 🔴 | **YouTube — Paglorieux** | [youtube.com/@Paglorieux](https://www.youtube.com/@Paglorieux) |

</div>
