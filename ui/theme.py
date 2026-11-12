"""
TarkovScope - Sistema Tipográfico Profesional (Segoe UI / Consolas) y Tema de Alto Contraste
Garantiza fuentes nítidas nativas de Windows (evitando el fallback borroso de Tkinter)
con jerarquía tipográfica clara y alto contraste.
"""
import sys
import functools
import customtkinter as ctk
from core.config import THEME

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
    """Retorna una fuente CTkFont con familia nativa Segoe UI o Consolas para máxima nitidez (en caché O(1))."""
    fam = FONT_MONO_FAMILY if mono else FONT_FAMILY
    return ctk.CTkFont(family=fam, size=size, weight=weight)


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


# Paleta semantica centralizada (valores identicos a los literales originales)
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
