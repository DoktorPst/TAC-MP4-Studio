"""Rendu frame par frame — OpenCV + PIL.

Update 4 : disque vinyle rotatif réactif aux beats.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from app.models import RenderSettings
from app.particles import FloatingParticle, SmokeBlob
from app.presets import (
    WIDTH, HEIGHT,
    PARTICLE_PRESETS, SMOKE_PRESETS, SMOKE_COLORS, REGGAE_PALETTE,
)

# ── Caches ────────────────────────────────────────────────────────────────────
_vignette_cache: dict[tuple[int, int], np.ndarray] = {}
_font_cache: dict[tuple[int, bool, str], Any] = {}
_font_registry: dict[str, str | None] = {}
_font_registry_built: bool = False
_color_cache: dict[str, tuple[int, int, int]] = {}   # hex → (r,g,b)


def _parse_hex(hex_color: str) -> tuple[int, int, int]:
    """Parse un hex color (#rrggbb) en tuple RGB, avec cache."""
    if hex_color not in _color_cache:
        h = hex_color.lstrip("#")
        try:
            _color_cache[hex_color] = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except (ValueError, IndexError):
            _color_cache[hex_color] = (255, 255, 255)
    return _color_cache[hex_color]


def _tint_bgr(brightness: int, r: int, g: int, b: int) -> tuple[int, int, int]:
    """Teinte une couleur BGR par (r,g,b) avec la luminosité donnée."""
    s = brightness / 255.0
    return (int(b * s), int(g * s), int(r * s))


def _lerp_color(c1: tuple, c2: tuple, t: float) -> tuple[int, int, int]:
    """Interpolation linéaire entre deux couleurs RGB."""
    t = max(0.0, min(1.0, t))
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def _tricolor_for_bar(i: int, n: int, brightness: int,
                      c_bass: tuple, c_mid: tuple, c_high: tuple,
                      kick: float = 0.0, reactive: bool = False) -> tuple[int, int, int]:
    """Retourne la couleur BGR d'une barre selon sa position (bass→mid→high).

    Update 7 :
    - Dégradé 3 couleurs sur la largeur du spectre
    - Mode réactif : flash blanc/brillant sur les kicks
    """
    t = i / max(1, n - 1)
    if t < 0.5:
        rgb = _lerp_color(c_bass, c_mid, t * 2.0)
    else:
        rgb = _lerp_color(c_mid, c_high, (t - 0.5) * 2.0)

    if reactive and kick > 0.3:
        flash = min(1.0, (kick - 0.3) / 0.7)
        white = (255, 255, 255)
        rgb = _lerp_color(rgb, white, flash * 0.65)

    s = brightness / 255.0
    return (int(rgb[2] * s), int(rgb[1] * s), int(rgb[0] * s))


def extract_dominant_color(cover_bgr: np.ndarray) -> str:
    """Extrait la couleur dominante d'une pochette (BGR numpy).

    Retourne un hex string (#rrggbb). Utilisé pour spectrum_color_auto.
    """
    small = cv2.resize(cover_bgr, (32, 32))
    hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1].flatten()
    mask = sat > 60
    if mask.sum() < 8:
        return "#ffffff"
    pixels = small.reshape(-1, 3)[mask]
    mean_bgr = pixels.mean(axis=0).astype(int)
    b, g, r = int(mean_bgr[0]), int(mean_bgr[1]), int(mean_bgr[2])
    # Booster la saturation : amplifier l'écart par rapport au gris
    gray = (r + g + b) // 3
    boost = 1.6
    r = min(255, max(0, int(gray + (r - gray) * boost)))
    g = min(255, max(0, int(gray + (g - gray) * boost)))
    b_out = min(255, max(0, int(gray + (b - gray) * boost)))
    return f"#{r:02x}{g:02x}{b_out:02x}"


# ── Utilitaires ───────────────────────────────────────────────────────────────

def _build_font_registry() -> None:
    """Construit le registre des polices (dossier fonts/ + système Windows)."""
    global _font_registry, _font_registry_built
    if _font_registry_built:
        return
    import os as _os2, platform

    fonts_dir = _os2.path.join(_os2.path.dirname(_os2.path.dirname(__file__)), "fonts")
    # Noms affichés → fichier sans extension
    bundled = {
        "Liberation Sans":   "LiberationSans-Bold",
        "Liberation Serif":  "LiberationSerif-Bold",
        "Liberation Mono":   "LiberationMono-Bold",
        "Carlito":           "Carlito-Bold",
        "Caladea":           "Caladea-Bold",
        "Montserrat":        "Montserrat-Bold",
        "Oswald":            "Oswald-Bold",
        "Bebas Neue":        "BebasNeue-Regular",
        "Russo One":         "RussoOne-Regular",
        "Pacifico":          "Pacifico-Regular",
        "Raleway":           "Raleway-Bold",
        "Playfair Display":  "PlayfairDisplay-Bold",
    }
    registry: dict[str, str | None] = {"Défaut": None}
    if _os2.path.isdir(fonts_dir):
        for label, stem in bundled.items():
            for ext in (".ttf", ".otf"):
                path = _os2.path.join(fonts_dir, stem + ext)
                if _os2.path.isfile(path):
                    registry[label] = path
                    break

    # Polices Windows sympas
    if platform.system() == "Windows":
        wf = _os2.path.join(_os2.environ.get("WINDIR", "C:/Windows"), "Fonts")
        win = {
            "Impact":      "impact.ttf",
            "Georgia":     "georgiabd.ttf",
            "Trebuchet":   "trebucbd.ttf",
            "Arial Black": "ariblk.ttf",
        }
        for label, fname in win.items():
            p = _os2.path.join(wf, fname)
            if _os2.path.isfile(p):
                registry[label] = p
        # Segoe UI toujours dispo sur Windows
        seg = _os2.path.join(wf, "segoeuib.ttf")
        if _os2.path.isfile(seg):
            registry["Segoe UI"] = seg

    _font_registry = registry
    _font_registry_built = True


def get_font_names() -> list[str]:
    _build_font_registry()
    return list(_font_registry.keys())


def safe_font(size: int, bold: bool = False, font_name: str = "Défaut") -> Any:
    """Charge une police PIL depuis le registre. Résultat mis en cache par (size, bold, font_name)."""
    _build_font_registry()
    size = max(12, (size // 2) * 2)
    key = (size, bold, font_name)
    if key not in _font_cache:
        path = _font_registry.get(font_name)
        try:
            if path:
                _font_cache[key] = ImageFont.truetype(path, size=size)
            else:
                # Défaut : Segoe UI si dispo
                candidates = [
                    "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
                    "C:/Windows/Fonts/arialbd.ttf"  if bold else "C:/Windows/Fonts/arial.ttf",
                ]
                for p in candidates:
                    if Path(p).exists():
                        _font_cache[key] = ImageFont.truetype(p, size=size)
                        break
                else:
                    _font_cache[key] = ImageFont.load_default()
        except Exception:
            _font_cache[key] = ImageFont.load_default()
    return _font_cache[key]


def _get_vignette(width: int, height: int) -> np.ndarray:
    key = (width, height)
    if key not in _vignette_cache:
        y_idx, x_idx = np.ogrid[:height, :width]
        dist = np.sqrt((x_idx - width / 2.0) ** 2 + (y_idx - height / 2.0) ** 2)
        mask = np.clip(1.0 - dist / (min(width, height) * 0.92), 0.16, 1.0)
        _vignette_cache[key] = mask[..., np.newaxis].astype(np.float32)
    return _vignette_cache[key]


def rounded_rectangle(img, pt1, pt2, radius, color, thickness=-1):
    x1, y1 = pt1
    x2, y2 = pt2
    radius = max(1, min(radius, abs(x2 - x1) // 2, abs(y2 - y1) // 2))
    if thickness == -1:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        for cx, cy in [(x1+radius, y1+radius), (x2-radius, y1+radius),
                       (x1+radius, y2-radius), (x2-radius, y2-radius)]:
            cv2.circle(img, (cx, cy), radius, color, -1)
    else:
        cv2.rectangle(img, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)


# ── Chargement image ──────────────────────────────────────────────────────────

def _hex_to_bgr(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


def generate_gradient_bg(color_top: str, color_bottom: str,
                          width: int, height: int) -> np.ndarray:
    """Génère un fond dégradé vertical BGR (numpy vectorisé)."""
    top = np.array(_hex_to_bgr(color_top),    dtype=np.float32)
    bot = np.array(_hex_to_bgr(color_bottom), dtype=np.float32)
    t = np.linspace(0.0, 1.0, height, dtype=np.float32)[:, np.newaxis, np.newaxis]
    gradient = (top[np.newaxis] * (1.0 - t) + bot[np.newaxis] * t).astype(np.uint8)
    return np.repeat(gradient, width, axis=1)


def load_cover_image(path, blur_radius, zoom, width=WIDTH, height=HEIGHT,
                     bg_mode="photo", gradient_top="#1a1a2e", gradient_bottom="#0f3460"):
    """Charge la pochette et génère le background (photo floutée ou dégradé).

    Update 3 : bg_mode "photo" | "gradient"
    """
    img = Image.open(path).convert("RGB")

    if bg_mode == "gradient":
        bg_arr = generate_gradient_bg(gradient_top, gradient_bottom, width, height)
    else:
        bg = img.copy()
        src_w, src_h = bg.size
        target_ratio = width / height
        src_ratio = src_w / src_h

        if src_ratio > target_ratio:
            new_w = int(src_h * target_ratio)
            left = (src_w - new_w) // 2
            bg = bg.crop((left, 0, left + new_w, src_h))
        else:
            new_h = int(src_w / target_ratio)
            top_px = (src_h - new_h) // 2
            bg = bg.crop((0, top_px, src_w, top_px + new_h))

        bg = bg.resize((width, height), Image.LANCZOS)
        if blur_radius > 0:
            bg = bg.filter(ImageFilter.GaussianBlur(blur_radius))
        bg = ImageEnhance.Brightness(bg).enhance(0.16)
        bg = ImageEnhance.Contrast(bg).enhance(1.25)
        bg_arr = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
        bg_arr = cv2.addWeighted(bg_arr, 0.50, np.zeros_like(bg_arr), 0.50, 0)

    # Pochette
    is_vertical = height > width
    zoom_factor = 0.60 if is_vertical else 0.53
    max_side = int(min(width, height) * zoom_factor * zoom)
    cover = img.copy()
    cover.thumbnail((max_side, max_side), Image.LANCZOS)
    cover_arr = cv2.cvtColor(np.array(cover), cv2.COLOR_RGB2BGR)

    return bg_arr, cover_arr


# ── Dessin éléments ───────────────────────────────────────────────────────────

def draw_vignette(frame):
    h, w = frame.shape[:2]
    frame[:] = (frame.astype(np.float32) * _get_vignette(w, h)).astype(np.uint8)


def overlay_center(base, overlay, bass, kick, pulse_strength, is_vertical=False):
    height, width = base.shape[:2]
    h, w = overlay.shape[:2]
    x = (width - w) // 2
    pulse = int((8 + bass * 20 * pulse_strength + kick * 35 * pulse_strength) * (width / WIDTH))

    if is_vertical:
        # En mode SHORT : pochette dans le tiers supérieur
        y = int(height * 0.12)
    else:
        y = (height - h) // 2 - int(height * 0.09)

    glow = np.zeros_like(base)
    rounded_rectangle(glow, (x - pulse, y - pulse), (x + w + pulse, y + h + pulse), 24, (150, 150, 150), -1)
    glow = cv2.GaussianBlur(glow, (91, 91), 0)
    cv2.addWeighted(glow, 0.38, base, 1.0, 0, base)

    pad = max(6, int(18 * width / WIDTH))
    rounded_rectangle(base, (x - pad, y - pad), (x + w + pad, y + h + pad), 18, (0, 0, 0), -1)
    rounded_rectangle(base, (x - pad, y - pad), (x + w + pad, y + h + pad), 18, (238, 238, 238), 2)
    base[y:y + h, x:x + w] = overlay


def _draw_text_line(draw, text, font, x_center, y, alpha, shadow_offset=4):
    """Dessine une ligne de texte centrée avec ombre diagonale."""
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = int(x_center - tw / 2)
    for ox, oy, a in [(-shadow_offset, -shadow_offset, 60),
                      ( shadow_offset, -shadow_offset, 60),
                      (-shadow_offset,  shadow_offset, 60),
                      ( shadow_offset,  shadow_offset, 60)]:
        draw.text((x + ox, y + oy), text, font=font, fill=(0, 0, 0, a))
    draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))


def draw_reactive_text(frame, title, rms, kick, text_x=0.50, text_y=0.70, artist="", font_name="Défaut"):
    """Rend le texte artiste + titre sur la frame.

    Update 2 : artiste et titre sont deux champs séparés avec tailles différentes.
    - Artiste : plus grand, bold, couleur pleine
    - Titre   : légèrement plus petit, style régulier, légèrement atténué
    - Si artiste vide : affichage titre seul (comportement original)
    """
    has_artist = bool(artist.strip())
    has_title  = bool(title.strip())

    if not has_artist and not has_title:
        return

    height, width = frame.shape[:2]
    scale = width / WIDTH
    kick_boost = 1.0 + kick * 0.10 + rms * 0.025

    artist_size = max(16, int(62 * scale * kick_boost))
    title_size  = max(14, int(44 * scale * kick_boost))

    font_artist = safe_font(artist_size, bold=True,  font_name=font_name)
    font_title  = safe_font(title_size,  bold=False, font_name=font_name)

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    cx = width * text_x
    base_y = int(height * text_y)
    text_alpha = int(min(255, 210 + kick * 45))
    title_alpha = int(text_alpha * 0.82)
    spacing = int(artist_size * 1.25)

    if has_artist and has_title:
        # Centrer le bloc artiste+titre autour de base_y
        total_h = spacing + title_size
        y_artist = base_y - total_h // 2
        y_title  = y_artist + spacing
        _draw_text_line(draw, artist.strip(), font_artist, cx, y_artist, text_alpha)
        _draw_text_line(draw, title.strip(), font_title, cx, y_title, title_alpha)

    elif has_artist:
        y = base_y - artist_size // 2
        _draw_text_line(draw, artist.strip(), font_artist, cx, y, text_alpha)

    else:
        # Titre seul — même comportement qu'avant avec wrapping
        max_width = int(width * 0.78)
        words = title.strip().split()
        lines, current = [], ""
        for word in words:
            test = (current + " " + word).strip()
            bbox = draw.textbbox((0, 0), test, font=font_title)
            if bbox[2] - bbox[0] <= max_width or not current:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        lines = lines[:2]
        lh = int(title_size * 1.16)
        y = base_y - len(lines) * lh // 2
        for i, line in enumerate(lines):
            _draw_text_line(draw, line, font_title, cx, y + i * lh, title_alpha)

    img = Image.alpha_composite(img.convert("RGBA"), layer)
    frame[:] = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def spectrum_bands(spec_frame, bar_count=84):
    bins = len(spec_frame)
    idx = np.geomspace(1, bins, bar_count + 1).astype(int) - 1
    idx = np.clip(idx, 0, bins - 1)
    starts, ends = idx[:-1], np.maximum(idx[1:], idx[:-1] + 1)
    vals = np.array([spec_frame[s:e].mean() for s, e in zip(starts, ends)], dtype=np.float32)
    return np.clip(np.power(vals, 1.55), 0.0, 1.0)


# ── Spectres ──────────────────────────────────────────────────────────────────

def draw_spectrum(frame, bands, rms, bass, mid, high, settings: RenderSettings,
                  raw_frame=None, kick: float = 0.0):
    """Rendu du spectre. Supporte la couleur personnalisée + 3 couleurs (Update 7)."""
    height, width = frame.shape[:2]
    is_v = settings.is_vertical

    eff_y = max(settings.spectrum_y, 0.72) if is_v else settings.spectrum_y
    base_y = int(height * eff_y)
    max_w = int(width * (0.86 if is_v else 0.74))
    gap = max(2, int(7 * width / WIDTH))
    bar_count = len(bands)
    bar_w = max(2, int((max_w - gap * (bar_count - 1)) / bar_count))
    total_w = bar_count * bar_w + (bar_count - 1) * gap
    start_x = width // 2 - total_w // 2
    size = settings.spectrum_size
    style = settings.spectrum_style

    # Update 7 — couleur simple ou 3 bandes
    sr, sg, sb = _parse_hex(settings.spectrum_color)
    use_custom = (sr, sg, sb) != (255, 255, 255)

    if settings.spectrum_tricolor:
        c_bass = _parse_hex(settings.spectrum_color)
        c_mid  = _parse_hex(settings.spectrum_color_mid)
        c_high = _parse_hex(settings.spectrum_color_high)

        def tint(brightness: int, bar_idx: int = 0) -> tuple:
            return _tricolor_for_bar(bar_idx, bar_count, brightness,
                                     c_bass, c_mid, c_high,
                                     kick, settings.spectrum_reactive)
    else:
        def tint(brightness: int, bar_idx: int = 0) -> tuple:
            if settings.spectrum_reactive and kick > 0.3:
                flash = min(1.0, (kick - 0.3) / 0.7)
                sr2 = int(sr + (255 - sr) * flash * 0.6)
                sg2 = int(sg + (255 - sg) * flash * 0.6)
                sb2 = int(sb + (255 - sb) * flash * 0.6)
                return _tint_bgr(brightness, sr2, sg2, sb2)
            return _tint_bgr(brightness, sr, sg, sb) if use_custom else (brightness, brightness, brightness)

    # ── Barres premium ────────────────────────────────────────────────────────
    if style == "Barres premium":
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h = int((height * 0.025 + value * height * 0.21 * size) * (0.82 + bass * 0.45 + rms * 0.2))
            bright = int(np.clip(105 + value * 150 + high * 55, 110, 255))
            rounded_rectangle(frame, (x1, base_y - h), (x2, base_y), max(1, bar_w // 2), tint(bright, i), -1)
        cv2.line(frame, (start_x, base_y + int(height * 0.022)),
                 (start_x + total_w, base_y + int(height * 0.022)),
                 tint(245, bar_count // 2), max(1, int(1 + bass * 5)), lineType=cv2.LINE_AA)

    # ── Barres néon (couleur propre, non affectée par tint) ───────────────────
    elif style == "Barres néon":
        glow_layer = np.zeros_like(frame)
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h = int((height * 0.025 + value * height * 0.21 * size) * (0.82 + bass * 0.45 + rms * 0.2))
            if h <= 0:
                continue
            t = min(1.0, float(i) / bar_count)
            r = int(255 * (1.0 - t * 0.6))
            g = int(80 + 120 * t)
            b = int(60 + 195 * t)
            bright = int(np.clip(0.6 + value * 0.4, 0, 1) * 255)
            color = (int(b * bright / 255), int(g * bright / 255), int(r * bright / 255))
            rounded_rectangle(frame, (x1, base_y - h), (x2, base_y), max(1, bar_w // 2), color, -1)
            glow_color = (min(255, b), min(255, g), min(255, r))
            rounded_rectangle(glow_layer, (x1 - 2, base_y - h - 4), (x2 + 2, base_y), max(1, bar_w // 2 + 2), glow_color, -1)
        blur_k = 15 | 1
        glow_layer = cv2.GaussianBlur(glow_layer, (blur_k, blur_k), 0)
        cv2.addWeighted(glow_layer, 0.55, frame, 1.0, 0, frame)

    # ── Symétrie miroir ───────────────────────────────────────────────────────
    elif style == "Symétrie miroir":
        center_y = base_y - int(height * 0.04)
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h_half = int((height * 0.015 + value * height * 0.13 * size) * (0.85 + bass * 0.55))
            bright = int(np.clip(115 + value * 140 + high * 55, 120, 255))
            rounded_rectangle(frame, (x1, center_y - h_half), (x2, center_y), max(1, bar_w // 2), tint(bright, i), -1)
            faded = int(bright * 0.65)
            rounded_rectangle(frame, (x1, center_y), (x2, center_y + h_half), max(1, bar_w // 2), tint(faded, i), -1)
        cv2.line(frame, (start_x, center_y), (start_x + total_w, center_y),
                 tint(255, bar_count // 2), max(1, int(1.5 + bass * 4)), lineType=cv2.LINE_AA)

    # ── Arc plasma / Onde plasma (couleurs propres) ───────────────────────────
    elif style == "Arc plasma":
        _draw_arc_plasma(frame, bands, bass, kick=0.0, settings=settings,
                         base_y=base_y, width=width, height=height, size=size)

    elif style == "Onde plasma":
        _draw_onde_plasma(frame, bands, rms, bass, mid, high,
                          base_y, start_x, total_w, bar_w, gap, height, width, size)

    # ── Waveform miroir ───────────────────────────────────────────────────────
    elif style == "Waveform miroir":
        center_y = base_y - int(height * 0.08)
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h = int((height * 0.012 + value * height * 0.12 * size) * (0.85 + bass * 0.55))
            bright = int(np.clip(105 + value * 150 + high * 55, 110, 255))
            rounded_rectangle(frame, (x1, center_y - h), (x2, center_y + h), max(1, bar_w // 2), tint(bright, i), -1)

    # ── Oscilloscope (Update 5) ───────────────────────────────────────────────
    elif style == "Oscilloscope":
        _draw_oscilloscope(frame, raw_frame, rms, bass, high, base_y,
                           start_x, total_w, height, width, size, tint)

    # ── Ligne fine ────────────────────────────────────────────────────────────
    elif style == "Ligne fine":
        pts = []
        for i, value in enumerate(bands):
            x = start_x + i * (bar_w + gap)
            y = base_y - int(value * height * 0.18 * size * (0.8 + mid * 0.4))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            cv2.line(frame, pts[i], pts[i + 1], tint(235, i),
                     max(1, int(2 * width / WIDTH)), lineType=cv2.LINE_AA)



def _draw_oscilloscope(frame, raw_frame, rms, bass, high, base_y,
                        start_x, total_w, height, width, size, tint_fn):
    """Oscilloscope : forme d'onde brute temps réel (Update 5).

    Trace les samples audio bruts sur toute la largeur du spectre.
    Deux lignes symétriques (haut/bas), épaisseur réactive.
    Halo lumineux sur les pics.
    """
    if raw_frame is None or len(raw_frame) == 0:
        return

    n_pts = 256
    samples = np.interp(
        np.linspace(0, len(raw_frame) - 1, n_pts),
        np.arange(len(raw_frame)),
        raw_frame,
    )

    amp_scale = height * 0.18 * size * (0.7 + bass * 0.8 + rms * 0.4)
    center_y  = base_y - int(height * 0.04)
    step      = total_w / max(1, n_pts - 1)
    lw        = max(1, int((1.5 + rms * 2.5) * width / WIDTH))

    glow = np.zeros_like(frame)
    pts_up   = []
    pts_down = []

    for i, s in enumerate(samples):
        x   = int(start_x + i * step)
        amp = int(np.clip(s * amp_scale, -height * 0.25, height * 0.25))
        pts_up.append(  (x, center_y - amp))
        pts_down.append((x, center_y + amp))

    bright = int(np.clip(140 + rms * 115 + high * 60, 140, 255))

    for pts in (pts_up, pts_down):
        for i in range(len(pts) - 1):
            cv2.line(frame, pts[i], pts[i + 1], tint_fn(bright), lw, cv2.LINE_AA)
            cv2.line(glow,  pts[i], pts[i + 1], tint_fn(bright), lw + 6, cv2.LINE_AA)

    # Ligne centrale de référence
    cv2.line(frame, (start_x, center_y), (start_x + total_w, center_y),
             tint_fn(60), 1, cv2.LINE_AA)

    glow = cv2.GaussianBlur(glow, (19, 19), 0)
    cv2.addWeighted(glow, 0.45, frame, 1.0, 0, frame)


def _draw_arc_plasma(frame, bands, bass, kick, settings, base_y, width, height, size):
    """Demi-cercle plasma au bas du cadre. Adapté automatiquement au format vertical."""
    n = min(len(bands), 96)
    sample = np.interp(np.linspace(0, len(bands) - 1, n), np.arange(len(bands)), bands)

    cx = width // 2
    cy = base_y + int(height * 0.05)

    # Rayon adapté à la largeur disponible
    radius = int(width * 0.32 * size + kick * 8)

    glow_layer = np.zeros_like(frame)

    for i, value in enumerate(sample):
        # Arc de -π à 0 (demi-cercle supérieur, ouverture vers le bas)
        angle = math.pi + (i / (n - 1)) * math.pi
        bar_len = int(8 + value * height * 0.09 * size + bass * 18)

        x1 = int(cx + math.cos(angle) * radius)
        y1 = int(cy + math.sin(angle) * radius)
        x2 = int(cx + math.cos(angle) * (radius + bar_len))
        y2 = int(cy + math.sin(angle) * (radius + bar_len))

        t = float(i) / n
        r = int(255 * (1.0 - t * 0.5))
        g = int(60 + 140 * t)
        b = int(80 + 175 * t)
        bright = int(np.clip(0.5 + value * 0.5, 0, 1))
        color = (int(b * (0.5 + bright * 0.5)), int(g * (0.5 + bright * 0.5)), int(r * (0.5 + bright * 0.5)))
        glow_color = (min(255, b), min(255, g), min(255, r))

        lw = max(1, int(3 * width / WIDTH))
        cv2.line(frame, (x1, y1), (x2, y2), color, lw, lineType=cv2.LINE_AA)
        cv2.line(glow_layer, (x1, y1), (x2, y2), glow_color, lw + 4, lineType=cv2.LINE_AA)

    # Cercle de référence
    bright_ring = int(np.clip(60 + bass * 80, 60, 140))
    cv2.circle(frame, (cx, cy), radius, (bright_ring, bright_ring, bright_ring),
               max(1, int(1.5 * width / WIDTH)), lineType=cv2.LINE_AA)

    blur_k = (31 | 1)
    glow_layer = cv2.GaussianBlur(glow_layer, (blur_k, blur_k), 0)
    cv2.addWeighted(glow_layer, 0.6, frame, 1.0, 0, frame)


def _draw_onde_plasma(frame, bands, rms, bass, mid, high, base_y, start_x, total_w, bar_w, gap, height, width, size):
    """Waveform épaisse avec halo lumineux coloré."""
    n = len(bands)
    glow_layer = np.zeros_like(frame)

    pts_main = []
    pts_mirror = []

    for i, value in enumerate(bands):
        x = start_x + i * (bar_w + gap)
        amplitude = int(value * height * 0.16 * size * (0.85 + bass * 0.5))
        pts_main.append((x, base_y - amplitude))
        pts_mirror.append((x, base_y + int(amplitude * 0.4)))

    # Onde principale avec épaisseur variable
    for i in range(len(pts_main) - 1):
        val = float(bands[i])
        t = float(i) / n
        r = int(200 + 55 * (1.0 - t))
        g = int(100 + 100 * t)
        b = int(50 + 200 * t)
        lw_main = max(2, int((2 + val * 5) * width / WIDTH))
        lw_glow = lw_main + 8
        cv2.line(frame, pts_main[i], pts_main[i + 1], (b // 2, g // 2, r // 2), lw_main, lineType=cv2.LINE_AA)
        cv2.line(glow_layer, pts_main[i], pts_main[i + 1], (b, g, r), lw_glow, lineType=cv2.LINE_AA)

    # Reflet atténué en bas
    for i in range(len(pts_mirror) - 1):
        bright = int(np.clip(80 + bands[i] * 80, 60, 160))
        cv2.line(frame, pts_mirror[i], pts_mirror[i + 1], (bright // 3, bright // 3, bright // 3),
                 max(1, int(1.5 * width / WIDTH)), lineType=cv2.LINE_AA)

    blur_k = (25 | 1)
    glow_layer = cv2.GaussianBlur(glow_layer, (blur_k, blur_k), 0)
    cv2.addWeighted(glow_layer, 0.65, frame, 1.0, 0, frame)


def draw_audio_orb(frame, bands, bass, kick, settings: RenderSettings):
    if settings.spectrum_style not in ("Cercle radial", "Cercle + barres"):
        return

    height, width = frame.shape[:2]
    is_v = settings.is_vertical

    if is_v:
        # En SHORT : orbe plus haut, sous la pochette
        center = (width // 2, int(height * 0.58))
    else:
        center = (width // 2, height // 2 - int(height * 0.09))

    radius = int(min(width, height) * 0.36 + kick * 12)
    n = min(len(bands), 112)
    sample = np.interp(np.linspace(0, len(bands) - 1, n), np.arange(len(bands)), bands)

    sr, sg, sb = _parse_hex(settings.spectrum_color)
    use_c = (sr, sg, sb) != (255, 255, 255)
    tri = settings.spectrum_tricolor
    if tri:
        c_bass = _parse_hex(settings.spectrum_color)
        c_mid  = _parse_hex(settings.spectrum_color_mid)
        c_high = _parse_hex(settings.spectrum_color_high)

    for i, value in enumerate(sample):
        angle = (i / n) * math.tau - math.pi / 2
        length = int(6 + value * height * 0.082 * settings.spectrum_size + bass * 12 + kick * 16)
        x1 = int(center[0] + math.cos(angle) * radius)
        y1 = int(center[1] + math.sin(angle) * radius)
        x2 = int(center[0] + math.cos(angle) * (radius + length))
        y2 = int(center[1] + math.sin(angle) * (radius + length))
        bright = int(np.clip(92 + value * 160 + bass * 40 + kick * 45, 105, 255))
        if tri:
            color = _tricolor_for_bar(i, n, bright, c_bass, c_mid, c_high,
                                      kick, settings.spectrum_reactive)
        elif use_c:
            color = _tint_bgr(bright, sr, sg, sb)
        else:
            color = (bright, bright, bright)
        cv2.line(frame, (x1, y1), (x2, y2), color,
                 max(1, int(2 * width / WIDTH)), lineType=cv2.LINE_AA)


def draw_music_linked_particles(frame, particles, high, kick, settings: RenderSettings):
    preset = PARTICLE_PRESETS[settings.particle_preset]
    if preset["count"] <= 0:
        particles.clear()
        return particles

    height, width = frame.shape[:2]
    target_count = int(preset["count"] * (width / WIDTH) ** 0.5)

    while len(particles) < target_count:
        particles.append(FloatingParticle(width, height, settings.particle_preset))
    if len(particles) > target_count:
        del particles[target_count:]

    layer = np.zeros_like(frame)
    for p in particles:
        p.update(high, kick, preset)
        p.draw(layer, high, kick, preset, width / WIDTH)

    layer = cv2.GaussianBlur(layer, (3, 3), 0)
    cv2.addWeighted(layer, 0.72, frame, 1.0, 0, frame)
    return particles


def draw_smoke(frame, smoke_blobs, bass, kick, settings: RenderSettings):
    preset = SMOKE_PRESETS[settings.smoke_preset]
    if preset["density"] <= 0:
        smoke_blobs.clear()
        return smoke_blobs

    height, width = frame.shape[:2]
    target = int(18 * preset["density"] * (width / WIDTH) ** 0.5)

    while len(smoke_blobs) < target:
        smoke_blobs.append(SmokeBlob(width, height))
    if len(smoke_blobs) > target:
        del smoke_blobs[target:]

    layer = np.zeros_like(frame)
    for blob in smoke_blobs:
        blob.update(bass, kick, preset)
        if settings.smoke_color == "Reggae":
            rgb = REGGAE_PALETTE[blob.color_index % len(REGGAE_PALETTE)]
        else:
            rgb = SMOKE_COLORS.get(settings.smoke_color, SMOKE_COLORS["Blanc"])
        color_bgr = (rgb[2], rgb[1], rgb[0])
        blob.draw(layer, color_bgr, bass, kick, preset)

    blur = preset["blur"] | 1
    if blur > 0:
        layer = cv2.GaussianBlur(layer, (blur, blur), 0)

    cv2.addWeighted(layer, 0.82, frame, 1.0, 0, frame)
    return smoke_blobs



# ── Disque vinyle + pochette ─────────────────────────────────────────────────
# Z-order : ombre → vinyle (tourne) → pochette sleeve (statique)
_vinyl_img_cache: dict[int, Image.Image] = {}    # vinyle.png redimensionné par rayon
# Chemins des assets (relatifs à ce fichier)
import os as _os
_ASSETS_DIR = _os.path.join(_os.path.dirname(_os.path.dirname(__file__)), "img")
_VINYL_PNG   = _os.path.join(_ASSETS_DIR, "vinyle.png")


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
    """Charge vinyle.png redimensionné au diamètre voulu, avec cache.
    Le fichier a déjà le centre transparent (trou du label).
    """
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
    """Génère le disque vinyle PIL (RGBA).

    Utilise vinyle.png comme corps du disque (avec sillons réels).
    La pochette s'affiche dans le label central circulaire.
    En mode vinyl_black=False, pochette visible dans le label uniquement.
    """
    size = radius * 2
    disk = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # ── Corps vinyle : vinyle.png réel ────────────────────────────────────────
    vinyl_base = _load_vinyl_png(cache_r if cache_r > 0 else radius)
    # ── Fond du disque : noir ou pochette selon le mode ──────────────────────
    # Le trou du vinyle.png représente 25.8% du rayon total
    # L'image doit remplir EXACTEMENT cette zone pour ne pas dépasser
    hole_ratio = 0.367   # mesuré sur vinyle.png (inner_r=188 / cx=512)
    hole_r = int(radius * hole_ratio)

    if vinyl_black:
        # Fond noir circulaire → trou reste noir (vinyle classique)
        base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circ_mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circ_mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        ImageDraw.Draw(base).ellipse((0, 0, size - 1, size - 1), fill=(10, 10, 10, 255))
        base.putalpha(circ_mask)
    else:
        # Fond noir + pochette dans le trou uniquement → ne dépasse PAS le vinyle
        base = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        circ_mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(circ_mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        ImageDraw.Draw(base).ellipse((0, 0, size - 1, size - 1), fill=(10, 10, 10, 255))
        base.putalpha(circ_mask)

        # Pochette dans la zone du trou uniquement
        label_sq = cover_pil.resize((hole_r * 2, hole_r * 2), Image.LANCZOS).convert("RGBA")
        label_mask = Image.new("L", (hole_r * 2, hole_r * 2), 0)
        ImageDraw.Draw(label_mask).ellipse((0, 0, hole_r * 2 - 1, hole_r * 2 - 1), fill=255)
        base.paste(label_sq, (radius - hole_r, radius - hole_r), mask=label_mask)

    disk = base

    # ── Superposer vinyle.png (sillons opaques, trou transparent) ─────────────
    if vinyl_base is not None:
        # Redimensionner si le pulse a changé la taille du disk vs le cache
        if vinyl_base.size != disk.size:
            vinyl_base = vinyl_base.resize(disk.size, Image.LANCZOS)
        disk = Image.alpha_composite(disk, vinyl_base)

    # ── Rotation globale (fond + vinyle ensemble) ─────────────────────────────
    disk = disk.rotate(-(angle % 360), resample=Image.BILINEAR, expand=False)

    # ── Trou de broche (après rotation, toujours centré) ─────────────────────
    c = size // 2
    hr = max(2, int(radius * 0.022))
    ImageDraw.Draw(disk).ellipse((c - hr, c - hr, c + hr, c + hr), fill=(8, 8, 8, 255))

    return disk


def _make_sleeve(cover_pil: Image.Image, side: int) -> Image.Image:
    """Génère la pochette d'album (RGBA) avec coins arrondis.
    Le cadre réactif est dessiné directement sur le numpy frame (draw_vinyl_disk).
    """
    radius_corner = max(4, int(side * 0.045))
    result = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq = cover_pil.resize((side, side), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, side - 1, side - 1),
                                            radius=radius_corner, fill=255)
    result.paste(sq, mask=mask)


    return result


def draw_vinyl_disk(
    frame: np.ndarray,
    cover_bgr: np.ndarray,
    angle: float,
    bass: float,
    kick: float,
    settings: RenderSettings,
) -> None:
    """Composition pochette + vinyle.

    Pochette d'album au premier plan (coins arrondis, statique, pulse sur beats).
    Vinyle qui sort à droite à l'arrière-plan (tourne en continu, réactif).
    """
    height, width = frame.shape[:2]
    is_v = settings.is_vertical
    scale = width / WIDTH

    # ── Dimensions ────────────────────────────────────────────────────────────
    # Pochette
    base_side = int(min(width, height) * 0.38 * settings.image_zoom)
    pulse_px   = int(base_side * (bass * 0.04 * settings.pulse_strength
                                  + kick * 0.07 * settings.pulse_strength))
    sleeve_side = max(40, base_side + pulse_px)

    # Vinyle : rayon basé sur base_side (sans pulse) pour la stabilité du cache
    base_vinyl_r = int(min(width, height) * 0.38 * settings.image_zoom * 0.52)
    pulse_vinyl  = int(base_vinyl_r * (bass * 0.04 + kick * 0.07) * settings.pulse_strength)
    vinyl_r = max(40, base_vinyl_r + pulse_vinyl)

    # ── Centre de la composition ───────────────────────────────────────────────
    group_cx = width // 2 - int(sleeve_side * 0.22)
    group_cy = int(height * 0.27) if is_v else height // 2 - int(height * 0.07)

    # Vinyle décalé à droite, centré VERTICALEMENT avec la pochette
    vinyl_cx = group_cx + int(sleeve_side * 0.62)
    vinyl_cy = group_cy   # même centre vertical que la pochette

    # ── Ombres ────────────────────────────────────────────────────────────────
    shadow = np.zeros_like(frame)
    # Ombre vinyle (uniquement la partie droite visible — masque par la pochette)
    cv2.circle(shadow, (vinyl_cx, vinyl_cy),
               vinyl_r + int(16 * scale), (35, 35, 35), -1)
    # Effacer l'ombre là où la pochette est dessinée (évite le débordement gauche)
    cv2.rectangle(shadow,
                  (group_cx - sleeve_side // 2 - 4, group_cy - sleeve_side // 2 - 4),
                  (group_cx + sleeve_side // 2 + 4, group_cy + sleeve_side // 2 + 4),
                  (0, 0, 0), -1)
    # Ombre de la pochette
    off = int(7 * scale)
    cv2.rectangle(shadow,
                  (group_cx - sleeve_side // 2 + off, group_cy - sleeve_side // 2 + off),
                  (group_cx + sleeve_side // 2 + off, group_cy + sleeve_side // 2 + off),
                  (35, 35, 35), -1)
    shadow = cv2.GaussianBlur(shadow, (45, 45), 0)
    cv2.addWeighted(shadow, 0.55, frame, 1.0, 0, frame)

    # ── Vinyle (arrière-plan) ──────────────────────────────────────────────────
    cover_pil = Image.fromarray(cv2.cvtColor(cover_bgr, cv2.COLOR_BGR2RGB))
    use_image_on_disk = not settings.vinyl_black
    vinyl_img  = _make_vinyl_disk(cover_pil, vinyl_r, angle,
                                  vinyl_black=not use_image_on_disk,
                                  cache_r=base_vinyl_r)
    _composite_image(frame, vinyl_img, vinyl_cx, vinyl_cy)

    # ── Pochette (avant-plan) ─────────────────────────────────────────────────
    sleeve_img = _make_sleeve(cover_pil, sleeve_side)
    _composite_image(frame, sleeve_img, group_cx, group_cy)




# ── Rendu complet d'une frame ─────────────────────────────────────────────────

def render_frame(bg, cover, particles, smoke_blobs, spec_frame, metrics,
                 smoothed_bands, settings: RenderSettings, vinyl_angle: float = 0.0,
                 frame_idx: int = 0, raw_frame=None):
    # Fond flottant (Update 5) — dérive sinusoïdale réactive aux basses
    # Utilise pad(edge) + crop pour éviter la ligne de bordure du np.roll
    if settings.floating_bg:
        phase = frame_idx * (2.0 * math.pi / (30 * 8))  # cycle 8s
        bass_val = float(metrics.get("bass", 0))
        dx = int(math.sin(phase) * 22 * (1.0 + bass_val * 1.8))
        dy = int(math.cos(phase * 0.65) * 12 * (1.0 + bass_val * 1.2))
        pad = 32  # pixels de marge — doit être >= max drift attendu
        padded = np.pad(bg, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
        py = pad + max(0, min(dy, pad * 2 - 1 - bg.shape[0] + bg.shape[0]))
        px = pad + max(0, min(dx, pad * 2 - 1 - bg.shape[1] + bg.shape[1]))
        # Clamp pour rester dans les limites
        py = max(0, min(py, padded.shape[0] - bg.shape[0]))
        px = max(0, min(px, padded.shape[1] - bg.shape[1]))
        frame = padded[py:py + bg.shape[0], px:px + bg.shape[1]].copy()
    else:
        frame = bg.copy()

    is_v = settings.is_vertical

    rms  = metrics["rms"]
    bass = metrics["bass"]
    mid  = metrics["mid"]
    high = metrics["high"]
    kick = metrics["kick"]

    particles   = draw_music_linked_particles(frame, particles, high, kick, settings)
    smoke_blobs = draw_smoke(frame, smoke_blobs, bass, kick, settings)

    bands = spectrum_bands(spec_frame, 84)
    smoothed_bands[:] = smoothed_bands * 0.76 + bands * 0.24

    draw_audio_orb(frame, smoothed_bands, bass, kick, settings)

    # Pochette / Vinyle — selon le mode
    if settings.vinyl_mode:
        # Vitesse de rotation : base + réactivité bass + kick
        new_vinyl_angle = vinyl_angle + 1.8   # vitesse constante — bass/kick n'affectent plus la rotation
        draw_vinyl_disk(frame, cover, vinyl_angle, bass, kick, settings)
    else:
        new_vinyl_angle = vinyl_angle
        overlay_center(frame, cover, bass, kick, settings.pulse_strength, is_vertical=is_v)

    # Texte
    eff_text_y = settings.text_y
    if is_v:
        eff_text_y = 0.62

    draw_reactive_text(frame, settings.title_text, rms, kick,
                       settings.text_x, eff_text_y,
                       artist=settings.artist_text,
                       font_name=getattr(settings, "font_name", "Défaut"))

    if settings.spectrum_style != "Cercle radial":
        draw_spectrum(frame, smoothed_bands, rms, bass, mid, high, settings, raw_frame=raw_frame, kick=kick)

    draw_vignette(frame)
    return frame, particles, smoke_blobs, smoothed_bands, new_vinyl_angle
