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

*Interface moderne CustomTkinter — sombre, propre, tout en une fenêtre*

</div>

TAC MP4 Studio génère automatiquement des **vidéos musicales réactives** à partir d'un fichier audio et d'une image. Le rendu visuel — spectre, fumée, particules, pochette animée — est entièrement synchronisé à la musique via une analyse audio frame par frame.

Conçu pour les producteurs, beatmakers et artistes qui veulent un rendu professionnel sans toucher à After Effects ou Premiere.

---

## 🎬 Rendus

<div align="center">

| Format horizontal | Format vertical SHORT |
|:---:|:---:|
| ![Rendu horizontal](https://i.imgur.com/Ffxk8Aw.png) | ![Rendu vertical](https://i.imgur.com/tliKqPo.png) |
| 1920×1080 · YouTube / SoundCloud | 1080×1920 · Instagram Reels / TikTok |

</div>

<div align="center">

![Presets visuels](https://i.imgur.com/moRgO9s.png)

*Presets disponibles : Dark Premium, Neon Club, Reggae Smoke, Chill Lo-Fi, Clean White…*

</div>

---

## ⚡ Fonctionnalités

### Analyse audio réactive
- Extraction frame par frame : **RMS, kick, basse, mids, aigus**
- Synchronisation parfaite entre le son et le visuel
- Analyse vectorisée via numpy + librosa (~50× plus rapide qu'une boucle Python)

### Spectres visuels (9 styles)
| Style | Description |
|---|---|
| **Barres premium** | Barres blanches montantes classiques |
| **Barres néon** | Dégradé rouge→bleu avec halo lumineux |
| **Cercle radial** | Lignes rayonnantes autour de la pochette |
| **Cercle + barres** | Combinaison orbe + spectre bas |
| **Symétrie miroir** | Barres symétriques haut/bas — idéal SHORT |
| **Arc plasma** | Demi-cercle coloré avec glow bas de cadre |
| **Onde plasma** | Waveform épaisse + halo + reflet |
| **Waveform miroir** | Forme d'onde symétrique |
| **Ligne fine** | Ligne monochrome minimaliste |

### Effets visuels
- **Fumée** : blobs animés avec turbulence organique (Légère / Cinématique / Dense)
- **Particules** : flottantes réactives aux kicks et aigus
- **Pochette** : pulse sur les beats, halo glow, bordure arrondie
- **Vignette** : cache vignette précalculé par résolution
- **Texte** : ombre multi-couches, réactif aux kicks

### 3 modes d'export
```
CHECK   →  15 secondes   ·  1920×1080 horizontal  ·  Aperçu rapide
SHORT   →  1 minute      ·  1080×1920 vertical    ·  Milieu du son  (Reels / TikTok)
COMPLET →  Son entier    ·  1920×1080 horizontal  ·  YouTube / SoundCloud
```

### Gestion de projets
- Dossier projet auto-créé avec musique et pochette copiées
- Historique persistant dans `%APPDATA%\DoktorP3st\TAC_MP4\`
- Config sauvegardée (presets, réglages sliders, géométrie fenêtre)
- Écriture config atomique (pas de corruption)

---

## 🖥️ Interface

<div align="center">

![Panneau de réglages](https://i.imgur.com/9UAfDY2.png)

*Panneau droit : presets 1-clic, sliders, 9 styles de spectre, export*

</div>

L'interface est construite avec **CustomTkinter** — rendu natif sombre, sans dépendance Qt ni Electron.

- Preview vidéo live dans la fenêtre principale
- Lecture audio preview synchronisée (via ffplay)
- Sliders avec debounce 600ms (pas d'écriture disque à chaque tick)
- Contrôles désactivés pendant l'export, overlay de progression

---

## 📦 Installation

### Prérequis

**Python 3.11+**
```
https://www.python.org/downloads/
```

**FFmpeg** (avec ffplay) — obligatoire pour l'export et la preview audio
```
https://www.gyan.dev/ffmpeg/builds/
```
> Télécharger `ffmpeg-release-essentials.zip` → extraire dans `C:\ffmpeg\` → ajouter `C:\ffmpeg\bin` au PATH Windows

### Installation du projet

```bash
# 1. Cloner le dépôt
git clone https://github.com/DoktorP3st/tac-mp4-studio.git
cd tac-mp4-studio

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer
python main.py
```

### Dépendances Python

```
numpy>=1.24
opencv-python>=4.8
Pillow>=10.0
librosa>=0.10
soundfile>=0.12
customtkinter>=5.2
```

---

## 🚀 Utilisation rapide

```
1. Lancer python main.py
2. Cliquer CRÉER → importer un fichier audio (MP3, WAV, FLAC, OGG, M4A)
3. Importer une pochette (JPG, PNG, WEBP)
4. Choisir un preset visuel dans le panneau droit
5. Ajuster les sliders si besoin (preview live)
6. Onglet Export → nommer le projet → choisir CHECK / SHORT / COMPLET → GÉNÉRER
```

---

## 🏗️ Architecture

```
tac_mp4_studio/
├── main.py              ← entry point (5 lignes)
├── app/
│   ├── config.py        ← persistance AppData
│   ├── presets.py       ← constantes & presets visuels
│   ├── models.py        ← RenderSettings dataclass
│   ├── audio.py         ← analyse librosa (vectorisé)
│   ├── particles.py     ← FloatingParticle, SmokeBlob
│   ├── renderer.py      ← rendu frame OpenCV + PIL (9 spectres)
│   ├── exporter.py      ← pipeline vidéo FFmpeg
│   └── ui/
│       ├── app.py       ← fenêtre CustomTkinter
│       └── widgets.py   ← ScrollFrame
└── requirements.txt
```

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
