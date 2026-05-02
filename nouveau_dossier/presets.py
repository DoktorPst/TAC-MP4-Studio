"""Constantes visuelles, presets et palettes couleurs."""
from __future__ import annotations

# ── Dimensions ────────────────────────────────────────────────────────────────
WIDTH = 1920
HEIGHT = 1080
SHORT_WIDTH = 1080
SHORT_HEIGHT = 1920
PREVIEW_W = 960
PREVIEW_H = 540
FPS = 30
PREVIEW_SECONDS = 22

# ── Palettes ──────────────────────────────────────────────────────────────────
SMOKE_COLORS: dict[str, tuple[int, int, int]] = {
    "Blanc":     (235, 235, 235),
    "Or chaud":  (214, 172, 86),
    "Rouge":     (255, 45,  35),
    "Bleu néon": (75,  145, 255),
    "Violet":    (168, 95,  255),
    "Vert":      (35,  255, 80),
    "Reggae":    (255, 220, 20),
}

REGGAE_PALETTE: list[tuple[int, int, int]] = [
    (255, 35, 25),
    (255, 225, 20),
    (25, 255, 70),
]

# ── Presets globaux ───────────────────────────────────────────────────────────
GLOBAL_PRESETS: dict[str, dict] = {
    "Clean White": {
        "particle_preset": "Épuré",
        "smoke_preset":    "Légère",
        "smoke_color":     "Blanc",
        "spectrum_style":  "Barres premium",
        "spectrum_size":   0.95,
        "spectrum_y":      0.90,
        "image_zoom":      1.00,
        "pulse_strength":  0.85,
    },
    "Dark Premium": {
        "particle_preset": "Premium",
        "smoke_preset":    "Cinématique",
        "smoke_color":     "Blanc",
        "spectrum_style":  "Cercle radial",
        "spectrum_size":   1.05,
        "spectrum_y":      0.90,
        "image_zoom":      1.00,
        "pulse_strength":  1.10,
    },
    "Neon Club": {
        "particle_preset": "Énergie",
        "smoke_preset":    "Dense",
        "smoke_color":     "Bleu néon",
        "spectrum_style":  "Barres néon",
        "spectrum_size":   1.20,
        "spectrum_y":      0.88,
        "image_zoom":      0.96,
        "pulse_strength":  1.45,
    },
    "Reggae Smoke": {
        "particle_preset": "Énergie",
        "smoke_preset":    "Dense",
        "smoke_color":     "Reggae",
        "spectrum_style":  "Arc plasma",
        "spectrum_size":   1.20,
        "spectrum_y":      0.88,
        "image_zoom":      1.00,
        "pulse_strength":  1.45,
    },
    "Chill Lo-Fi": {
        "particle_preset": "Pluie lumineuse",
        "smoke_preset":    "Cinématique",
        "smoke_color":     "Violet",
        "spectrum_style":  "Onde plasma",
        "spectrum_size":   0.85,
        "spectrum_y":      0.91,
        "image_zoom":      1.05,
        "pulse_strength":  0.75,
    },
    "Short Vertical": {
        "particle_preset": "Premium",
        "smoke_preset":    "Cinématique",
        "smoke_color":     "Blanc",
        "spectrum_style":  "Symétrie miroir",
        "spectrum_size":   1.10,
        "spectrum_y":      0.82,
        "image_zoom":      1.05,
        "pulse_strength":  1.20,
    },
}

PARTICLE_PRESETS: dict[str, dict] = {
    "Aucune":          {"count": 0,   "speed": 0.00, "size": 0.00, "alpha": 0.00},
    "Épuré":           {"count": 120, "speed": 0.65, "size": 1.00, "alpha": 0.65},
    "Premium":         {"count": 260, "speed": 1.00, "size": 1.15, "alpha": 0.85},
    "Énergie":         {"count": 440, "speed": 1.55, "size": 1.25, "alpha": 1.00},
    "Pluie lumineuse": {"count": 360, "speed": 1.20, "size": 0.90, "alpha": 0.75},
}

SMOKE_PRESETS: dict[str, dict] = {
    "Aucune":      {"density": 0.00, "speed": 0.00, "blur": 0},
    "Légère":      {"density": 0.35, "speed": 0.55, "blur": 31},
    "Cinématique": {"density": 0.78, "speed": 0.85, "blur": 45},
    "Dense":       {"density": 1.18, "speed": 1.15, "blur": 59},
}

SPECTRUM_STYLES: list[str] = [
    "Barres premium",
    "Barres néon",
    "Cercle radial",
    "Cercle + barres",
    "Symétrie miroir",
    "Arc plasma",
    "Onde plasma",
    "Waveform miroir",
    "Ligne fine",
]
