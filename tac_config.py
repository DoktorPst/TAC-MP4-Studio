from __future__ import annotations

import json
import os
from pathlib import Path


APP_DATA_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "DoktorP3st" / "TAC_MP4"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

CONFIG_PATH = APP_DATA_DIR / "config.json"
DEFAULT_CREATIONS_DIR = APP_DATA_DIR / "Creations"
DEFAULT_CREATIONS_DIR.mkdir(parents=True, exist_ok=True)


def safe_name(name: str) -> str:
    invalid = '<>:"/\\|?*'
    cleaned = "".join(c for c in name.strip() if c not in invalid)
    cleaned = " ".join(cleaned.split())
    return cleaned or "Projet sans nom"


def default_config() -> dict:
    return {
        "project_root": str(DEFAULT_CREATIONS_DIR),
        "history": [],
        "settings": {
            "global_preset": "Dark Premium",
            "particle_preset": "Premium",
            "smoke_preset": "Cinématique",
            "smoke_color": "Blanc",
            "spectrum_style": "Cercle radial",
            "spectrum_size": 1.05,
            "spectrum_y": 0.90,
            "image_zoom": 1.00,
            "pulse_strength": 1.10,
            "duration": "",
            "preview_start": "0",
            "window_geometry": "1220x780+80+40",
            "text_x": 0.50,
            "text_y": 0.70,
            "title_text": "",
        },
    }


def load_config() -> dict:
    cfg = default_config()
    if CONFIG_PATH.exists():
        try:
            loaded = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                cfg.update({k: v for k, v in loaded.items() if k != "settings"})
                settings = cfg.get("settings", {})
                settings.update(loaded.get("settings", {}))
                cfg["settings"] = settings
        except Exception:
            pass

    Path(cfg.get("project_root", DEFAULT_CREATIONS_DIR)).mkdir(parents=True, exist_ok=True)
    return cfg


def save_config(cfg: dict) -> None:
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
