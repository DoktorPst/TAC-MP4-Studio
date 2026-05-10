"""PagesMixin — méthodes de navigation et pages.

Extrait de app/ui/app.py.
"""
from __future__ import annotations

import math
import random
import time

from tkinter import messagebox, filedialog


class PagesMixin:

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE ACCUEIL
    # ══════════════════════════════════════════════════════════════════════════

    def show_home(self):
        import tkinter as tk
        import customtkinter as ctk
        from app.ui.app import (
            BG, SURF2, BORDER, ACCENT, ACCLT, TEXT, MUTED, FONT_H2, FONT_SM,
            FONT_MU, VERSION, _btn,
        )
        self._clear_main()
        self._set_status("Accueil")

        canvas = tk.Canvas(self.main, bg="#080808", highlightthickness=0)
        canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        _rng = random.Random(1337)
        _base_heights = [
            (math.sin(i / 95 * math.pi) ** 1.4
             * (0.55 + 0.45 * math.sin(i / 95 * math.pi * 7 + 0.9))
             * (0.7 + 0.3 * _rng.random()))
            for i in range(96)
        ]
        _anim_t = [0.0]

        def _draw_bg(t=0.0):
            try:
                if not canvas.winfo_exists():
                    return
            except Exception:
                return
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w < 50:
                return

            cx, cy = w // 2, h // 2

            pulse = 1.0 + 0.06 * math.sin(t * 0.8)
            for i in range(22, 0, -1):
                r = i / 22 * pulse
                rw = int(w * 0.48 * r)
                rh = int(h * 0.58 * r)
                hue_shift = math.sin(t * 0.25) * 0.15
                rc = int(max(0, min(255, 30 + (i / 22) * 55 * (1 + hue_shift))))
                gc = 0
                bc = int(max(0, min(255, 60 + (i / 22) * 110)))
                canvas.create_oval(cx - rw, cy - rh, cx + rw, cy + rh,
                                   fill=f"#{rc:02x}{gc:02x}{bc:02x}", outline="")

            n = 96
            bar_w = w / n
            for i in range(n):
                ti = i / (n - 1)
                phase = t * 1.4 + i * 0.18
                anim = 0.55 + 0.45 * math.sin(phase)
                val = _base_heights[i] * anim
                bar_h = int(val * h * 0.34)
                if bar_h < 2:
                    continue
                x0 = int(i * bar_w)
                x1 = max(x0 + 1, int((i + 1) * bar_w) - 1)

                hue = (ti + t * 0.04) % 1.0
                if hue < 0.5:
                    rc = int(40 + (1 - hue * 2) * 160)
                    gc = int(hue * 2 * 30)
                    bc = int(100 + hue * 2 * 155)
                else:
                    rc = int(40 + (hue - 0.5) * 2 * 160)
                    gc = int((1 - (hue - 0.5) * 2) * 30)
                    bc = int(255 - (hue - 0.5) * 2 * 100)
                intensity = int(val * 0.85 + 0.15)
                rc = int(min(255, rc * intensity))
                gc = int(min(255, gc * intensity))
                bc = int(min(255, bc * intensity))

                canvas.create_rectangle(x0, h, x1, h - bar_h,
                                        fill=f"#{rc:02x}{gc:02x}{bc:02x}",
                                        outline="")

                if bar_h > 8:
                    tip_r = min(rc + 80, 255)
                    tip_g = min(gc + 40, 255)
                    tip_b = min(bc + 80, 255)
                    canvas.create_rectangle(x0, h - bar_h, x1, h - bar_h + 2,
                                            fill=f"#{tip_r:02x}{tip_g:02x}{tip_b:02x}",
                                            outline="")

            canvas.create_line(0, h - 1, w, h - 1, fill="#141414", width=1)

        def _anim_loop():
            try:
                if not canvas.winfo_exists():
                    return
            except Exception:
                return
            _anim_t[0] += 0.045
            _draw_bg(_anim_t[0])
            self._home_anim_job = self.after(42, _anim_loop)

        canvas.bind("<Configure>", lambda e: _draw_bg(_anim_t[0]))
        self.after(30, _anim_loop)

        card = ctk.CTkFrame(self.main, fg_color="#0f0f0f",
                            corner_radius=20, border_color="#1e1e1e", border_width=1,
                            width=420)
        card.place(relx=0.5, rely=0.46, anchor="center")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=40, pady=36)

        from pathlib import Path
        import numpy as _np
        from PIL import Image
        _logo_path = Path(__file__).resolve().parent.parent.parent / "img" / "tac.png"
        _logo_ok = False
        if _logo_path.exists():
            try:
                _logo_img = Image.open(str(_logo_path)).convert("RGBA")
                _arr = _np.array(_logo_img)
                _black = (_arr[:,:,0] < 18) & (_arr[:,:,1] < 18) & (_arr[:,:,2] < 18)
                _arr[:,:,3] = _np.where(_black, 0, _arr[:,:,3])
                _logo_img = Image.fromarray(_arr)
                _ctk_logo = ctk.CTkImage(
                    light_image=_logo_img,
                    dark_image=_logo_img,
                    size=(130, 130),
                )
                ctk.CTkLabel(inner, image=_ctk_logo, text="").pack(pady=(0, 14))
                _logo_ok = True
            except Exception:
                pass

        if not _logo_ok:
            icon_frame = ctk.CTkFrame(inner, fg_color=ACCENT, corner_radius=14,
                                      width=54, height=54)
            icon_frame.pack(pady=(0, 18))
            icon_frame.pack_propagate(False)
            ctk.CTkLabel(icon_frame, text="▶",
                         font=ctk.CTkFont("Segoe UI", 22, "bold"),
                         text_color="#ffffff").place(relx=0.52, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text="TAC MP4 Studio",
                     font=ctk.CTkFont("Segoe UI", 26, "bold"),
                     text_color=TEXT).pack()
        ctk.CTkLabel(inner, text="Music Visualizer",
                     font=ctk.CTkFont("Segoe UI", 11),
                     text_color=MUTED).pack(pady=(2, 24))

        ctk.CTkFrame(inner, height=1, fg_color="#1e1e1e", corner_radius=0).pack(
            fill="x", pady=(0, 24))

        _btn(inner, "  ✦  NOUVELLE CRÉATION", self.show_step_audio,
             accent=True, height=48, width=340,
             font=ctk.CTkFont("Segoe UI", 13, "bold")).pack(pady=(0, 10))

        hist_btn = ctk.CTkButton(inner, text="Historique",
                                 command=self.show_history,
                                 fg_color="transparent",
                                 hover_color="#161616",
                                 text_color=MUTED,
                                 border_color="#1e1e1e", border_width=1,
                                 font=FONT_SM, corner_radius=8,
                                 height=40, width=340)
        hist_btn.pack(pady=(0, 6))
        ctk.CTkButton(inner, text="⚡ TURBO — Production rapide",
                      command=self.show_turbo,
                      fg_color="transparent",
                      hover_color="#161616",
                      text_color="#f59e0b",
                      border_color="#2a2000", border_width=1,
                      font=FONT_SM, corner_radius=8,
                      height=40, width=340).pack()

        ctk.CTkFrame(inner, height=1, fg_color="#1e1e1e", corner_radius=0).pack(
            fill="x", pady=(22, 16))

        feat_row = ctk.CTkFrame(inner, fg_color="transparent")
        feat_row.pack()
        for text in ["10 spectres", "Vinyle", "Oscilloscope", "Dégradé"]:
            dot = ctk.CTkLabel(feat_row, text=f"● {text}",
                               text_color="#333333",
                               font=ctk.CTkFont("Segoe UI", 9))
            dot.pack(side="left", padx=7)

        ctk.CTkLabel(inner, text=f"v{VERSION}",
                     text_color="#252525",
                     font=ctk.CTkFont("Segoe UI", 8)).pack(pady=(10, 0))

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE ÉTAPE AUDIO
    # ══════════════════════════════════════════════════════════════════════════

    def show_step_audio(self):
        import customtkinter as ctk
        from app.ui.app import TEXT, MUTED, FONT_SM, _btn
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

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE ÉTAPE IMAGE
    # ══════════════════════════════════════════════════════════════════════════

    def show_step_image(self):
        import customtkinter as ctk
        from pathlib import Path
        from app.ui.app import TEXT, MUTED, ACCLT, FONT_SM, FONT_MU, _btn, _card
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

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE HISTORIQUE
    # ══════════════════════════════════════════════════════════════════════════

    def show_history(self):
        import customtkinter as ctk
        from pathlib import Path
        from PIL import Image
        from app.exporter import open_file
        from app.ui.app import (
            BG, SURF3, BORDER, ACCENT, ACCLT, TEXT, MUTED, SUCCESS, WARN, DANGER,
            FONT_H1, FONT_H2, FONT_SEC, FONT_SM, FONT_MU, _btn, _card,
        )
        self._clear_main()
        self._set_status("Historique")
        _cover = ctk.CTkFrame(self.main, fg_color=BG)
        _cover.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.main.update_idletasks()
        outer = ctk.CTkFrame(self.main, fg_color=BG)
        outer.pack(fill="both", expand=True, padx=32, pady=24)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(top, text="Historique", font=FONT_H1, text_color=TEXT).pack(side="left")
        _btn(top, "← Accueil", self.show_home, small=True, width=120).pack(side="right")
        _btn(top, "🗑  Vider l'historique", self._clear_all_history,
             small=True, width=160, danger=True).pack(side="right", padx=(0, 8))

        items = self._sorted_history()
        if not items:
            ctk.CTkLabel(outer, text="Aucune création pour l'instant.",
                         text_color=MUTED, font=FONT_SM).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                        scrollbar_button_color=SURF3,
                                        scrollbar_button_hover_color=ACCENT)
        scroll.pack(fill="both", expand=True)

        self.main.update_idletasks()
        try:
            _cover.destroy()
        except Exception:
            pass

        for item in items:
            card = _card(scroll)
            card.pack(fill="x", pady=5, padx=2)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=12, pady=10)

            thumb_path = Path(item.get("folder", "")) / "_thumb.jpg"
            if not thumb_path.exists():
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
        import customtkinter as ctk
        from app.ui.app import SURF3, MUTED
        ph = ctk.CTkFrame(parent, fg_color=SURF3, corner_radius=6,
                          width=160, height=90)
        ph.pack(side="left", padx=(0, 14))
        ph.pack_propagate(False)
        ctk.CTkLabel(ph, text="🎵", font=ctk.CTkFont("Segoe UI", 28),
                     text_color=MUTED).place(relx=0.5, rely=0.5, anchor="center")

    def _sorted_history(self):
        return sorted(self.history, key=lambda x: x.get("created_at", ""), reverse=True)

    def _clear_all_history(self):
        if not self.history:
            return
        n = len(self.history)
        if messagebox.askyesno(
            "Vider l historique",
            f"Supprimer les {n} entrees ? Les fichiers restent sur le disque.",
            icon="warning"
        ):
            self.history.clear()
            self._persist_now()
            self.show_history()

    def _delete_history_item(self, item):
        if messagebox.askyesno("Historique",
                               f"Supprimer '{item.get('name')}' de l'historique ?\n(Fichiers conservés.)"):
            self.history = [h for h in self.history if h.get("folder") != item.get("folder")]
            self._persist_now()
            self.show_history()

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE TURBO
    # ══════════════════════════════════════════════════════════════════════════

    def show_turbo(self):
        import customtkinter as ctk
        import tkinter as tk
        from pathlib import Path
        from app.ui.app import (
            BG, SURF2, SURF3, BORDER, ACCENT, ACCLT, TEXT, MUTED, WARN,
            FONT_H1, FONT_SM, FONT_MU, AUDIO_EXTS, _btn, _card,
        )
        self._clear_main()
        self._turbo_view_active = True
        self._set_status("⚡ Turbo")

        outer = ctk.CTkFrame(self.main, fg_color=BG)
        outer.pack(fill="both", expand=True, padx=32, pady=24)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(top, text="⚡ Turbo", font=FONT_H1, text_color="#f59e0b").pack(side="left")
        _btn(top, "← Accueil", self.show_home, small=True, width=120).pack(side="right")
        ctk.CTkLabel(top, text="Production rapide · sans preview",
                     text_color=MUTED, font=FONT_MU).pack(side="left", padx=(14, 0))

        ctrl = _card(outer)
        ctrl.pack(fill="x", pady=(0, 10))
        ci = ctk.CTkFrame(ctrl, fg_color="transparent")
        ci.pack(fill="x", padx=16, pady=12)

        r1 = ctk.CTkFrame(ci, fg_color="transparent")
        r1.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(r1, text="Pochette", text_color=MUTED, font=FONT_MU, width=60, anchor="w").pack(side="left")
        self._turbo_img_var = tk.StringVar(value=Path(self._turbo_image).name if self._turbo_image else "")
        turbo_img_entry = ctk.CTkEntry(r1, textvariable=self._turbo_img_var,
                                        placeholder_text="Obligatoire pour l'export",
                                        fg_color=SURF3, border_color=BORDER, text_color=TEXT,
                                        font=FONT_MU, width=210, state="readonly")
        turbo_img_entry.pack(side="left", padx=(4, 0))
        _btn(r1, "📂", self._turbo_pick_image, small=True, width=32, height=28).pack(side="left", padx=(4, 24))

        ctk.CTkLabel(r1, text="Preset ★", text_color=MUTED, font=FONT_MU, width=60, anchor="w").pack(side="left")
        fav_names = [n for n in self.user_presets if n in self.user_preset_favorites]
        if not fav_names:
            fav_names = list(self.user_presets.keys())
        turbo_preset_values = fav_names if fav_names else ["(aucun preset — créez-en un)"]
        self._turbo_preset_var = tk.StringVar(value=turbo_preset_values[0])
        ctk.CTkComboBox(r1, variable=self._turbo_preset_var,
                        values=turbo_preset_values,
                        fg_color=SURF3, border_color=BORDER,
                        button_color=SURF2, button_hover_color=BORDER,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM, width=190).pack(side="left", padx=(4, 24))

        ctk.CTkLabel(r1, text="Format", text_color=MUTED, font=FONT_MU, width=50, anchor="w").pack(side="left")
        self._turbo_format_var = tk.StringVar(value="COMPLET")
        ctk.CTkComboBox(r1, variable=self._turbo_format_var,
                        values=["COMPLET", "SHORT", "CHECK"],
                        fg_color=SURF3, border_color=BORDER,
                        button_color=SURF2, button_hover_color=BORDER,
                        dropdown_fg_color=SURF2, text_color=TEXT,
                        font=FONT_SM, width=130).pack(side="left", padx=(4, 0))

        r2 = ctk.CTkFrame(ci, fg_color="transparent")
        r2.pack(fill="x")
        _btn(r2, "➕ Ajouter des fichiers", self._turbo_pick_files,
             small=True, height=32, width=185).pack(side="left")
        self._turbo_stop_btn = _btn(r2, "⏹ Stopper", self._turbo_stop_fn,
                                     height=32, width=110, danger=True)
        self._turbo_stop_btn.pack(side="right", padx=(6, 0))
        self._turbo_launch_btn = _btn(r2, "▶ Lancer", self._turbo_start,
                                       accent=True, height=32, width=110)
        self._turbo_launch_btn.pack(side="right")

        hdr = ctk.CTkFrame(outer, fg_color=SURF3, corner_radius=6)
        hdr.pack(fill="x", pady=(0, 2))
        for col_txt, col_w in [("Fichier audio", 168), ("Pochette", 52),
                                ("Artiste", 138), ("Titre", 168), ("Statut", 86)]:
            ctk.CTkLabel(hdr, text=col_txt, text_color=MUTED, font=FONT_MU,
                         width=col_w, anchor="w").pack(side="left", padx=6, pady=5)
        ctk.CTkLabel(hdr, text="", width=42).pack(side="right")

        self._turbo_scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                                     scrollbar_button_color=SURF3,
                                                     scrollbar_button_hover_color=ACCENT)
        self._turbo_scroll.pack(fill="both", expand=True, pady=(0, 0))

        if self._turbo_queue:
            for item in self._turbo_queue:
                self._turbo_add_row_ui(item)
        else:
            self._turbo_empty_lbl = ctk.CTkLabel(self._turbo_scroll,
                                                  text="Ajoutez des fichiers audio ou glissez-déposez ici.",
                                                  text_color=MUTED, font=FONT_SM)
            self._turbo_empty_lbl.pack(pady=40)

        self._turbo_bottom_bar = ctk.CTkFrame(outer, fg_color="transparent")
        self._turbo_bottom_bar.pack(fill="x", pady=(6, 0))
        if any(it["status"].startswith("✅") for it in self._turbo_queue):
            self._turbo_show_open_folder_btn()

    def _turbo_add_paths(self, paths: list[str]):
        import tkinter as tk
        from pathlib import Path
        from app.ui.app import AUDIO_EXTS, MUTED, FONT_SM
        import customtkinter as ctk
        added = 0
        for p in paths:
            ext = Path(p).suffix.lower()
            if ext not in AUDIO_EXTS:
                continue
            stem = Path(p).stem
            if " - " in stem:
                left, right = stem.split(" - ", 1)
                artist_val, title_val = left.strip(), right.strip()
            else:
                artist_val, title_val = "", stem.strip()
            item = {
                "audio":      p,
                "image":      "",
                "artist_var": tk.StringVar(value=artist_val),
                "title_var":  tk.StringVar(value=title_val),
                "status":     "⏳ En attente",
                "_status_lbl": None,
                "_img_btn":    None,
            }
            self._turbo_queue.append(item)
            if self._turbo_view_active and hasattr(self, "_turbo_scroll"):
                if hasattr(self, "_turbo_empty_lbl") and self._turbo_empty_lbl:
                    try:
                        self._turbo_empty_lbl.destroy()
                    except Exception:
                        pass
                    self._turbo_empty_lbl = None
                self._turbo_add_row_ui(item)
            added += 1
        if added:
            self._set_status(f"⚡ Turbo — {len(self._turbo_queue)} fichier(s)")

    # ══════════════════════════════════════════════════════════════════════════
    # PAGE PRESETS
    # ══════════════════════════════════════════════════════════════════════════

    def show_presets(self):
        import customtkinter as ctk
        from app.presets import GLOBAL_PRESETS
        from app.ui.app import (
            BG, SURF2, SURF3, BORDER, ACCENT, ACCLT, TEXT, MUTED,
            FONT_H1, FONT_SEC, FONT_SM, FONT_MU, _btn, _sep,
        )
        self._clear_main()
        self._set_status("🎛️ Presets")

        outer = ctk.CTkFrame(self.main, fg_color=BG)
        outer.pack(fill="both", expand=True, padx=32, pady=24)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(top, text="🎛️ Presets", font=FONT_H1, text_color=TEXT).pack(side="left")
        _btn(top, "← Accueil", self.show_home, small=True, width=120).pack(side="right")

        content = ctk.CTkFrame(outer, fg_color="transparent")
        content.pack(fill="both", expand=True)

        left_wrap = ctk.CTkFrame(content, fg_color=SURF2, corner_radius=10,
                                  border_color=BORDER, border_width=1, width=340)
        left_wrap.pack(side="left", fill="y", padx=(0, 12))
        left_wrap.pack_propagate(False)
        self._presets_left_scroll = ctk.CTkScrollableFrame(left_wrap, fg_color="transparent",
                                                            scrollbar_button_color=SURF3)
        self._presets_left_scroll.pack(fill="both", expand=True, padx=6, pady=6)

        self._presets_right_scroll = ctk.CTkScrollableFrame(content, fg_color="transparent",
                                                              scrollbar_button_color=SURF3)
        self._presets_right_scroll.pack(side="left", fill="both", expand=True)

        self._presets_refresh_list()
        self._presets_show_placeholder()

    def _presets_refresh_list(self):
        import customtkinter as ctk
        from app.presets import GLOBAL_PRESETS
        from app.ui.app import (
            SURF3, BORDER, ACCENT, ACCLT, TEXT, MUTED,
            FONT_SEC, FONT_SM, _btn, _sep,
        )
        if not hasattr(self, "_presets_left_scroll"):
            return
        scroll = self._presets_left_scroll
        try:
            if not scroll.winfo_exists():
                return
        except Exception:
            return
        for w in scroll.winfo_children():
            try: w.destroy()
            except Exception: pass

        ctk.CTkLabel(scroll, text="Presets intégrés", text_color=ACCLT,
                     font=FONT_SEC, anchor="w").pack(anchor="w", pady=(4, 4))
        for name in GLOBAL_PRESETS:
            row = ctk.CTkFrame(scroll, fg_color=SURF3, corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=name, text_color=MUTED, font=FONT_SM,
                         anchor="w").pack(side="left", padx=10, pady=6, fill="x", expand=True)
            _btn(row, "▶", lambda n=name: self._apply_global_preset_by_name(n),
                 small=True, width=30, height=26, accent=True).pack(side="right", padx=(0, 6))

        _sep(scroll)

        ctk.CTkLabel(scroll, text="Mes presets", text_color=ACCLT,
                     font=FONT_SEC, anchor="w").pack(anchor="w", pady=(8, 4))
        if not self.user_presets:
            ctk.CTkLabel(scroll, text="Aucun preset — créez-en un ci-dessous",
                         text_color=MUTED, font=FONT_SM).pack(pady=8)
        else:
            for name, data in list(self.user_presets.items()):
                is_fav = name in self.user_preset_favorites
                row = ctk.CTkFrame(scroll, fg_color=SURF3, corner_radius=6)
                row.pack(fill="x", pady=2)
                _btn(row, "★", lambda n=name: self._toggle_favorite(n),
                     small=True, width=28, height=26,
                     fg_color="#d97706" if is_fav else SURF3,
                     hover_color="#b45309").pack(side="left", padx=(4, 0))
                ctk.CTkLabel(row, text=name, text_color=TEXT, font=FONT_SM,
                             anchor="w").pack(side="left", padx=8, pady=6, fill="x", expand=True)
                _btn(row, "✏️", lambda n=name, d=data: self._presets_show_editor(d.copy(), n),
                     small=True, width=30, height=26).pack(side="right", padx=(0, 4))
                _btn(row, "🗑", lambda n=name: self._presets_delete(n),
                     small=True, width=30, height=26, danger=True).pack(side="right", padx=(0, 4))

        _sep(scroll)
        _btn(scroll, "＋  Nouveau preset", lambda: self._presets_show_editor(None, ""),
             accent=True, height=34).pack(fill="x", pady=(8, 4))

    def _presets_show_placeholder(self):
        import customtkinter as ctk
        from app.ui.app import MUTED, FONT_SM
        right = getattr(self, "_presets_right_scroll", None)
        if not right:
            return
        try:
            if not right.winfo_exists():
                return
        except Exception:
            return
        for w in right.winfo_children():
            try: w.destroy()
            except Exception: pass
        ctk.CTkLabel(right,
                     text="← Sélectionnez un preset à modifier\n   ou créez-en un nouveau.",
                     text_color=MUTED, font=FONT_SM, justify="left").pack(pady=60, padx=20, anchor="w")

    def _presets_show_editor(self, preset_data: dict | None, preset_name: str):
        import tkinter as tk
        import customtkinter as ctk
        from tkinter import colorchooser
        from app.presets import SPECTRUM_STYLES, SMOKE_PRESETS, SMOKE_COLORS, PARTICLE_PRESETS
        from app.ui.app import (
            SURF3, BORDER, ACCENT, ACCHOV, ACCLT, TEXT, MUTED,
            FONT_H1, FONT_H2, FONT_MU, FONT_SM, _btn, _sep,
        )
        right = getattr(self, "_presets_right_scroll", None)
        if not right:
            return
        try:
            if not right.winfo_exists():
                return
        except Exception:
            return
        for w in right.winfo_children():
            try: w.destroy()
            except Exception: pass

        is_new = preset_data is None
        data   = preset_data if preset_data is not None else {}

        title_txt = "Nouveau preset" if is_new else f"Modifier : {preset_name}"
        ctk.CTkLabel(right, text=title_txt, font=FONT_H1, text_color=TEXT,
                     anchor="w").pack(anchor="w", pady=(4, 14))

        _p_name   = tk.StringVar(value="" if is_new else preset_name)
        _p_spec   = tk.StringVar(value=data.get("spectrum_style", "Cercle radial"))
        _p_parts  = tk.StringVar(value=data.get("particle_preset", "Premium"))
        _p_smoke  = tk.StringVar(value=data.get("smoke_preset", "Cinématique"))
        _p_sc_col = tk.StringVar(value=data.get("smoke_color", "Blanc"))
        _p_vinyl  = tk.BooleanVar(value=bool(data.get("vinyl_mode", False)))
        _p_vblk   = tk.BooleanVar(value=bool(data.get("vinyl_black", False)))
        _p_float  = tk.BooleanVar(value=bool(data.get("floating_bg", False)))
        _p_bgmode = tk.StringVar(value=data.get("bg_mode", "photo"))
        _p_react  = tk.BooleanVar(value=bool(data.get("spectrum_reactive", False)))
        _p_fav    = tk.BooleanVar(value=preset_name in self.user_preset_favorites)
        _sc = [data.get("spectrum_color", "#ffffff")]

        ctk.CTkLabel(right, text="Nom du preset", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w")
        ctk.CTkEntry(right, textvariable=_p_name, placeholder_text="Nom unique du preset",
                     fg_color=SURF3, border_color=BORDER, text_color=TEXT,
                     font=FONT_SM).pack(fill="x", pady=(2, 10))

        _sep(right)

        ctk.CTkLabel(right, text="Style de spectre", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(8, 2))
        ctk.CTkComboBox(right, variable=_p_spec, values=SPECTRUM_STYLES,
                        fg_color=SURF3, border_color=BORDER, button_color=SURF3,
                        button_hover_color=BORDER, dropdown_fg_color=SURF3,
                        text_color=TEXT, font=FONT_SM).pack(fill="x", pady=(0, 8))

        sc_row = ctk.CTkFrame(right, fg_color="transparent")
        sc_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(sc_row, text="Couleur spectre", text_color=MUTED, font=FONT_MU,
                     anchor="w").pack(side="left", fill="x", expand=True)
        _sc_swatch = tk.Label(sc_row, bg=_sc[0], width=3, relief="flat")
        _sc_swatch.pack(side="right", padx=(4, 0))
        _sc_hex = ctk.CTkLabel(sc_row, text=_sc[0], text_color=TEXT, font=FONT_MU, width=65, anchor="e")
        _sc_hex.pack(side="right")
        def _pick_sc():
            res = colorchooser.askcolor(color=_sc[0], title="Couleur du spectre")
            if res and res[1]:
                _sc[0] = res[1]
                try: _sc_swatch.configure(bg=res[1])
                except Exception: pass
                try: _sc_hex.configure(text=res[1])
                except Exception: pass
        _btn(sc_row, "Choisir", _pick_sc, small=True, width=70, height=24).pack(side="right", padx=(0, 6))

        react_row = ctk.CTkFrame(right, fg_color="transparent")
        react_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(react_row, text="Flash beats", text_color=TEXT, font=FONT_H2, anchor="w").pack(side="left")
        ctk.CTkSwitch(react_row, text="", variable=_p_react,
                      progress_color=ACCENT, button_color=ACCLT,
                      button_hover_color=ACCENT, width=44, height=22).pack(side="right")

        _sep(right)

        ctk.CTkLabel(right, text="Ambiance (fumée)", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(8, 2))
        ctk.CTkComboBox(right, variable=_p_smoke, values=list(SMOKE_PRESETS.keys()),
                        fg_color=SURF3, border_color=BORDER, button_color=SURF3,
                        button_hover_color=BORDER, dropdown_fg_color=SURF3,
                        text_color=TEXT, font=FONT_SM).pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(right, text="Couleur fumée", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(0, 2))
        ctk.CTkComboBox(right, variable=_p_sc_col, values=list(SMOKE_COLORS.keys()),
                        fg_color=SURF3, border_color=BORDER, button_color=SURF3,
                        button_hover_color=BORDER, dropdown_fg_color=SURF3,
                        text_color=TEXT, font=FONT_SM).pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(right, text="Particules", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(0, 2))
        ctk.CTkComboBox(right, variable=_p_parts, values=list(PARTICLE_PRESETS.keys()),
                        fg_color=SURF3, border_color=BORDER, button_color=SURF3,
                        button_hover_color=BORDER, dropdown_fg_color=SURF3,
                        text_color=TEXT, font=FONT_SM).pack(fill="x", pady=(0, 8))

        _sep(right)

        vr = ctk.CTkFrame(right, fg_color="transparent")
        vr.pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(vr, text="🎵  Disque vinyle", text_color=TEXT, font=FONT_H2, anchor="w").pack(side="left")
        ctk.CTkSwitch(vr, text="", variable=_p_vinyl,
                      progress_color=ACCENT, button_color=ACCLT,
                      button_hover_color=ACCENT, width=44, height=22).pack(side="right")
        vt = ctk.CTkFrame(right, fg_color="transparent")
        vt.pack(fill="x", pady=(0, 8))
        for val, lbl in [(False, "🖼 Image"), (True, "⚫ Noir classique")]:
            ctk.CTkRadioButton(vt, text=lbl, variable=_p_vblk, value=val,
                               fg_color=ACCENT, hover_color=ACCHOV,
                               text_color=TEXT, font=FONT_SM).pack(side="left", padx=(0, 14))

        _sep(right)

        fr = ctk.CTkFrame(right, fg_color="transparent")
        fr.pack(fill="x", pady=(8, 4))
        ctk.CTkLabel(fr, text="🌊  Fond flottant", text_color=TEXT, font=FONT_H2, anchor="w").pack(side="left")
        ctk.CTkSwitch(fr, text="", variable=_p_float,
                      progress_color=ACCENT, button_color=ACCLT,
                      button_hover_color=ACCENT, width=44, height=22).pack(side="right")
        ctk.CTkLabel(right, text="Type de fond", text_color=MUTED, font=FONT_MU, anchor="w").pack(anchor="w", pady=(4, 2))
        bg_row = ctk.CTkFrame(right, fg_color="transparent")
        bg_row.pack(fill="x", pady=(0, 8))
        for val, label in [("photo", "📷 Photo floue"), ("gradient", "🌈 Dégradé")]:
            ctk.CTkRadioButton(bg_row, text=label, variable=_p_bgmode, value=val,
                               fg_color=ACCENT, hover_color=ACCHOV,
                               text_color=TEXT, font=FONT_SM).pack(side="left", padx=(0, 14))

        _sep(right)

        fav_row = ctk.CTkFrame(right, fg_color="transparent")
        fav_row.pack(fill="x", pady=(8, 12))
        ctk.CTkLabel(fav_row, text="Favori ★", text_color=TEXT, font=FONT_H2, anchor="w").pack(side="left")
        ctk.CTkSwitch(fav_row, text="", variable=_p_fav,
                      progress_color="#d97706", button_color="#f59e0b",
                      button_hover_color="#d97706", width=44, height=22).pack(side="right")

        btn_row = ctk.CTkFrame(right, fg_color="transparent")
        btn_row.pack(fill="x", pady=(0, 24))

        def _do_save():
            name = _p_name.get().strip()
            if not name:
                return
            saved = dict(data)
            saved.update({
                "particle_preset":     _p_parts.get(),
                "smoke_preset":        _p_smoke.get(),
                "smoke_color":         _p_sc_col.get(),
                "spectrum_style":      _p_spec.get(),
                "spectrum_size":       float(data.get("spectrum_size", 1.05)),
                "spectrum_y":          float(data.get("spectrum_y", 0.90)),
                "image_zoom":          float(data.get("image_zoom", 1.00)),
                "pulse_strength":      float(data.get("pulse_strength", 1.10)),
                "vinyl_mode":          bool(_p_vinyl.get()),
                "vinyl_black":         bool(_p_vblk.get()),
                "spectrum_color":      _sc[0],
                "spectrum_color_auto": False,
                "floating_bg":         bool(_p_float.get()),
                "bg_mode":             _p_bgmode.get(),
                "gradient_top":        data.get("gradient_top", "#1a1a2e"),
                "gradient_bottom":     data.get("gradient_bottom", "#0f3460"),
                "spectrum_reactive":   bool(_p_react.get()),
            })
            self.user_presets[name] = saved
            if bool(_p_fav.get()):
                self.user_preset_favorites.add(name)
            else:
                self.user_preset_favorites.discard(name)
            self._persist_now()
            self._refresh_user_presets_ui()
            self._presets_refresh_list()
            self._presets_show_placeholder()

        _btn(btn_row, "💾  Sauvegarder", _do_save, accent=True, height=36, width=160).pack(side="left")
        _btn(btn_row, "Annuler", self._presets_show_placeholder, height=36, width=100).pack(side="left", padx=(8, 0))

    def _presets_delete(self, name: str):
        if not messagebox.askyesno("Presets", f"Supprimer le preset « {name} » ?"):
            return
        self.user_presets.pop(name, None)
        self.user_preset_favorites.discard(name)
        self._persist_now()
        self._refresh_user_presets_ui()
        self._presets_refresh_list()
        self._presets_show_placeholder()

    def _apply_global_preset_by_name(self, name: str):
        from app.presets import GLOBAL_PRESETS
        if name not in GLOBAL_PRESETS:
            return
        self.global_preset.set(name)
        self._apply_global_preset()
