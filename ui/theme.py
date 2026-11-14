"""
TarkovScope - Sistema Tipográfico Profesional (Bender / Bahnschrift / Segoe UI / Consolas) y 3 Skins Tácticas
Garantiza fuentes nítidas nativas de Windows (evitando el fallback borroso de Tkinter)
con jerarquía tipográfica clara, alto contraste y soporte dinámico para 3 skins.
"""
import os
import sys
import functools
import customtkinter as ctk
from core.config import THEME, THEME_SKINS, THEME_SKIN_META, BASE_DIR, BUNDLE_DIR, CACHE_DIR, apply_skin_to_theme
from core.user_data import get_user_preference

_TARKOV_FONT_LOADED = False


def _detect_tarkov_font_family() -> str:
    """
    Carga Bender.ttf en memoria privada de Windows si existe en assets/fonts o cache/fonts;
    de lo contrario usa Bahnschrift (tipografía militar condensada nativa de Windows 10/11)
    con respaldo a Segoe UI.
    """
    global _TARKOV_FONT_LOADED
    if sys.platform.startswith("win"):
        if not _TARKOV_FONT_LOADED:
            font_candidates = [
                os.path.join(BASE_DIR, "assets", "fonts", "Bender.ttf"),
                os.path.join(BASE_DIR, "assets", "fonts", "Bender-Bold.ttf"),
                os.path.join(CACHE_DIR, "fonts", "Bender.ttf"),
                os.path.join(CACHE_DIR, "fonts", "Bender-Bold.ttf"),
                os.path.join(BUNDLE_DIR, "assets", "fonts", "Bender.ttf"),
                os.path.join(BUNDLE_DIR, "cache", "fonts", "Bender.ttf"),
            ]
            loaded_bender = False
            try:
                import ctypes
                FR_PRIVATE = 0x10
                for fp in font_candidates:
                    if os.path.exists(fp):
                        if ctypes.windll.gdi32.AddFontResourceExW(fp, FR_PRIVATE, 0) > 0:
                            loaded_bender = True
            except Exception:
                pass
            _TARKOV_FONT_LOADED = loaded_bender
        if _TARKOV_FONT_LOADED:
            return "Bender"
        return "Bahnschrift"
    return "Segoe UI"


TARKOV_FONT_FAMILY = _detect_tarkov_font_family()
FONT_FAMILY = "Segoe UI"
FONT_MONO_FAMILY = "Consolas"

# Tuplas tipográficas con familia explícita
FONT_TITLE = (FONT_FAMILY, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 17, "bold")
FONT_SECTION = (FONT_FAMILY, 15, "bold")
FONT_BODY = (FONT_FAMILY, 13)
FONT_BODY_BOLD = (FONT_FAMILY, 13, "bold")
FONT_SMALL = (FONT_FAMILY, 11, "bold")
FONT_MONO = (FONT_MONO_FAMILY, 12)
FONT_MONO_BOLD = (FONT_MONO_FAMILY, 12, "bold")


def apply_global_smooth_scroll(pixels_per_notch: int = 80) -> None:
    """
    Optimiza globalmente la velocidad de scroll de CTkScrollableFrame en Windows.
    CustomTkinter por defecto solo desplaza 20px por muesca de rueda (delta / 6),
    lo que resulta excesivamente lento para tablas y listas largas.
    Esta función calibra el desplazamiento a ~80px por muesca (estándar Windows).
    """
    orig_mouse_wheel_all = getattr(ctk.CTkScrollableFrame, "_mouse_wheel_all", None)
    if not orig_mouse_wheel_all or getattr(ctk.CTkScrollableFrame, "_smooth_scroll_patched", False):
        return

    def _fast_mouse_wheel_all(self, event):
        if self._check_if_valid_scroll(event.widget):
            if sys.platform.startswith("win"):
                step = -int(event.delta * (pixels_per_notch / 120.0))
                if step == 0 and event.delta != 0:
                    step = -1 if event.delta > 0 else 1
                if getattr(self, "_shift_pressed", False):
                    if self._parent_canvas.xview() != (0.0, 1.0):
                        self._parent_canvas.xview("scroll", step, "units")
                else:
                    if self._parent_canvas.yview() != (0.0, 1.0):
                        self._parent_canvas.yview("scroll", step, "units")
            else:
                orig_mouse_wheel_all(self, event)

    ctk.CTkScrollableFrame._mouse_wheel_all = _fast_mouse_wheel_all
    ctk.CTkScrollableFrame._smooth_scroll_patched = True


# Aplicar automáticamente al importar theme en la interfaz
apply_global_smooth_scroll()


@functools.lru_cache(maxsize=256)
def ui_font(size: int = 13, weight: str = "normal", mono: bool = False) -> ctk.CTkFont:
    """Retorna una fuente CTkFont con familia activa (Bender/Bahnschrift o Segoe UI / Consolas) en caché O(1)."""
    fam = FONT_MONO_FAMILY if mono else FONT_FAMILY
    return ctk.CTkFont(family=fam, size=size, weight=weight)


_ACTIVE_SKIN_ID = "tarkov_classic"


def get_active_skin_id() -> str:
    return _ACTIVE_SKIN_ID


_SYNCED_COLOR_NAMES = (
    "C_TEXT", "C_TEXT_SOFT", "C_TEXT_MUTED", "C_TEXT_DIM", "C_BLUE",
    "C_BORDER", "C_BORDER_SOFT", "C_BORDER_ALT",
    "C_BG_DEEP", "C_BG_DARKEST", "C_BG_INSET",
    "C_BG_PANEL", "C_BG_PANEL_ALT", "C_BG_PANEL_ALT2",
    "C_SLATE_800", "C_SLATE_700", "C_BG_ROW", "C_BG_ROW_ALT",
    "C_GREEN_LIGHT", "C_GREEN", "C_EMERALD", "C_RED", "C_RED_DARK", "C_AMBER",
)


def _sync_imported_color_constants() -> None:
    """Propaga los valores actualizados de C_* a los módulos UI que los importaron por nombre."""
    mod_globals = globals()
    new_vals = {name: mod_globals[name] for name in _SYNCED_COLOR_NAMES if name in mod_globals}
    for mod_name, mod in list(sys.modules.items()):
        if mod is None or mod_name == __name__:
            continue
        if not (mod_name == "__main__" or mod_name == "TarkovScope" or mod_name.startswith("ui.")):
            continue
        mod_dict = getattr(mod, "__dict__", None)
        if not isinstance(mod_dict, dict):
            continue
        for c_name, c_val in new_vals.items():
            if c_name in mod_dict:
                mod_dict[c_name] = c_val


def apply_ui_skin(skin_id: str) -> str:
    """Aplica una de las 3 skins tácticas a THEME, constantes C_* (en todos los módulos) y tipografía activa."""
    global _ACTIVE_SKIN_ID, FONT_FAMILY
    global C_TEXT, C_TEXT_SOFT, C_TEXT_MUTED, C_TEXT_DIM, C_BLUE
    global C_BORDER, C_BORDER_SOFT, C_BORDER_ALT
    global C_BG_DEEP, C_BG_DARKEST, C_BG_INSET, C_BG_PANEL, C_BG_PANEL_ALT, C_BG_PANEL_ALT2
    global C_SLATE_800, C_SLATE_700, C_BG_ROW, C_BG_ROW_ALT
    global C_GREEN_LIGHT, C_GREEN, C_EMERALD, C_RED, C_RED_DARK, C_AMBER

    valid_id = apply_skin_to_theme(skin_id)
    _ACTIVE_SKIN_ID = valid_id

    use_tarkov_font = bool(THEME_SKIN_META.get(valid_id, {}).get("use_tarkov_font", False))
    FONT_FAMILY = TARKOV_FONT_FAMILY if use_tarkov_font else "Segoe UI"
    ui_font.cache_clear()

    THEME_SETTINGS.update({
        "fg_color": THEME["bg_dark"],
        "card_color": THEME["bg_card"],
        "card_hover": THEME["bg_card_hover"],
        "border_color": THEME["border"],
        "accent_orange": THEME["accent_orange"],
        "accent_gold": THEME.get("accent_gold", "#D4B886"),
        "accent_olive": THEME["accent_olive"],
        "text_main": THEME["text_main"],
        "text_muted": THEME["text_muted"],
    })

    C_TEXT = THEME["text_main"]
    C_TEXT_SOFT = THEME.get("text_soft", "#E2E8F0")
    C_TEXT_MUTED = THEME["text_muted"]
    C_TEXT_DIM = THEME.get("text_dim", "#94A3B8")
    C_BLUE = THEME["accent_blue"]
    C_BORDER = THEME["border"]
    C_BORDER_SOFT = THEME.get("border_soft", "#262C38")
    C_BORDER_ALT = THEME.get("border_alt", "#384152")
    C_BG_DEEP = THEME.get("bg_deep", "#0D1016")
    C_BG_DARKEST = THEME.get("bg_darkest", "#090B0E")
    C_BG_INSET = THEME.get("bg_inset", "#0B0D11")
    C_BG_PANEL = THEME["bg_card"]
    C_BG_PANEL_ALT = THEME.get("bg_panel_alt", "#131721")
    C_BG_PANEL_ALT2 = THEME.get("bg_panel_alt2", "#161B26")
    C_SLATE_800 = THEME.get("slate_800", "#1E293B")
    C_SLATE_700 = THEME.get("slate_700", "#334155")
    C_BG_ROW = THEME.get("bg_row", "#1A202C")
    C_BG_ROW_ALT = THEME.get("bg_row_alt", "#222938")
    C_GREEN_LIGHT = THEME.get("green_light", "#4ADE80")
    C_GREEN = THEME["accent_green"]
    C_EMERALD = THEME.get("emerald", "#10B981")
    C_RED = THEME["accent_red"]
    C_RED_DARK = THEME.get("red_dark", "#DC2626")
    C_AMBER = THEME["accent_yellow"]

    _sync_imported_color_constants()
    return valid_id


THEME_SETTINGS = {
    "fg_color": THEME["bg_dark"],
    "card_color": THEME["bg_card"],
    "card_hover": THEME["bg_card_hover"],
    "border_color": THEME["border"],
    "accent_orange": THEME["accent_orange"],
    "accent_gold": THEME.get("accent_gold", "#D4B886"),
    "accent_olive": THEME["accent_olive"],
    "text_main": THEME["text_main"],
    "text_muted": THEME["text_muted"],
}


# Paleta semantica centralizada
C_WHITE = "#FFFFFF"  # Blanco puro
C_TEXT = "#F8FAFC"  # Texto principal (alto contraste)
C_TEXT_SOFT = "#E2E8F0"  # Texto suave
C_TEXT_MUTED = "#CBD5E1"  # Texto secundario
C_TEXT_DIM = "#94A3B8"  # Texto terciario / placeholders
C_BLUE = "#38BDF8"  # Azul cian tactico
C_BORDER = "#2D3545"  # Borde estructural
C_BORDER_SOFT = "#262C38"  # Borde suave de paneles
C_BG_DEEP = "#0D1016"  # Fondo profundo
C_BG_DARKEST = "#090B0E"  # Fondo mas oscuro
C_BG_INSET = "#0B0D11"  # Fondo de areas empotradas
C_BG_PANEL = "#12161F"  # Fondo de panel
C_BG_PANEL_ALT = "#121620"  # Fondo de panel alternativo
C_BG_PANEL_ALT2 = "#121722"  # Fondo de panel alternativo 2
C_SLATE_800 = "#1E293B"  # Pizarra oscura
C_SLATE_700 = "#334155"  # Pizarra media
C_BG_ROW = "#1A202C"  # Fondo de fila
C_BG_ROW_ALT = "#222938"  # Fondo de fila alternativa
C_BORDER_ALT = "#2D3748"  # Borde alternativo
C_GREEN_LIGHT = "#4ADE80"  # Verde claro (completado)
C_GREEN = "#22C55E"  # Verde esmeralda brillante
C_EMERALD = "#10B981"  # Esmeralda
C_RED = "#EF4444"  # Rojo de alerta
C_RED_DARK = "#DC2626"  # Rojo oscuro
C_AMBER = "#F59E0B"  # Ambar

# Aplicar skin guardada al cargar el módulo (por defecto EFT Hideout)
apply_ui_skin(get_user_preference("ui_skin", "tarkov_classic"))
