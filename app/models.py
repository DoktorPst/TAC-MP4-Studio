"""Modèles de données du projet."""
from __future__ import annotations

from dataclasses import dataclass, field

from app.presets import WIDTH, HEIGHT


@dataclass
class RenderSettings:
    """Paramètres complets d'un rendu vidéo.

    Toutes les valeurs nécessaires au renderer et à l'exporter sont ici.
    Cela évite de passer des dizaines d'arguments en cascade.
    """
    audio_path: str
    image_path: str
    output_path: str
    title_text: str
    duration_limit: float | None  # None = audio entier
    start_offset: float           # Secondes de départ dans l'audio

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
        """True si le rendu est au format vertical (SHORT)."""
        return self.output_height > self.output_width
