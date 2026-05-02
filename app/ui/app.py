"""TAC MP4 Studio — Update 1

Nouveautés :
  1. Switch preview format 16:9 ↔ 9:16 (bouton toggle dans les contrôles preview)
  2. Vérification FFmpeg au démarrage (bannière d'avertissement non-bloquante)
  3. Nom projet obligatoire avant export (validation inline, plus de simpledialog surprise)
  4. Drag & drop audio + image sur la fenêtre (tkinterdnd2)
"""
from __future__ import annotations

import re
import shutil
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox
import tkinter as tk

import customtkinter as ctk
import cv2
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

# ── Constantes preview verticale ─────────────────────────────────────────────
# 9:16 scalé à la même hauteur que la preview 16:9
PREVIEW_W_V = 304   # 540 * (1080/1920) ≈ 304
PREVIEW_H_V = 540

# ── Thème ─────────────────────────────────────────────────────────────────────
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


# ── Widget helpers ────────────────────────────────────────────────────────────

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


# ── App ───────────────────────────────────────────────────────────────────────

class App(ctk.CTk if not _DND_AVAILABLE else TkinterDnD.Tk):
    """Fenêtre principale TAC MP4 Studio — Update 1."""

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
        self.audio_path: str = ""
        self.image_path: str = ""
        self.output_path: str = ""
        self.project_root: str = self.config_data.get("project_root", str(DEFAULT_CREATIONS_DIR))
        Path(self.project_root).mkdir(parents=True, exist_ok=True)
        self.history: list[dict] = self.config_data.get("history", [])

        # ── Tkinter vars ───────────────────────────────────────────────────────
        self.title_text       = tk.StringVar(value=settings.get("title_text", ""))
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

        # ── Update 1 : preview vertical toggle ────────────────────────────────
        self.preview_is_vertical: bool = False  # False = 16:9, True = 9:16

        # ── Preview state ──────────────────────────────────────────────────────
        self.preview_ready      = False
        self.preview_running    = False
        self.audio_playing      = False
        self.preview_started_at: float | None = None
        self.ffplay_process     = None
        self.preview_index      = 0
        self.preview_features: dict | None = None
        self.preview_bg: np.ndarray | None  = None
        self.preview_cover: np.ndarray | None = None
        self.preview_particles: list = []
        self.preview_smoke: list     = []
        self.preview_smoothed        = np.zeros(84, dtype=np.float32)
        self.photo: ImageTk.PhotoImage | None = None
        self.is_rendering       = False
        self._persist_job: str | None = None
        self._export_overlay_frame: ctk.CTkFrame | None = None
        self._ffmpeg_banner: ctk.CTkFrame | None = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── Drag & drop (Update 1) ─────────────────────────────────────────────
        if _DND_AVAILABLE:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self._on_drop)

        self.show_home()

        # ── FFmpeg check au démarrage (Update 1) ──────────────────────────────
        self.after(400, self._check_ffmpeg)

    # ══════════════════════════════════════════════════════════════════════════
    # FFmpeg CHECK (Update 1 — Feature 2)
    # ══════════════════════════════════════════════════════════════════════════

    def _check_ffmpeg(self):
        """Vérifie ffmpeg + ffplay au démarrage. Affiche une bannière si absent."""
        missing = []
        if not shutil.which("ffmpeg"):
            missing.append("ffmpeg")
        if not shutil.which("ffplay"):
            missing.append("ffplay")

        if not missing:
            return

        tools = " et ".join(missing)
        banner = ctk.CTkFrame(self, fg_color="#431407", corner_radius=0, height=40)
        banner.pack(fill="x", side="bottom")
        banner.pack_propagate(False)
        self._ffmpeg_banner = banner

        msg = f"⚠  {tools} introuvable — l'export et la preview audio ne fonctionneront pas."
        ctk.CTkLabel(banner, text=msg, text_color=WARN,
                     font=FONT_SM).pack(side="left", padx=16, pady=10)

        ctk.CTkLabel(banner, text="→ Installe FFmpeg et ajoute-le au PATH Windows",
                     text_color="#fdba74", font=FONT_MU).pack(side="left", padx=(0, 12))

        _btn(banner, "✕", self._hide_ffmpeg_banner,
             small=True, width=32, height=24,
             fg_color="transparent", hover_color="#7c2d12").pack(side="right", padx=12)

    def _hide_ffmpeg_banner(self):
        if self._ffmpeg_banner:
            self._ffmpeg_banner.destroy()
            self._ffmpeg_banner = None

    # ══════════════════════════════════════════════════════════════════════════
    # DRAG & DROP (Update 1 — Feature 4)
    # ══════════════════════════════════════════════════════════════════════════

    def _on_drop(self, event):
        """Reçoit des fichiers glissés-déposés sur la fenêtre."""
        # tkinterdnd2 retourne les chemins entre {} sur Windows si espaces
        raw = event.data.strip()
        paths = []
        if raw.startswith("{"):
            # Format : {C:/path/to/file} {C:/other}
            import re as _re
            paths = _re.findall(r"\{([^}]+)\}", raw)
        else:
            paths = raw.split()

        audio_found = ""
        image_found = ""
        for p in paths:
            ext = Path(p).suffix.lower()
            if ext in AUDIO_EXTS and not audio_found:
                audio_found = p
            elif ext in IMAGE_EXTS and not image_found:
                image_found = p

        changed = False
        if audio_found:
            self.audio_path = audio_found
            changed = True
            self._set_status(f"Audio : {Path(audio_found).name}", SUCCESS)
        if image_found:
            self.image_path = image_found
            changed = True

        if not changed:
            self._set_status("Format non reconnu (audio ou image requis)", DANGER)
            return

        # Navigation automatique selon ce qu'on a
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

        # Badge drag & drop dans le header si disponible
        if _DND_AVAILABLE:
            ctk.CTkLabel(hdr, text="  ⬇ Glisse tes fichiers ici",
                         text_color=MUTED, font=FONT_MU).pack(side="left", padx=20, pady=14)

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
        for child in self.main.winfo_children():
            child.destroy()

    def _set_status(self, text: str, color: str = MUTED):
        self.status_var.set(text)
        if hasattr(self, "_status_dot"):
            self._status_dot.configure(text_color=color)
            self._status_lbl.configure(text_color=color)

    def _on_close(self):
        try:
            self._persist_now()
            self._stop_audio()
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
                     text_color=MUTED, font=FONT_SM).pack(pady=(0, 6))

        if _DND_AVAILABLE:
            ctk.CTkLabel(center, text="⬇  Glisse un fichier audio ou image directement sur la fenêtre",
                         text_color=MUTED, font=FONT_MU).pack(pady=(0, 32))
        else:
            ctk.CTkFrame(center, height=32, fg_color="transparent").pack()

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
                     text_color=MUTED, font=FONT_SM).pack(pady=(0, 4))
        if _DND_AVAILABLE:
            ctk.CTkLabel(center, text="ou glisse le fichier directement sur la fenêtre",
                         text_color=MUTED, font=FONT_MU).pack(pady=(0, 28))
        else:
            ctk.CTkFrame(center, height=28, fg_color="transparent").pack()

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

        if _DND_AVAILABLE:
            ctk.CTkLabel(center, text="ou glisse l'image directement sur la fenêtre",
                         text_color=MUTED, font=FONT_MU).pack(pady=(0, 12))

        _btn(center, "  🖼  Importer une image", self._pick_image,
             accent=True, width=300, height=50).pack(pady=6)
        ctk.CTkLabel(center, text="PNG · JPG · JPEG · WEBP",
                     text_color=MUTED, font=FONT_MU).pack(pady=(4, 16))
        _btn(center, "← Retour", self.show_step_audio, small=True, width=140).pack()

    # ── Historique ────────────────────────────────────────────────────────────

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
            inner.pack(fill="x", padx=16, pady=12)

            kind = item.get("type", "complet").upper()
            kind_color = {"SHORT": ACCLT, "CHECK": WARN, "COMPLET": SUCCESS}.get(kind, TEXT)

            left_col = ctk.CTkFrame(inner, fg_color="transparent")
            left_col.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(left_col, text=item.get("name", "Sans nom"),
                         font=FONT_H2, text_color=TEXT, anchor="w").pack(anchor="w")
            ctk.CTkLabel(left_col, text=item.get("created_at", ""),
                         font=FONT_MU, text_color=MUTED, anchor="w").pack(anchor="w")

            right_col = ctk.CTkFrame(inner, fg_color="transparent")
            right_col.pack(side="right")
            ctk.CTkLabel(right_col, text=f"[{kind}]",
                         font=FONT_SEC, text_color=kind_color).pack(side="left", padx=(0, 12))
            _btn(right_col, "📂 Ouvrir",
                 lambda f=item.get("folder", ""): open_file(f),
                 small=True, width=90).pack(side="left", padx=4)
            _btn(right_col, "✕",
                 lambda i=item: self._delete_history_item(i),
                 small=True, width=36, danger=True).pack(side="left")

    def _sorted_history(self):
        return sorted(self.history, key=lambda x: x.get("created_at", ""), reverse=True)

    def _delete_history_item(self, item: dict):
        if messagebox.askyesno("Historique",
                               f"Supprimer '{item.get('name')}' de l'historique ?\n(Les fichiers restent sur le disque.)"):
            self.history = [h for h in self.history if h.get("folder") != item.get("folder")]
            self._persist_now()
            self.show_history()

    # ── Éditeur ───────────────────────────────────────────────────────────────

    def show_editor(self):
        self._clear_main()
        self._set_status("Preview", SUCCESS)

        left = ctk.CTkFrame(self.main, fg_color=BG)
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        right_outer = ctk.CTkFrame(self.main, fg_color=BG, width=340)
        right_outer.pack(side="right", fill="y", padx=(0, 16), pady=16)
        right_outer.pack_propagate(False)

        # ── Zone preview ───────────────────────────────────────────────────
        preview_wrap = ctk.CTkFrame(left, fg_color="#000000", corner_radius=12,
                                    border_color=BORDER, border_width=1)
        preview_wrap.pack(fill="both", expand=True)

        self.preview_label = tk.Label(preview_wrap, bg="#000000", bd=0,
                                      highlightthickness=0)
        self.preview_label.pack(fill="both", expand=True, padx=2, pady=2)

        # ── Contrôles preview ──────────────────────────────────────────────
        ctrl = ctk.CTkFrame(left, fg_color="transparent")
        ctrl.pack(fill="x", pady=(8, 0))

        _btn(ctrl, "▶ Preview", self._play_preview_audio,
             accent=True, width=110, height=34, small=True).pack(side="left", padx=(0, 6))
        _btn(ctrl, "⏸", self._pause_preview_audio,
             width=42, height=34, small=True).pack(side="left", padx=(0, 6))
        _btn(ctrl, "⟲ Recharger", self._prepare_preview,
             width=110, height=34, small=True).pack(side="left", padx=(0, 12))

        # ── Toggle format preview (Update 1 — Feature 1) ──────────────────
        self._fmt_btn = _btn(ctrl, "9:16  →  16:9" if self.preview_is_vertical else "16:9  →  9:16",
                             self._toggle_preview_format,
                             width=130, height=34, small=True,
                             fg_color=ACCENT if self.preview_is_vertical else SURF3,
                             hover_color=ACCHOV if self.preview_is_vertical else SURF2)
        self._fmt_btn.pack(side="left")

        _btn(ctrl, "← Accueil", self.show_home,
             width=100, height=34, small=True).pack(side="right")

        # ── Panneau droit ──────────────────────────────────────────────────
        right_scroll = ctk.CTkScrollableFrame(right_outer, fg_color="transparent",
                                              scrollbar_button_color=SURF3,
                                              scrollbar_button_hover_color=ACCENT)
        right_scroll.pack(fill="both", expand=True)
        r = right_scroll

        # Section Fichiers
        self._section_title(r, "📁  Fichiers")
        files_card = _card(r)
        files_card.pack(fill="x", pady=(0, 10), padx=4)
        self._audio_name_lbl = ctk.CTkLabel(files_card, text=self._short_name(self.audio_path),
                                             text_color=ACCLT, font=FONT_SM, anchor="w")
        self._audio_name_lbl.pack(fill="x", padx=14, pady=(10, 2))
        self._img_name_lbl = ctk.CTkLabel(files_card, text=self._short_name(self.image_path),
                                           text_color=MUTED, font=FONT_MU, anchor="w")
        self._img_name_lbl.pack(fill="x", padx=14, pady=(0, 8))
        btns_row = ctk.CTkFrame(files_card, fg_color="transparent")
        btns_row.pack(fill="x", padx=10, pady=(0, 10))
        _btn(btns_row, "🎵 Musique", self.show_step_audio, small=True, height=30).pack(
            side="left", padx=(0, 6), fill="x", expand=True)
        _btn(btns_row, "🖼 Pochette", self.show_step_image, small=True, height=30).pack(
            side="left", fill="x", expand=True)

        # Section Texte
        self._section_title(r, "✍  Texte")
        txt_card = _card(r)
        txt_card.pack(fill="x", pady=(0, 10), padx=4)
        ctk.CTkEntry(txt_card, textvariable=self.title_text,
                     placeholder_text="Titre affiché (laisser vide = aucun)",
                     fg_color=SURF3, border_color=BORDER,
                     text_color=TEXT, font=FONT_SM).pack(fill="x", padx=10, pady=10)
        txt_pos = ctk.CTkFrame(txt_card, fg_color="transparent")
        txt_pos.pack(fill="x", padx=10, pady=(0, 10))
        self._slider_row(txt_pos, "Position X", self.text_x, 0.05, 0.95)
        self._slider_row(txt_pos, "Position Y", self.text_y, 0.15, 0.92)

        # Section Preset
        self._section_title(r, "⚡  Preset rapide")
        preset_card = _card(r)
        preset_card.pack(fill="x", pady=(0, 10), padx=4)
        ctk.CTkComboBox(preset_card, variable=self.global_preset,
                        values=list(GLOBAL_PRESETS.keys()),
                        command=lambda _: self._apply_global_preset(),
                        fg_color=SURF3, border_color=BORDER,
                        button_color=ACCENT, button_hover_color=ACCHOV,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM).pack(fill="x", padx=10, pady=(10, 6))
        _btn(preset_card, "APPLIQUER", self._apply_global_preset,
             accent=True, height=34, small=True).pack(fill="x", padx=10, pady=(0, 10))

        # Section Ambiance
        self._section_title(r, "🌫  Ambiance")
        amb_card = _card(r)
        amb_card.pack(fill="x", pady=(0, 10), padx=4)
        ac = ctk.CTkFrame(amb_card, fg_color="transparent")
        ac.pack(fill="x", padx=10, pady=10)
        self._combo_row(ac, "Particules",    self.particle_preset, list(PARTICLE_PRESETS.keys()))
        self._combo_row(ac, "Fumée",         self.smoke_preset,    list(SMOKE_PRESETS.keys()))
        self._combo_row(ac, "Couleur fumée", self.smoke_color,     list(SMOKE_COLORS.keys()))
        _sep(ac)
        self._slider_row(ac, "Taille image", self.image_zoom,     0.65, 1.35)
        self._slider_row(ac, "Pulse image",  self.pulse_strength, 0.0,  2.2)

        # Section Spectre
        self._section_title(r, "📊  Spectre")
        spec_card = _card(r)
        spec_card.pack(fill="x", pady=(0, 10), padx=4)
        sc = ctk.CTkFrame(spec_card, fg_color="transparent")
        sc.pack(fill="x", padx=10, pady=10)
        self._combo_row(sc, "Style",          self.spectrum_style, SPECTRUM_STYLES)
        _sep(sc)
        self._slider_row(sc, "Taille",        self.spectrum_size,  0.55, 1.65)
        self._slider_row(sc, "Position Y",    self.spectrum_y,     0.62, 0.95)

        # Section Export
        self._section_title(r, "🚀  Export")
        exp_card = _card(r)
        exp_card.pack(fill="x", pady=(0, 6), padx=4)
        ec = ctk.CTkFrame(exp_card, fg_color="transparent")
        ec.pack(fill="x", padx=10, pady=10)

        # Dossier
        ctk.CTkLabel(ec, text="Dossier de sortie", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        root_row = ctk.CTkFrame(ec, fg_color="transparent")
        root_row.pack(fill="x", pady=(2, 8))
        ctk.CTkLabel(root_row, textvariable=self.project_root_var,
                     text_color=MUTED, font=FONT_MU, anchor="w", wraplength=210).pack(side="left", fill="x", expand=True)
        _btn(root_row, "...", self._choose_project_root, small=True, width=36, height=26).pack(side="right")

        # Preview start
        ctk.CTkLabel(ec, text="Départ preview (secondes)", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        prow = ctk.CTkFrame(ec, fg_color="transparent")
        prow.pack(fill="x", pady=(2, 8))
        ctk.CTkEntry(prow, textvariable=self.preview_start,
                     fg_color=SURF3, border_color=BORDER, text_color=TEXT,
                     font=FONT_SM, width=80).pack(side="left")
        _btn(prow, "Analyser", self._prepare_preview, small=True, width=90, height=28).pack(side="left", padx=(8, 0))

        # Nom projet (Update 1 — Feature 3 : validation inline)
        ctk.CTkLabel(ec, text="Nom du projet *", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        self._proj_name_entry = ctk.CTkEntry(ec, textvariable=self.project_name_var,
                                              placeholder_text="ex : MonSon_RageMix  (obligatoire)",
                                              fg_color=SURF3, border_color=BORDER,
                                              text_color=TEXT, font=FONT_SM)
        self._proj_name_entry.pack(fill="x", pady=(2, 2))
        self._proj_name_error = ctk.CTkLabel(ec, text="", text_color=DANGER, font=FONT_MU, anchor="w")
        self._proj_name_error.pack(anchor="w", pady=(0, 10))

        # Modes export
        ctk.CTkLabel(ec, text="Type d'export", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(0, 6))
        self._duration_btns: dict[str, ctk.CTkButton] = {}
        MODES = [
            ("CHECK",   "CHECK — 15 secondes",  "Horizontal 1920×1080"),
            ("SHORT",   "SHORT — 1 minute",      "Milieu · vertical 1080×1920"),
            ("COMPLET", "COMPLET — Son entier",  "Durée totale · horizontal 1920×1080"),
        ]
        for val, title, desc in MODES:
            b = ctk.CTkButton(ec, text=f"{title}\n{desc}",
                              command=lambda v=val: self._set_export_mode(v),
                              fg_color=SURF3, hover_color=SURF2,
                              text_color=MUTED, font=FONT_H2,
                              corner_radius=8, height=52, anchor="w")
            b.pack(fill="x", pady=3)
            self._duration_btns[val] = b
        self._refresh_mode_btns()

        _btn(ec, "  ▶  GÉNÉRER", self._start_export,
             accent=True, height=46).pack(fill="x", pady=(12, 0))

        self._prepare_preview()

    # ── Toggle preview format (Update 1 — Feature 1) ──────────────────────────

    def _toggle_preview_format(self):
        """Bascule preview entre 16:9 et 9:16 et relance l'analyse."""
        self.preview_is_vertical = not self.preview_is_vertical
        label = "9:16  →  16:9" if self.preview_is_vertical else "16:9  →  9:16"
        fg    = ACCENT if self.preview_is_vertical else SURF3
        hov   = ACCHOV if self.preview_is_vertical else SURF2
        if hasattr(self, "_fmt_btn") and self._fmt_btn:
            self._fmt_btn.configure(text=label, fg_color=fg, hover_color=hov)
        self._prepare_preview()

    # ── Helpers UI ────────────────────────────────────────────────────────────

    @staticmethod
    def _short_name(path: str, maxlen: int = 35) -> str:
        if not path:
            return "—"
        name = Path(path).name
        return name if len(name) <= maxlen else "…" + name[-(maxlen - 1):]

    def _section_title(self, parent, text: str):
        ctk.CTkLabel(parent, text=text, font=FONT_SEC, text_color=ACCLT, anchor="w").pack(
            anchor="w", pady=(14, 4), padx=4)

    def _combo_row(self, parent, label: str, var: tk.StringVar, values: list):
        ctk.CTkLabel(parent, text=label, text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(4, 0))
        ctk.CTkComboBox(parent, variable=var, values=values,
                        command=lambda _: self._on_setting_changed(),
                        fg_color=SURF3, border_color=BORDER,
                        button_color=SURF2, button_hover_color=BORDER,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM).pack(fill="x", pady=(2, 6))

    def _slider_row(self, parent, label: str, var: tk.DoubleVar, minv: float, maxv: float):
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

    def _set_export_mode(self, val: str):
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
            "title_text":      self.title_text.get(),
            "global_preset":   self.global_preset.get(),
            "particle_preset": self.particle_preset.get(),
            "smoke_preset":    self.smoke_preset.get(),
            "smoke_color":     self.smoke_color.get(),
            "spectrum_style":  self.spectrum_style.get(),
            "spectrum_size":   self.spectrum_size.get(),
            "spectrum_y":      self.spectrum_y.get(),
            "image_zoom":      self.image_zoom.get(),
            "pulse_strength":  self.pulse_strength.get(),
            "preview_start":   self.preview_start.get(),
            "window_geometry": self.geometry(),
            "text_x":          self.text_x.get(),
            "text_y":          self.text_y.get(),
            "export_mode":     self.export_mode.get(),
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

    def _get_audio_duration(self) -> float:
        try:
            info = sf.info(self.audio_path)
            return float(info.frames / info.samplerate)
        except Exception:
            return 0.0

    def _get_export_timing(self) -> tuple[float | None, float]:
        mode = self.export_mode.get()
        if mode == "CHECK":
            return 15.0, 0.0
        if mode == "SHORT":
            total = self._get_audio_duration()
            if total <= 60:
                return None, 0.0
            return 60.0, max(0.0, (total / 2.0) - 30.0)
        return None, 0.0

    def _preview_dimensions(self) -> tuple[int, int]:
        """Retourne (w, h) de la preview selon le format sélectionné."""
        return (PREVIEW_W_V, PREVIEW_H_V) if self.preview_is_vertical else (PREVIEW_W, PREVIEW_H)

    def _current_settings(self, preview: bool = False, short_mode: bool = False) -> RenderSettings:
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
        self._set_status(f"Analyse audio [{fmt}]...", WARN)
        settings = self._current_settings(preview=True)

        def worker():
            try:
                feat = compute_audio_features(
                    settings.audio_path, FPS, PREVIEW_SECONDS, settings.start_offset)
                bg, cov = load_cover_image(
                    settings.image_path, settings.background_blur,
                    settings.image_zoom, settings.output_width, settings.output_height)
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
                s.output_width, s.output_height)
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

        settings = self._current_settings(preview=True)
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
            metrics, self.preview_smoothed,
            settings.title_text, settings,
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
            self._set_status("▶ Audio preview", SUCCESS)
        except Exception as exc:
            messagebox.showerror("Audio preview", str(exc))

    def _pause_preview_audio(self):
        self._stop_audio()
        self._set_status("Preview pausée")

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

    def _validate_project_name(self) -> str | None:
        """Retourne le nom nettoyé ou None si invalide (affiche l'erreur inline)."""
        name = self.project_name_var.get().strip()
        if not name:
            if hasattr(self, "_proj_name_error"):
                self._proj_name_error.configure(text="⚠  Nom du projet obligatoire avant de générer.")
            if hasattr(self, "_proj_name_entry"):
                self._proj_name_entry.configure(border_color=DANGER)
            return None
        # Reset style si valide
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

    def _copy_assets(self, proj_dir: Path, name: str):
        a   = Path(self.audio_path)
        img = Path(self.image_path)
        ad  = proj_dir / f"{name}{a.suffix.lower()}"
        id_ = proj_dir / f"{name}_cover{img.suffix.lower()}"
        shutil.copy2(a, ad)
        shutil.copy2(img, id_)
        return str(ad), str(id_)

    def _show_export_overlay(self, label: str):
        if not hasattr(self, "preview_label") or not self.preview_label:
            return
        ov = ctk.CTkFrame(self.preview_label, fg_color="#050505", corner_radius=0)
        ov.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._export_overlay_frame = ov

        box = ctk.CTkFrame(ov, fg_color=SURF2, corner_radius=14,
                           border_color=BORDER, border_width=1)
        box.place(relx=0.5, rely=0.5, anchor="center", width=360, height=160)

        ctk.CTkLabel(box, text=label, font=FONT_H2, text_color=TEXT).pack(pady=(22, 8))
        self._exp_bar = ctk.CTkProgressBar(box, progress_color=ACCENT, fg_color=SURF3)
        self._exp_bar.pack(fill="x", padx=32, pady=6)
        self._exp_bar.set(0)
        self._exp_detail = ctk.CTkLabel(box, text="Préparation...", text_color=MUTED, font=FONT_MU)
        self._exp_detail.pack(pady=(4, 0))

    def _update_export_overlay(self, text: str):
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

        # Update 1 — Feature 3 : validation nom AVANT tout le reste
        if not self._validate_project_name():
            return

        mode     = self.export_mode.get()
        is_short = (mode == "SHORT")

        try:
            suffix   = "_SHORT" if is_short else ""
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
            print(f"[Export] SHORT : offset={settings.start_offset:.1f}s durée={settings.duration_limit}s")

        self.preview_running = False
        self._stop_audio()
        self.is_rendering = True

        label_map = {"CHECK": "CHECK — 15s", "SHORT": "SHORT — 1min vertical", "COMPLET": "COMPLET"}
        label = label_map.get(mode, mode)
        self._set_status(f"Export {label}...", WARN)
        self._show_export_overlay(f"Export {label}")

        def worker():
            try:
                render_video(
                    settings,
                    progress_callback=lambda t: self.after(
                        0, lambda txt=t: self._update_export_overlay(txt)),
                )
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
