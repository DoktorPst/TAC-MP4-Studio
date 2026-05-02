"""TAC MP4 Studio — Update 3

Nouveautés :
  1. Fond dégradé configurable avec color pickers (alternative à la photo floutée)
  2. Miniatures dans l'historique (screenshot auto après chaque export)
  3. Mode plein écran preview (bouton ⛶ ou double-clic sur la preview)
"""
from __future__ import annotations

import re
import shutil
import threading
import time
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox
import tkinter as tk

import customtkinter as ctk
import cv2
import librosa
import numpy as np
import soundfile as sf
from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

from app.audio import compute_audio_features
from app.config import load_config, save_config, safe_name, DEFAULT_CREATIONS_DIR
from app.exporter import render_video, open_file
from app.models import RenderSettings
from app.presets import (
    GLOBAL_PRESETS, PARTICLE_PRESETS, SMOKE_COLORS, SMOKE_PRESETS, SPECTRUM_STYLES,
    PREVIEW_SECONDS, PREVIEW_W, PREVIEW_H, SHORT_WIDTH, SHORT_HEIGHT, FPS,
)
from app.renderer import load_cover_image, render_frame

PREVIEW_W_V = 304
PREVIEW_H_V = 540
WAVEFORM_H  = 56

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG      = "#0a0a0a"
SURF    = "#111111"
SURF2   = "#191919"
SURF3   = "#212121"
BORDER  = "#2a2a2a"
ACCENT  = "#7c3aed"
ACCHOV  = "#6d28d9"
ACCLT   = "#a78bfa"
TEXT    = "#f4f4f5"
MUTED   = "#71717a"
SUCCESS = "#22c55e"
WARN    = "#f59e0b"
DANGER  = "#ef4444"

FONT_H1 = FONT_H2 = FONT_SEC = FONT_SM = FONT_MU = None
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}


def _init_fonts():
    global FONT_H1, FONT_H2, FONT_SEC, FONT_SM, FONT_MU
    FONT_H1  = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
    FONT_H2  = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")
    FONT_SEC = ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
    FONT_SM  = ctk.CTkFont(family="Segoe UI", size=10)
    FONT_MU  = ctk.CTkFont(family="Segoe UI", size=9)


def _btn(parent, text, command, accent=False, danger=False, small=False, **kw):
    defaults = {
        "fg_color":      ACCENT if accent else ("#7f1d1d" if danger else SURF3),
        "hover_color":   ACCHOV if accent else ("#991b1b" if danger else SURF2),
        "text_color":    TEXT,
        "font":          FONT_SM if small else FONT_H2,
        "corner_radius": 8,
    }
    defaults.update(kw)
    return ctk.CTkButton(parent, text=text, command=command, **defaults)


def _card(parent, **kw):
    return ctk.CTkFrame(parent, fg_color=SURF2, corner_radius=10,
                        border_color=BORDER, border_width=1, **kw)


def _sep(parent):
    ctk.CTkFrame(parent, height=1, fg_color=BORDER, corner_radius=0).pack(
        fill="x", padx=12, pady=(8, 0))


class App(ctk.CTk if not _DND_AVAILABLE else TkinterDnD.Tk):

    def __init__(self) -> None:
        super().__init__()
        _init_fonts()

        self.title("TAC MP4 Studio")
        self.configure(bg=BG) if _DND_AVAILABLE else self.configure(fg_color=BG)
        self.config_data = load_config()
        settings = self.config_data.get("settings", {})
        self.geometry(settings.get("window_geometry", "1300x820+60+30"))
        self.minsize(1180, 760)

        # ── State ─────────────────────────────────────────────────────────────
        self.audio_path   = ""
        self.image_path   = ""
        self.output_path  = ""
        self.project_root = self.config_data.get("project_root", str(DEFAULT_CREATIONS_DIR))
        Path(self.project_root).mkdir(parents=True, exist_ok=True)
        self.history: list[dict] = self.config_data.get("history", [])

        # ── Tkinter vars ───────────────────────────────────────────────────────
        self.title_text       = tk.StringVar(value=settings.get("title_text", ""))
        self.artist_text      = tk.StringVar(value=settings.get("artist_text", ""))
        self.status_var       = tk.StringVar(value="Prêt")
        self.project_root_var = tk.StringVar(value=self.project_root)
        self.global_preset    = tk.StringVar(value=settings.get("global_preset",   "Dark Premium"))
        self.particle_preset  = tk.StringVar(value=settings.get("particle_preset", "Premium"))
        self.smoke_preset     = tk.StringVar(value=settings.get("smoke_preset",    "Cinématique"))
        self.smoke_color      = tk.StringVar(value=settings.get("smoke_color",     "Blanc"))
        self.spectrum_style   = tk.StringVar(value=settings.get("spectrum_style",  "Cercle radial"))
        self.spectrum_size    = tk.DoubleVar(value=float(settings.get("spectrum_size",  1.05)))
        self.spectrum_y       = tk.DoubleVar(value=float(settings.get("spectrum_y",     0.90)))
        self.image_zoom       = tk.DoubleVar(value=float(settings.get("image_zoom",     1.00)))
        self.pulse_strength   = tk.DoubleVar(value=float(settings.get("pulse_strength", 1.10)))
        self.text_x           = tk.DoubleVar(value=float(settings.get("text_x",         0.50)))
        self.text_y           = tk.DoubleVar(value=float(settings.get("text_y",         0.70)))
        self.preview_start    = tk.StringVar(value=settings.get("preview_start", "0"))
        self.project_name_var = tk.StringVar()
        self.export_mode      = tk.StringVar(value=settings.get("export_mode", "COMPLET"))

        # Update 3 — fond dégradé
        self.bg_mode         = tk.StringVar(value=settings.get("bg_mode", "photo"))
        self.gradient_top    = settings.get("gradient_top",    "#1a1a2e")
        self.gradient_bottom = settings.get("gradient_bottom", "#0f3460")

        # ── Preview state ──────────────────────────────────────────────────────
        self.preview_is_vertical  = False
        self.preview_ready        = False
        self.preview_running      = False
        self.audio_playing        = False
        self.preview_started_at: float | None = None
        self.ffplay_process       = None
        self.preview_index        = 0
        self.preview_features: dict | None    = None
        self.preview_bg: np.ndarray | None    = None
        self.preview_cover: np.ndarray | None = None
        self.preview_particles: list = []
        self.preview_smoke: list     = []
        self.preview_smoothed        = np.zeros(84, dtype=np.float32)
        self.photo: ImageTk.PhotoImage | None = None
        self.is_rendering            = False
        self._persist_job: str | None = None
        self._export_overlay_frame: ctk.CTkFrame | None = None
        self._ffmpeg_banner: ctk.CTkFrame | None = None

        # Waveform
        self.waveform_data: np.ndarray | None = None
        self.audio_total_duration: float = 0.0
        self._waveform_canvas: tk.Canvas | None = None

        # Update 3 — plein écran
        self._fullscreen_win: ctk.CTkToplevel | None   = None
        self._fullscreen_label: tk.Label | None         = None
        self._fullscreen_photo: ImageTk.PhotoImage | None = None
        self._fullscreen_running: bool = False

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<space>",  lambda e: self._kb_play_pause())
        self.bind("<r>",      lambda e: self._prepare_preview())
        self.bind("<R>",      lambda e: self._prepare_preview())
        self.bind("<Escape>", lambda e: self._kb_escape())
        self.bind("<F11>",    lambda e: self._open_fullscreen())

        if _DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)

        self.show_home()
        self.after(400, self._check_ffmpeg)

    # ══════════════════════════════════════════════════════════════════════════
    # RACCOURCIS
    # ══════════════════════════════════════════════════════════════════════════

    def _kb_play_pause(self):
        if not hasattr(self, "preview_label") or not self.preview_label:
            return
        if self.audio_playing:
            self._pause_preview_audio()
        else:
            self._play_preview_audio()

    def _kb_escape(self):
        if self._fullscreen_win:
            self._close_fullscreen()
        elif hasattr(self, "preview_label") and self.preview_label:
            self.show_home()

    # ══════════════════════════════════════════════════════════════════════════
    # PLEIN ÉCRAN (Update 3 — Feature 3)
    # ══════════════════════════════════════════════════════════════════════════

    def _open_fullscreen(self):
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

        frame, _, _, _ = render_frame(
            self.preview_bg, self.preview_cover,
            [], [],
            self.preview_features["spec"][:, i],
            metrics, self.preview_smoothed.copy(), settings,
        )

        try:
            fw = self._fullscreen_win.winfo_width()
            fh = self._fullscreen_win.winfo_height()
            if fw > 10 and fh > 10:
                # Calcul letterbox
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
    # FFMPEG CHECK
    # ══════════════════════════════════════════════════════════════════════════

    def _check_ffmpeg(self):
        missing = [t for t in ("ffmpeg", "ffplay") if not shutil.which(t)]
        if not missing:
            return
        tools = " et ".join(missing)
        banner = ctk.CTkFrame(self, fg_color="#431407", corner_radius=0, height=40)
        banner.pack(fill="x", side="bottom")
        banner.pack_propagate(False)
        ctk.CTkLabel(banner, text=f"⚠  {tools} introuvable — export et preview audio indisponibles.",
                     text_color=WARN, font=FONT_SM).pack(side="left", padx=16, pady=10)
        ctk.CTkLabel(banner, text="→ Installe FFmpeg et ajoute-le au PATH",
                     text_color="#fdba74", font=FONT_MU).pack(side="left")
        _btn(banner, "✕", banner.destroy, small=True, width=32, height=24,
             fg_color="transparent", hover_color="#7c2d12").pack(side="right", padx=12)

    # ══════════════════════════════════════════════════════════════════════════
    # DRAG & DROP
    # ══════════════════════════════════════════════════════════════════════════

    def _on_drop(self, event):
        raw = event.data.strip()
        paths = re.findall(r"\{([^}]+)\}", raw) if raw.startswith("{") else raw.split()
        audio_found = image_found = ""
        for p in paths:
            ext = Path(p).suffix.lower()
            if ext in AUDIO_EXTS and not audio_found:
                audio_found = p
            elif ext in IMAGE_EXTS and not image_found:
                image_found = p
        if not audio_found and not image_found:
            self._set_status("Format non reconnu", DANGER)
            return
        if audio_found:
            self.audio_path = audio_found
        if image_found:
            self.image_path = image_found
        if self.audio_path and self.image_path:
            self.show_editor()
        elif self.audio_path:
            self.show_step_image()

    # ══════════════════════════════════════════════════════════════════════════
    # UI BUILD
    # ══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        hdr = ctk.CTkFrame(self, height=58, fg_color=SURF, corner_radius=0)
        hdr.pack(fill="x", side="top")
        hdr.pack_propagate(False)
        ctk.CTkLabel(hdr, text="TAC", font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=ACCLT).pack(side="left", padx=(20, 0), pady=14)
        ctk.CTkLabel(hdr, text=" Studio", font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=TEXT).pack(side="left", pady=14)
        ctk.CTkLabel(hdr, text="  ⌨  Espace · R · Échap · F11",
                     text_color=MUTED, font=FONT_MU).pack(side="left", padx=20)
        self._status_dot = ctk.CTkLabel(hdr, text="●", text_color=MUTED,
                                        font=ctk.CTkFont("Segoe UI", 11))
        self._status_dot.pack(side="right", padx=(0, 8))
        self._status_lbl = ctk.CTkLabel(hdr, textvariable=self.status_var,
                                        text_color=MUTED, font=FONT_SM)
        self._status_lbl.pack(side="right", padx=(0, 4))

        self.main = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.main.pack(fill="both", expand=True)

    def _clear_main(self):
        self._stop_audio()
        self.preview_running = False
        self._waveform_canvas = None
        self._close_fullscreen()
        for child in self.main.winfo_children():
            child.destroy()

    def _set_status(self, text, color=MUTED):
        self.status_var.set(text)
        if hasattr(self, "_status_dot"):
            self._status_dot.configure(text_color=color)
            self._status_lbl.configure(text_color=color)

    def _on_close(self):
        try:
            self._persist_now()
            self._stop_audio()
            self._close_fullscreen()
        finally:
            self.destroy()

    # ══════════════════════════════════════════════════════════════════════════
    # PAGES
    # ══════════════════════════════════════════════════════════════════════════

    def show_home(self):
        self._clear_main()
        self._set_status("Accueil")
        center = ctk.CTkFrame(self.main, fg_color="transparent")
        center.place(relx=0.5, rely=0.46, anchor="center")
        ctk.CTkLabel(center, text="TAC", font=ctk.CTkFont("Segoe UI", 64, "bold"),
                     text_color=ACCLT).pack()
        ctk.CTkLabel(center, text="MP4 Studio", font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=TEXT).pack(pady=(0, 4))
        ctk.CTkLabel(center, text="Vidéos musicales réactives automatiques",
                     text_color=MUTED, font=FONT_SM).pack(pady=(0, 32))
        _btn(center, "  ✦  CRÉER UNE VIDÉO", self.show_step_audio,
             accent=True, width=280, height=52,
             font=ctk.CTkFont("Segoe UI", 14, "bold")).pack(pady=6)
        _btn(center, "  ☰  Historique", self.show_history,
             width=280, height=42).pack(pady=6)

    def show_step_audio(self):
        self._clear_main()
        self._set_status("Étape 1 / 2 — Audio")
        center = ctk.CTkFrame(self.main, fg_color="transparent")
        center.place(relx=0.5, rely=0.44, anchor="center")
        ctk.CTkLabel(center, text="Choisir la musique",
                     font=ctk.CTkFont("Segoe UI", 24, "bold"), text_color=TEXT).pack(pady=(0, 6))
        ctk.CTkLabel(center, text="MP3 · WAV · FLAC · OGG · M4A",
                     text_color=MUTED, font=FONT_SM).pack(pady=(0, 32))
        _btn(center, "  🎵  Importer un fichier audio", self._pick_audio,
             accent=True, width=300, height=50).pack(pady=6)
        _btn(center, "← Retour", self.show_home, small=True, width=140).pack(pady=(16, 0))

    def show_step_image(self):
        self._clear_main()
        self._set_status("Étape 2 / 2 — Pochette")
        center = ctk.CTkFrame(self.main, fg_color="transparent")
        center.place(relx=0.5, rely=0.44, anchor="center")
        ctk.CTkLabel(center, text="Choisir la pochette",
                     font=ctk.CTkFont("Segoe UI", 24, "bold"), text_color=TEXT).pack(pady=(0, 6))
        fname_card = _card(center)
        fname_card.pack(fill="x", pady=(0, 28), ipady=8, ipadx=12)
        ctk.CTkLabel(fname_card, text="🎵  " + Path(self.audio_path).name,
                     text_color=ACCLT, font=FONT_SM).pack(padx=16, pady=8)
        _btn(center, "  🖼  Importer une image", self._pick_image,
             accent=True, width=300, height=50).pack(pady=6)
        ctk.CTkLabel(center, text="PNG · JPG · JPEG · WEBP",
                     text_color=MUTED, font=FONT_MU).pack(pady=(4, 16))
        _btn(center, "← Retour", self.show_step_audio, small=True, width=140).pack()

    # ── Historique avec miniatures (Update 3 — Feature 2) ─────────────────────

    def show_history(self):
        self._clear_main()
        self._set_status("Historique")
        outer = ctk.CTkFrame(self.main, fg_color=BG)
        outer.pack(fill="both", expand=True, padx=32, pady=24)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(top, text="Historique", font=FONT_H1, text_color=TEXT).pack(side="left")
        _btn(top, "← Accueil", self.show_home, small=True, width=120).pack(side="right")

        items = self._sorted_history()
        if not items:
            ctk.CTkLabel(outer, text="Aucune création pour l'instant.",
                         text_color=MUTED, font=FONT_SM).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                        scrollbar_button_color=SURF3,
                                        scrollbar_button_hover_color=ACCENT)
        scroll.pack(fill="both", expand=True)

        for item in items:
            card = _card(scroll)
            card.pack(fill="x", pady=5, padx=2)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            # ── Miniature (Update 3) ───────────────────────────────────────
            thumb_path = Path(item.get("folder", "")) / "_thumb.jpg"
            if not thumb_path.exists():
                # Chercher aussi _SHORT_thumb.jpg ou thumb direct de la vidéo
                vid = item.get("video", "")
                if vid:
                    thumb_path = Path(vid).parent / (Path(vid).stem + "_thumb.jpg")

            if thumb_path.exists():
                try:
                    thumb_img = Image.open(thumb_path).convert("RGB")
                    thumb_img.thumbnail((160, 90))
                    ctk_img = ctk.CTkImage(light_image=thumb_img, dark_image=thumb_img,
                                           size=(160, 90))
                    ctk.CTkLabel(inner, image=ctk_img, text="").pack(side="left", padx=(0, 14))
                except Exception:
                    self._thumb_placeholder(inner)
            else:
                self._thumb_placeholder(inner)

            # ── Infos ──────────────────────────────────────────────────────
            info = ctk.CTkFrame(inner, fg_color="transparent")
            info.pack(side="left", fill="x", expand=True)

            kind = item.get("type", "complet").upper()
            kind_color = {"SHORT": ACCLT, "CHECK": WARN, "COMPLET": SUCCESS}.get(kind, TEXT)

            row1 = ctk.CTkFrame(info, fg_color="transparent")
            row1.pack(fill="x", anchor="w")
            ctk.CTkLabel(row1, text=item.get("name", "Sans nom"),
                         font=FONT_H2, text_color=TEXT, anchor="w").pack(side="left")
            ctk.CTkLabel(row1, text=f"  [{kind}]",
                         font=FONT_SEC, text_color=kind_color).pack(side="left")

            ctk.CTkLabel(info, text=item.get("created_at", ""),
                         font=FONT_MU, text_color=MUTED, anchor="w").pack(anchor="w", pady=(2, 8))

            btns = ctk.CTkFrame(info, fg_color="transparent")
            btns.pack(anchor="w")
            _btn(btns, "📂 Ouvrir dossier",
                 lambda f=item.get("folder", ""): open_file(f),
                 small=True, width=130, height=28).pack(side="left", padx=(0, 6))
            _btn(btns, "▶ Ouvrir vidéo",
                 lambda v=item.get("video", ""): open_file(v),
                 small=True, width=110, height=28).pack(side="left", padx=(0, 6))
            _btn(btns, "✕ Supprimer",
                 lambda i=item: self._delete_history_item(i),
                 small=True, width=100, height=28, danger=True).pack(side="left")

    def _thumb_placeholder(self, parent):
        ph = ctk.CTkFrame(parent, fg_color=SURF3, corner_radius=6,
                          width=160, height=90)
        ph.pack(side="left", padx=(0, 14))
        ph.pack_propagate(False)
        ctk.CTkLabel(ph, text="🎵", font=ctk.CTkFont("Segoe UI", 28),
                     text_color=MUTED).place(relx=0.5, rely=0.5, anchor="center")

    def _sorted_history(self):
        return sorted(self.history, key=lambda x: x.get("created_at", ""), reverse=True)

    def _delete_history_item(self, item):
        if messagebox.askyesno("Historique",
                               f"Supprimer '{item.get('name')}' de l'historique ?\n(Fichiers conservés.)"):
            self.history = [h for h in self.history if h.get("folder") != item.get("folder")]
            self._persist_now()
            self.show_history()

    # ── Éditeur ───────────────────────────────────────────────────────────────

    def show_editor(self):
        self._clear_main()
        self._set_status("Preview", SUCCESS)

        if self.audio_path:
            self._load_waveform(self.audio_path)

        left = ctk.CTkFrame(self.main, fg_color=BG)
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)
        right_outer = ctk.CTkFrame(self.main, fg_color=BG, width=340)
        right_outer.pack(side="right", fill="y", padx=(0, 16), pady=16)
        right_outer.pack_propagate(False)

        # Preview
        preview_wrap = ctk.CTkFrame(left, fg_color="#000000", corner_radius=12,
                                    border_color=BORDER, border_width=1)
        preview_wrap.pack(fill="both", expand=True)
        self.preview_label = tk.Label(preview_wrap, bg="#000000", bd=0, highlightthickness=0)
        self.preview_label.pack(fill="both", expand=True, padx=2, pady=2)
        self.preview_label.bind("<Double-Button-1>", lambda e: self._open_fullscreen())

        # Waveform
        wf_frame = ctk.CTkFrame(left, fg_color=SURF, corner_radius=8,
                                 border_color=BORDER, border_width=1, height=WAVEFORM_H)
        wf_frame.pack(fill="x", pady=(6, 0))
        wf_frame.pack_propagate(False)
        self._waveform_canvas = tk.Canvas(wf_frame, bg="#0d0d0d", bd=0,
                                          highlightthickness=0, height=WAVEFORM_H - 4)
        self._waveform_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self._waveform_canvas.bind("<Button-1>", self._on_waveform_click)
        self._waveform_canvas.bind("<Configure>", lambda e: self._draw_waveform())
        ctk.CTkLabel(wf_frame, text="Clic = déplacer preview · Zone violette = durée preview · Double-clic preview = plein écran",
                     text_color=MUTED, font=FONT_MU).pack(side="bottom", pady=1)

        # Contrôles
        ctrl = ctk.CTkFrame(left, fg_color="transparent")
        ctrl.pack(fill="x", pady=(8, 0))
        _btn(ctrl, "▶ Preview", self._play_preview_audio,
             accent=True, width=110, height=34, small=True).pack(side="left", padx=(0, 6))
        _btn(ctrl, "⏸", self._pause_preview_audio,
             width=42, height=34, small=True).pack(side="left", padx=(0, 6))
        _btn(ctrl, "⟲ Recharger", self._prepare_preview,
             width=110, height=34, small=True).pack(side="left", padx=(0, 6))
        _btn(ctrl, "⛶ Plein écran", self._open_fullscreen,
             width=120, height=34, small=True).pack(side="left", padx=(0, 12))
        self._fmt_btn = _btn(ctrl,
                             "9:16 → 16:9" if self.preview_is_vertical else "16:9 → 9:16",
                             self._toggle_preview_format,
                             width=120, height=34, small=True,
                             fg_color=ACCENT if self.preview_is_vertical else SURF3,
                             hover_color=ACCHOV if self.preview_is_vertical else SURF2)
        self._fmt_btn.pack(side="left")
        _btn(ctrl, "← Accueil", self.show_home,
             width=100, height=34, small=True).pack(side="right")

        # Panneau droit
        right_scroll = ctk.CTkScrollableFrame(right_outer, fg_color="transparent",
                                              scrollbar_button_color=SURF3,
                                              scrollbar_button_hover_color=ACCENT)
        right_scroll.pack(fill="both", expand=True)
        r = right_scroll

        # Fichiers
        self._section_title(r, "📁  Fichiers")
        fc = _card(r)
        fc.pack(fill="x", pady=(0, 10), padx=4)
        ctk.CTkLabel(fc, text=self._short_name(self.audio_path),
                     text_color=ACCLT, font=FONT_SM, anchor="w").pack(fill="x", padx=14, pady=(10, 2))
        ctk.CTkLabel(fc, text=self._short_name(self.image_path),
                     text_color=MUTED, font=FONT_MU, anchor="w").pack(fill="x", padx=14, pady=(0, 8))
        br = ctk.CTkFrame(fc, fg_color="transparent")
        br.pack(fill="x", padx=10, pady=(0, 10))
        _btn(br, "🎵 Musique", self.show_step_audio, small=True, height=30).pack(
            side="left", padx=(0, 6), fill="x", expand=True)
        _btn(br, "🖼 Pochette", self.show_step_image, small=True, height=30).pack(
            side="left", fill="x", expand=True)

        # Texte
        self._section_title(r, "✍  Texte")
        tc = _card(r)
        tc.pack(fill="x", pady=(0, 10), padx=4)
        ti = ctk.CTkFrame(tc, fg_color="transparent")
        ti.pack(fill="x", padx=10, pady=10)
        ctk.CTkLabel(ti, text="Artiste", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        ctk.CTkEntry(ti, textvariable=self.artist_text,
                     placeholder_text="Nom de l'artiste  (optionnel)",
                     fg_color=SURF3, border_color=BORDER, text_color=TEXT,
                     font=FONT_SM).pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(ti, text="Titre", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        ctk.CTkEntry(ti, textvariable=self.title_text,
                     placeholder_text="Titre du son  (optionnel)",
                     fg_color=SURF3, border_color=BORDER, text_color=TEXT,
                     font=FONT_SM).pack(fill="x", pady=(2, 8))
        self._text_preview_lbl = ctk.CTkLabel(ti, text="", text_color=ACCLT,
                                               font=FONT_MU, anchor="w")
        self._text_preview_lbl.pack(anchor="w", pady=(0, 4))
        self.artist_text.trace_add("write", lambda *_: self._update_text_preview())
        self.title_text.trace_add("write",  lambda *_: self._update_text_preview())
        self._update_text_preview()
        _sep(ti)
        self._slider_row(ti, "Position X", self.text_x, 0.05, 0.95)
        self._slider_row(ti, "Position Y", self.text_y, 0.15, 0.92)

        # Preset
        self._section_title(r, "⚡  Preset rapide")
        pc = _card(r)
        pc.pack(fill="x", pady=(0, 10), padx=4)
        ctk.CTkComboBox(pc, variable=self.global_preset,
                        values=list(GLOBAL_PRESETS.keys()),
                        command=lambda _: self._apply_global_preset(),
                        fg_color=SURF3, border_color=BORDER,
                        button_color=ACCENT, button_hover_color=ACCHOV,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM).pack(fill="x", padx=10, pady=(10, 6))
        _btn(pc, "APPLIQUER", self._apply_global_preset,
             accent=True, height=34, small=True).pack(fill="x", padx=10, pady=(0, 10))

        # Ambiance
        self._section_title(r, "🌫  Ambiance")
        ac = _card(r)
        ac.pack(fill="x", pady=(0, 10), padx=4)
        ai = ctk.CTkFrame(ac, fg_color="transparent")
        ai.pack(fill="x", padx=10, pady=10)
        self._combo_row(ai, "Particules",    self.particle_preset, list(PARTICLE_PRESETS.keys()))
        self._combo_row(ai, "Fumée",         self.smoke_preset,    list(SMOKE_PRESETS.keys()))
        self._combo_row(ai, "Couleur fumée", self.smoke_color,     list(SMOKE_COLORS.keys()))
        _sep(ai)
        self._slider_row(ai, "Taille image", self.image_zoom,     0.65, 1.35)
        self._slider_row(ai, "Pulse image",  self.pulse_strength, 0.0,  2.2)

        # ── Fond dégradé (Update 3 — Feature 1) ───────────────────────────
        self._section_title(r, "🎨  Fond")
        bg_card = _card(r)
        bg_card.pack(fill="x", pady=(0, 10), padx=4)
        bg_inner = ctk.CTkFrame(bg_card, fg_color="transparent")
        bg_inner.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(bg_inner, text="Mode de fond", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        mode_row = ctk.CTkFrame(bg_inner, fg_color="transparent")
        mode_row.pack(fill="x", pady=(2, 8))
        for val, label in [("photo", "📷 Photo floue"), ("gradient", "🌈 Dégradé")]:
            ctk.CTkRadioButton(mode_row, text=label, variable=self.bg_mode, value=val,
                               command=self._on_bg_mode_changed,
                               fg_color=ACCENT, hover_color=ACCHOV,
                               text_color=TEXT, font=FONT_SM).pack(side="left", padx=(0, 16))

        self._gradient_frame = ctk.CTkFrame(bg_inner, fg_color="transparent")
        self._gradient_frame.pack(fill="x")
        self._build_gradient_pickers(self._gradient_frame)
        self._refresh_gradient_visibility()

        # Spectre
        self._section_title(r, "📊  Spectre")
        sc = _card(r)
        sc.pack(fill="x", pady=(0, 10), padx=4)
        si = ctk.CTkFrame(sc, fg_color="transparent")
        si.pack(fill="x", padx=10, pady=10)
        self._combo_row(si, "Style",      self.spectrum_style, SPECTRUM_STYLES)
        _sep(si)
        self._slider_row(si, "Taille",    self.spectrum_size,  0.55, 1.65)
        self._slider_row(si, "Position Y", self.spectrum_y,   0.62, 0.95)

        # Export
        self._section_title(r, "🚀  Export")
        ec = _card(r)
        ec.pack(fill="x", pady=(0, 6), padx=4)
        ei = ctk.CTkFrame(ec, fg_color="transparent")
        ei.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(ei, text="Dossier de sortie", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        rr = ctk.CTkFrame(ei, fg_color="transparent")
        rr.pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(rr, textvariable=self.project_root_var,
                     text_color=MUTED, font=FONT_MU, anchor="w", wraplength=210).pack(side="left", fill="x", expand=True)
        _btn(rr, "...", self._choose_project_root, small=True, width=36, height=26).pack(side="right")

        ctk.CTkLabel(ei, text="Nom du projet *", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        self._proj_name_entry = ctk.CTkEntry(ei, textvariable=self.project_name_var,
                                              placeholder_text="ex : MonSon_RageMix  (obligatoire)",
                                              fg_color=SURF3, border_color=BORDER,
                                              text_color=TEXT, font=FONT_SM)
        self._proj_name_entry.pack(fill="x", pady=(2, 2))
        self._proj_name_error = ctk.CTkLabel(ei, text="", text_color=DANGER, font=FONT_MU, anchor="w")
        self._proj_name_error.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(ei, text="Type d'export", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(0, 6))
        self._duration_btns: dict[str, ctk.CTkButton] = {}
        for val, title, desc in [
            ("CHECK",   "CHECK — 15 secondes",  "Horizontal 1920×1080"),
            ("SHORT",   "SHORT — 1 minute",      "Milieu · vertical 1080×1920"),
            ("COMPLET", "COMPLET — Son entier",  "Durée totale · horizontal 1920×1080"),
        ]:
            b = ctk.CTkButton(ei, text=f"{title}\n{desc}",
                              command=lambda v=val: self._set_export_mode(v),
                              fg_color=SURF3, hover_color=SURF2, text_color=MUTED,
                              font=FONT_H2, corner_radius=8, height=52, anchor="w")
            b.pack(fill="x", pady=3)
            self._duration_btns[val] = b
        self._refresh_mode_btns()

        _btn(ei, "  ▶  GÉNÉRER", self._start_export,
             accent=True, height=46).pack(fill="x", pady=(12, 0))

        self._prepare_preview()

    # ── Fond dégradé UI ───────────────────────────────────────────────────────

    def _build_gradient_pickers(self, parent):
        # Stocker les refs pour mise à jour depuis le color picker
        self._grad_swatches: dict[str, tk.Label] = {}
        self._grad_hex_lbls: dict[str, ctk.CTkLabel] = {}

        for label, attr in [("Couleur haut", "gradient_top"), ("Couleur bas", "gradient_bottom")]:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(row, text=label, text_color=MUTED, font=FONT_MU,
                         anchor="w").pack(side="left")

            color_val = getattr(self, attr)

            swatch = tk.Label(row, bg=color_val, width=5, relief="flat",
                              bd=1, highlightbackground=BORDER, highlightthickness=1)
            swatch.pack(side="right", padx=(6, 0))

            hex_lbl = ctk.CTkLabel(row, text=color_val, text_color=TEXT,
                                   font=FONT_MU, width=65, anchor="e")
            hex_lbl.pack(side="right")

            self._grad_swatches[attr] = swatch
            self._grad_hex_lbls[attr] = hex_lbl

            def pick(a=attr):
                current = getattr(self, a)
                result = colorchooser.askcolor(color=current, title="Choisir la couleur")
                if result and result[1]:
                    setattr(self, a, result[1])
                    self._grad_swatches[a].configure(bg=result[1])
                    self._grad_hex_lbls[a].configure(text=result[1])
                    self._schedule_persist()
                    self._reload_visuals_only()

            _btn(row, "Choisir", pick, small=True, width=70, height=24).pack(side="right", padx=(0, 6))

    def _on_bg_mode_changed(self):
        self._refresh_gradient_visibility()
        self._schedule_persist()
        self._reload_visuals_only()

    def _refresh_gradient_visibility(self):
        if not hasattr(self, "_gradient_frame"):
            return
        if self.bg_mode.get() == "gradient":
            self._gradient_frame.pack(fill="x")
        else:
            self._gradient_frame.pack_forget()

    # ── Update text preview ───────────────────────────────────────────────────

    def _update_text_preview(self):
        artist = self.artist_text.get().strip()
        title  = self.title_text.get().strip()
        if artist and title:
            preview = f'"{artist}" · "{title}"'
        elif artist:
            preview = f'"{artist}"'
        elif title:
            preview = f'"{title}"'
        else:
            preview = "Aucun texte affiché"
        if hasattr(self, "_text_preview_lbl"):
            self._text_preview_lbl.configure(text=f"→ {preview}")

    def _toggle_preview_format(self):
        self.preview_is_vertical = not self.preview_is_vertical
        label = "9:16 → 16:9" if self.preview_is_vertical else "16:9 → 9:16"
        fg    = ACCENT if self.preview_is_vertical else SURF3
        hov   = ACCHOV if self.preview_is_vertical else SURF2
        if hasattr(self, "_fmt_btn") and self._fmt_btn:
            self._fmt_btn.configure(text=label, fg_color=fg, hover_color=hov)
        self._prepare_preview()

    # ── Helpers UI ────────────────────────────────────────────────────────────

    @staticmethod
    def _short_name(path, maxlen=35):
        if not path:
            return "—"
        name = Path(path).name
        return name if len(name) <= maxlen else "…" + name[-(maxlen - 1):]

    def _section_title(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=FONT_SEC, text_color=ACCLT, anchor="w").pack(
            anchor="w", pady=(14, 4), padx=4)

    def _combo_row(self, parent, label, var, values):
        ctk.CTkLabel(parent, text=label, text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(4, 0))
        ctk.CTkComboBox(parent, variable=var, values=values,
                        command=lambda _: self._on_setting_changed(),
                        fg_color=SURF3, border_color=BORDER,
                        button_color=SURF2, button_hover_color=BORDER,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM).pack(fill="x", pady=(2, 6))

    def _slider_row(self, parent, label, var, minv, maxv):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(row, text=label, text_color=MUTED, font=FONT_MU, anchor="w").pack(side="left")
        val_lbl = ctk.CTkLabel(row, text=f"{var.get():.2f}", text_color=TEXT, font=FONT_MU, width=38, anchor="e")
        val_lbl.pack(side="right")

        def on_slide(v):
            val_lbl.configure(text=f"{float(v):.2f}")
            self._schedule_persist()
            if self.preview_ready:
                self._reload_visuals_only()

        ctk.CTkSlider(parent, from_=minv, to=maxv, variable=var, command=on_slide,
                      progress_color=ACCENT, button_color=ACCLT,
                      button_hover_color=ACCENT).pack(fill="x", pady=(2, 6))

    def _set_export_mode(self, val):
        self.export_mode.set(val)
        self._refresh_mode_btns()
        self._schedule_persist()

    def _refresh_mode_btns(self):
        if not hasattr(self, "_duration_btns"):
            return
        sel = self.export_mode.get()
        for val, btn in self._duration_btns.items():
            if val == sel:
                btn.configure(fg_color=ACCENT, hover_color=ACCHOV, text_color=TEXT)
            else:
                btn.configure(fg_color=SURF3, hover_color=SURF2, text_color=MUTED)

    # ══════════════════════════════════════════════════════════════════════════
    # CONFIG
    # ══════════════════════════════════════════════════════════════════════════

    def _schedule_persist(self):
        if self._persist_job:
            self.after_cancel(self._persist_job)
        self._persist_job = self.after(600, self._persist_now)

    def _persist_now(self):
        self._persist_job = None
        self.config_data["project_root"] = self.project_root
        self.config_data["history"]      = self.history
        self.config_data["settings"] = {
            "title_text":       self.title_text.get(),
            "artist_text":      self.artist_text.get(),
            "global_preset":    self.global_preset.get(),
            "particle_preset":  self.particle_preset.get(),
            "smoke_preset":     self.smoke_preset.get(),
            "smoke_color":      self.smoke_color.get(),
            "spectrum_style":   self.spectrum_style.get(),
            "spectrum_size":    self.spectrum_size.get(),
            "spectrum_y":       self.spectrum_y.get(),
            "image_zoom":       self.image_zoom.get(),
            "pulse_strength":   self.pulse_strength.get(),
            "preview_start":    self.preview_start.get(),
            "window_geometry":  self.geometry(),
            "text_x":           self.text_x.get(),
            "text_y":           self.text_y.get(),
            "export_mode":      self.export_mode.get(),
            "bg_mode":          self.bg_mode.get(),
            "gradient_top":     self.gradient_top,
            "gradient_bottom":  self.gradient_bottom,
        }
        save_config(self.config_data)

    def _on_setting_changed(self):
        self._schedule_persist()
        if not self.is_rendering:
            self._reload_visuals_only()

    def _apply_global_preset(self):
        p = GLOBAL_PRESETS[self.global_preset.get()]
        self.particle_preset.set(p["particle_preset"])
        self.smoke_preset.set(p["smoke_preset"])
        self.smoke_color.set(p["smoke_color"])
        self.spectrum_style.set(p["spectrum_style"])
        self.spectrum_size.set(p["spectrum_size"])
        self.spectrum_y.set(p["spectrum_y"])
        self.image_zoom.set(p["image_zoom"])
        self.pulse_strength.set(p["pulse_strength"])
        self._schedule_persist()
        if not self.is_rendering:
            self._reload_visuals_only()

    # ══════════════════════════════════════════════════════════════════════════
    # FICHIERS
    # ══════════════════════════════════════════════════════════════════════════

    def _pick_audio(self):
        path = filedialog.askopenfilename(
            filetypes=[("Audio", "*.mp3 *.wav *.flac *.ogg *.m4a"), ("Tous", "*.*")])
        if path:
            self.audio_path = path
            self.show_step_image()

    def _pick_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("Tous", "*.*")])
        if path:
            self.image_path = path
            self.show_editor()

    def _choose_project_root(self):
        path = filedialog.askdirectory(title="Dossier racine des créations")
        if path:
            self.project_root = path
            Path(path).mkdir(parents=True, exist_ok=True)
            self.project_root_var.set(path)
            self._schedule_persist()

    # ══════════════════════════════════════════════════════════════════════════
    # TIMING / SETTINGS
    # ══════════════════════════════════════════════════════════════════════════

    def _get_audio_duration(self):
        try:
            info = sf.info(self.audio_path)
            return float(info.frames / info.samplerate)
        except Exception:
            return 0.0

    def _get_export_timing(self):
        mode = self.export_mode.get()
        if mode == "CHECK":
            return 15.0, 0.0
        if mode == "SHORT":
            total = self._get_audio_duration()
            if total <= 60:
                return None, 0.0
            return 60.0, max(0.0, (total / 2.0) - 30.0)
        return None, 0.0

    def _preview_dimensions(self):
        return (PREVIEW_W_V, PREVIEW_H_V) if self.preview_is_vertical else (PREVIEW_W, PREVIEW_H)

    def _current_settings(self, preview=False, short_mode=False):
        if preview:
            duration_limit = float(PREVIEW_SECONDS)
            raw = self.preview_start.get().strip().replace(",", ".")
            start_offset = float(raw) if raw else 0.0
            out_w, out_h = self._preview_dimensions()
        else:
            duration_limit, start_offset = self._get_export_timing()
            out_w = SHORT_WIDTH  if short_mode else 1920
            out_h = SHORT_HEIGHT if short_mode else 1080

        return RenderSettings(
            audio_path=self.audio_path,
            image_path=self.image_path,
            output_path=self.output_path,
            title_text=self.title_text.get().strip(),
            artist_text=self.artist_text.get().strip(),
            duration_limit=duration_limit,
            start_offset=start_offset,
            particle_preset=self.particle_preset.get(),
            smoke_preset=self.smoke_preset.get(),
            smoke_color=self.smoke_color.get(),
            spectrum_style=self.spectrum_style.get(),
            spectrum_size=float(self.spectrum_size.get()),
            spectrum_y=float(self.spectrum_y.get()),
            image_zoom=float(self.image_zoom.get()),
            pulse_strength=float(self.pulse_strength.get()),
            background_blur=38,
            output_width=out_w,
            output_height=out_h,
            text_x=float(self.text_x.get()),
            text_y=float(self.text_y.get()),
            bg_mode=self.bg_mode.get(),
            gradient_top=self.gradient_top,
            gradient_bottom=self.gradient_bottom,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # PREVIEW
    # ══════════════════════════════════════════════════════════════════════════

    def _prepare_preview(self):
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
                self.after(0, self._tick_preview)
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
            )
            self.preview_bg        = bg
            self.preview_cover     = cov
            self.preview_particles = []
            self.preview_smoke     = []
            self.preview_smoothed  = np.zeros(84, dtype=np.float32)
        except Exception:
            pass

    def _tick_preview(self):
        if not self.preview_running or not self.preview_ready or self.preview_features is None:
            return

        s = self._current_settings(preview=True)
        total = len(self.preview_features["rms"])

        if self.audio_playing and self.preview_started_at is not None:
            self.preview_index = int((time.time() - self.preview_started_at) * FPS) % total

        i = self.preview_index % total
        metrics = {k: float(self.preview_features[k][i])
                   for k in ("rms", "kick", "bass", "mid", "high")}

        frame, self.preview_particles, self.preview_smoke, self.preview_smoothed = render_frame(
            self.preview_bg, self.preview_cover,
            self.preview_particles, self.preview_smoke,
            self.preview_features["spec"][:, i],
            metrics, self.preview_smoothed, s,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.preview_label.configure(image=self.photo)

        if not self.audio_playing:
            self.preview_index += 1

        self.after(int(1000 / FPS), self._tick_preview)

    def _play_preview_audio(self):
        import subprocess as _sp
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
            except Exception:
                pass
            self.ffplay_process = None

    # ══════════════════════════════════════════════════════════════════════════
    # EXPORT
    # ══════════════════════════════════════════════════════════════════════════

    def _validate_project_name(self):
        name = self.project_name_var.get().strip()
        if not name:
            if hasattr(self, "_proj_name_error"):
                self._proj_name_error.configure(text="⚠  Nom du projet obligatoire avant de générer.")
            if hasattr(self, "_proj_name_entry"):
                self._proj_name_entry.configure(border_color=DANGER)
            return None
        if hasattr(self, "_proj_name_error"):
            self._proj_name_error.configure(text="")
        if hasattr(self, "_proj_name_entry"):
            self._proj_name_entry.configure(border_color=BORDER)
        return safe_name(name)

    def _ask_project_name_and_folder(self, suffix=""):
        clean = self._validate_project_name()
        if not clean:
            raise RuntimeError("Nom du projet obligatoire.")
        root = Path(self.project_root)
        root.mkdir(parents=True, exist_ok=True)
        folder = f"{clean}{suffix}"
        proj_dir = root / folder
        ctr = 2
        while proj_dir.exists():
            proj_dir = root / f"{folder}_{ctr}"
            ctr += 1
        proj_dir.mkdir(parents=True, exist_ok=True)
        return clean, proj_dir

    def _copy_assets(self, proj_dir, name):
        a   = Path(self.audio_path)
        img = Path(self.image_path)
        ad  = proj_dir / f"{name}{a.suffix.lower()}"
        id_ = proj_dir / f"{name}_cover{img.suffix.lower()}"
        shutil.copy2(a, ad)
        shutil.copy2(img, id_)
        return str(ad), str(id_)

    def _show_export_overlay(self, label):
        if not hasattr(self, "preview_label") or not self.preview_label:
            return
        ov = ctk.CTkFrame(self.preview_label, fg_color="#050505", corner_radius=0)
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._export_overlay_frame = ov
        box = ctk.CTkFrame(ov, fg_color=SURF2, corner_radius=14,
                           border_color=BORDER, border_width=1,
                           width=360, height=160)
        box.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(box, text=label, font=FONT_H2, text_color=TEXT).pack(pady=(22, 8))
        self._exp_bar = ctk.CTkProgressBar(box, progress_color=ACCENT, fg_color=SURF3)
        self._exp_bar.pack(fill="x", padx=32, pady=6)
        self._exp_bar.set(0)
        self._exp_detail = ctk.CTkLabel(box, text="Préparation...", text_color=MUTED, font=FONT_MU)
        self._exp_detail.pack(pady=(4, 0))

    def _update_export_overlay(self, text):
        self._set_status(text, WARN)
        if hasattr(self, "_exp_detail") and self._exp_detail:
            try:
                self._exp_detail.configure(text=text)
            except Exception:
                pass
        if hasattr(self, "_exp_bar") and self._exp_bar:
            try:
                m = re.search(r"([0-9]+(?:\.[0-9]+)?)%", text)
                if m:
                    self._exp_bar.set(float(m.group(1)) / 100)
                elif "Encodage" in text:
                    self._exp_bar.set(0.97)
                elif "Terminé" in text:
                    self._exp_bar.set(1.0)
            except Exception:
                pass
        self.update_idletasks()

    def _hide_export_overlay(self):
        if self._export_overlay_frame:
            try:
                self._export_overlay_frame.destroy()
            except Exception:
                pass
            self._export_overlay_frame = None

    def _start_export(self):
        if self.is_rendering:
            return
        if not self.audio_path or not self.image_path:
            messagebox.showerror("Erreur", "Musique ou pochette manquante.")
            return
        if not self._validate_project_name():
            return

        mode     = self.export_mode.get()
        is_short = (mode == "SHORT")

        try:
            suffix    = "_SHORT" if is_short else ""
            proj_name, proj_dir = self._ask_project_name_and_folder(suffix=suffix)
            file_name = f"{proj_name}_SHORT" if is_short else proj_name
            self.audio_path, self.image_path = self._copy_assets(proj_dir, file_name)
            self.output_path = str(proj_dir / f"{file_name}.mp4")
            self._persist_now()
        except Exception as exc:
            messagebox.showerror("Export", str(exc))
            return

        settings = self._current_settings(preview=False, short_mode=is_short)
        settings.output_path = self.output_path

        if is_short:
            print(f"[Export] SHORT offset={settings.start_offset:.1f}s durée={settings.duration_limit}s")

        self.preview_running = False
        self._stop_audio()
        self.is_rendering = True

        label_map = {"CHECK": "CHECK — 15s", "SHORT": "SHORT — 1min vertical", "COMPLET": "COMPLET"}
        label = label_map.get(mode, mode)
        self._set_status(f"Export {label}...", WARN)
        self._show_export_overlay(f"Export {label}")

        def worker():
            try:
                render_video(settings,
                             progress_callback=lambda t: self.after(
                                 0, lambda txt=t: self._update_export_overlay(txt)))
                self.history.append({
                    "name":       file_name,
                    "folder":     str(proj_dir),
                    "video":      settings.output_path,
                    "audio":      settings.audio_path,
                    "image":      settings.image_path,
                    "type":       mode.lower(),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                })
                self._persist_now()
                self.after(0, lambda: messagebox.showinfo(
                    "Terminé ✓", f"Vidéo créée :\n{settings.output_path}"))
                self.after(0, self._hide_export_overlay)
                self.after(0, lambda: open_file(str(proj_dir)))
                self.after(0, lambda: self._set_status("Export terminé ✓", SUCCESS))
            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda: messagebox.showerror("Erreur export", msg))
                self.after(0, self._hide_export_overlay)
                self.after(0, lambda: self._set_status("Erreur export", DANGER))
            finally:
                self.is_rendering = False

        threading.Thread(target=worker, daemon=True).start()
