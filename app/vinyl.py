"""Disque vinyle + pochette — rendu PIL/OpenCV.

Extrait de app/renderer.py pour séparation des responsabilités.
"""
from __future__ import annotations

import os as _os

import cv2
import numpy as np
from PIL import Image, ImageDraw

from app.models import RenderSettings

# ── Assets ─────────────────────────────────────────────────────────────────────
_ASSETS_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "img")
_VINYL_PNG   = _os.path.join(_ASSETS_DIR, "vinyle.png")

# ── Cache ──────────────────────────────────────────────────────────────────────
_vinyl_img_cache: dict[int, Image.Image] = {}


def _composite_image(frame: np.ndarray, img_pil: Image.Image, cx: int, cy: int) -> None:
    """Colle une image RGBA PIL centrée en (cx, cy) sur la frame BGR numpy."""
    w_img, h_img = img_pil.size
    x1, y1 = cx - w_img // 2, cy - h_img // 2
    x2, y2 = x1 + w_img, y1 + h_img

    height, width = frame.shape[:2]
    fx1, fy1 = max(0, x1), max(0, y1)
    fx2, fy2 = min(width, x2), min(height, y2)
    dx1, dy1 = fx1 - x1, fy1 - y1
    dx2, dy2 = dx1 + (fx2 - fx1), dy1 + (fy2 - fy1)

    if fx2 <= fx1 or fy2 <= fy1:
        return

    img_bgr   = cv2.cvtColor(np.array(img_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    img_alpha = np.array(img_pil.getchannel("A"), dtype=np.float32) / 255.0

    roi = frame[fy1:fy2, fx1:fx2].astype(np.float32)
    src = img_bgr[dy1:dy2, dx1:dx2].astype(np.float32)
    alp = img_alpha[dy1:dy2, dx1:dx2, np.newaxis]
    frame[fy1:fy2, fx1:fx2] = (roi * (1.0 - alp) + src * alp).astype(np.uint8)


def _load_vinyl_png(radius: int) -> Image.Image | None:
    """Charge vinyle.png redimensionné au diamètre voulu, avec cache."""
    if radius in _vinyl_img_cache:
        return _vinyl_img_cache[radius]
    try:
        raw = Image.open(_VINYL_PNG).convert("RGBA")
        size = radius * 2
        result = raw.resize((size, size), Image.LANCZOS)
        _vinyl_img_cache[radius] = result
        return result
    except Exception:
        return None


def _make_vinyl_disk(cover_pil: Image.Image, radius: int, angle: float,
                     vinyl_black: bool = False, cache_r: int = 0) -> Image.Image:
    """Génère le disque vinyle PIL (RGBA)."""
    size = radius * 2
    disk = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    vinyl_base = _load_vinyl_png(cache_r if cache_r > 0 else radius)
    hole_ratio = 0.367
    hole_r = int(radius * hole_ratio)

    if vinyl_black:
        base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circ_mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circ_mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        ImageDraw.Draw(base).ellipse((0, 0, size - 1, size - 1), fill=(10, 10, 10, 255))
        base.putalpha(circ_mask)
    else:
        base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circ_mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circ_mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        ImageDraw.Draw(base).ellipse((0, 0, size - 1, size - 1), fill=(10, 10, 10, 255))
        base.putalpha(circ_mask)

        label_sq = cover_pil.resize((hole_r * 2, hole_r * 2), Image.LANCZOS).convert("RGBA")
        label_mask = Image.new("L", (hole_r * 2, hole_r * 2), 0)
        ImageDraw.Draw(label_mask).ellipse((0, 0, hole_r * 2 - 1, hole_r * 2 - 1), fill=255)
        base.paste(label_sq, (radius - hole_r, radius - hole_r), mask=label_mask)

    disk = base

    if vinyl_base is not None:
        if vinyl_base.size != disk.size:
            vinyl_base = vinyl_base.resize(disk.size, Image.LANCZOS)
        disk = Image.alpha_composite(disk, vinyl_base)

    disk = disk.rotate(-(angle % 360), resample=Image.BILINEAR, expand=False)

    c = size // 2
    hr = max(2, int(radius * 0.022))
    ImageDraw.Draw(disk).ellipse((c - hr, c - hr, c + hr, c + hr), fill=(8, 8, 8, 255))

    return disk


def _make_sleeve(cover_pil: Image.Image, side: int) -> Image.Image:
    """Génère la pochette d'album (RGBA) carrée."""
    return cover_pil.resize((side, side), Image.LANCZOS).convert("RGBA")


def draw_vinyl_disk(
    frame: np.ndarray,
    cover_bgr: np.ndarray,
    angle: float,
    bass: float,
    kick: float,
    settings: RenderSettings,
) -> None:
    """Composition pochette + vinyle."""
    height, width = frame.shape[:2]
    is_v = settings.is_vertical
    scale = width / 1920

    base_side = int(min(width, height) * 0.38 * settings.image_zoom)
    pulse_px   = int(base_side * (bass * 0.04 * settings.pulse_strength
                                  + kick * 0.07 * settings.pulse_strength))
    sleeve_side = max(40, base_side + pulse_px)

    base_vinyl_r = int(min(width, height) * 0.38 * settings.image_zoom * 0.52)
    pulse_vinyl  = int(base_vinyl_r * (bass * 0.04 + kick * 0.07) * settings.pulse_strength)
    vinyl_r = max(40, base_vinyl_r + pulse_vinyl)

    group_cx = width // 2 - int(sleeve_side * 0.22)
    group_cy = int(height * 0.27) if is_v else height // 2 - int(height * 0.07)

    vinyl_cx = group_cx + int(sleeve_side * 0.62)
    vinyl_cy = group_cy

    shadow = np.zeros_like(frame)
    cv2.circle(shadow, (vinyl_cx, vinyl_cy),
               vinyl_r + int(16 * scale), (35, 35, 35), -1)
    cv2.rectangle(shadow,
                  (group_cx - sleeve_side // 2 - 4, group_cy - sleeve_side // 2 - 4),
                  (group_cx + sleeve_side // 2 + 4, group_cy + sleeve_side // 2 + 4),
                  (0, 0, 0), -1)
    off = int(7 * scale)
    cv2.rectangle(shadow,
                  (group_cx - sleeve_side // 2 + off, group_cy - sleeve_side // 2 + off),
                  (group_cx + sleeve_side // 2 + off, group_cy + sleeve_side // 2 + off),
                  (35, 35, 35), -1)
    shadow = cv2.GaussianBlur(shadow, (45, 45), 0)
    cv2.addWeighted(shadow, 0.55, frame, 1.0, 0, frame)

    cover_pil = Image.fromarray(cv2.cvtColor(cover_bgr, cv2.COLOR_BGR2RGB))
    use_image_on_disk = not settings.vinyl_black
    vinyl_img  = _make_vinyl_disk(cover_pil, vinyl_r, angle,
                                  vinyl_black=not use_image_on_disk,
                                  cache_r=base_vinyl_r)
    _composite_image(frame, vinyl_img, vinyl_cx, vinyl_cy)

    sleeve_img = _make_sleeve(cover_pil, sleeve_side)
    _composite_image(frame, sleeve_img, group_cx, group_cy)
