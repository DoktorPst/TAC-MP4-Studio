<div align="center">

<img src="img/tac.png" width="120" alt="TAC MP4 Studio Logo"/>

# TAC MP4 Studio

**Générateur automatique de vidéos musicales réactives**

*Transforme n'importe quel audio en clip visuel professionnel en quelques clics.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1F6FEB?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![Version](https://img.shields.io/badge/Version-1.7.1-7c3aed?style=for-the-badge)](#-roadmap)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

---

## ✦ Accueil

<div align="center">

![Page d'accueil TAC MP4 Studio](https://i.imgur.com/fByY54g.png)

*Page d'accueil — fond animé · spectre vivant · logo TAC*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image de pochette. Spectre, fumée, particules, pochette animée, disque vinyle — tout est synchronisé à la musique frame par frame via une analyse audio bas niveau.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel **sans abonnement, sans upload, 100% offline**.

---

## 🚀 Workflow en 3 étapes

<div align="center">

| Étape 1 | Étape 2 |
|:---:|:---:|
| ![Importer la musique](https://i.imgur.com/Avjy1Jt.png) | ![Importer la pochette](https://i.imgur.com/Tr5mobX.png) |
| Importer un fichier audio | Importer la pochette |

*MP3 · WAV · FLAC · OGG · M4A — PNG · JPG · WEBP — ou glisse directement sur la fenêtre*

</div>

---

## 🖥️ Interface principale

<div align="center">

![Interface principale TAC MP4 Studio](https://i.imgur.com/h5l3yQg.png)

*Éditeur complet — waveform interactive · preview live · 5 onglets de réglages*

</div>

---

## 🎛️ Réglages

<div align="center">

| Ambiance & Vinyle | Fond & Dégradé |
|:---:|:---:|
| ![Réglages ambiance et vinyle](https://i.imgur.com/rlaOouR.png) | ![Réglages fond](https://i.imgur.com/NY6vDl8.png) |
| Particules · Fumée · Disque vinyle | Photo floutée · Dégradé · Fond flottant |

</div>

<div align="center">

| Spectre & Couleurs | Export |
|:---:|:---:|
| ![Réglages spectre](https://i.imgur.com/t3lXSBG.png) | ![Panel export](https://i.imgur.com/x71qF4G.png) |
| 10 styles · Couleur · Auto depuis pochette | CHECK · SHORT · COMPLET |

</div>

---

## 📱 Format SHORT vertical

<div align="center">

![Format SHORT vertical 1080x1920](https://i.imgur.com/QKm14cz.png)

*Format 1080×1920 — milieu automatique du son · Reels · TikTok · YouTube Shorts*

</div>

---

## 🗂️ Historique

<div align="center">

![Historique des créations](https://i.imgur.com/8xaf3GL.png)

*Historique — miniatures auto · ouvrir dossier · ouvrir vidéo · supprimer*

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

<div align="center">

![Pochette sleeve + disque vinyle rotatif](https://i.imgur.com/nRXXVRs.png)

*Pochette sleeve au premier plan · vinyle rotatif à droite · réactif aux beats*

</div>

- Composition pochette sleeve (premier plan) + disque rotatif (arrière-plan)
- **Image** : pochette visible sur tout le disque
- **Noir classique** : sillons + label central uniquement
- Rotation réactive — basses = accélération · kicks = saccades

### 🌫 Effets visuels
- **Fumée** — blobs animés (Légère · Cinématique · Dense)
- **Particules** — réactives aux kicks et aux aigus
- **Fond flottant** — dérive sinusoïdale réactive aux basses
- **Fond dégradé** — color pickers + couleurs aléatoires vives
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

<details>
<summary><b>v1.7.1</b> — Patch optimisation ✅</summary>

- 🐛 Fix fuite mémoire animation accueil (timers accumulés)
- 🐛 Fix processus ffplay zombie sur Windows
- 🐛 Fix cache vinyle invalide à chaque frame
- 🐛 Fix crash user_presets config absente
- ⚡ Analyse audio ~40× plus rapide (raw_frames vectorisé numpy)
- 🎵 Qualité audio export améliorée (resampler SoX haute qualité)
- 🖥️ Interface sans chargement progressif (rendu en une passe)
- 🧹 Suppression code mort renderer

</details>

<details>
<summary><b>v1.7.0</b> — Spectre 3 couleurs · Flash beats ✅</summary>

- 🎨 Mode 3 couleurs : grave / médiums / aigus chacun avec sa couleur
- ⚡ Flash beats réactif sur les kicks
- 🌈 Preset Reggae amélioré : rouge/jaune/vert par bande fréquentielle
- ✨ 2 nouveaux presets : Neon Tricolor · Sunrise

</details>

<details>
<summary><b>v1.5.1</b> — Fix & Polish ✅</summary>

- 🐛 Fix ligne parasite sur la pochette d'album
- 🏠 Page d'accueil redesignée avec fond animé et logo
- 🚀 Panel export redesigné en cards cliquables avec badges colorés
- 🔢 Version visible dans la fenêtre Réglages ⚙

</details>

<details>
<summary><b>v1.5.0</b> — Couleurs · Fond flottant · Oscilloscope ✅</summary>

- 🎨 Couleur du spectre personnalisable + extraction auto depuis la pochette
- 🌊 Fond flottant animé réactif aux basses
- 📊 Oscilloscope — 10ème style de spectre
- ⚫ Vinyle noir classique ou image au choix
- 🎲 Couleurs aléatoires vives pour le dégradé
- ✨ 5 nouveaux presets : Vinyl Classic · Vinyl Gold · Acid Wave · Purple Dream · Midnight Vinyl

</details>

<details>
<summary><b>v1.4.0</b> — Disque Vinyle rotatif ✅</summary>

- 🎵 Composition pochette sleeve + disque vinyle rotatif réactif aux beats
- Deux modes : image sur le disque ou vinyle noir classique

</details>

<details>
<summary><b>v1.3.0</b> — Fond dégradé · Miniatures · Plein écran ✅</summary>

- 🎨 Fond dégradé configurable avec color pickers
- 🖼 Miniatures automatiques dans l'historique
- ⛶ Mode plein écran preview (F11 ou double-clic)

</details>

<details>
<summary><b>v1.2.0</b> — Waveform · Artiste/Titre · Raccourcis ✅</summary>

- 🎚 Waveform globale cliquable pour naviguer dans le son
- ✍ Champs Artiste + Titre séparés avec rendu différencié
- ⌨ Raccourcis clavier : Espace · R · F11 · Échap

</details>

<details>
<summary><b>v1.1.0</b> — Switch format · Drag & Drop ✅</summary>

- 🔄 Preview 16:9↔9:16
- 📂 Drag & Drop audio et image
- ⚠️ Vérification FFmpeg au démarrage
- ✅ Validation nom projet avant export

</details>

<details>
<summary><b>v1.0.0</b> — Release initiale ✅</summary>

- 9 styles de spectre · fumée · particules · 3 modes export · interface CustomTkinter

</details>

---

## 🖥️ Organisation de l'interface

L'éditeur est organisé en **5 onglets** — plus de scroll infini :

| Onglet | Contenu |
|:---:|---|
| ⚡ | Presets intégrés + **Mes presets** (sauvegarde personnalisée) |
| 🎵 | Ambiance · Vinyle · Texte Artiste/Titre |
| 🎨 | Fond photo ou dégradé · Couleurs aléatoires · Fond flottant |
| 📊 | Style spectre · Taille · Position · Couleur |
| 🚀 | Export · Dossier · Nom projet · CHECK / SHORT / COMPLET |

**Raccourcis clavier :**

| Touche | Action |
|---|---|
| `Espace` | Play / Pause preview audio |
| `R` | Recharger la preview |
| `F11` | Plein écran preview |
| `Échap` | Fermer plein écran / Retour accueil |

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

Le projet est développé en **Python** (OpenCV · librosa · CustomTkinter · FFmpeg). Si l'outil devient utile à un plus grand nombre, une migration vers une stack plus performante est envisageable.

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

## 🖥️ Utilisation rapide

```
1. python main.py
2. CRÉER → musique (ou glisser le fichier)
3. Pochette (ou glisser)
4. Preset ⚡ → APPLIQUER
5. Ajuster dans les onglets 🎵 🎨 📊
6. Clic waveform → positionner la preview
7. Espace → preview audio synchronisée
8. Onglet 🚀 → nom → CHECK / SHORT / COMPLET → GÉNÉRER
```

---

## 🗺️ Roadmap

| Version | Status | Contenu |
|---|---|---|
| v1.0 | ✅ | Release initiale |
| v1.1 | ✅ | Switch 16:9↔9:16 · Drag & Drop |
| v1.2 | ✅ | Waveform · Artiste/Titre · Raccourcis |
| v1.3 | ✅ | Fond dégradé · Miniatures · Plein écran |
| v1.4 | ✅ | Disque vinyle rotatif |
| v1.5 | ✅ | Couleur spectre · Fond flottant · Oscilloscope |
| v1.5.1 | ✅ | Fix glitch · Accueil animé · Export cards |
| v1.7.0 | ✅ | Spectre 3 couleurs · Flash beats · Nouveaux presets |
| v1.7.1 | ✅ | Patch perf · Fix fuites · UI instantanée · Audio SoX |
| **v1.8** | 📋 | Texte amélioré · Police custom · Sous-titres |

---

## 🎁 Packaging Windows (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "TAC_MP4_Studio" --collect-data librosa main.py
```

---

## 🏗️ Architecture

```
tac_mp4_studio/
├── main.py
├── img/
│   └── tac.png          ← logo
├── app/
│   ├── config.py
│   ├── presets.py        ← 11 presets · 10 styles spectre
│   ├── models.py
│   ├── audio.py
│   ├── particles.py
│   ├── renderer.py       ← rendu frame · vinyle · 10 spectres
│   ├── exporter.py
│   └── ui/
│       └── app.py        ← fenêtre · 5 onglets · presets custom
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
