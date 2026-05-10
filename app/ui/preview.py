"""PreviewMixin — méthodes de preview live, waveform et audio.

Extrait de app/ui/app.py.
"""
from __future__ import annotations

import threading
import time

import cv2
import numpy as np
import librosa
from PIL import Image, ImageTk

from app.audio import compute_audio_features
from app.presets import PREVIEW_SECONDS, FPS
from app.renderer import load_cover_image, render_frame


class PreviewMixin:

    # ══════════════════════════════════════════════════════════════════════════
    # WAVEFORM
    # ══════════════════════════════════════════════════════════════════════════

    def _load_waveform(self, audio_path):
        def worker():
            try:
                y, sr = librosa.load(audio_path, sr=4000, mono=True)
                duration = len(y) / sr
                hop = max(1, int(sr * 0.08))
                rms = librosa.feature.rms(y=y, frame_length=hop*2, hop_length=hop)[0]
                rms = (rms / (np.max(rms) + 1e-9)).astype(np.float32)
                self.waveform_data = rms
                self.audio_total_duration = duration
                self.after(0, self._draw_waveform)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def _draw_waveform(self, cursor_t=None):
        from app.ui.app import ACCENT, ACCLT, MUTED, SUCCESS
        c = self._waveform_canvas
        if c is None or self.waveform_data is None:
            return
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 2 or h < 2:
            return

        data = self.waveform_data
        n = len(data)
        bar_w = max(1, w / n)
        center = h / 2
        for i, val in enumerate(data):
            x = i * bar_w
            amp = val * (h * 0.44)
            bright = int(70 + val * 120)
            color = f"#{bright:02x}{bright:02x}{bright:02x}"
            c.create_rectangle(x, center - amp, x + bar_w - 0.5, center + amp,
                                fill=color, outline="")

        if self.audio_total_duration > 0:
            try:
                t_start = float(self.preview_start.get().replace(",", ".") or 0)
            except ValueError:
                t_start = 0.0
            t_end = t_start + PREVIEW_SECONDS
            x0 = (t_start / self.audio_total_duration) * w
            x1 = min(w, (t_end / self.audio_total_duration) * w)
            c.create_rectangle(x0, 0, x1, h, fill=ACCENT, stipple="gray25", outline="")
            c.create_line(x0, 0, x0, h, fill=ACCLT, width=1)

        if cursor_t is not None and self.audio_total_duration > 0:
            cx = (cursor_t / self.audio_total_duration) * w
            c.create_line(cx, 0, cx, h, fill=SUCCESS, width=2)

        dur = self.audio_total_duration
        if dur > 0:
            tot = int(dur)
            mid_s = int(dur / 2)
            c.create_text(4,     h-4, text="0:00",                     anchor="sw", fill=MUTED, font=("Segoe UI", 7))
            c.create_text(w/2,   h-4, text=f"{mid_s//60}:{mid_s%60:02d}", anchor="s",  fill=MUTED, font=("Segoe UI", 7))
            c.create_text(w-4,   h-4, text=f"{tot//60}:{tot%60:02d}",  anchor="se", fill=MUTED, font=("Segoe UI", 7))

    def _on_waveform_click(self, event):
        c = self._waveform_canvas
        if c is None or self.audio_total_duration <= 0:
            return
        w = c.winfo_width()
        if w <= 0:
            return
        t = max(0.0, min((event.x / w) * self.audio_total_duration, self.audio_total_duration - 1))
        self.preview_start.set(f"{t:.1f}")
        self._draw_waveform()
        self._prepare_preview()

    def _tick_waveform_cursor(self):
        if not self.preview_running:
            return
        if self.audio_playing and self.preview_started_at is not None:
            try:
                t0 = float(self.preview_start.get().replace(",", ".") or 0)
            except ValueError:
                t0 = 0.0
            self._draw_waveform(cursor_t=t0 + (time.time() - self.preview_started_at))
        self.after(200, self._tick_waveform_cursor)

    # ══════════════════════════════════════════════════════════════════════════
    # PLEIN ÉCRAN
    # ══════════════════════════════════════════════════════════════════════════

    def _open_fullscreen(self):
        import customtkinter as ctk
        import tkinter as tk
        from app.ui.app import SUCCESS
        if self._fullscreen_win or not self.preview_ready:
            return

        win = ctk.CTkToplevel(self)
        win.title("TAC Studio — Preview plein écran  (Échap pour fermer)")
        win.configure(fg_color="#000000")
        win.attributes("-fullscreen", True)
        win.bind("<Escape>", lambda e: self._close_fullscreen())
        win.bind("<Double-Button-1>", lambda e: self._close_fullscreen())
        win.protocol("WM_DELETE_WINDOW", self._close_fullscreen)

        lbl = tk.Label(win, bg="#000000", bd=0, highlightthickness=0)
        lbl.pack(fill="both", expand=True)
        lbl.bind("<Escape>", lambda e: self._close_fullscreen())
        lbl.bind("<Double-Button-1>", lambda e: self._close_fullscreen())

        self._fullscreen_win    = win
        self._fullscreen_label  = lbl
        self._fullscreen_running = True
        self._tick_fullscreen()
        self._set_status("Plein écran actif — Échap ou double-clic pour fermer", SUCCESS)

    def _close_fullscreen(self):
        from app.ui.app import SUCCESS
        self._fullscreen_running = False
        if self._fullscreen_win:
            try:
                self._fullscreen_win.destroy()
            except Exception:
                pass
        self._fullscreen_win    = None
        self._fullscreen_label  = None
        self._fullscreen_photo  = None
        self._set_status("Preview active", SUCCESS)

    def _tick_fullscreen(self):
        if not self._fullscreen_running or not self._fullscreen_label:
            return
        if not self.preview_ready or self.preview_features is None:
            self.after(100, self._tick_fullscreen)
            return

        settings = self._current_settings(preview=True)
        total = len(self.preview_features["rms"])
        i = self.preview_index % total
        metrics = {k: float(self.preview_features[k][i])
                   for k in ("rms", "kick", "bass", "mid", "high")}

        raw_f = self.preview_features["raw"][i] if "raw" in self.preview_features else None
        frame, _, _, _, _ = render_frame(
            self.preview_bg, self.preview_cover,
            [], [],
            self.preview_features["spec"][:, i],
            metrics, self.preview_smoothed.copy(), settings,
            self.vinyl_angle,
            frame_idx=i,
            raw_frame=raw_f,
        )

        try:
            fw = self._fullscreen_win.winfo_width()
            fh = self._fullscreen_win.winfo_height()
            if fw > 10 and fh > 10:
                fr_ratio = frame.shape[1] / frame.shape[0]
                win_ratio = fw / fh
                if fr_ratio > win_ratio:
                    dw = fw
                    dh = int(fw / fr_ratio)
                else:
                    dh = fh
                    dw = int(fh * fr_ratio)
                resized = cv2.resize(frame, (dw, dh), interpolation=cv2.INTER_LINEAR)
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                self._fullscreen_photo = ImageTk.PhotoImage(Image.fromarray(rgb))
                self._fullscreen_label.configure(image=self._fullscreen_photo)
        except Exception:
            pass

        self.after(int(1000 / FPS), self._tick_fullscreen)

    # ══════════════════════════════════════════════════════════════════════════
    # PREVIEW
    # ══════════════════════════════════════════════════════════════════════════

    def _prepare_preview(self):
        from tkinter import messagebox
        from app.ui.app import WARN, DANGER, SUCCESS
        self._stop_audio()
        if not self.audio_path or not self.image_path:
            return
        self.preview_running = False
        fmt = "9:16" if self.preview_is_vertical else "16:9"
        self._set_status(f"Analyse [{fmt}]...", WARN)
        s = self._current_settings(preview=True)

        def worker():
            try:
                feat = compute_audio_features(s.audio_path, FPS, PREVIEW_SECONDS, s.start_offset)
                bg, cov = load_cover_image(
                    s.image_path, s.background_blur, s.image_zoom,
                    s.output_width, s.output_height,
                    bg_mode=s.bg_mode,
                    gradient_top=s.gradient_top,
                    gradient_bottom=s.gradient_bottom,
                    background_brightness=s.background_brightness,
                )
                self.preview_features  = feat
                self.preview_bg        = bg
                self.preview_cover     = cov
                self.preview_particles = []
                self.preview_smoke     = []
                self.preview_smoothed  = np.zeros(84, dtype=np.float32)
                self.preview_index     = 0
                self.preview_ready     = True
                self.preview_running   = True
                self._preview_job = self.after(0, self._tick_preview)
                self.after(0, self._draw_waveform)
                self.after(0, lambda: self._set_status(f"Preview [{fmt}] active", SUCCESS))
            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda: messagebox.showerror("Erreur preview", msg))
                self.after(0, lambda: self._set_status("Erreur preview", DANGER))

        threading.Thread(target=worker, daemon=True).start()

    def _reload_visuals_only(self):
        if not self.audio_path or not self.image_path:
            return
        try:
            s = self._current_settings(preview=True)
            bg, cov = load_cover_image(
                s.image_path, s.background_blur, s.image_zoom,
                s.output_width, s.output_height,
                bg_mode=s.bg_mode,
                gradient_top=s.gradient_top,
                gradient_bottom=s.gradient_bottom,
                background_brightness=s.background_brightness,
            )
            self.preview_bg        = bg
            self.preview_cover     = cov
            self.preview_particles = []
            self.preview_smoke     = []
            self.preview_smoothed  = np.zeros(84, dtype=np.float32)
            self.vinyl_angle       = 0.0
        except Exception:
            pass

    def _tick_preview(self):
        from app.ui.app import FPS
        if not self.preview_running or self.is_rendering or not self.preview_ready or self.preview_features is None:
            return

        s = self._current_settings(preview=True)
        total = len(self.preview_features["rms"])

        if self.audio_playing and self.preview_started_at is not None:
            self.preview_index = int((time.time() - self.preview_started_at) * FPS) % total

        i = self.preview_index % total
        metrics = {k: float(self.preview_features[k][i])
                   for k in ("rms", "kick", "bass", "mid", "high")}

        raw_f = self.preview_features["raw"][i] if "raw" in self.preview_features else None
        if s.spectrum_color_auto and self.preview_bg is not None and i == 0:
            from app.renderer import extract_dominant_color
            auto_c = extract_dominant_color(self.preview_cover)
            if hasattr(self, "_spec_swatch"):
                self._set_spectrum_color(auto_c)

        frame, self.preview_particles, self.preview_smoke, self.preview_smoothed, self.vinyl_angle = render_frame(
            self.preview_bg, self.preview_cover,
            self.preview_particles, self.preview_smoke,
            self.preview_features["spec"][:, i],
            metrics, self.preview_smoothed, s,
            self.vinyl_angle,
            frame_idx=self.preview_index,
            raw_frame=raw_f,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb)

        try:
            wrap_w = self.preview_wrap.winfo_width()
            wrap_h = self.preview_wrap.winfo_height()
        except Exception:
            wrap_w, wrap_h = 0, 0

        if wrap_w < 10 or wrap_h < 10:
            self._preview_job = self.after(int(1000 / FPS), self._tick_preview)
            return

        if self.preview_is_vertical:
            pw = int(wrap_h * 9 / 16)
            if pw <= wrap_w:
                ph = wrap_h
            else:
                pw = wrap_w
                ph = int(wrap_w * 16 / 9)
            content_img = img.resize((pw, ph), Image.LANCZOS)
            final = Image.new("RGB", (wrap_w, wrap_h), (0, 0, 0))
            final.paste(content_img, ((wrap_w - pw) // 2, (wrap_h - ph) // 2))
        else:
            final = img.resize((wrap_w, wrap_h), Image.LANCZOS)

        self.photo = ImageTk.PhotoImage(final)
        self.preview_label.configure(image=self.photo)

        if not self.audio_playing:
            self.preview_index += 1

        self._preview_job = self.after(int(1000 / FPS), self._tick_preview)

    def _play_preview_audio(self):
        import subprocess as _sp
        import shutil
        from tkinter import messagebox
        from app.ui.app import SUCCESS, PREVIEW_SECONDS
        if not shutil.which("ffplay"):
            messagebox.showerror("Audio", "ffplay introuvable — installe FFmpeg complet.")
            return
        try:
            self._stop_audio()
            start = float(self.preview_start.get().strip().replace(",", ".") or 0)
            self.ffplay_process = _sp.Popen([
                "ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet",
                "-ss", f"{start:.3f}", "-t", str(PREVIEW_SECONDS), self.audio_path,
            ])
            self.audio_playing = True
            self.preview_started_at = time.time()
            self.preview_index = 0
            self._set_status("▶ Preview  (Espace = pause · F11 = plein écran)", SUCCESS)
            self._tick_waveform_cursor()
        except Exception as exc:
            messagebox.showerror("Audio preview", str(exc))

    def _pause_preview_audio(self):
        self._stop_audio()
        self._set_status("Preview pausée  (Espace pour reprendre)")
        self._draw_waveform()

    def _stop_audio(self):
        self.audio_playing = False
        self.preview_started_at = None
        if self.ffplay_process:
            try:
                self.ffplay_process.terminate()
                self.ffplay_process.wait(timeout=2)
            except Exception:
                pass
            self.ffplay_process = None
