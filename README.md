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

## ✦ Aperçu

<div align="center">

![TAC MP4 Studio — Interface principale](https://i.imgur.com/WghlJ6F.png)

*Interface dark CustomTkinter — waveform interactive, preview live, tout en une fenêtre*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image de pochette. Spectre, fumée, particules, pochette animée — tout est synchronisé à la musique frame par frame via une analyse audio bas niveau.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel sans toucher à After Effects ou Premiere.

---

## 🎬 Rendus

<div align="center">

![Rendu horizontal](https://i.imgur.com/Ffxk8Aw.png)

*Format horizontal 1920×1080 — YouTube · SoundCloud · Bandcamp*

</div>

<div align="center">

![Interface éditeur](https://i.imgur.com/Yo1x0k4.png)

*Éditeur avec waveform cliquable, preview live 16:9 ou 9:16, et panneau de réglages*

</div>

<div align="center">

![Presets visuels](https://i.imgur.com/moRgO9s.png)

*6 presets globaux — Dark Premium, Neon Club, Reggae Smoke, Chill Lo-Fi, Clean White, Short Vertical*

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
- **Texte** — artiste et titre séparés · tailles différentes · ombre réactive

### 🚀 3 modes d'export

```
CHECK   →  15 secondes  ·  1920×1080 horizontal  ·  Aperçu rapide
SHORT   →  1 minute     ·  1080×1920 vertical    ·  Milieu du son  (Reels · TikTok)
COMPLET →  Son entier   ·  1920×1080 horizontal  ·  YouTube · SoundCloud
```

> Le mode **SHORT** extrait automatiquement 60 secondes centrées sur le milieu de la musique.

---

## 🆕 Dernières mises à jour

### Update 2 — Waveform · Artiste/Titre · Raccourcis clavier

<div align="center">

![Panneau de réglages](https://i.imgur.com/9UAfDY2.png)

</div>

**🎚 Waveform globale cliquable**
Une barre de forme d'onde apparaît sous la preview dès l'ouverture de l'éditeur. Elle représente la totalité du son, avec la zone preview surlignée en violet. Un simple **clic** déplace le point de départ de la preview à cet instant — plus besoin de taper les secondes à la main. Pendant la lecture, un curseur vert avance en temps réel.

**✍ Artiste + Titre séparés**
Deux champs distincts dans le panneau texte. Sur la vidéo, l'artiste s'affiche en plus grand et bold au-dessus, avec une fine ligne de séparation, et le titre en dessous légèrement plus petit. Si un seul champ est rempli, l'affichage s'adapte automatiquement. Un aperçu textuel s'affiche en temps réel sous les champs.

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

**✅ Nom projet obligatoire** — Validation inline avant l'export avec message d'erreur sous le champ. Plus de popup surprise en plein workflow.

**📂 Drag & Drop** — Glisse directement tes fichiers audio et image depuis l'Explorateur Windows sur la fenêtre.

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
| `librosa` | Analyse audio (beat, spectre, bandes, waveform) | ✅ |
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
6. Espace pour lancer la preview audio synchronisée
7. Basculer 16:9 ↔ 9:16 pour voir le rendu SHORT
8. Renseigner Artiste et/ou Titre
9. Saisir le nom du projet  →  choisir CHECK / SHORT / COMPLET  →  GÉNÉRER
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
| **Update 3** | 📋 Planifié | Fond dégradé · Miniatures historique · Mode plein écran preview |

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
Distribuer avec FFmpeg ou indiquer à l'utilisateur de l'installer séparément.

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
