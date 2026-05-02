<div align="center">

# 🎵 TAC MP4 Studio

**Générateur automatique de vidéos musicales réactives**

*Transforme n'importe quel audio en clip visuel professionnel en quelques clics.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2+-1F6FEB?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-required-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

</div>

---

## ✦ Aperçu

<div align="center">

![TAC MP4 Studio — Interface principale](https://i.imgur.com/WghlJ6F.png)

*Interface moderne CustomTkinter — dark, propre, tout en une fenêtre*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image de pochette. Le rendu visuel — spectre, fumée, particules, pochette animée — est entièrement synchronisé à la musique frame par frame.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel sans toucher à After Effects ou Premiere.

---

## 🎬 Rendus

<div align="center">

![Rendu horizontal](https://i.imgur.com/Ffxk8Aw.png)

*Format horizontal 1920×1080 — YouTube · SoundCloud · Bandcamp*

</div>

<div align="center">

![Interface éditeur](https://i.imgur.com/Yo1x0k4.png)

*Interface éditeur avec preview live et panneau de réglages*

</div>

<div align="center">

![Presets visuels](https://i.imgur.com/moRgO9s.png)

*Presets disponibles : Dark Premium, Neon Club, Reggae Smoke, Chill Lo-Fi…*

</div>

---

## ⚡ Fonctionnalités

### 🎧 Analyse audio réactive
- Extraction frame par frame : **RMS, kick, basse, mids, aigus**
- Synchronisation parfaite son ↔ visuel
- Vectorisé numpy + librosa — 50× plus rapide qu'une boucle Python

### 📊 9 styles de spectre
| Style | Description |
|---|---|
| **Barres premium** | Barres blanches montantes classiques |
| **Barres néon** | Dégradé rouge→bleu avec halo lumineux |
| **Cercle radial** | Lignes rayonnantes autour de la pochette |
| **Cercle + barres** | Orbe + spectre bas combinés |
| **Symétrie miroir** | Barres symétriques haut/bas — idéal SHORT vertical |
| **Arc plasma** | Demi-cercle coloré avec glow |
| **Onde plasma** | Waveform épaisse + halo + reflet |
| **Waveform miroir** | Forme d'onde symétrique simple |
| **Ligne fine** | Ligne monochrome minimaliste |

### 🌫 Effets visuels
- **Fumée** : blobs animés avec turbulence organique (Légère / Cinématique / Dense)
- **Particules** : réactives aux kicks et aux aigus
- **Pochette** : pulse sur les beats, halo glow, bordure arrondie, adaptation automatique au format vertical
- **Vignette** : masque précalculé par résolution (zéro overhead)
- **Texte** : ombre multi-couches réactive, position X/Y réglable

### 🚀 3 modes d'export

```
CHECK   →  15 secondes  ·  1920×1080 horizontal  ·  Aperçu rapide
SHORT   →  1 minute     ·  1080×1920 vertical    ·  Milieu du son  (Reels / TikTok)
COMPLET →  Son entier   ·  1920×1080 horizontal  ·  YouTube / SoundCloud
```

> Le mode **SHORT** prend automatiquement le milieu de ta musique — pas le début.

---

## 🆕 Update 1

<div align="center">

![Panneau de réglages](https://i.imgur.com/9UAfDY2.png)

</div>

### 🔄 Switch preview 16:9 ↔ 9:16
Un bouton toggle dans les contrôles de preview te permet de basculer instantanément entre le rendu horizontal et vertical **sans relancer l'export**. La preview se recharge avec le bon format, la pochette et le spectre se repositionnent automatiquement.

### ⚠️ Vérification FFmpeg au démarrage
Si `ffmpeg` ou `ffplay` est absent ou pas dans le PATH, une bannière orange apparaît au bas de la fenêtre dès le démarrage — avec le message d'erreur et le lien pour installer. L'app reste entièrement utilisable.

### ✅ Validation nom projet
Le champ nom de projet est maintenant **obligatoire avant de générer**. Si vide au moment de cliquer GÉNÉRER, un message d'erreur rouge apparaît directement sous le champ et l'export est bloqué. Plus de popup surprise en plein workflow.

### 📂 Drag & Drop
Glisse directement tes fichiers sur la fenêtre depuis l'Explorateur Windows :
- **Audio** glissé → navigation automatique vers le choix de pochette
- **Image** glissée (audio déjà chargé) → éditeur direct
- **Audio + Image** simultanément → éditeur direct
- Fichier non reconnu → message d'erreur propre, aucun crash
- Fonctionne avec les chemins contenant des espaces

> Nécessite `tkinterdnd2` (`pip install tkinterdnd2`). Si absent, le drag & drop est silencieusement désactivé — l'app tourne normalement.

---

## 📦 Installation

### 1. Prérequis

**Python 3.11+**
```
https://www.python.org/downloads/
```

**FFmpeg** (avec ffplay) — obligatoire pour l'export et la preview audio
```
https://www.gyan.dev/ffmpeg/builds/
```

> Télécharger `ffmpeg-release-essentials.zip` → extraire dans `C:\ffmpeg\` → ajouter `C:\ffmpeg\bin` au PATH Windows :
> Démarrer → "Variables d'environnement" → `Path` → Modifier → Nouveau → `C:\ffmpeg\bin`

### 2. Installer le projet

```bash
# Cloner
git clone https://github.com/DoktorP3st/tac-mp4-studio.git
cd tac-mp4-studio

# Installer les dépendances
pip install -r requirements.txt

# Lancer
python main.py
```

### 3. Dépendances Python

| Package | Rôle |
|---|---|
| `numpy` | Calculs matriciels audio + vidéo |
| `opencv-python` | Rendu frame OpenCV |
| `Pillow` | Texte, fonts, compositing |
| `librosa` | Analyse audio (beat, spectre, bandes) |
| `soundfile` | Lecture durée audio |
| `customtkinter` | Interface moderne dark |
| `tkinterdnd2` | Drag & drop *(optionnel)* |

---

## 🖥️ Utilisation

```
1. Lancer python main.py
2. Cliquer CRÉER (ou glisser un fichier audio sur la fenêtre)
3. Choisir la pochette (ou la glisser directement)
4. Choisir un preset visuel dans le panneau droit
5. Ajuster les sliders — la preview se met à jour en live
6. Basculer entre 16:9 et 9:16 pour voir le rendu SHORT
7. Renseigner le nom du projet
8. Choisir CHECK / SHORT / COMPLET → GÉNÉRER
```

---

## 🏗️ Architecture

```
tac_mp4_studio/
├── main.py              ← entry point
├── app/
│   ├── config.py        ← persistance AppData
│   ├── presets.py       ← constantes & presets visuels
│   ├── models.py        ← RenderSettings dataclass
│   ├── audio.py         ← analyse librosa vectorisée
│   ├── particles.py     ← FloatingParticle, SmokeBlob
│   ├── renderer.py      ← rendu frame (9 spectres, adaptation vertical)
│   ├── exporter.py      ← pipeline FFmpeg (bug SHORT offset corrigé)
│   └── ui/
│       ├── app.py       ← fenêtre CustomTkinter (Update 1)
│       └── widgets.py   ← ScrollFrame
└── requirements.txt
```

---

## 🗺️ Roadmap

| Update | Status | Contenu |
|---|---|---|
| **Update 1** | ✅ Disponible | Switch preview 16:9↔9:16 · Vérif FFmpeg · Nom projet obligatoire · Drag & Drop |
| **Update 2** | 🔜 En cours | Waveform globale · Champs Artiste + Titre séparés · Raccourcis clavier |
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

L'exécutable est dans `dist/TAC_MP4_Studio.exe`.
Distribuer avec FFmpeg ou demander à l'utilisateur de l'installer séparément.

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
