"""Modèles de données du projet — Update 2 : ajout artist_text."""
from __future__ import annotations

from dataclasses import dataclass

from app.presets import WIDTH, HEIGHT


@dataclass
class RenderSettings:
    audio_path: str
    image_path: str
    output_path: str
    title_text: str
    artist_text: str           # Update 2 — champ artiste séparé
    duration_limit: float | None
    start_offset: float

    # Visuels
    particle_preset: str
    smoke_preset: str
    smoke_color: str
    spectrum_style: str
    spectrum_size: float
    spectrum_y: float
    image_zoom: float
    pulse_strength: float

    # Texte
    text_x: float = 0.50
    text_y: float = 0.70

    # Rendu
    background_blur: int = 38
    output_width: int = WIDTH
    output_height: int = HEIGHT

    @property
    def is_vertical(self) -> bool:
        return self.output_height > self.output_width
