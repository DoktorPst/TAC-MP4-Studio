# TAC MP4 Studio

**Générateur de vidéos musicales réactives** — spectre audio, fumée, particules, vinyle, pochette, texte.  
Chaque frame est rendue en temps réel et synchronisée à l'audio.

---

## Aperçu

- 10 styles de spectre (barres, néon, cercle radial, arc plasma, oscilloscope…)
- Disque vinyle rotatif réactif aux beats
- Particules et fumée animées
- Fond photo floue ou dégradé personnalisable
- Texte Artiste / Titre avec ombre paramétrable et 12+ polices
- Preview live 30 fps dans l'éditeur
- Export horizontal (1920×1080) ou vertical (1080×1920)
- Encodage GPU (NVENC) automatique si disponible, sinon CPU (libx264)
- 12 presets intégrés + presets utilisateur sauvegardés

---

## Prérequis

| Outil | Version | Lien |
|---|---|---|
| Windows | 10 / 11 | — |
| Python | 3.11+ | https://www.python.org/downloads/ |
| FFmpeg + ffplay | release essentials | https://www.gyan.dev/ffmpeg/builds/ |

### Installer FFmpeg

1. Télécharger `ffmpeg-release-essentials.zip`
2. Extraire dans `C:\ffmpeg\`
3. Ajouter `C:\ffmpeg\bin` au PATH Windows :  
   Démarrer → *Variables d'environnement système* → `Path` → Modifier → Nouveau → `C:\ffmpeg\bin`
4. Vérifier : `ffmpeg -version` dans un terminal

---

## Installation

```bash
git clone https://github.com/ton-repo/tac_mp4_studio
cd tac_mp4_studio
pip install -r requirements.txt
python main.py
```

Ou directement via le lanceur Windows :

```
TAC.bat
```

---

## Utilisation rapide

1. Cliquer **✦ NOUVELLE CRÉATION**
2. Importer un fichier audio (MP3, WAV, FLAC, OGG, M4A)
3. Importer une pochette (PNG, JPG, WEBP)
4. Ajuster les réglages dans le panneau de droite (6 onglets)
5. Onglet **🚀 Export** → nommer le projet → choisir le mode → **GÉNÉRER**

### Modes d'export

| Mode | Résolution | Durée | Usage |
|---|---|---|---|
| CHECK | 1920×1080 | 15 s | Vérification rapide du rendu |
| SHORT | 1080×1920 | ~1 min | Reel / Story vertical |
| COMPLET | 1920×1080 | Fichier entier | Publication finale |

### Raccourcis clavier

| Touche | Action |
|---|---|
| `Espace` | Play / Pause la preview audio |
| `R` | Recharger la preview |
| `F11` | Preview plein écran |
| `Échap` | Quitter le plein écran |

---

## Onglets de l'éditeur

| Onglet | Contenu |
|---|---|
| ⚡ Presets | 12 presets intégrés + gestion des presets utilisateur |
| 📸 Image | Taille pochette · Pulse · Vinyle · Fond (flou, luminosité, dégradé, oscillation) |
| ✨ Effets | Particules · Fumée · Couleur fumée |
| 📊 Spectre | Style · Taille · Position · Couleur (mono ou 3 bandes) · Flash beats |
| 📝 Texte | Artiste · Titre · Police · Taille · Position · Ombre |
| 🚀 Export | Dossier de sortie · Mode · Génération |

---

## Architecture

```
tac_mp4_studio/
├── main.py                  ← point d'entrée
├── requirements.txt
├── TAC.bat                  ← lanceur Windows
├── img/
│   ├── tac.png              ← logo
│   └── vinyle.png           ← asset disque vinyle
├── fonts/                   ← polices TTF incluses
└── app/
    ├── audio.py             ← analyse audio (librosa + soundfile)
    ├── config.py            ← persistance JSON (AppData)
    ├── exporter.py          ← pipeline export FFmpeg
    ├── loading.py           ← écran de chargement animé
    ├── models.py            ← RenderSettings (dataclass)
    ├── particles.py         ← FloatingParticle, SmokeBlob
    ├── presets.py           ← constantes, presets visuels, palettes
    ├── renderer.py          ← rendu frame (image, texte, fond, vignette)
    ├── spectrum.py          ← 9 styles de spectre + orb audio
    ├── vinyl.py             ← disque vinyle rotatif + pochette
    └── ui/
        ├── app.py           ← App (état, lifecycle, navigation)
        ├── editor.py        ← EditorMixin (onglets éditeur)
        ├── pages.py         ← PagesMixin (accueil, historique, turbo, presets)
        ├── preview.py       ← PreviewMixin (preview live, waveform, audio)
        └── widgets.py       ← widgets réutilisables
```

### Flux de rendu

```
Audio → compute_audio_features() → features (rms, bass, kick, mid, high, spec)
                                         ↓
Image → load_cover_image()       → bg_arr + cover_arr
                                         ↓
                              render_frame() ← spectrum.py
                                         ↓   ← vinyl.py
                              frame BGR numpy
                                         ↓
                              cv2.VideoWriter → vidéo muette
                                         ↓
                              FFmpeg → vidéo finale + audio
```

---

## Configuration

Sauvegardée automatiquement dans :
```
%APPDATA%\DoktorP3st\TAC_MP4\config.json
```

Projets exportés dans (modifiable dans les réglages) :
```
%APPDATA%\DoktorP3st\TAC_MP4\Creations\
```

---

## Packaging en .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "TAC_MP4_Studio" --collect-data librosa main.py
```

Exécutable dans `dist/TAC_MP4_Studio.exe`.  
Distribuer avec FFmpeg ou indiquer à l'utilisateur de l'installer séparément.

---

## Dépendances Python

```
numpy >= 1.24
opencv-python >= 4.8
Pillow >= 10.0
librosa >= 0.10
soundfile >= 0.12
customtkinter >= 5.2
tkinterdnd2 >= 0.3.0   # optionnel — drag & drop désactivé si absent
scipy                  # installé automatiquement via librosa
```

---

## Auteur

Développé par **DoktorP3st**
