"""Modèles de données — Update 5 : couleur spectre, fond flottant."""
from __future__ import annotations
from dataclasses import dataclass
from app.presets import WIDTH, HEIGHT


@dataclass
class RenderSettings:
    audio_path: str
    image_path: str
    output_path: str
    title_text: str
    artist_text: str
    duration_limit: float | None
    start_offset: float

    particle_preset: str
    smoke_preset: str
    smoke_color: str
    spectrum_style: str
    spectrum_size: float
    spectrum_y: float
    image_zoom: float
    pulse_strength: float

    text_x: float = 0.50
    text_y: float = 0.70
    background_blur: int = 38
    output_width: int = WIDTH
    output_height: int = HEIGHT

    bg_mode: str = "photo"
    gradient_top: str = "#1a1a2e"
    gradient_bottom: str = "#0f3460"

    vinyl_mode: bool = False
    vinyl_black: bool = False     # True = vinyle noir classique (label uniquement)

    # Update 5
    spectrum_color: str = "#ffffff"       # couleur de base du spectre (hex)
    spectrum_color_auto: bool = False     # extraire couleur dominante de la pochette
    floating_bg: bool = False             # fond qui dérive lentement

    @property
    def is_vertical(self) -> bool:
        return self.output_height > self.output_width
