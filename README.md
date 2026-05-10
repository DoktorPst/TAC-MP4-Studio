# TAC MP4 Studio

<div align="center">

**Générateur de vidéos musicales réactives — local, rapide, sans abonnement.**

Transforme n'importe quel fichier audio en vidéo visualisée frame par frame,
synchronisée beat par beat, exportée en qualité broadcast.

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-1F6AA5?style=flat-square)
![FFmpeg](https://img.shields.io/badge/Export-FFmpeg-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?style=flat-square&logo=windows&logoColor=white)

</div>

---

## Ce que ça fait

TAC MP4 Studio analyse l'audio en temps réel et génère une vidéo réactive où chaque élément visuel répond à la musique. Les basses, les kicks, les aigus et l'énergie globale pilotent directement le rendu frame par frame.

```
Audio ──► Analyse librosa ──► Features (bass / kick / rms / high)
                                        │
                               Rendu OpenCV + PIL
                         ┌──────────────┬──────────────┐
                         │   Spectre    │  Atmosphère  │
                         │   Pochette   │  Particules  │
                         │   Texte      │   Vinyle     │
                         └──────────────┴──────────────┘
                                        │
                         FFmpeg ──► MP4 (NVENC ou libx264)
```

---

## Fonctionnalités

### Visuels

| Composant | Détail |
|---|---|
| **10 styles de spectre** | Barres premium · Barres néon · Symétrie miroir · Cercle radial · Arc plasma · Onde plasma · Waveform miroir · Oscilloscope · Ligne fine · Cercle + barres |
| **7 effets atmosphère** | Aucune · Légère · Cinématique · Dense · **Voiles** · **Lueur ambiante** · **Traces plasma** |
| **Particules** | 5 presets · cycle de vie · fade in/out · drift organique · bloom two-pass |
| **Disque vinyle** | Rotatif · réactif aux beats · pochette image ou noir classique |
| **Fond** | Photo floue (flou + luminosité réglables) · Dégradé personnalisé · Fond flottant · Micro-oscillation |
| **Texte** | Artiste + Titre · 12+ polices · taille · position · ombre paramétrable |

### Export

| Mode | Résolution | Durée | Usage |
|---|---|---|---|
| **CHECK** | 1920 × 1080 | 15 s | Vérification rapide |
| **SHORT** | 1080 × 1920 | ~1 min (centre audio) | Reel · Story · Short |
| **COMPLET** | 1920 × 1080 | Fichier entier | Publication finale |

- Encodage **GPU automatique** (NVIDIA NVENC) si disponible, sinon CPU libx264
- Preview **live 30 fps** dans l'éditeur avant export
- Historique des exports avec miniatures

---

## Démarrage rapide

### Prérequis

- **Windows 10 / 11**
- **Python 3.11+** — [python.org](https://www.python.org/downloads/)
- **FFmpeg** (avec `ffplay`) — [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)

<details>
<summary><b>Installer FFmpeg</b></summary>

1. Télécharger `ffmpeg-release-essentials.zip`
2. Extraire dans `C:\ffmpeg\`
3. Ajouter `C:\ffmpeg\bin` au PATH Windows :
   - `Démarrer` → *Variables d'environnement* → `Path` → Nouveau → `C:\ffmpeg\bin`
4. Vérifier dans un terminal : `ffmpeg -version`

</details>

### Installation

```bash
git clone https://github.com/ton-repo/tac_mp4_studio
cd tac_mp4_studio
pip install -r requirements.txt
python main.py
```

Ou via le lanceur Windows :

```
TAC.bat
```

---

## Utilisation

```
1.  ✦ NOUVELLE CRÉATION
2.  Importer un fichier audio    (MP3 · WAV · FLAC · OGG · M4A)
3.  Importer une pochette        (PNG · JPG · WEBP)
4.  Régler les visuels dans l'éditeur
5.  🚀 Export → nommer le projet → choisir le mode → GÉNÉRER
```

### Onglets de l'éditeur

| Onglet | Contenu |
|---|---|
| ⚡ **Presets** | 12 presets intégrés · gestion des presets utilisateur |
| 📸 **Image** | Taille pochette · Réactivité · Vinyle · Fond (flou, luminosité, dégradé, oscillation) |
| ✨ **Effets** | Particules · Atmosphère · Couleur |
| 📊 **Spectre** | Style · Taille · Position · Couleur (mono ou 3 bandes) · Flash beats |
| 📝 **Texte** | Artiste · Titre · Police · Taille · Position · Ombre |
| 🚀 **Export** | Dossier · Mode · Génération |

### Raccourcis clavier

| Touche | Action |
|---|---|
| `Espace` | Play / Pause preview audio |
| `R` | Recharger la preview |
| `F11` | Preview plein écran |
| `Échap` | Quitter le plein écran |

---

## Architecture

```
tac_mp4_studio/
│
├── main.py                    Point d'entrée
├── TAC.bat                    Lanceur Windows
├── requirements.txt
│
├── img/                       Assets (logo, disque vinyle)
├── fonts/                     Polices TTF incluses
│
└── app/
    ├── audio.py               Analyse audio (librosa + soundfile + scipy)
    ├── config.py              Persistance JSON (AppData)
    ├── exporter.py            Pipeline export FFmpeg
    ├── loading.py             Écran de chargement animé
    ├── models.py              RenderSettings (dataclass)
    ├── particles.py           Particules · Fumée · Voiles · Plasma · Lueur ambiante
    ├── presets.py             Constantes · Presets visuels · Palettes
    ├── renderer.py            Rendu frame (image, texte, fond, vignette, glow)
    ├── spectrum.py            10 styles de spectre + orbe audio
    ├── vinyl.py               Disque vinyle rotatif + pochette
    │
    └── ui/
        ├── app.py             App — état, lifecycle, navigation, éditeur
        ├── editor.py          EditorMixin — onglets éditeur + callbacks
        ├── pages.py           PagesMixin — accueil, historique, turbo, presets
        ├── preview.py         PreviewMixin — preview live, waveform, audio
        └── widgets.py         Widgets réutilisables
```

### Flux de dépendances

```
App
 ├─ EditorMixin · PagesMixin · PreviewMixin
 ├─ renderer ──► spectrum · vinyl · particles
 ├─ exporter ──► renderer · audio
 └─ config · models · presets
```

---

## Configuration

Sauvegarde automatique dans :

```
%APPDATA%\DoktorP3st\TAC_MP4\config.json
```

Dossier de sortie par défaut (modifiable dans l'app) :

```
%APPDATA%\DoktorP3st\TAC_MP4\Creations\
```

---

## Packaging .exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name "TAC_MP4_Studio" --collect-data librosa main.py
```

L'exécutable se trouve dans `dist/TAC_MP4_Studio.exe`.  
À distribuer avec FFmpeg, ou indiquer à l'utilisateur de l'installer séparément.

---

## Stack

```
numpy            Calcul vectorisé — audio et rendu
opencv-python    Pipeline vidéo frame par frame
Pillow           Traitement image · texte · polices
librosa          Analyse audio (STFT · onset · RMS)
soundfile        Chargement WAV/FLAC/OGG (fast path)
scipy            Resampling audio · interpolation
customtkinter    Interface dark theme moderne
tkinterdnd2      Drag & drop fichiers (optionnel)
FFmpeg           Encodage MP4 (NVENC / libx264)
```

---

<div align="center">

Développé par **DoktorP3st**

</div>
