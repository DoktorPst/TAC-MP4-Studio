from __future__ import annotations

import json
import shutil
import subprocess
import threading
import time
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
import tkinter as tk

import cv2
import numpy as np
from PIL import Image, ImageTk

from tac_config import load_config, save_config, safe_name, DEFAULT_CREATIONS_DIR
from visualizer_core import (
    GLOBAL_PRESETS,
    PARTICLE_PRESETS,
    SMOKE_COLORS,
    SMOKE_PRESETS,
    SPECTRUM_STYLES,
    PREVIEW_SECONDS,
    PREVIEW_W,
    PREVIEW_H,
    FPS,
    RenderSettings,
    compute_audio_features,
    load_cover_image,
    render_frame,
    render_video,
    open_file,
)


class ScrollFrame(ttk.Frame):
    def __init__(self, parent, width=340, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg="#111111", highlightthickness=0, width=width)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas, style="Panel.TFrame")

        self.inner.bind("<Configure>", lambda _e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<MouseWheel>", self._wheel)
        self.inner.bind("<MouseWheel>", self._wheel)

    def _wheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("TAC Visualizer Studio")
        self.geometry("1220x780")
        self.minsize(1080, 720)
        self.configure(bg="#080808")

        self.config_data = load_config()
        settings = self.config_data.get("settings", {})

        self.audio_path = ""
        self.image_path = ""
        self.project_root = self.config_data.get("project_root", str(DEFAULT_CREATIONS_DIR))
        Path(self.project_root).mkdir(parents=True, exist_ok=True)
        self.history = self.config_data.get("history", [])

        self.title_text = tk.StringVar(value=settings.get("title_text", ""))
        self.status_var = tk.StringVar(value="Accueil")
        self.project_root_var = tk.StringVar(value=self.project_root)

        self.global_preset = tk.StringVar(value=settings.get("global_preset", "Dark Premium"))
        self.particle_preset = tk.StringVar(value=settings.get("particle_preset", "Premium"))
        self.smoke_preset = tk.StringVar(value=settings.get("smoke_preset", "Cinématique"))
        self.smoke_color = tk.StringVar(value=settings.get("smoke_color", "Blanc"))
        self.spectrum_style = tk.StringVar(value=settings.get("spectrum_style", "Cercle radial"))

        self.spectrum_size = tk.DoubleVar(value=float(settings.get("spectrum_size", 1.05)))
        self.spectrum_y = tk.DoubleVar(value=float(settings.get("spectrum_y", 0.90)))
        self.image_zoom = tk.DoubleVar(value=float(settings.get("image_zoom", 1.00)))
        self.pulse_strength = tk.DoubleVar(value=float(settings.get("pulse_strength", 1.10)))
        self.duration = tk.StringVar(value=settings.get("duration", ""))
        self.preview_start = tk.StringVar(value=settings.get("preview_start", "0"))

        self.project_name = ""
        self.output_path = ""

        self.preview_ready = False
        self.preview_running = False
        self.audio_playing = False
        self.preview_started_at = None
        self.ffplay_process = None

        self.preview_index = 0
        self.preview_features = None
        self.preview_bg = None
        self.preview_cover = None
        self.preview_particles = []
        self.preview_smoke = []
        self.preview_smoothed = np.zeros(84, dtype=np.float32)
        self.photo = None
        self.is_rendering = False

        self.setup_style()
        self.build_base()
        self.show_home()

    def setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Root.TFrame", background="#080808")
        style.configure("Panel.TFrame", background="#111111")
        style.configure("TLabel", background="#080808", foreground="#f5f5f5", font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background="#111111", foreground="#f5f5f5", font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background="#111111", foreground="#a8a8a8", font=("Segoe UI", 9))
        style.configure("Title.TLabel", background="#080808", foreground="#ffffff", font=("Segoe UI", 22, "bold"))
        style.configure("Step.TLabel", background="#080808", foreground="#ffffff", font=("Segoe UI", 18, "bold"))

        style.configure("TButton", background="#242424", foreground="#ffffff", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TButton", background=[("active", "#343434")])

        style.configure("Accent.TButton", background="#ffffff", foreground="#000000", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#dcdcdc")])

        style.configure("TEntry", fieldbackground="#0d0d0d", foreground="#ffffff", insertcolor="#ffffff", bordercolor="#303030")
        style.configure("TCombobox", fieldbackground="#0d0d0d", background="#161616", foreground="#ffffff", arrowcolor="#ffffff")
        style.configure("Horizontal.TScale", background="#111111", troughcolor="#252525")

        style.configure("TNotebook", background="#111111", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1d1d1d", foreground="#ffffff", padding=(10, 6))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", "#000000")])

    def build_base(self):
        header = ttk.Frame(self, style="Root.TFrame")
        header.pack(fill="x", padx=18, pady=(14, 8))

        ttk.Label(header, text="TAC Visualizer Studio", style="Title.TLabel").pack(side="left")
        ttk.Label(header, textvariable=self.status_var).pack(side="right")

        self.main = ttk.Frame(self, style="Root.TFrame")
        self.main.pack(fill="both", expand=True, padx=18, pady=(0, 16))

    def clear_main(self):
        self.stop_audio()
        self.preview_running = False
        for child in self.main.winfo_children():
            child.destroy()

    def show_home(self):
        self.clear_main()
        self.status_var.set("Accueil")

        box = ttk.Frame(self.main, style="Root.TFrame")
        box.place(relx=0.5, rely=0.47, anchor="center")

        ttk.Label(box, text="TAC Studio", style="Title.TLabel").pack(pady=(0, 24))

        ttk.Button(box, text="CRÉER", command=self.show_step_audio, style="Accent.TButton").pack(ipadx=58, ipady=16, pady=10)
        ttk.Button(box, text="HISTORIQUE", command=self.show_history).pack(ipadx=45, ipady=14, pady=10)

    def show_step_audio(self):
        self.clear_main()
        self.status_var.set("Création : importer la musique")

        box = ttk.Frame(self.main, style="Root.TFrame")
        box.place(relx=0.5, rely=0.45, anchor="center")

        ttk.Label(box, text="1. Choisir la musique", style="Step.TLabel").pack(pady=16)
        ttk.Button(box, text="Importer un fichier audio", command=self.pick_audio, style="Accent.TButton").pack(ipadx=34, ipady=13)
        ttk.Button(box, text="Retour", command=self.show_home).pack(ipadx=20, ipady=8, pady=12)

    def show_step_image(self):
        self.clear_main()
        self.status_var.set("Création : importer la pochette")

        box = ttk.Frame(self.main, style="Root.TFrame")
        box.place(relx=0.5, rely=0.45, anchor="center")

        ttk.Label(box, text="2. Choisir la pochette", style="Step.TLabel").pack(pady=16)
        ttk.Label(box, text=Path(self.audio_path).name).pack(pady=4)
        ttk.Button(box, text="Importer une image", command=self.pick_image, style="Accent.TButton").pack(ipadx=34, ipady=13)
        ttk.Button(box, text="Retour", command=self.show_step_audio).pack(ipadx=20, ipady=8, pady=12)

    def show_history(self):
        self.clear_main()
        self.status_var.set("Historique")

        container = ttk.Frame(self.main, style="Root.TFrame")
        container.pack(fill="both", expand=True, padx=24, pady=24)

        top = ttk.Frame(container, style="Root.TFrame")
        top.pack(fill="x", pady=(0, 12))

        ttk.Label(top, text="Historique des créations", style="Step.TLabel").pack(side="left")
        ttk.Button(top, text="Retour", command=self.show_home).pack(side="right", ipadx=18, ipady=6)

        list_frame = ttk.Frame(container, style="Root.TFrame")
        list_frame.pack(fill="both", expand=True)

        self.history_listbox = tk.Listbox(
            list_frame,
            bg="#0d0d0d",
            fg="#ffffff",
            selectbackground="#ffffff",
            selectforeground="#000000",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#303030",
            font=("Segoe UI", 11),
        )
        self.history_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.configure(yscrollcommand=scrollbar.set)

        items = self.sorted_history()
        for item in items:
            self.history_listbox.insert(tk.END, f"{item.get('created_at', '')}  |  {item.get('name', 'Sans nom')}")

        actions = ttk.Frame(container, style="Root.TFrame")
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(actions, text="Ouvrir dossier", command=lambda: self.open_history_selection(items)).pack(side="left", ipadx=18, ipady=8)
        ttk.Button(actions, text="Supprimer de l'historique", command=lambda: self.delete_history_selection(items)).pack(side="left", padx=8, ipadx=18, ipady=8)

    def sorted_history(self):
        return sorted(self.history, key=lambda x: x.get("created_at", ""), reverse=True)

    def open_history_selection(self, items):
        selection = self.history_listbox.curselection()
        if not selection:
            return
        item = items[selection[0]]
        open_file(item.get("folder", ""))

    def delete_history_selection(self, items):
        selection = self.history_listbox.curselection()
        if not selection:
            return
        item = items[selection[0]]

        if not messagebox.askyesno("Historique", f"Supprimer '{item.get('name')}' de l'historique ?\nLes fichiers ne seront pas supprimés."):
            return

        self.history = [h for h in self.history if h.get("folder") != item.get("folder")]
        self.persist_config()
        self.show_history()

    def show_editor(self):
        self.clear_main()
        self.status_var.set("Création : preview et réglages")

        left = ttk.Frame(self.main, style="Root.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 14))

        right_scroll = ScrollFrame(self.main, width=350, style="Panel.TFrame")
        right_scroll.pack(side="right", fill="y")
        right = right_scroll.inner

        self.preview_label = tk.Label(left, bg="#000000", bd=0, highlightthickness=1, highlightbackground="#222222")
        self.preview_label.pack(fill="both", expand=True)

        controls = ttk.Frame(left, style="Root.TFrame")
        controls.pack(fill="x", pady=(10, 0))

        ttk.Button(controls, text="▶ Lecture preview", command=self.play_preview_audio).pack(side="left", ipadx=12, ipady=6)
        ttk.Button(controls, text="⏸ Pause", command=self.pause_preview_audio).pack(side="left", padx=8, ipadx=12, ipady=6)
        ttk.Button(controls, text="⟲ Recharger preview", command=self.prepare_preview).pack(side="left", ipadx=12, ipady=6)
        ttk.Button(controls, text="Accueil", command=self.show_home).pack(side="right", ipadx=12, ipady=6)

        notebook = ttk.Notebook(right)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        tab_project = ttk.Frame(notebook, style="Panel.TFrame")
        tab_look = ttk.Frame(notebook, style="Panel.TFrame")
        tab_spectrum = ttk.Frame(notebook, style="Panel.TFrame")
        tab_export = ttk.Frame(notebook, style="Panel.TFrame")

        notebook.add(tab_project, text="Projet")
        notebook.add(tab_look, text="Ambiance")
        notebook.add(tab_spectrum, text="Spectre")
        notebook.add(tab_export, text="Export")

        self.section(tab_project, "Fichiers")
        self.small_button(tab_project, "Changer musique", self.show_step_audio)
        self.small_button(tab_project, "Changer pochette", self.show_step_image)

        self.section(tab_project, "Texte optionnel")
        self.entry(tab_project, "Texte affiché, vide = aucun texte", self.title_text)

        self.section(tab_look, "Presets 1 clic")
        self.combo(tab_look, "Preset global", self.global_preset, list(GLOBAL_PRESETS.keys()), self.apply_global_preset)
        ttk.Button(tab_look, text="APPLIQUER PRESET", command=lambda: self.apply_global_preset(None), style="Accent.TButton").pack(fill="x", pady=(3, 12), padx=8, ipady=7)

        self.section(tab_look, "Visuels liés à la musique")
        self.combo(tab_look, "Particules", self.particle_preset, list(PARTICLE_PRESETS.keys()), self.on_setting_changed)
        self.combo(tab_look, "Fumée", self.smoke_preset, list(SMOKE_PRESETS.keys()), self.on_setting_changed)
        self.combo(tab_look, "Couleur fumée", self.smoke_color, list(SMOKE_COLORS.keys()), self.on_setting_changed)
        self.slider(tab_look, "Taille image", self.image_zoom, 0.65, 1.35)
        self.slider(tab_look, "Pulse image", self.pulse_strength, 0.0, 2.2)

        self.section(tab_spectrum, "Modes spectre")
        self.combo(tab_spectrum, "Style", self.spectrum_style, SPECTRUM_STYLES, self.on_setting_changed)
        self.slider(tab_spectrum, "Taille spectre", self.spectrum_size, 0.55, 1.65)
        self.slider(tab_spectrum, "Position spectre", self.spectrum_y, 0.62, 0.95)

        self.section(tab_export, "Dossier de travail")
        ttk.Label(tab_export, textvariable=self.project_root_var, style="Muted.TLabel", wraplength=300).pack(anchor="w", padx=8, pady=(0, 6))
        self.small_button(tab_export, "Choisir dossier racine", self.choose_project_root)

        self.section(tab_export, "Preview audio")
        self.entry(tab_export, "Départ preview en secondes", self.preview_start)
        self.small_button(tab_export, "Analyser depuis ce départ", self.prepare_preview)

        self.section(tab_export, "Export")
        self.entry(tab_export, "Durée export vide = complète", self.duration)
        ttk.Label(tab_export, text="Nom du projet demandé au lancement export.\nIl servira au dossier, musique, image et vidéo.", style="Muted.TLabel").pack(anchor="w", padx=8, pady=(4, 12))
        ttk.Button(tab_export, text="GÉNÉRER MP4", command=self.start_export, style="Accent.TButton").pack(fill="x", pady=(14, 4), padx=8, ipady=10)

        self.prepare_preview()

    def section(self, parent, title):
        ttk.Label(parent, text=title, style="Panel.TLabel", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(12, 6), padx=8)

    def entry(self, parent, label, var):
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor="w", padx=8)
        entry = ttk.Entry(parent, textvariable=var)
        entry.pack(fill="x", pady=(2, 8), padx=8)
        entry.bind("<FocusOut>", lambda _e: self.persist_config())
        return entry

    def combo(self, parent, label, var, values, callback=None):
        ttk.Label(parent, text=label, style="Muted.TLabel").pack(anchor="w", padx=8)
        cb = ttk.Combobox(parent, textvariable=var, values=values, state="readonly")
        cb.pack(fill="x", pady=(2, 8), padx=8)
        cb.bind("<<ComboboxSelected>>", callback if callback else self.on_setting_changed)
        return cb

    def small_button(self, parent, text, command):
        ttk.Button(parent, text=text, command=command).pack(fill="x", pady=3, padx=8, ipady=4)

    def slider(self, parent, label, var, minv, maxv):
        row = ttk.Frame(parent, style="Panel.TFrame")
        row.pack(fill="x", pady=(3, 0), padx=8)

        value_label = ttk.Label(row, text="", style="Panel.TLabel", width=6)
        ttk.Label(row, text=label, style="Muted.TLabel").pack(side="left")
        value_label.pack(side="right")

        scale = ttk.Scale(parent, from_=minv, to=maxv, orient="horizontal", variable=var, command=lambda _=None: self.update_slider_label(value_label, var))
        scale.pack(fill="x", pady=(0, 8), padx=8)

        self.update_slider_label(value_label, var)

    def update_slider_label(self, label, var):
        label.configure(text=f"{var.get():.2f}")
        self.persist_config()
        if self.preview_ready:
            self.reload_preview_visuals_only()

    def on_setting_changed(self, _event=None):
        self.persist_config()
        self.reload_preview_visuals_only()

    def pick_audio(self):
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.mp3 *.wav *.flac *.ogg *.m4a"), ("Tous", "*.*")])
        if path:
            self.audio_path = path
            self.show_step_image()

    def pick_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.webp"), ("Tous", "*.*")])
        if path:
            self.image_path = path
            self.show_editor()

    def choose_project_root(self):
        path = filedialog.askdirectory(title="Choisir le dossier racine des créations")
        if not path:
            return
        self.project_root = path
        Path(self.project_root).mkdir(parents=True, exist_ok=True)
        self.project_root_var.set(path)
        self.persist_config()
        self.status_var.set("Dossier racine enregistré.")

    def persist_config(self):
        self.config_data["project_root"] = self.project_root
        self.config_data["history"] = self.history
        self.config_data["settings"] = {
            "title_text": self.title_text.get(),
            "global_preset": self.global_preset.get(),
            "particle_preset": self.particle_preset.get(),
            "smoke_preset": self.smoke_preset.get(),
            "smoke_color": self.smoke_color.get(),
            "spectrum_style": self.spectrum_style.get(),
            "spectrum_size": self.spectrum_size.get(),
            "spectrum_y": self.spectrum_y.get(),
            "image_zoom": self.image_zoom.get(),
            "pulse_strength": self.pulse_strength.get(),
            "duration": self.duration.get(),
            "preview_start": self.preview_start.get(),
        }
        save_config(self.config_data)

    def apply_global_preset(self, _event=None):
        preset = GLOBAL_PRESETS[self.global_preset.get()]
        self.particle_preset.set(preset["particle_preset"])
        self.smoke_preset.set(preset["smoke_preset"])
        self.smoke_color.set(preset["smoke_color"])
        self.spectrum_style.set(preset["spectrum_style"])
        self.spectrum_size.set(preset["spectrum_size"])
        self.spectrum_y.set(preset["spectrum_y"])
        self.image_zoom.set(preset["image_zoom"])
        self.pulse_strength.set(preset["pulse_strength"])
        self.persist_config()
        self.reload_preview_visuals_only()

    def current_settings(self, preview=False):
        duration_text = self.duration.get().strip().replace(",", ".")
        duration = float(duration_text) if duration_text else None

        if preview:
            duration = PREVIEW_SECONDS

        start_text = self.preview_start.get().strip().replace(",", ".")
        start = float(start_text) if start_text else 0.0

        return RenderSettings(
            audio_path=self.audio_path,
            image_path=self.image_path,
            output_path=self.output_path,
            title_text=self.title_text.get().strip(),
            duration_limit=duration,
            start_offset=start if preview else 0.0,
            particle_preset=self.particle_preset.get(),
            smoke_preset=self.smoke_preset.get(),
            smoke_color=self.smoke_color.get(),
            spectrum_style=self.spectrum_style.get(),
            spectrum_size=float(self.spectrum_size.get()),
            spectrum_y=float(self.spectrum_y.get()),
            image_zoom=float(self.image_zoom.get()),
            pulse_strength=float(self.pulse_strength.get()),
            background_blur=38,
        )

    def ask_project_name_and_prepare_folder(self):
        if not self.project_root:
            self.choose_project_root()

        project_name = simpledialog.askstring("Nom du projet", "Nom du projet :", parent=self)

        if not project_name:
            raise RuntimeError("Nom du projet obligatoire.")

        clean_name = safe_name(project_name)
        root = Path(self.project_root)
        root.mkdir(parents=True, exist_ok=True)

        project_dir = root / clean_name
        counter = 2

        while project_dir.exists():
            project_dir = root / f"{clean_name}_{counter}"
            counter += 1

        project_dir.mkdir(parents=True, exist_ok=True)
        return clean_name, project_dir

    def copy_assets_to_project(self, project_dir: Path, project_name: str):
        audio_src = Path(self.audio_path)
        image_src = Path(self.image_path)

        audio_dst = project_dir / f"{project_name}{audio_src.suffix.lower()}"
        image_dst = project_dir / f"{project_name}_cover{image_src.suffix.lower()}"

        shutil.copy2(audio_src, audio_dst)
        shutil.copy2(image_src, image_dst)

        return str(audio_dst), str(image_dst)

    def prepare_preview(self):
        self.stop_audio()

        if not self.audio_path or not self.image_path:
            return

        self.preview_running = False
        self.status_var.set("Analyse preview bass/kick/aigus...")

        settings = self.current_settings(preview=True)

        def worker():
            try:
                features = compute_audio_features(settings.audio_path, FPS, PREVIEW_SECONDS, settings.start_offset)
                self.preview_features = features
                self.preview_bg, self.preview_cover = load_cover_image(settings.image_path, settings.background_blur, settings.image_zoom, PREVIEW_W, PREVIEW_H)

                self.preview_particles = []
                self.preview_smoke = []
                self.preview_smoothed = np.zeros(84, dtype=np.float32)
                self.preview_index = 0
                self.preview_ready = True
                self.preview_running = True

                self.after(0, self.update_preview)
                self.after(0, lambda: self.status_var.set("Preview visuelle active."))

            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda: messagebox.showerror("Erreur preview", msg))

        threading.Thread(target=worker, daemon=True).start()

    def reload_preview_visuals_only(self):
        if not self.audio_path or not self.image_path:
            return

        try:
            settings = self.current_settings(preview=True)
            self.preview_bg, self.preview_cover = load_cover_image(settings.image_path, settings.background_blur, settings.image_zoom, PREVIEW_W, PREVIEW_H)
            self.preview_particles = []
            self.preview_smoke = []
            self.preview_smoothed = np.zeros(84, dtype=np.float32)
        except Exception:
            pass

    def update_preview(self):
        if not self.preview_running or not self.preview_ready or self.preview_features is None:
            return

        settings = self.current_settings(preview=True)
        total = len(self.preview_features["rms"])

        if self.audio_playing and self.preview_started_at is not None:
            elapsed = time.time() - self.preview_started_at
            self.preview_index = int(elapsed * FPS) % total

        i = self.preview_index % total

        metrics = {
            "rms": float(self.preview_features["rms"][i]),
            "kick": float(self.preview_features["kick"][i]),
            "bass": float(self.preview_features["bass"][i]),
            "mid": float(self.preview_features["mid"][i]),
            "high": float(self.preview_features["high"][i]),
        }

        frame, self.preview_particles, self.preview_smoke, self.preview_smoothed = render_frame(
            self.preview_bg,
            self.preview_cover,
            self.preview_particles,
            self.preview_smoke,
            self.preview_features["spec"][:, i],
            metrics,
            self.preview_smoothed,
            settings.title_text,
            settings,
        )

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.photo = ImageTk.PhotoImage(Image.fromarray(rgb))
        self.preview_label.configure(image=self.photo)

        if not self.audio_playing:
            self.preview_index += 1

        self.after(int(1000 / FPS), self.update_preview)

    def play_preview_audio(self):
        if shutil.which("ffplay") is None:
            messagebox.showerror(
                "Audio preview",
                "FFplay est introuvable. Installe une version complète de FFmpeg contenant ffplay.exe.",
            )
            return

        try:
            self.stop_audio()

            start = float(self.preview_start.get().strip().replace(",", ".") or 0)
            cmd = [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel", "quiet",
                "-ss", f"{start:.3f}",
                "-t", str(PREVIEW_SECONDS),
                self.audio_path,
            ]

            self.ffplay_process = subprocess.Popen(cmd)
            self.audio_playing = True
            self.preview_started_at = time.time()
            self.preview_index = 0
            self.status_var.set("Lecture preview avec audio.")

        except Exception as exc:
            messagebox.showerror("Audio preview", str(exc))

    def pause_preview_audio(self):
        self.stop_audio()
        self.status_var.set("Preview audio en pause.")

    def stop_audio(self):
        self.audio_playing = False
        self.preview_started_at = None

        if self.ffplay_process is not None:
            try:
                self.ffplay_process.terminate()
            except Exception:
                pass
            self.ffplay_process = None

    def start_export(self):
        if self.is_rendering:
            return

        if not self.audio_path or not self.image_path:
            messagebox.showerror("Erreur", "Musique ou pochette manquante.")
            return

        try:
            project_name, project_dir = self.ask_project_name_and_prepare_folder()
            project_audio, project_image = self.copy_assets_to_project(project_dir, project_name)

            self.project_name = project_name
            self.audio_path = project_audio
            self.image_path = project_image
            self.output_path = str(project_dir / f"{project_name}.mp4")

            self.persist_config()

        except Exception as exc:
            messagebox.showerror("Export", str(exc))
            return

        settings = self.current_settings(preview=False)

        self.stop_audio()
        self.is_rendering = True
        self.status_var.set(f"Export final : {project_name}...")

        def worker():
            try:
                render_video(settings, progress_callback=lambda t: self.after(0, lambda txt=t: self.status_var.set(txt)))

                self.history.append({
                    "name": project_name,
                    "folder": str(project_dir),
                    "video": settings.output_path,
                    "audio": settings.audio_path,
                    "image": settings.image_path,
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                })

                self.persist_config()

                self.after(
                    0,
                    lambda: messagebox.showinfo(
                        "Terminé",
                        f"Dossier créé :\n{project_dir}\n\nVidéo générée :\n{settings.output_path}",
                    ),
                )
                self.after(0, lambda: open_file(str(project_dir)))

            except Exception as exc:
                msg = str(exc)
                self.after(0, lambda: messagebox.showerror("Erreur export", msg))
                self.after(0, lambda: self.status_var.set("Erreur export."))

            finally:
                self.is_rendering = False

        threading.Thread(target=worker, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()
