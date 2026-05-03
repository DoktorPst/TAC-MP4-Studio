"""Analyse audio — extraction des features réactives.

Update 8 (patch) :
- raw_frames vectorisé numpy (suppression boucle Python ~5400 iter)
- imports déplacés en tête de fichier
"""
from __future__ import annotations

import numpy as np
import librosa


def _resize_1d(arr: np.ndarray, target_len: int) -> np.ndarray:
    if len(arr) == target_len:
        return arr
    x_old = np.linspace(0.0, 1.0, len(arr))
    x_new = np.linspace(0.0, 1.0, target_len)
    return np.interp(x_new, x_old, arr).astype(np.float32)


def _resize_2d_time(spec: np.ndarray, target_frames: int) -> np.ndarray:
    if spec.shape[1] == target_frames:
        return spec
    old_frames = spec.shape[1]
    indices = np.linspace(0.0, old_frames - 1, target_frames)
    left  = np.floor(indices).astype(np.int32)
    right = np.minimum(left + 1, old_frames - 1)
    frac  = (indices - left).astype(np.float32)
    return (spec[:, left] * (1.0 - frac) + spec[:, right] * frac).astype(np.float32)


def _band_energy(spec: np.ndarray, freqs: np.ndarray,
                 low: float, high: float) -> np.ndarray:
    mask = (freqs >= low) & (freqs <= high)
    if not np.any(mask):
        return np.zeros(spec.shape[1], dtype=np.float32)
    vals = np.mean(spec[mask, :], axis=0)
    return (vals / (np.max(vals) + 1e-9)).astype(np.float32)


def compute_audio_features(
    audio_path: str,
    fps: int,
    duration_limit: float | None = None,
    start_offset: float = 0.0,
) -> dict:
    """Extrait toutes les features audio nécessaires au rendu frame par frame."""
    y, sr = librosa.load(audio_path, sr=44100, mono=True,
                         duration=duration_limit, offset=start_offset)
    duration = len(y) / sr
    if duration <= 0:
        raise RuntimeError("Audio vide ou illisible.")

    hop    = max(1, int(sr / fps))
    frames = max(1, int(duration * fps))

    rms   = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms   = (rms / (np.max(rms) + 1e-9)).astype(np.float32)

    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onset = (onset / (np.max(onset) + 1e-9)).astype(np.float32)

    stft_amp = np.abs(librosa.stft(y, n_fft=4096, hop_length=hop))
    freqs    = librosa.fft_frequencies(sr=sr, n_fft=4096)
    bass     = _band_energy(stft_amp, freqs, 20,   180)
    mid      = _band_energy(stft_amp, freqs, 180,  2500)
    high     = _band_energy(stft_amp, freqs, 2500, 12000)

    spec_db = librosa.amplitude_to_db(stft_amp, ref=np.max)
    spec    = np.clip((spec_db + 80.0) / 80.0, 0.0, 1.0).astype(np.float32)

    # ── Oscilloscope : raw_frames vectorisé (Update 8 — fix PERF 1) ──────────
    # Construit la matrice (frames × osc_len) sans boucle Python
    osc_len    = 512
    half       = osc_len // 2
    frame_idxs = np.arange(frames, dtype=np.int32) * hop        # centre de chaque frame
    starts     = np.clip(frame_idxs - half, 0, max(0, len(y) - osc_len))
    # Vectorisé : index matrix shape (frames, osc_len)
    col_idxs   = starts[:, np.newaxis] + np.arange(osc_len, dtype=np.int32)
    col_idxs   = np.clip(col_idxs, 0, len(y) - 1)
    raw_frames  = y[col_idxs].astype(np.float32)                # (frames, osc_len)

    return {
        "rms":      _resize_1d(rms,    frames),
        "kick":     _resize_1d(onset,  frames),
        "bass":     _resize_1d(bass,   frames),
        "mid":      _resize_1d(mid,    frames),
        "high":     _resize_1d(high,   frames),
        "spec":     _resize_2d_time(spec, frames),
        "raw":      raw_frames,
        "duration": duration,
    }
