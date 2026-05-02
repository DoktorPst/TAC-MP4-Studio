"""Entités visuelles animées : particules flottantes et blobs de fumée."""
from __future__ import annotations

import math
import random

import cv2
import numpy as np

from app.presets import WIDTH, REGGAE_PALETTE, SMOKE_COLORS


class FloatingParticle:
    """Particule lumineuse réactive à l'énergie des aigus et aux kicks."""

    __slots__ = ("width", "height", "preset_name", "x", "y", "base_size", "speed", "angle", "alpha")

    def __init__(self, width: int, height: int, preset_name: str) -> None:
        self.width = width
        self.height = height
        self.preset_name = preset_name
        self.reset()

    def reset(self) -> None:
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(0, self.height)
        self.base_size = random.uniform(1.0, 3.8)
        self.speed = random.uniform(0.25, 1.35)
        if self.preset_name == "Pluie lumineuse":
            self.angle = random.uniform(math.pi * 0.42, math.pi * 0.58)
        else:
            self.angle = random.uniform(-math.pi * 0.92, -math.pi * 0.08)
        self.alpha = random.uniform(35, 145)

    def update(self, high: float, kick: float, preset: dict) -> None:
        boost = 1.0 + high * preset["speed"] * 7.5 + kick * 4.5
        self.x += math.cos(self.angle) * self.speed * boost
        self.y += math.sin(self.angle) * self.speed * boost
        if self.x < -40 or self.x > self.width + 40 or self.y < -40 or self.y > self.height + 40:
            self.reset()
            self.y = -20 if self.preset_name == "Pluie lumineuse" else self.height + 20

    def draw(self, layer: np.ndarray, high: float, kick: float, preset: dict, scale: float) -> None:
        energy = min(1.0, high * 0.8 + kick * 0.5)
        size = int(self.base_size * preset["size"] * scale * (1.0 + energy * 3.2))
        alpha = int(min(235, (self.alpha + energy * 125) * preset["alpha"]))
        cv2.circle(layer, (int(self.x), int(self.y)), max(1, size), (alpha, alpha, alpha), -1, lineType=cv2.LINE_AA)


class SmokeBlob:
    """Blob de fumée avec mouvement ascendant organique."""

    __slots__ = ("width", "height", "x", "y", "radius", "speed", "drift", "phase", "alpha", "color_index")

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.reset(first=True)

    def reset(self, first: bool = False) -> None:
        self.x = random.uniform(-0.15 * self.width, 1.15 * self.width)
        self.y = (
            random.uniform(0.48 * self.height, 1.15 * self.height)
            if first
            else self.height + random.uniform(20, 180)
        )
        self.radius = random.uniform(90, 250) * (self.width / WIDTH)
        self.speed = random.uniform(0.15, 0.8)
        self.drift = random.uniform(-0.45, 0.45)
        self.phase = random.uniform(0, math.tau)
        self.alpha = random.uniform(28, 85)
        self.color_index = random.randint(0, 2)

    def update(self, bass: float, kick: float, preset: dict) -> None:
        self.y -= self.speed * (1.0 + bass * 3.5 + kick * 2.0) * preset["speed"]
        self.x += self.drift * (1.0 + bass * 1.6)
        self.phase += 0.025 + bass * 0.06
        if self.y < -self.radius * 2:
            self.reset()

    def draw(
        self,
        layer: np.ndarray,
        color_bgr: tuple[int, int, int],
        bass: float,
        kick: float,
        preset: dict,
    ) -> None:
        if preset["density"] <= 0:
            return
        r = int(self.radius * (1.0 + bass * 0.65 + kick * 0.35 + 0.08 * math.sin(self.phase)))
        alpha = int(min(155, self.alpha * preset["density"] * (1.0 + bass * 1.1 + kick * 0.5)))
        color = tuple(int(v * alpha / 255) for v in color_bgr)
        cv2.circle(layer, (int(self.x), int(self.y)), max(5, r), color, -1, lineType=cv2.LINE_AA)
