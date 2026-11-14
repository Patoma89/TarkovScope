"""
TarkovScope - Configuración Global, Rutas y Paleta de Alto Contraste Profesional
"""
import os
import sys

APP_NAME = "TTC (Tactical Tarkov Companion)"
APP_FULL_NAME = "TTC (Tactical Tarkov Companion)"
APP_VERSION = "1.3.1"
APP_AUTHOR = "Patoma89"
GITHUB_REPO = "Patoma89/TarkovScope"

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

THEME_SKIN_META = {
    "tarkov_classic": {"label": "EFT Hideout", "use_tarkov_font": True},
    "labs_nvg": {"label": "Labs NVG", "use_tarkov_font": True},
    "tactical_slate": {"label": "Tactical Slate", "use_tarkov_font": False},
}

# Paletas tácticas (3 Skins seleccionables, solo valores hex #RRGGBB)
THEME_SKINS = {
    "tarkov_classic": {
        "bg_dark": "#0B0B09",          # Negro carbón menú EFT
        "bg_darkest": "#070706",
        "bg_inset": "#090907",
        "bg_deep": "#0E0E0B",
        "bg_card": "#161714",          # Acero/oliva oscuro inventario
        "bg_panel_alt": "#131411",
        "bg_panel_alt2": "#181915",
        "bg_card_hover": "#21221D",
        "bg_row": "#1A1B17",
        "bg_row_alt": "#22241E",
        "bg_row_done": "#111D13",
        "active_tab_bg": "#25261F",
        "btn_surface": "#191A16",
        "btn_hover": "#272922",
        "slate_800": "#23251E",
        "slate_700": "#36382E",
        "border": "#33352D",
        "border_soft": "#282A23",
        "border_alt": "#3E4036",
        "text_main": "#F5F3EC",
        "text_soft": "#E3DFD3",
        "text_muted": "#C7C3B6",
        "text_dim": "#949084",
        "accent_gold": "#C8B07E",      # Dorado arena oficial EFT
        "accent_orange": "#D96B27",
        "accent_olive": "#556B45",
        "accent_blue": "#5AA9D6",
        "accent_red": "#E04F5F",
        "red_dark": "#B83B4A",
        "accent_yellow": "#EAB308",
        "accent_green": "#4A9E5B",
        "green_light": "#6FD083",
        "emerald": "#389E68",
    },
    "labs_nvg": {
        "bg_dark": "#070B0E",          # Negro laboratorio nocturno
        "bg_darkest": "#04070A",
        "bg_inset": "#05090C",
        "bg_deep": "#090F14",
        "bg_card": "#0E171F",
        "bg_panel_alt": "#0C141B",
        "bg_panel_alt2": "#101B24",
        "bg_card_hover": "#162430",
        "bg_row": "#111C26",
        "bg_row_alt": "#172634",
        "bg_row_done": "#0B2219",
        "active_tab_bg": "#152836",
        "btn_surface": "#0F1A24",
        "btn_hover": "#192C3C",
        "slate_800": "#152432",
        "slate_700": "#243C52",
        "border": "#1E3A4C",
        "border_soft": "#162A38",
        "border_alt": "#26485E",
        "text_main": "#F0FDF4",
        "text_soft": "#D1F7E3",
        "text_muted": "#B8D8E8",
        "text_dim": "#7CA3B8",
        "accent_gold": "#4ADE80",      # Verde fósforo NVG
        "accent_orange": "#22D3EE",    # Cian TerraGroup
        "accent_olive": "#15803D",
        "accent_blue": "#38BDF8",
        "accent_red": "#FB7185",
        "red_dark": "#D94A64",
        "accent_yellow": "#A3E635",
        "accent_green": "#22C55E",
        "green_light": "#6EE7A0",
        "emerald": "#10B981",
    },
    "tactical_slate": {
        "bg_dark": "#0A0C10",          # Fondo principal negro obsidiana profundo
        "bg_darkest": "#090B0E",
        "bg_inset": "#0B0D11",
        "bg_deep": "#0D1016",
        "bg_card": "#12161E",          # Fondo de paneles con contraste nítido
        "bg_panel_alt": "#131721",
        "bg_panel_alt2": "#161B26",
        "bg_card_hover": "#1C222E",    # Estado hover elevado
        "bg_row": "#1A202C",
        "bg_row_alt": "#222938",
        "bg_row_done": "#0E1C16",
        "active_tab_bg": "#1E2536",
        "btn_surface": "#151A25",
        "btn_hover": "#232B3D",
        "slate_800": "#1E293B",
        "slate_700": "#334155",
        "border": "#2D3545",           # Bordes estructurales definidos
        "border_soft": "#262C38",
        "border_alt": "#384152",
        "text_main": "#F8FAFC",        # Blanco puro de máximo contraste para lectura
        "text_soft": "#E2E8F0",
        "text_muted": "#CBD5E1",       # Gris plata brillante
        "text_dim": "#94A3B8",
        "accent_gold": "#D4B886",      # Dorado arena oficial de Tarkov / Wiki
        "accent_orange": "#E86C25",    # Naranja táctico de alto contraste
        "accent_olive": "#4D6B43",     # Verde militar táctico
        "accent_blue": "#38BDF8",      # Azul cian táctico de alta visibilidad
        "accent_red": "#EF4444",       # Rojo carmesí nítido
        "red_dark": "#DC2626",
        "accent_yellow": "#F59E0B",    # Ámbar brillante de alto contraste
        "accent_green": "#22C55E",     # Verde esmeralda brillante
        "green_light": "#4ADE80",
        "emerald": "#10B981",
    },
}

# Paleta táctica activa (mutable in-place para soportar cambio de skin)
THEME = dict(THEME_SKINS["tactical_slate"])


def apply_skin_to_theme(skin_id: str) -> str:
    """Actualiza THEME in-place con la skin seleccionada y retorna el skin_id válido."""
    valid_id = skin_id if skin_id in THEME_SKINS else "tactical_slate"
    THEME.clear()
    THEME.update(THEME_SKINS[valid_id])
    return valid_id
