import os
import json

DEFAULT_CONFIG = {
    "download_path": os.path.join(os.getcwd(), "Downloads"),
    "hotkeys": {
        "play_pause": "ctrl+alt+p",
        "next": "ctrl+alt+right",
        "prev": "ctrl+alt+left"
    }
}

ARQUIVO_CONFIG = 'config.json'
ARQUIVO_PLAYLISTS = 'playlists.json'

def load_config():
    cfg = DEFAULT_CONFIG.copy()
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as f:
                saved = json.load(f)
                cfg.update(saved)
        except Exception:
            pass
    return cfg

def save_config(config):
    try:
        with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def load_playlists():
    if os.path.exists(ARQUIVO_PLAYLISTS):
        try:
            with open(ARQUIVO_PLAYLISTS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_playlists(playlists):
    try:
        with open(ARQUIVO_PLAYLISTS, 'w', encoding='utf-8') as f:
            json.dump(playlists, f, indent=4, ensure_ascii=False)
    except Exception:
        pass