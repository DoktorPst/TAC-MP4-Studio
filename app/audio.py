"""Analyse audio — extraction des features réactives.

Optimisations vs version originale :
- resize_2d_time : vectorisé numpy (boucle Python élim., ~50× plus rapide)
- band_energy : freqs calculées une seule fois, passées en paramètre
- API publique stable : compute_audio_features()
"""
from __future__ import annotations

import numpy as np
import librosa


def _resize_1d(arr: np.ndarray, target_len: int) -> np.ndarray:
    """Rééchantillonne un tableau 1D vers target_len points (interpolation linéaire)."""
    if len(arr) == target_len:
        return arr
    x_old = np.linspace(0.0, 1.0, len(arr))
    x_new = np.linspace(0.0, 1.0, target_len)
    return np.interp(x_new, x_old, arr).astype(np.float32)


def _resize_2d_time(spec: np.ndarray, target_frames: int) -> np.ndarray:
    """Rééchantillonne un spectrogramme 2D (bins × frames) sur l'axe temporel.

    Version vectorisée : pas de boucle Python sur les bins.
    Gain typique : 50× sur un spectrogramme 2049×5400.
    """
    if spec.shape[1] == target_frames:
        return spec

    old_frames = spec.shape[1]
    # Indices flottants dans l'ancien domaine
    indices = np.linspace(0.0, old_frames - 1, target_frames)
    left = np.floor(indices).astype(np.int32)
    right = np.minimum(left + 1, old_frames - 1)
    frac = (indices - left).astype(np.float32)  # shape: (target_frames,)

    # Interpolation matricielle : shape (bins, target_frames)
    return (spec[:, left] * (1.0 - frac) + spec[:, right] * frac).astype(np.float32)


def _band_energy(
    spec: np.ndarray,
    freqs: np.ndarray,
    low: float,
    high: float,
) -> np.ndarray:
    """Énergie normalisée [0-1] dans une bande fréquentielle.

    Reçoit freqs pré-calculé pour éviter le recalcul redondant.
    """
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
    """Extrait toutes les features audio nécessaires au rendu frame par frame.

    Retourne un dict avec les clés :
    - rms, kick, bass, mid, high : arrays float32 de longueur `frames`
    - spec : array float32 (bins × frames)
    - duration : durée effective en secondes
    """
    y, sr = librosa.load(
        audio_path,
        sr=44100,
        mono=True,
        duration=duration_limit,
        offset=start_offset,
    )
    duration = len(y) / sr

    if duration <= 0:
        raise RuntimeError("Audio vide ou illisible.")

    hop = max(1, int(sr / fps))
    frames = max(1, int(duration * fps))

    # RMS
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop)[0]
    rms = (rms / (np.max(rms) + 1e-9)).astype(np.float32)

    # Onset (kick)
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    onset = (onset / (np.max(onset) + 1e-9)).astype(np.float32)

    # Spectrogramme STFT
    stft_amp = np.abs(librosa.stft(y, n_fft=4096, hop_length=hop))

    # Fréquences calculées UNE SEULE FOIS pour les 3 bandes
    freqs = librosa.fft_frequencies(sr=sr, n_fft=4096)
    bass = _band_energy(stft_amp, freqs, 20, 180)
    mid  = _band_energy(stft_amp, freqs, 180, 2500)
    high = _band_energy(stft_amp, freqs, 2500, 12000)

    # Spectrogramme normalisé [0-1] pour affichage
    spec_db = librosa.amplitude_to_db(stft_amp, ref=np.max)
    spec = np.clip((spec_db + 80.0) / 80.0, 0.0, 1.0).astype(np.float32)

    return {
        "rms":      _resize_1d(rms,    frames),
        "kick":     _resize_1d(onset,  frames),
        "bass":     _resize_1d(bass,   frames),
        "mid":      _resize_1d(mid,    frames),
        "high":     _resize_1d(high,   frames),
        "spec":     _resize_2d_time(spec, frames),
        "duration": duration,
    }
