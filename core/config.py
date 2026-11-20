"""
TarkovScope - Configuración Global, Rutas y Paleta de Alto Contraste Profesional
"""
import os
import sys
import tempfile
from typing import Callable, Dict, List, Optional

APP_NAME = "TTC (Tactical Tarkov Companion)"
APP_FULL_NAME = "TTC (Tactical Tarkov Companion)"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Patoma89"
GITHUB_REPO = "Patoma89/TarkovScope"


def _is_dir_writable(dir_path: str) -> bool:
    """Verifica con un archivo temporal real si el usuario actual tiene permiso de escritura."""
    if not dir_path or not os.path.isdir(dir_path):
        return False
    try:
        with tempfile.NamedTemporaryFile(dir=dir_path, prefix=".ttc_w_", delete=True):
            pass
        return True
    except OSError:
        return False


def resolve_runtime_paths(
    is_frozen: bool,
    executable_path: Optional[str] = None,
    meipass_dir: Optional[str] = None,
    localappdata_dir: Optional[str] = None,
    writable_checker: Optional[Callable[[str], bool]] = None,
) -> Dict[str, str]:
    """Resuelve rutas de lectura/escritura soportando instalación en carpetas protegidas (Program Files).

    Si el ejecutable corre desde un directorio sin permisos de escritura para el usuario estándar
    (p. ej. `C:\\Program Files (x86)\\TTC`), los datos editables (`data/` y `cache/`) se almacenan en
    `%LOCALAPPDATA%\\TTC` mientras se conserva el acceso de solo lectura a la caché preinstalada.
    """
    checker = writable_checker or _is_dir_writable
    if not is_frozen:
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        return {
            "install_dir": repo_root,
            "bundle_dir": repo_root,
            "data_dir": os.path.join(repo_root, "data"),
            "cache_dir": os.path.join(repo_root, "cache"),
            "readonly_cache_dir": "",
        }

    install_dir = os.path.dirname(os.path.abspath(executable_path or sys.executable))
    bundle_dir = meipass_dir or install_dir
    install_data_dir = os.path.join(install_dir, "data")
    install_writable = checker(install_dir) and (
        not os.path.exists(install_data_dir) or checker(install_data_dir)
    )
    if install_writable:
        return {
            "install_dir": install_dir,
            "bundle_dir": bundle_dir,
            "data_dir": install_data_dir,
            "cache_dir": os.path.join(install_dir, "cache"),
            "readonly_cache_dir": "",
        }

    user_root = os.path.join(
        localappdata_dir or os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"),
        "TTC",
    )
    return {
        "install_dir": install_dir,
        "bundle_dir": bundle_dir,
        "data_dir": os.path.join(user_root, "data"),
        "cache_dir": os.path.join(user_root, "cache"),
        "readonly_cache_dir": os.path.join(install_dir, "cache"),
    }


_RUNTIME_PATHS = resolve_runtime_paths(
    is_frozen=getattr(sys, "frozen", False),
    executable_path=sys.executable,
    meipass_dir=getattr(sys, "_MEIPASS", None),
    localappdata_dir=os.environ.get("LOCALAPPDATA"),
)

BASE_DIR = _RUNTIME_PATHS["install_dir"]
BUNDLE_DIR = _RUNTIME_PATHS["bundle_dir"]
DATA_DIR = _RUNTIME_PATHS["data_dir"]
CACHE_DIR = _RUNTIME_PATHS["cache_dir"]
READONLY_CACHE_DIR = _RUNTIME_PATHS["readonly_cache_dir"]

DB_PATH = os.path.join(DATA_DIR, "tarkov_data.db")
WIKI_QUESTS_JSON_PATH = os.path.join(DATA_DIR, "wiki_quests_459.json")
WIKI_HIDEOUT_JSON_PATH = os.path.join(DATA_DIR, "wiki_hideout_modules.json")
WIKI_AMMO_JSON_PATH = os.path.join(DATA_DIR, "wiki_ammunition.json")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_read_candidates(*subpaths: str) -> List[str]:
    """Devuelve candidatos en orden de prioridad: caché editable, caché de instalación y bundle _MEIPASS."""
    candidates: List[str] = [os.path.join(CACHE_DIR, *subpaths)]
    if READONLY_CACHE_DIR:
        candidates.append(os.path.join(READONLY_CACHE_DIR, *subpaths))
    bundle_candidate = os.path.join(BUNDLE_DIR, "cache", *subpaths)
    if bundle_candidate not in candidates:
        candidates.append(bundle_candidate)
    return candidates


def resolve_cache_read_path(*subpaths: str, min_bytes: int = 1) -> str:
    """Retorna la primera ruta existente en caché o la ruta editable destino si aún no existe."""
    candidates = get_cache_read_candidates(*subpaths)
    for cand in candidates:
        if os.path.exists(cand) and os.path.getsize(cand) >= min_bytes:
            return cand
    return candidates[0]


def _seed_frozen_data_file(filename: str, overwrite: bool = False) -> None:
    dst = os.path.join(DATA_DIR, filename)
    if os.path.exists(dst) and not overwrite:
        return
    for src_dir in (os.path.join(BASE_DIR, "data"), os.path.join(BUNDLE_DIR, "data")):
        src = os.path.join(src_dir, filename)
        if os.path.abspath(src) != os.path.abspath(dst) and os.path.exists(src):
            try:
                import shutil
                shutil.copy2(src, dst)
                return
            except Exception:
                pass


# Inicialización de datos empaquetados en ejecutable standalone PyInstaller
if getattr(sys, "frozen", False):
    for _fname, _overwrite in (
        ("tarkov_data.db", False),
        ("wiki_ammunition.json", True),
        ("wiki_quests_459.json", False),
        ("wiki_hideout_modules.json", False),
        ("wiki_story_chapters_full.json", True),
    ):
        _seed_frozen_data_file(_fname, overwrite=_overwrite)

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
    "modern_obsidian": {"label": "🌌 Modern Obsidian", "use_tarkov_font": True},
    "terragroup_clean": {"label": "🧬 TerraGroup Clean", "use_tarkov_font": True},
    "halloween_cultist": {"label": "🎃 Halloween", "use_tarkov_font": True},
}

# Paletas tácticas (6 Skins seleccionables, solo valores hex #RRGGBB)
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
    "halloween_cultist": {
        "bg_dark": "#0B0710",          # Obsidiana nocturna evento Halloween
        "bg_darkest": "#07050B",
        "bg_inset": "#09060E",
        "bg_deep": "#100B17",
        "bg_card": "#171122",          # Panel púrpura-carbón ritual Cultista
        "bg_panel_alt": "#140F1E",
        "bg_panel_alt2": "#1A1326",
        "bg_card_hover": "#231933",
        "bg_row": "#1D152B",
        "bg_row_alt": "#261C38",
        "bg_row_done": "#132318",
        "active_tab_bg": "#2B1B24",
        "btn_surface": "#1E1629",
        "btn_hover": "#2E213D",
        "slate_800": "#241B35",
        "slate_700": "#372A4D",
        "border": "#44325B",
        "border_soft": "#312344",
        "border_alt": "#573D6E",
        "text_main": "#FFF7ED",        # Blanco hueso cálido de alto contraste
        "text_soft": "#FDE7D4",
        "text_muted": "#D8C3B8",
        "text_dim": "#A28C88",
        "accent_gold": "#FF8A2B",      # Calabaza luminosa Jack-o'-lantern
        "accent_orange": "#F97316",    # Naranja Halloween intenso
        "accent_olive": "#5E467A",     # Púrpura Cultista
        "accent_blue": "#A78BFA",      # Violeta espectral
        "accent_red": "#F43F5E",       # Carmesí Blood Moon
        "red_dark": "#BE123C",
        "accent_yellow": "#FACC15",    # Amarillo vela ritual
        "accent_green": "#22C55E",     # Verde tóxico Cultista
        "green_light": "#4ADE80",
        "emerald": "#10B981",
    },
    "modern_obsidian": {
        "bg_dark": "#060911",          # Azul noche OLED ultra-profundo
        "bg_darkest": "#04060C",
        "bg_inset": "#080C16",
        "bg_deep": "#0A0F1C",
        "bg_card": "#101726",          # Tarjeta elevada estilo Linear/Vercel
        "bg_panel_alt": "#121A2B",
        "bg_panel_alt2": "#151E31",
        "bg_card_hover": "#1B263D",
        "bg_row": "#141D2F",
        "bg_row_alt": "#19243A",
        "bg_row_done": "#0D241B",
        "active_tab_bg": "#1E2B45",
        "btn_surface": "#131C2E",
        "btn_hover": "#212F4B",
        "slate_800": "#1E293B",
        "slate_700": "#334155",
        "border": "#26354D",
        "border_soft": "#1C283B",
        "border_alt": "#344868",
        "text_main": "#F8FAFC",
        "text_soft": "#E2E8F0",
        "text_muted": "#CBD5E1",
        "text_dim": "#94A3B8",
        "accent_gold": "#F5B041",      # Ámbar dorado moderno de alto contraste
        "accent_orange": "#FB923C",
        "accent_olive": "#3B7A57",
        "accent_blue": "#38BDF8",
        "accent_red": "#F43F5E",
        "red_dark": "#E11D48",
        "accent_yellow": "#FACC15",
        "accent_green": "#22C55E",
        "green_light": "#4ADE80",
        "emerald": "#10B981",
    },
    "terragroup_clean": {
        "bg_dark": "#070C12",          # Pizarra cristalina TerraGroup Labs
        "bg_darkest": "#05080D",
        "bg_inset": "#080E15",
        "bg_deep": "#0A121B",
        "bg_card": "#0F1A27",          # Panel clínico limpio
        "bg_panel_alt": "#111E2D",
        "bg_panel_alt2": "#142334",
        "bg_card_hover": "#1A2D42",
        "bg_row": "#132030",
        "bg_row_alt": "#18283B",
        "bg_row_done": "#0C2520",
        "active_tab_bg": "#173047",
        "btn_surface": "#122132",
        "btn_hover": "#1E354F",
        "slate_800": "#1B2E44",
        "slate_700": "#2B4666",
        "border": "#233D58",
        "border_soft": "#192D42",
        "border_alt": "#2F5174",
        "text_main": "#F1F8FF",
        "text_soft": "#DCEBFA",
        "text_muted": "#B8CFE6",
        "text_dim": "#7FA0C2",
        "accent_gold": "#22D3EE",      # Cian laboratorio TerraGroup
        "accent_orange": "#38BDF8",
        "accent_olive": "#0D9488",
        "accent_blue": "#60A5FA",
        "accent_red": "#FB7185",
        "red_dark": "#E11D48",
        "accent_yellow": "#FBBF24",
        "accent_green": "#34D399",
        "green_light": "#6EE7B7",
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
