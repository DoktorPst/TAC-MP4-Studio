<div align="center">

# 🎵 TAC MP4 Studio

**Générateur automatique de vidéos musicales réactives**

*Transforme n'importe quel audio en clip visuel professionnel en quelques clics.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1F6FEB?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)
[![Update](https://img.shields.io/badge/Update-2.0-7c3aed?style=for-the-badge)](#-roadmap)

</div>

---

## ✦ Accueil

<div align="center">

![TAC MP4 Studio — Page d'accueil](https://i.imgur.com/cHnKviv.png)

*Page d'accueil — interface dark CustomTkinter*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image de pochette. Spectre, fumée, particules, pochette animée — tout est synchronisé à la musique frame par frame via une analyse audio bas niveau.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel sans toucher à After Effects ou Premiere.

---

## 🚀 Workflow en 3 étapes

<div align="center">

![Import musique et pochette](https://i.imgur.com/cRNg6WM.png)

*Étape 1 & 2 — Import audio et pochette · Drag & Drop ou sélection fichier*

</div>

---

## 🖥️ Interface principale

<div align="center">

![Interface principale 1920x1080](https://i.imgur.com/hVCWmPk.png)

*Éditeur complet — waveform interactive · preview live · 9 styles de spectre · presets 1 clic*

</div>

---

## 📱 Format SHORT vertical

<div align="center">

![Rendu SHORT vertical 1080x1920](https://i.imgur.com/hVCWmPk.png)

*Format 1080×1920 — Milieu automatique du son · Idéal Instagram Reels · TikTok · YouTube Shorts*

</div>

---

## 🚀 Export

<div align="center">

![Panel export](https://i.imgur.com/WldOrGr.png)

*Panel export — CHECK 15s · SHORT 1min vertical · COMPLET son entier*

</div>

---

## ⚡ Fonctionnalités

### 🎧 Analyse audio réactive
- Extraction frame par frame : **RMS · kick · basse · mids · aigus**
- Synchronisation parfaite son ↔ visuel
- Vectorisé numpy + librosa — ~50× plus rapide qu'une boucle Python

### 📊 9 styles de spectre

| Style | Description | Format |
|---|---|---|
| **Barres premium** | Barres blanches montantes | 16:9 · 9:16 |
| **Barres néon** | Dégradé rouge→bleu avec halo lumineux | 16:9 · 9:16 |
| **Cercle radial** | Lignes rayonnantes autour de la pochette | 16:9 · 9:16 |
| **Cercle + barres** | Orbe + spectre bas combinés | 16:9 · 9:16 |
| **Symétrie miroir** | Barres symétriques haut/bas | ✅ Idéal 9:16 |
| **Arc plasma** | Demi-cercle coloré avec glow | 16:9 · 9:16 |
| **Onde plasma** | Waveform épaisse + halo + reflet | 16:9 · 9:16 |
| **Waveform miroir** | Forme d'onde symétrique simple | 16:9 · 9:16 |
| **Ligne fine** | Ligne monochrome minimaliste | 16:9 · 9:16 |

### 🌫 Effets visuels
- **Fumée** — blobs animés avec turbulence organique (Légère · Cinématique · Dense)
- **Particules** — réactives aux kicks et aux aigus
- **Pochette** — pulse sur les beats · halo glow · repositionnement automatique en 9:16
- **Vignette** — masque précalculé par résolution, zéro overhead
- **Texte** — champs Artiste et Titre séparés · tailles différentes · ombre réactive aux kicks

### 🚀 3 modes d'export

```
CHECK   →  15 secondes  ·  1920×1080 horizontal  ·  Aperçu rapide
SHORT   →  1 minute     ·  1080×1920 vertical    ·  Milieu du son  (Reels · TikTok · Shorts)
COMPLET →  Son entier   ·  1920×1080 horizontal  ·  YouTube · SoundCloud
```

> Le mode **SHORT** extrait automatiquement 60 secondes centrées sur le milieu de la musique.

---

## 🆕 Dernières mises à jour

### Update 2 — Waveform · Artiste/Titre · Raccourcis clavier

<div align="center">

![Fond dégradé configurable](https://i.imgur.com/K4p0h4l.png)

*Fond dégradé — color pickers natifs · aperçu live dans la preview*

</div>

**🎚 Waveform globale cliquable**
Une barre de forme d'onde apparaît sous la preview dès l'ouverture de l'éditeur. Elle représente la totalité du son, avec la zone preview surlignée en violet. Un **clic** déplace le point de départ de la preview à cet instant. Pendant la lecture, un curseur vert avance en temps réel.

**✍ Artiste + Titre séparés**
Deux champs distincts dans le panneau texte. Sur la vidéo, l'artiste s'affiche en plus grand et bold au-dessus, avec une fine ligne de séparation, et le titre en dessous. Un aperçu s'affiche en temps réel sous les champs.

**⌨ Raccourcis clavier**

| Touche | Action |
|---|---|
| `Espace` | Play / Pause preview audio |
| `R` | Recharger la preview |
| `Échap` | Retour à l'accueil |

---

### Update 1 — Switch format · FFmpeg check · Validation · Drag & Drop

**🔄 Switch preview 16:9 ↔ 9:16** — Bouton toggle dans les contrôles de preview. La pochette et le spectre se repositionnent automatiquement selon le format.

**⚠️ Vérification FFmpeg au démarrage** — Bannière orange non-bloquante si `ffmpeg` ou `ffplay` est absent du PATH.

**✅ Nom projet obligatoire** — Validation inline avant l'export. Plus de popup surprise en plein workflow.

**📂 Drag & Drop** — Glisse directement tes fichiers audio et image depuis l'Explorateur Windows sur la fenêtre.

---

---

## 🆕 Update 4 — Pochette + Vinyle rotatif

Toggle **🎵 Disque vinyle** dans la section Ambiance de l'éditeur.

Au lieu d'afficher la pochette simple, le logiciel génère une composition à deux plans :

<div align="center">

![Pochette + Vinyle rotatif](https://i.imgur.com/VaMRIP6.png)

*Composition pochette sleeve au premier plan · vinyle rotatif à droite · réactif aux beats*

</div>

**Avant-plan — Pochette sleeve**
La pochette s'affiche avec coins arrondis, fine bordure lumineuse et micro-effet 3D. Elle pulse sur les beats.

**Arrière-plan — Vinyle rotatif**
Un disque vinyle sort à droite derrière la pochette — environ 50% visible. Il tourne en continu et réagit à la musique : basses = accélération, kicks = saccades. Les sillons restent fixes (comme un vrai vinyle), le reflet crescent aussi. Trou de broche présent.

Compatible **16:9 et 9:16** — la composition s'adapte automatiquement au format vertical.

---

## 🆚 Alternative gratuite à Tuneform

TAC MP4 Studio est une **alternative open source et gratuite à [Tuneform](https://tuneform.com)** — le générateur de vidéos musicales réactives en ligne.

L'objectif n'est pas de le concurrencer ou de faire mieux. C'est un outil pensé pour mes propres besoins, que je partage librement. Si Tuneform correspond à ce que tu cherches, vas-y. Si tu veux quelque chose de **gratuit, local, sans abonnement, sans upload de tes fichiers sur un serveur**, TAC MP4 Studio est fait pour ça.

**Ce que TAC propose que Tuneform ne fait pas :**
- 100% offline — tes fichiers ne quittent pas ton PC
- Open source — modifiable à volonté
- Gratuit sans limite de durée ni de rendu

**Ce que Tuneform fait mieux pour l'instant :**
- Interface web sans installation
- Plus de templates et d'effets
- Rendu cloud plus rapide sur petites machines

Le projet est développé en **Python** (OpenCV · librosa · CustomTkinter · FFmpeg). C'est le bon choix pour prototyper vite et rester accessible. Si l'outil devient utile à un plus grand nombre, je n'exclus pas de migrer vers une stack plus performante ou multiplateforme — mais pour l'instant Python fait le job.

> Tu utilises TAC et tu as des idées d'amélioration ? Ouvre une issue ou une PR — toutes les contributions sont les bienvenues.

---

## 📦 Installation

### 1. Prérequis

**Python 3.11+**
```
https://www.python.org/downloads/
```

**FFmpeg** — obligatoire pour l'export et la preview audio
```
https://www.gyan.dev/ffmpeg/builds/
→ Télécharger : ffmpeg-release-essentials.zip
→ Extraire dans : C:\ffmpeg\
→ Ajouter au PATH : C:\ffmpeg\bin
```

> Vérification : ouvre un terminal et tape `ffmpeg -version`

### 2. Cloner et installer

```bash
git clone https://github.com/DoktorP3st/tac-mp4-studio.git
cd tac-mp4-studio

pip install -r requirements.txt

python main.py
```

### 3. Dépendances

| Package | Rôle | Obligatoire |
|---|---|---|
| `numpy` | Calculs matriciels audio + vidéo | ✅ |
| `opencv-python` | Rendu frame OpenCV | ✅ |
| `Pillow` | Texte, fonts, compositing | ✅ |
| `librosa` | Analyse audio + waveform | ✅ |
| `soundfile` | Lecture durée audio | ✅ |
| `customtkinter` | Interface modern dark | ✅ |
| `tkinterdnd2` | Drag & drop fichiers | ⚡ Optionnel |

---

## 🖥️ Utilisation

```
1. Lancer python main.py
2. CRÉER  →  choisir la musique  (ou glisser le fichier sur la fenêtre)
3. Choisir la pochette  (ou la glisser directement)
4. Choisir un preset visuel dans le panneau droit
5. Cliquer sur la waveform pour positionner la preview
6. Appuyer sur Espace pour lancer la preview audio synchronisée
7. Basculer 16:9 ↔ 9:16 pour voir le rendu SHORT
8. Renseigner Artiste et/ou Titre
9. Saisir le nom du projet  →  CHECK / SHORT / COMPLET  →  GÉNÉRER
```

---

## 🏗️ Architecture

```
tac_mp4_studio/
├── main.py                  ← entry point (5 lignes)
├── app/
│   ├── config.py            ← persistance AppData  (écriture atomique)
│   ├── presets.py           ← constantes & 6 presets visuels
│   ├── models.py            ← RenderSettings  (artiste + titre)
│   ├── audio.py             ← analyse librosa vectorisée
│   ├── particles.py         ← FloatingParticle · SmokeBlob
│   ├── renderer.py          ← 9 spectres · artiste/titre · adaptation 9:16
│   ├── exporter.py          ← pipeline FFmpeg  (bug SHORT offset corrigé)
│   └── ui/
│       ├── app.py           ← fenêtre CustomTkinter  (Update 1 + 2)
│       └── widgets.py       ← ScrollFrame
└── requirements.txt
```

---

## 🗺️ Roadmap

| Update | Status | Contenu |
|---|---|---|
| **Update 1** | ✅ Stable | Switch preview 16:9↔9:16 · Vérif FFmpeg · Nom obligatoire · Drag & Drop |
| **Update 2** | ✅ Stable | Waveform cliquable · Artiste + Titre séparés · Raccourcis clavier |
| **Update 3** | ✅ Stable | Fond dégradé · Miniatures historique · Mode plein écran preview |
| **Update 4** | ✅ Stable | Pochette sleeve + Vinyle rotatif réactif |
| **Update 5** | 📋 Planifié | Couleur du spectre · Fond flottant · Oscilloscope |

---

## 🎁 Packaging Windows (.exe)

```bash
pip install pyinstaller

pyinstaller --onefile --noconsole \
  --name "TAC_MP4_Studio" \
  --collect-data librosa \
  main.py
```

Exécutable dans `dist/TAC_MP4_Studio.exe` (~100MB avec toutes les dépendances).

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
