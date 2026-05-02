from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import librosa
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


WIDTH = 1920
HEIGHT = 1080
PREVIEW_W = 960
PREVIEW_H = 540
FPS = 30
PREVIEW_SECONDS = 22


SMOKE_COLORS = {
    "Blanc": (235, 235, 235),
    "Or chaud": (214, 172, 86),
    "Rouge": (215, 70, 65),
    "Bleu néon": (75, 145, 255),
    "Violet": (168, 95, 255),
    "Vert": (92, 220, 130),
    "Reggae": (90, 210, 95),
}

GLOBAL_PRESETS = {
    "Clean White": {
        "particle_preset": "Épuré",
        "smoke_preset": "Légère",
        "smoke_color": "Blanc",
        "spectrum_style": "Barres premium",
        "spectrum_size": 0.95,
        "spectrum_y": 0.90,
        "image_zoom": 1.00,
        "pulse_strength": 0.85,
    },
    "Dark Premium": {
        "particle_preset": "Premium",
        "smoke_preset": "Cinématique",
        "smoke_color": "Blanc",
        "spectrum_style": "Cercle radial",
        "spectrum_size": 1.05,
        "spectrum_y": 0.90,
        "image_zoom": 1.00,
        "pulse_strength": 1.10,
    },
    "Neon Club": {
        "particle_preset": "Énergie",
        "smoke_preset": "Dense",
        "smoke_color": "Bleu néon",
        "spectrum_style": "Cercle + barres",
        "spectrum_size": 1.20,
        "spectrum_y": 0.88,
        "image_zoom": 0.96,
        "pulse_strength": 1.45,
    },
    "Reggae Smoke": {
        "particle_preset": "Premium",
        "smoke_preset": "Dense",
        "smoke_color": "Reggae",
        "spectrum_style": "Waveform miroir",
        "spectrum_size": 1.10,
        "spectrum_y": 0.88,
        "image_zoom": 1.00,
        "pulse_strength": 1.25,
    },
    "Chill Lo-Fi": {
        "particle_preset": "Pluie lumineuse",
        "smoke_preset": "Cinématique",
        "smoke_color": "Violet",
        "spectrum_style": "Ligne fine",
        "spectrum_size": 0.85,
        "spectrum_y": 0.91,
        "image_zoom": 1.05,
        "pulse_strength": 0.75,
    },
}

PARTICLE_PRESETS = {
    "Aucune": {"count": 0, "speed": 0.0, "size": 0.0, "alpha": 0.0},
    "Épuré": {"count": 120, "speed": 0.65, "size": 1.0, "alpha": 0.65},
    "Premium": {"count": 260, "speed": 1.0, "size": 1.15, "alpha": 0.85},
    "Énergie": {"count": 440, "speed": 1.55, "size": 1.25, "alpha": 1.0},
    "Pluie lumineuse": {"count": 360, "speed": 1.2, "size": 0.9, "alpha": 0.75},
}

SMOKE_PRESETS = {
    "Aucune": {"density": 0.0, "speed": 0.0, "blur": 0},
    "Légère": {"density": 0.35, "speed": 0.55, "blur": 31},
    "Cinématique": {"density": 0.78, "speed": 0.85, "blur": 45},
    "Dense": {"density": 1.18, "speed": 1.15, "blur": 59},
}

SPECTRUM_STYLES = ["Barres premium", "Cercle radial", "Cercle + barres", "Waveform miroir", "Ligne fine"]


@dataclass
class RenderSettings:
    audio_path: str
    image_path: str
    output_path: str
    title_text: str
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
    background_blur: int = 38


class FloatingParticle:
    def __init__(self, width: int, height: int, preset_name: str):
        self.width = width
        self.height = height
        self.preset_name = preset_name
        self.reset()

    def reset(self):
        self.x = random.uniform(0, self.width)
        self.y = random.uniform(0, self.height)
        self.base_size = random.uniform(1.0, 3.8)
        self.speed = random.uniform(0.25, 1.35)
        if self.preset_name == "Pluie lumineuse":
            self.angle = random.uniform(math.pi * 0.42, math.pi * 0.58)
        else:
            self.angle = random.uniform(-math.pi * 0.92, -math.pi * 0.08)
        self.alpha = random.uniform(35, 145)

    def update(self, high: float, kick: float, preset: dict):
        boost = 1.0 + high * preset["speed"] * 7.5 + kick * 4.5
        self.x += math.cos(self.angle) * self.speed * boost
        self.y += math.sin(self.angle) * self.speed * boost
        if self.x < -40 or self.x > self.width + 40 or self.y < -40 or self.y > self.height + 40:
            self.reset()
            self.y = -20 if self.preset_name == "Pluie lumineuse" else self.height + 20

    def draw(self, layer: np.ndarray, high: float, kick: float, preset: dict, scale: float):
        energy = min(1.0, high * 0.8 + kick * 0.5)
        size = int(self.base_size * preset["size"] * scale * (1.0 + energy * 3.2))
        alpha = int(min(235, (self.alpha + energy * 125) * preset["alpha"]))
        cv2.circle(layer, (int(self.x), int(self.y)), max(1, size), (alpha, alpha, alpha), -1, lineType=cv2.LINE_AA)


class SmokeBlob:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.reset(first=True)

    def reset(self, first=False):
        self.x = random.uniform(-0.15 * self.width, 1.15 * self.width)
        self.y = random.uniform(0.48 * self.height, 1.15 * self.height) if first else self.height + random.uniform(20, 180)
        self.radius = random.uniform(90, 250) * (self.width / WIDTH)
        self.speed = random.uniform(0.15, 0.8)
        self.drift = random.uniform(-0.45, 0.45)
        self.phase = random.uniform(0, math.tau)
        self.alpha = random.uniform(22, 70)

    def update(self, bass: float, kick: float, preset: dict):
        self.y -= self.speed * (1.0 + bass * 3.5 + kick * 2.0) * preset["speed"]
        self.x += self.drift * (1.0 + bass * 1.6)
        self.phase += 0.025 + bass * 0.06
        if self.y < -self.radius * 2:
            self.reset()

    def draw(self, layer: np.ndarray, color_bgr: tuple[int, int, int], bass: float, kick: float, preset: dict):
        if preset["density"] <= 0:
            return
        r = int(self.radius * (1.0 + bass * 0.65 + kick * 0.35 + 0.08 * math.sin(self.phase)))
        alpha = int(min(155, self.alpha * preset["density"] * (1.0 + bass * 1.1 + kick * 0.5)))
        color = tuple(int(v * alpha / 255) for v in color_bgr)
        cv2.circle(layer, (int(self.x), int(self.y)), max(5, r), color, -1, lineType=cv2.LINE_AA)


def require_ffmpeg():
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("FFmpeg est introuvable. Ajoute son dossier bin au PATH Windows.")


def ffmpeg_has_nvenc() -> bool:
    try:
        result = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return "h264_nvenc" in (result.stdout + result.stderr)
    except Exception:
        return False


def run_ffmpeg(cmd: list[str]) -> None:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError("Erreur FFmpeg :\n" + result.stderr[-3000:])


def safe_font(size: int, bold=False):
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return ImageFont.truetype(p, size=size)
    return ImageFont.load_default()


def load_cover_image(path: str, blur_radius: int, zoom: float, width=WIDTH, height=HEIGHT):
    img = Image.open(path).convert("RGB")
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
        top = (src_h - new_h) // 2
        bg = bg.crop((0, top, src_w, top + new_h))

    bg = bg.resize((width, height), Image.LANCZOS)
    if blur_radius > 0:
        bg = bg.filter(ImageFilter.GaussianBlur(blur_radius))
    bg = ImageEnhance.Brightness(bg).enhance(0.16)
    bg = ImageEnhance.Contrast(bg).enhance(1.25)
    bg_arr = cv2.cvtColor(np.array(bg), cv2.COLOR_RGB2BGR)
    bg_arr = cv2.addWeighted(bg_arr, 0.50, np.zeros_like(bg_arr), 0.50, 0)

    cover = img.copy()
    max_side = int(min(width, height) * 0.53 * zoom)
    cover.thumbnail((max_side, max_side), Image.LANCZOS)
    cover_arr = cv2.cvtColor(np.array(cover), cv2.COLOR_RGB2BGR)
    return bg_arr, cover_arr


def rounded_rectangle(img, pt1, pt2, radius, color, thickness=-1):
    x1, y1 = pt1
    x2, y2 = pt2
    radius = max(1, min(radius, abs(x2 - x1) // 2, abs(y2 - y1) // 2))

    if thickness == -1:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)
    else:
        cv2.rectangle(img, pt1, pt2, color, thickness, lineType=cv2.LINE_AA)


def overlay_center(base, overlay, bass, kick, pulse_strength):
    height, width = base.shape[:2]
    h, w = overlay.shape[:2]
    x = (width - w) // 2
    y = (height - h) // 2 - int(height * 0.09)
    pulse = int((8 + bass * 20 * pulse_strength + kick * 35 * pulse_strength) * (width / WIDTH))

    glow = np.zeros_like(base)
    rounded_rectangle(glow, (x - pulse, y - pulse), (x + w + pulse, y + h + pulse), 24, (150, 150, 150), -1)
    glow = cv2.GaussianBlur(glow, (61, 61), 0)
    cv2.addWeighted(glow, 0.42, base, 1.0, 0, base)

    pad = max(6, int(18 * width / WIDTH))
    rounded_rectangle(base, (x - pad, y - pad), (x + w + pad, y + h + pad), 18, (0, 0, 0), -1)
    rounded_rectangle(base, (x - pad, y - pad), (x + w + pad, y + h + pad), 18, (238, 238, 238), 2)
    base[y:y + h, x:x + w] = overlay


def draw_reactive_text(frame, text, rms, kick):
    if not text.strip():
        return

    height, width = frame.shape[:2]
    scale = width / WIDTH
    font_size = max(18, int(56 * scale * (1.0 + kick * 0.10 + rms * 0.025)))
    font = safe_font(font_size, bold=True)

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    max_width = int(width * 0.78)
    words = text.strip().split()
    lines, current = [], ""

    for word in words:
        test = (current + " " + word).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width or not current:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)
    lines = lines[:2]

    line_h = int(font_size * 1.16)
    y = int(height * 0.70) - len(lines) * line_h // 2
    text_alpha = int(210 + kick * 45)

    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (width - tw) // 2
        yy = y + idx * line_h

        for offset, alpha in [(5, 60), (2, 120)]:
            draw.text((x - offset, yy), line, font=font, fill=(0, 0, 0, alpha))
            draw.text((x + offset, yy), line, font=font, fill=(0, 0, 0, alpha))
            draw.text((x, yy - offset), line, font=font, fill=(0, 0, 0, alpha))
            draw.text((x, yy + offset), line, font=font, fill=(0, 0, 0, alpha))

        draw.text((x, yy), line, font=font, fill=(255, 255, 255, text_alpha))

    img = Image.alpha_composite(img.convert("RGBA"), layer)
    frame[:] = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2BGR)


def resize_1d(arr, target_len):
    if len(arr) == target_len:
        return arr
    x_old = np.linspace(0, 1, len(arr))
    x_new = np.linspace(0, 1, target_len)
    return np.interp(x_new, x_old, arr)


def resize_2d_time(spec, target_frames):
    old_frames = spec.shape[1]
    if old_frames == target_frames:
        return spec
    x_old = np.linspace(0, 1, old_frames)
    x_new = np.linspace(0, 1, target_frames)
    resized = np.zeros((spec.shape[0], target_frames), dtype=np.float32)
    for i in range(spec.shape[0]):
        resized[i] = np.interp(x_new, x_old, spec[i])
    return resized


def band_energy(spec, sr, low, high):
    freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return np.zeros(spec.shape[1], dtype=np.float32)
    vals = np.mean(spec[mask, :], axis=0)
    return (vals / (np.max(vals) + 1e-9)).astype(np.float32)


def compute_audio_features(audio_path, fps, duration_limit=None, start_offset=0.0):
    y, sr = librosa.load(audio_path, sr=44100, mono=True, duration=duration_limit, offset=start_offset)
    duration = len(y) / sr

    if duration <= 0:
        raise RuntimeError("Audio vide ou illisible.")

    hop = max(1, int(sr / fps))

    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms = rms / (np.max(rms) + 1e-9)

    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onset = onset / (np.max(onset) + 1e-9)

    stft_amp = np.abs(librosa.stft(y, n_fft=4096, hop_length=hop))
    bass = band_energy(stft_amp, sr, 20, 180)
    mid = band_energy(stft_amp, sr, 180, 2500)
    high = band_energy(stft_amp, sr, 2500, 12000)

    spec_db = librosa.amplitude_to_db(stft_amp, ref=np.max)
    spec = np.clip((spec_db + 80.0) / 80.0, 0.0, 1.0)

    frames = max(1, int(duration * fps))

    return {
        "rms": resize_1d(rms, frames),
        "kick": resize_1d(onset, frames),
        "bass": resize_1d(bass, frames),
        "mid": resize_1d(mid, frames),
        "high": resize_1d(high, frames),
        "spec": resize_2d_time(spec, frames),
        "duration": duration,
    }


def spectrum_bands(spec_frame, bar_count=84):
    bins = len(spec_frame)
    idx = np.geomspace(1, bins, bar_count + 1).astype(int) - 1
    idx = np.clip(idx, 0, bins - 1)

    vals = []
    for i in range(bar_count):
        start = idx[i]
        end = max(idx[i + 1], start + 1)
        vals.append(float(np.mean(spec_frame[start:end])))

    return np.clip(np.power(np.array(vals, dtype=np.float32), 1.55), 0, 1)


def draw_spectrum(frame, bands, rms, bass, mid, high, settings):
    height, width = frame.shape[:2]
    base_y = int(height * settings.spectrum_y)
    max_w = int(width * 0.74)
    gap = max(2, int(7 * width / WIDTH))
    bar_count = len(bands)
    bar_w = max(2, int((max_w - gap * (bar_count - 1)) / bar_count))
    total_w = bar_count * bar_w + (bar_count - 1) * gap
    start_x = width // 2 - total_w // 2
    size = settings.spectrum_size

    if settings.spectrum_style == "Ligne fine":
        pts = []
        for i, value in enumerate(bands):
            x = start_x + i * (bar_w + gap)
            y = base_y - int(value * height * 0.18 * size * (0.8 + mid * 0.4))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            cv2.line(frame, pts[i], pts[i + 1], (235, 235, 235), max(1, int(2 * width / WIDTH)), lineType=cv2.LINE_AA)

    elif settings.spectrum_style == "Waveform miroir":
        center_y = base_y - int(height * 0.08)
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h = int((height * 0.012 + value * height * 0.12 * size) * (0.85 + bass * 0.55))
            bright = int(np.clip(105 + value * 150 + high * 55, 110, 255))
            rounded_rectangle(frame, (x1, center_y - h), (x2, center_y + h), max(1, bar_w // 2), (bright, bright, bright), -1)

    else:
        for i, value in enumerate(bands):
            x1 = start_x + i * (bar_w + gap)
            x2 = x1 + bar_w
            h = int((height * 0.025 + value * height * 0.21 * size) * (0.82 + bass * 0.45 + rms * 0.2))
            y1 = base_y - h
            bright = int(np.clip(105 + value * 150 + high * 55, 110, 255))
            rounded_rectangle(frame, (x1, y1), (x2, base_y), max(1, bar_w // 2), (bright, bright, bright), -1)

        cv2.line(
            frame,
            (start_x, base_y + int(height * 0.022)),
            (start_x + total_w, base_y + int(height * 0.022)),
            (245, 245, 245),
            max(1, int(1 + bass * 5)),
            lineType=cv2.LINE_AA,
        )


def draw_audio_orb(frame, bands, bass, kick, settings):
    if settings.spectrum_style not in ["Cercle radial", "Cercle + barres"]:
        return

    height, width = frame.shape[:2]
    center = (width // 2, height // 2 - int(height * 0.09))
    radius = int(min(width, height) * 0.36 + kick * 12)
    n = min(len(bands), 112)
    sample = np.interp(np.linspace(0, len(bands) - 1, n), np.arange(len(bands)), bands)

    for i, value in enumerate(sample):
        angle = (i / n) * math.tau - math.pi / 2
        length = int(6 + value * height * 0.082 * settings.spectrum_size + bass * 12 + kick * 16)

        x1 = int(center[0] + math.cos(angle) * radius)
        y1 = int(center[1] + math.sin(angle) * radius)
        x2 = int(center[0] + math.cos(angle) * (radius + length))
        y2 = int(center[1] + math.sin(angle) * (radius + length))

        bright = int(np.clip(92 + value * 160 + bass * 40 + kick * 45, 105, 255))
        cv2.line(frame, (x1, y1), (x2, y2), (bright, bright, bright), max(1, int(2 * width / WIDTH)), lineType=cv2.LINE_AA)


def draw_music_linked_particles(frame, particles, high, kick, settings):
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


def draw_smoke(frame, smoke_blobs, bass, kick, settings):
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

    rgb = SMOKE_COLORS.get(settings.smoke_color, SMOKE_COLORS["Blanc"])
    color_bgr = (rgb[2], rgb[1], rgb[0])

    layer = np.zeros_like(frame)

    for blob in smoke_blobs:
        blob.update(bass, kick, preset)
        blob.draw(layer, color_bgr, bass, kick, preset)

    blur = preset["blur"]
    if blur > 0:
        if blur % 2 == 0:
            blur += 1
        layer = cv2.GaussianBlur(layer, (blur, blur), 0)

    cv2.addWeighted(layer, 0.82, frame, 1.0, 0, frame)
    return smoke_blobs


def draw_vignette(frame):
    height, width = frame.shape[:2]
    y, x = np.ogrid[:height, :width]
    cx, cy = width / 2, height / 2
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    mask = np.clip(1 - dist / (min(width, height) * 0.92), 0.16, 1.0)
    frame[:] = (frame.astype(np.float32) * mask[..., None]).astype(np.uint8)


def render_frame(bg, cover, particles, smoke_blobs, spec_frame, metrics, smoothed_bands, title, settings):
    frame = bg.copy()

    rms = metrics["rms"]
    bass = metrics["bass"]
    mid = metrics["mid"]
    high = metrics["high"]
    kick = metrics["kick"]

    particles = draw_music_linked_particles(frame, particles, high, kick, settings)
    smoke_blobs = draw_smoke(frame, smoke_blobs, bass, kick, settings)

    bands = spectrum_bands(spec_frame, 84)
    smoothed_bands[:] = smoothed_bands * 0.76 + bands * 0.24

    draw_audio_orb(frame, smoothed_bands, bass, kick, settings)
    overlay_center(frame, cover, bass, kick, settings.pulse_strength)
    draw_reactive_text(frame, title, rms, kick)

    if settings.spectrum_style != "Cercle radial":
        draw_spectrum(frame, smoothed_bands, rms, bass, mid, high, settings)

    draw_vignette(frame)
    return frame, particles, smoke_blobs, smoothed_bands


def add_audio_to_video(temp_video, audio_path, output_path, duration, start_offset):
    if ffmpeg_has_nvenc():
        cmd = [
            "ffmpeg", "-y",
            "-i", temp_video,
            "-ss", f"{start_offset:.3f}",
            "-i", audio_path,
            "-t", f"{duration:.3f}",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "h264_nvenc",
            "-preset", "p6",
            "-tune", "hq",
            "-rc", "vbr",
            "-cq", "16",
            "-b:v", "0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            "-shortest",
            output_path,
        ]

        try:
            run_ffmpeg(cmd)
            return
        except RuntimeError:
            pass

    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-ss", f"{start_offset:.3f}",
        "-i", audio_path,
        "-t", f"{duration:.3f}",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "16",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "320k",
        "-ar", "44100",
        "-ac", "2",
        "-movflags", "+faststart",
        "-shortest",
        output_path,
    ]
    run_ffmpeg(cmd)


def render_video(settings: RenderSettings, progress_callback=None):
    require_ffmpeg()

    out_dir = Path(settings.output_path).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    temp_video = str(out_dir / "_temp_tac_visualizer_no_audio.mp4")

    if progress_callback:
        progress_callback("Analyse audio bass/kick/aigus...")

    features = compute_audio_features(settings.audio_path, FPS, settings.duration_limit, settings.start_offset)
    bg, cover = load_cover_image(settings.image_path, settings.background_blur, settings.image_zoom, WIDTH, HEIGHT)

    particles, smoke_blobs = [], []
    writer = cv2.VideoWriter(temp_video, cv2.VideoWriter_fourcc(*"mp4v"), FPS, (WIDTH, HEIGHT))

    if not writer.isOpened():
        raise RuntimeError("Impossible d'ouvrir le moteur vidéo OpenCV.")

    smoothed = np.zeros(84, dtype=np.float32)
    smooth_kick = 0.0

    try:
        total = len(features["rms"])

        for i in range(total):
            smooth_kick = smooth_kick * 0.68 + float(features["kick"][i]) * 0.32

            metrics = {
                "rms": float(features["rms"][i]),
                "kick": smooth_kick,
                "bass": float(features["bass"][i]),
                "mid": float(features["mid"][i]),
                "high": float(features["high"][i]),
            }

            frame, particles, smoke_blobs, smoothed = render_frame(
                bg, cover, particles, smoke_blobs, features["spec"][:, i], metrics, smoothed, settings.title_text, settings
            )

            writer.write(frame)

            if progress_callback and i % FPS == 0:
                progress_callback(f"Rendu : {i / max(1, total - 1) * 100:.1f}%")

    finally:
        writer.release()

    if progress_callback:
        progress_callback("Encodage MP4 qualité max avec musique...")

    add_audio_to_video(temp_video, settings.audio_path, settings.output_path, features["duration"], settings.start_offset)

    try:
        os.remove(temp_video)
    except OSError:
        pass

    if progress_callback:
        progress_callback(f"Terminé : {settings.output_path}")


def open_file(path: str):
    try:
        os.startfile(path)  # type: ignore[attr-defined]
    except Exception:
        pass
