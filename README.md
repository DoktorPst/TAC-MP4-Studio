# 🎧 TAC MP4 Studio — Générateur de vidéos musicales réactives en Python

## Présentation

TAC MP4 Studio est un petit logiciel Python permettant de générer automatiquement des vidéos musicales à partir d’une musique et d’une image.

Le but est simple : créer rapidement une vidéo MP4 prête pour YouTube avec un visualizer audio réactif, sans passer par After Effects ou un logiciel de montage lourd.

## Fonctionnalités

- Import d’un fichier audio
- Import d’une pochette / illustration
- Preview vidéo avec audio
- Spectre audio réactif
- Détection bass / kick / aigus
- Particules liées à la musique
- Fumée animée et colorable
- Plusieurs modes de spectre
- Export MP4 en 1920x1080
- Encodage GPU avec NVENC si disponible
- Historique local des créations
- Création automatique d’un dossier par projet

## Technologies utilisées

- Python
- Tkinter
- OpenCV
- Librosa
- NumPy
- Pillow
- FFmpeg

## Installation

### 1. Installer Python

Télécharger Python :

https://www.python.org/downloads/

Pendant l’installation, cocher obligatoirement :

```text
Add Python to PATH
2. Installer FFmpeg

Télécharger FFmpeg :

https://www.gyan.dev/ffmpeg/builds/

Il faut une version complète contenant :

ffmpeg.exe
ffplay.exe

Ajouter le dossier bin de FFmpeg au PATH Windows.

Vérification :

ffmpeg -version
ffplay -version
3. Installer les dépendances Python

Dans le dossier du projet :

python -m pip install -r requirements.txt

Contenu attendu du fichier requirements.txt :

numpy
opencv-python
pillow
librosa
soundfile
Lancement
python main.py
Utilisation

Au lancement, deux choix sont proposés :

CRÉER
HISTORIQUE
Créer une vidéo
Cliquer sur CRÉER
Importer une musique
Importer une image
Régler le style visuel si besoin
Lancer la preview
Cliquer sur GÉNÉRER MP4
Donner un nom au projet

Le nom du projet est utilisé pour :

le dossier du projet
le fichier audio copié
l’image copiée
la vidéo finale

Exemple :

NomProjet/
├── NomProjet.mp3
├── NomProjet_cover.jpg
└── NomProjet.mp4
Historique

L’historique est accessible depuis l’écran d’accueil.

Il affiche les créations triées par date de création.

Chaque entrée permet de retrouver rapidement le dossier du projet.

Emplacement des données locales

La configuration et l’historique sont stockés localement dans :

%APPDATA%\DoktorP3st\TAC_MP4\config.json

Les créations sont stockées par défaut dans :

%APPDATA%\DoktorP3st\TAC_MP4\Creations

Le dossier racine peut être changé depuis l’interface.

Presets inclus

Le logiciel inclut plusieurs presets visuels :

Clean White
Dark Premium
Neon Club
Reggae Smoke
Chill Lo-Fi

Chaque preset règle automatiquement :

les particules
la fumée
la couleur de fumée
le style de spectre
la taille de l’image
le pulse visuel
Modes de spectre

Modes disponibles :

Barres premium
Cercle radial
Cercle + barres
Waveform miroir
Ligne fine
Export vidéo

L’export est fait en MP4 avec :

vidéo H.264
audio AAC 320 kbps
résolution 1920x1080
format compatible YouTube

Si une carte NVIDIA compatible est disponible, l’encodage utilise :

h264_nvenc

Sinon, le logiciel utilise automatiquement :

libx264
Objectif du projet

L’objectif est de créer un outil simple pour produire des vidéos musicales automatiquement, notamment pour :

YouTube
remix
covers IA
playlists
visualizers
chaînes musicales automatisées
Limitations actuelles
Interface basée sur Tkinter
Pas encore de batch export
Pas encore de timeline avancée
Pas encore de drag and drop
Roadmap possible

Améliorations possibles :

interface plus moderne
export batch
templates visuels avancés
meilleure synchronisation BPM
miniatures dans l’historique
édition d’un ancien projet
système de presets personnalisés
Contribution

Les retours sont bienvenus :

idées d’effets visuels
optimisation du rendu
amélioration de l’interface
nouveaux presets
Licence

Projet personnel / expérimental.

À adapter selon l’usage souhaité.
