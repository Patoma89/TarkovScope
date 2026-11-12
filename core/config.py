"""
TarkovScope - Configuración Global, Rutas y Paleta de Alto Contraste Profesional
"""
import os
import sys

APP_NAME = "TTC (Tactical Tarkov Companion)"
APP_FULL_NAME = "TTC (Tactical Tarkov Companion)"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Patoma89"

# Directorio raíz del proyecto
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    BUNDLE_DIR = BASE_DIR

DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(BASE_DIR, "cache")
DB_PATH = os.path.join(DATA_DIR, "tarkov_data.db")
WIKI_QUESTS_JSON_PATH = os.path.join(DATA_DIR, "wiki_quests_459.json")
WIKI_HIDEOUT_JSON_PATH = os.path.join(DATA_DIR, "wiki_hideout_modules.json")
WIKI_AMMO_JSON_PATH = os.path.join(DATA_DIR, "wiki_ammunition.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Inicialización de datos empaquetados en ejecutable standalone PyInstaller
if getattr(sys, 'frozen', False):
    import shutil
    bundled_db = os.path.join(BUNDLE_DIR, "data", "tarkov_data.db")
    if not os.path.exists(DB_PATH) and os.path.exists(bundled_db):
        try:
            shutil.copy2(bundled_db, DB_PATH)
        except Exception:
            pass

    bundled_ammo = os.path.join(BUNDLE_DIR, "data", "wiki_ammunition.json")
    if not os.path.exists(WIKI_AMMO_JSON_PATH) and os.path.exists(bundled_ammo):
        try:
            shutil.copy2(bundled_ammo, WIKI_AMMO_JSON_PATH)
        except Exception:
            pass

    bundled_q = os.path.join(BUNDLE_DIR, "data", "wiki_quests_459.json")
    if not os.path.exists(WIKI_QUESTS_JSON_PATH) and os.path.exists(bundled_q):
        try:
            shutil.copy2(bundled_q, WIKI_QUESTS_JSON_PATH)
        except Exception:
            pass

    bundled_h = os.path.join(BUNDLE_DIR, "data", "wiki_hideout_modules.json")
    if not os.path.exists(WIKI_HIDEOUT_JSON_PATH) and os.path.exists(bundled_h):
        try:
            shutil.copy2(bundled_h, WIKI_HIDEOUT_JSON_PATH)
        except Exception:
            pass

    bundled_story = os.path.join(BUNDLE_DIR, "data", "wiki_story_chapters_full.json")
    story_dst = os.path.join(DATA_DIR, "wiki_story_chapters_full.json")
    if os.path.exists(bundled_story):
        try:
            shutil.copy2(bundled_story, story_dst)
        except Exception:
            pass

# Endpoints de datos de la comunidad de Tarkov
TARKOV_DATA_BASE_URL = "https://raw.githubusercontent.com/TarkovTracker/tarkovdata/master/"
DATA_FILES = {
    "quests": "quests.json",
    "hideout": "hideout.json",
    "items": "items.en.json",
    "maps": "maps.json",
    "traders": "traders.json",
    "ammo": "ammunition.json",
}

TARKOV_DEV_GRAPHQL_URL = "https://api.tarkov.dev/graphql"

# Paleta táctica de alto contraste inspirada en Escape from Tarkov & Wiki Oficial
THEME = {
    "bg_dark": "#0A0C10",          # Fondo principal negro obsidiana profundo
    "bg_card": "#12161E",          # Fondo de paneles con contraste nítido
    "bg_card_hover": "#1C222E",    # Estado hover elevado
    "border": "#2D3545",           # Bordes estructurales definidos
    "text_main": "#F8FAFC",        # Blanco puro de máximo contraste para lectura
    "text_muted": "#CBD5E1",       # Gris plata brillante (alta legibilidad, nunca apagado)
    "accent_gold": "#D4B886",      # Dorado arena oficial de Tarkov / Wiki
    "accent_orange": "#E86C25",    # Naranja táctico de alto contraste
    "accent_olive": "#4D6B43",     # Verde militar táctico
    "accent_blue": "#38BDF8",      # Azul cian táctico de alta visibilidad
    "accent_red": "#F43F5E",       # Rojo carmesí nítido
    "accent_yellow": "#FACC15",    # Ámbar brillante de alto contraste
    "accent_green": "#22C55E",     # Verde esmeralda brillante
}
