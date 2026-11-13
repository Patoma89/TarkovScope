"""
TarkovScope - Visor Táctico Interactivo de Mapas en Alta Resolución (Modal Zoom, Pan & Alfileres de Colores)
Permite:
- Zoom con la rueda del ratón (0.45x a 3.5x) y arrastrar (Pan) con clic izquierdo.
- Modo interactivo "Elegir Punto y Poner Nota" (o Clic Derecho directo) para colocar
  múltiples alfileres con cabezas esféricas 3D que cambian de color automáticamente.
- Selector visual con círculos 3D reales renderizados por PIL del color exacto de cada opción.
"""
import re
import threading
import tkinter as tk
from typing import Optional, Dict, Any, Callable
import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from core.image_cache import (
    load_boss_spawn_map_image,
    render_map_with_user_markers
)
from ui.theme import C_AMBER, C_BG_DEEP, C_BG_INSET, C_BG_PANEL, C_BORDER, C_EMERALD, C_RED, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE

MARKER_CATEGORIES = [
    ("Alfiler Rojo Carmesí — Peligro / Boss / Francotirador", C_RED),
    ("Alfiler Azul Eléctrico — Objetivo de Misión (Quest)", "#3B82F6"),
    ("Alfiler Verde Esmeralda — Botín / Alijo / Mochila", C_EMERALD),
    ("Alfiler Amarillo Ámbar — Puerta con Llave / Extracción", C_AMBER),
    ("Alfiler Violeta Intenso — Punto Estratégico / Ruta", "#A855F7"),
    ("Alfiler Cian Brillante — Nota Personal / Escondite", "#06B6D4"),
    ("Alfiler Rosa Magenta — Punto de Encuentro / Spawn", "#EC4899"),
    ("Alfiler Verde Lima — Suministros / Cajas Tácticas", "#84CC16"),
]

_PIN_CIRCLE_CACHE: Dict[str, ctk.CTkImage] = {}


def get_pinhead_circle_ctk_image(hex_color: str, size: int = 18) -> ctk.CTkImage:
    """
    Genera un círculo 3D anti-aliased (supersampling 2x) del color exacto solicitado
    para representar prolijamente la cabeza del alfiler en la UI sin depender de emojis de Windows.
    """
    cache_key = f"{hex_color.upper()}_{size}"
    if cache_key in _PIN_CIRCLE_CACHE:
        return _PIN_CIRCLE_CACHE[cache_key]

    clean_hex = hex_color.lstrip("#")
    try:
        rgb = tuple(int(clean_hex[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        rgb = (239, 68, 68)

    dark_rgb = (max(0, int(rgb[0] * 0.55)), max(0, int(rgb[1] * 0.55)), max(0, int(rgb[2] * 0.55)))
    light_rgb = (
        min(255, int(rgb[0] + (255 - rgb[0]) * 0.45)),
        min(255, int(rgb[1] + (255 - rgb[1]) * 0.45)),
        min(255, int(rgb[2] + (255 - rgb[2]) * 0.45)),
    )

    ss = size * 2
    img = Image.new("RGBA", (ss, ss), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Borde exterior + base sombreada
    draw.ellipse([2, 2, ss - 3, ss - 3], fill=(dark_rgb[0], dark_rgb[1], dark_rgb[2], 255), outline=(15, 23, 42, 255), width=2)
    # Esfera principal del color exacto
    draw.ellipse([4, 4, ss - 5, ss - 5], fill=(rgb[0], rgb[1], rgb[2], 255))
    # Volumen interior más claro
    pad_in = max(6, int(ss * 0.22))
    draw.ellipse([pad_in - 2, pad_in - 2, ss - pad_in - 2, ss - pad_in - 2], fill=(light_rgb[0], light_rgb[1], light_rgb[2], 210))
    # Brillo especular blanco arriba a la izquierda
    sp = max(3, int(ss * 0.14))
    sx = int(ss * 0.34)
    sy = int(ss * 0.32)
    draw.ellipse([sx - sp, sy - sp, sx + sp, sy + sp], fill=(255, 255, 255, 235))

    smooth = img.resize((size, size), Image.Resampling.LANCZOS)
    ctk_img = ctk.CTkImage(light_image=smooth, dark_image=smooth, size=(size, size))
    _PIN_CIRCLE_CACHE[cache_key] = ctk_img
    return ctk_img


def clean_category_label(cat_str: str) -> str:
    """Elimina cualquier emoji antiguo al inicio del nombre de categoría."""
    return re.sub(r"^[^\wÁÉÍÓÚáéíóúÑñ]+\s*", "", cat_str or "").strip()


class AddMarkerDialog(ctk.CTkToplevel):
    """Modal táctico con selector de círculos 3D reales del color exacto de cada alfiler."""

    def __init__(
        self,
        parent,
        map_name: str,
        x_pct: float,
        y_pct: float,
        on_saved: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.title(f"Colocar Alfiler en {map_name}")
        self.geometry("540x535")
        self.resizable(False, False)
        self.configure(fg_color="#0B0E14")
        self.transient(parent)
        self.grab_set()

        self.map_name = map_name
        self.x_pct = max(0.01, min(0.99, x_pct))
        self.y_pct = max(0.01, min(0.99, y_pct))
        self.on_saved = on_saved

        existing_count = len(get_datastore().get_markers(map_name))
        default_idx = existing_count % len(MARKER_CATEGORIES)
        self.selected_cat = MARKER_CATEGORIES[default_idx][0]
        self.selected_color = MARKER_CATEGORIES[default_idx][1]
        self.option_buttons: Dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)

        # Cabecera con el círculo de color real del alfiler actual
        hdr_row = ctk.CTkFrame(self, fg_color="transparent")
        hdr_row.grid(row=0, column=0, padx=20, pady=(16, 2), sticky="ew")

        self.header_icon_lbl = ctk.CTkLabel(
            hdr_row,
            text="",
            image=get_pinhead_circle_ctk_image(self.selected_color, 22)
        )
        self.header_icon_lbl.pack(side="left", padx=(0, 8))

        self.header_lbl = ctk.CTkLabel(
            hdr_row,
            text=f"COLOCAR ALFILER #{existing_count + 1} EN {map_name.upper()}",
            font=ui_font(size=15, weight="bold"),
            text_color=self.selected_color
        )
        self.header_lbl.pack(side="left")

        ctk.CTkLabel(
            self,
            text=f"Coordenada de la aguja: X={self.x_pct * 100:.1f}%  •  Y={self.y_pct * 100:.1f}%",
            font=ui_font(size=12, weight="bold"),
            text_color=THEME["accent_green"]
        ).grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        ctk.CTkLabel(
            self,
            text="Texto de la Nota o Recordatorio:",
            font=ui_font(size=13, weight="bold"),
            text_color=C_TEXT
        ).grid(row=2, column=0, padx=20, pady=(0, 4), sticky="w")

        self.note_entry = ctk.CTkEntry(
            self,
            placeholder_text="Ej: Mochila oculta / Escondite Jaeger / Llave 206 / Francotirador...",
            height=36,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(size=13)
        )
        self.note_entry.grid(row=3, column=0, padx=20, pady=(0, 12), sticky="ew")
        self.note_entry.bind("<Return>", lambda e: self._save())

        ctk.CTkLabel(
            self,
            text="Color de la Cabeza del Alfiler (Círculos del color exacto):",
            font=ui_font(size=13, weight="bold"),
            text_color=C_TEXT
        ).grid(row=4, column=0, padx=20, pady=(0, 4), sticky="w")

        # Lista prolija de los 8 colores con círculos reales renderizados por PIL
        list_box = ctk.CTkFrame(
            self,
            fg_color="#11151E",
            corner_radius=8,
            border_width=1,
            border_color="#283040"
        )
        list_box.grid(row=5, column=0, padx=20, pady=(0, 14), sticky="ew")
        list_box.grid_columnconfigure(0, weight=1)

        for idx, (cat_label, hex_col) in enumerate(MARKER_CATEGORIES):
            is_sel = (cat_label == self.selected_cat)
            circle_img = get_pinhead_circle_ctk_image(hex_col, 18)

            btn = ctk.CTkButton(
                list_box,
                text=f"  {cat_label}",
                image=circle_img,
                compound="left",
                anchor="w",
                height=32,
                corner_radius=5,
                border_width=1,
                border_color=hex_col if is_sel else "#11151E",
                fg_color="#1E2636" if is_sel else "transparent",
                hover_color="#1A2130",
                text_color=C_WHITE if is_sel else C_TEXT_MUTED,
                font=ui_font(size=12, weight="bold" if is_sel else "normal"),
                command=lambda c_lbl=cat_label, c_hex=hex_col: self._select_category(c_lbl, c_hex)
            )
            btn.grid(row=idx, column=0, padx=6, pady=2, sticky="ew")
            self.option_buttons[cat_label] = btn

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=6, column=0, padx=20, pady=(0, 14), sticky="e")

        ctk.CTkButton(
            btn_row,
            text="Cancelar",
            width=105,
            height=34,
            fg_color="#161B24",
            hover_color="#262F3F",
            text_color=C_TEXT_MUTED,
            font=ui_font(size=12, weight="bold"),
            command=self.destroy
        ).pack(side="left", padx=(0, 8))

        self.save_btn = ctk.CTkButton(
            btn_row,
            text="Clavar Alfiler",
            image=get_pinhead_circle_ctk_image(self.selected_color, 16),
            compound="left",
            width=175,
            height=34,
            fg_color=self.selected_color,
            hover_color=THEME["accent_orange"],
            text_color=C_WHITE,
            font=ui_font(size=13, weight="bold"),
            command=self._save
        )
        self.save_btn.pack(side="left")

        self.after(80, lambda: self.note_entry.focus_set())

    def _select_category(self, cat_label: str, hex_col: str):
        self.selected_cat = cat_label
        self.selected_color = hex_col
        self.header_icon_lbl.configure(image=get_pinhead_circle_ctk_image(hex_col, 22))
        self.header_lbl.configure(text_color=hex_col)
        self.save_btn.configure(
            fg_color=hex_col,
            image=get_pinhead_circle_ctk_image(hex_col, 16)
        )
        for lbl, btn in self.option_buttons.items():
            is_sel = (lbl == cat_label)
            btn.configure(
                fg_color="#1E2636" if is_sel else "transparent",
                border_color=hex_col if is_sel else "#11151E",
                text_color=C_WHITE if is_sel else C_TEXT_MUTED,
                font=ui_font(size=12, weight="bold" if is_sel else "normal")
            )

    def _save(self):
        txt = self.note_entry.get().strip()
        if not txt:
            txt = self.selected_cat.split("—")[-1].strip()
        get_datastore().add_marker(
            map_key=self.map_name,
            x_pct=self.x_pct,
            y_pct=self.y_pct,
            title=txt,
            category=self.selected_cat,
            color=self.selected_color
        )
        if self.on_saved:
            self.on_saved()
        self.destroy()


class MapViewerModal(ctk.CTkToplevel):
    """Ventana modal interactiva con Zoom, Pan y colocación de múltiples alfileres de colores."""

    def __init__(
        self,
        parent,
        title: str,
        pil_image: Image.Image,
        map_name_for_markers: Optional[str] = None,
        on_markers_changed: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.title(f"TarkovScope — {title}")
        self.geometry("1220x820")
        self.minsize(880, 580)
        self.configure(fg_color=THEME["bg_dark"])

        self._orig_img = pil_image
        self._map_name = map_name_for_markers
        self._on_markers_changed = on_markers_changed
        self._placing_marker_mode = False
        self._moving_marker_id: Optional[int] = None
        self._zoom = 1.0
        self._min_zoom = 0.45
        self._max_zoom = 3.5
        self._tk_img: Optional[ImageTk.PhotoImage] = None
        self._img_id: Optional[int] = None
        self._zoom_job: Optional[str] = None
        self._layer_render_token: int = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2 if self._map_name else 1, weight=1)

        top_bar = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            height=54,
            corner_radius=0,
            border_width=1,
            border_color=THEME["border"]
        )
        top_bar.grid(row=0, column=0, sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_bar,
            text=f"🗺️  {title}",
            font=ui_font(size=16, weight="bold"),
            text_color=THEME["accent_orange"]
        ).grid(row=0, column=0, padx=18, pady=12, sticky="w")

        hint_txt = "🖱️ Rueda: Zoom  |  Arrastrar: Mover"
        if self._map_name:
            hint_txt += "  |  📌 Clic Derecho: Clavar Alfiler"
        self.hint_lbl = ctk.CTkLabel(
            top_bar,
            text=hint_txt,
            font=ui_font(size=12, weight="bold"),
            text_color=THEME["accent_yellow"] if self._map_name else THEME["text_muted"]
        )
        self.hint_lbl.grid(row=0, column=1, padx=10, pady=12)

        controls = ctk.CTkFrame(top_bar, fg_color="transparent")
        controls.grid(row=0, column=2, padx=14, pady=8, sticky="e")

        if self._map_name:
            self.btn_place_mode = ctk.CTkButton(
                controls,
                text="📌 Clavar Alfiler",
                width=140,
                height=32,
                fg_color=THEME["accent_orange"],
                hover_color="#C2591A",
                font=ui_font(size=12, weight="bold"),
                command=self._toggle_place_mode
            )
            self.btn_place_mode.pack(side="left", padx=(0, 8))

        self.zoom_lbl = ctk.CTkLabel(
            controls,
            text="100%",
            width=54,
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["text_main"]
        )
        self.zoom_lbl.pack(side="left", padx=4)

        ctk.CTkButton(
            controls,
            text="➖",
            width=34,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            command=lambda: self._step_zoom(0.8)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            controls,
            text="➕",
            width=34,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            command=lambda: self._step_zoom(1.25)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            controls,
            text="🔄 Ajustar",
            width=82,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            command=self._fit_to_window
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            controls,
            text="✕ Cerrar",
            width=82,
            height=32,
            fg_color=THEME["accent_red"],
            hover_color="#B91C1C",
            font=ui_font(size=13, weight="bold"),
            command=self.destroy
        ).pack(side="left", padx=(4, 0))

        # Barra de Capas Interactivas (si es un mapa táctico con nombre)
        if self._map_name:
            layers_bar = ctk.CTkFrame(self, fg_color="#10141D", height=38, corner_radius=0, border_width=1, border_color="#1E2532")
            layers_bar.grid(row=1, column=0, sticky="ew")

            ctk.CTkLabel(layers_bar, text="CAPAS:", font=ui_font(11, "bold"), text_color=C_TEXT_DIM).pack(side="left", padx=(18, 10))

            self.show_pins = ctk.BooleanVar(value=True)
            self.show_pmc = ctk.BooleanVar(value=True)
            self.show_scav = ctk.BooleanVar(value=True)
            self.show_boss = ctk.BooleanVar(value=True)
            self.show_keys = ctk.BooleanVar(value=True)
            self.show_loot = ctk.BooleanVar(value=True)

            ctk.CTkCheckBox(layers_bar, text="Alfileres", variable=self.show_pins, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=THEME["accent_orange"], width=88, height=24).pack(side="left", padx=4)
            ctk.CTkCheckBox(layers_bar, text="Extracciones PMC", variable=self.show_pmc, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=C_EMERALD, width=138, height=24).pack(side="left", padx=4)
            ctk.CTkCheckBox(layers_bar, text="Extracciones Scav", variable=self.show_scav, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=C_AMBER, width=138, height=24).pack(side="left", padx=4)
            ctk.CTkCheckBox(layers_bar, text="Spawns Boss", variable=self.show_boss, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=C_RED, width=110, height=24).pack(side="left", padx=4)
            ctk.CTkCheckBox(layers_bar, text="🔑 Llaves / Marked", variable=self.show_keys, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color="#A855F7", width=138, height=24).pack(side="left", padx=4)
            ctk.CTkCheckBox(layers_bar, text="💎 Cajas Fuertes / Loot", variable=self.show_loot, command=self._refresh_map_layers, font=ui_font(12, "bold"), text_color=C_TEXT, fg_color="#06B6D4", width=155, height=24).pack(side="left", padx=4)

            self.btn_move_marker = ctk.CTkButton(
                layers_bar,
                text="📍 Mover Alfiler",
                height=26,
                fg_color=C_SLATE_800,
                hover_color=C_SLATE_700,
                font=ui_font(11, "bold"),
                command=self._prompt_move_marker
            )
            self.btn_move_marker.pack(side="right", padx=16)

        self.canvas = tk.Canvas(
            self,
            bg=C_BG_INSET,
            highlightthickness=0,
            cursor="fleur"
        )
        self.canvas.grid(row=2 if self._map_name else 1, column=0, sticky="nsew")

        self.canvas.bind("<ButtonPress-1>", self._on_left_press)
        self.canvas.bind("<B1-Motion>", self._on_pan_move)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        if self._map_name:
            self.canvas.bind("<Button-3>", self._on_place_marker_at_event)
        self.bind("<Escape>", lambda e: self.destroy())

        self.after(60, self._fit_to_window)
        self.after(100, self._bring_to_front)

    def _bring_to_front(self):
        if not self.winfo_exists():
            return
        self.lift()
        self.focus_force()

    def _toggle_place_mode(self):
        self._placing_marker_mode = not self._placing_marker_mode
        if self._placing_marker_mode:
            self.canvas.configure(cursor="tcross")
            self.btn_place_mode.configure(
                text="🎯 Hacé Clic en el Mapa...",
                fg_color=THEME["accent_green"],
                text_color="#0F1115"
            )
            self.hint_lbl.configure(
                text="🎯 MODO ACTIVO: Hacé Clic Izquierdo en el punto exacto donde quieras clavar el alfiler",
                text_color=THEME["accent_green"]
            )
        else:
            self.canvas.configure(cursor="fleur")
            self.btn_place_mode.configure(
                text="📌 Elegir Punto en Mapa",
                fg_color=THEME["accent_orange"],
                text_color=C_WHITE
            )
            self.hint_lbl.configure(
                text="🖱️ Rueda: Zoom  |  Arrastrar: Mover  |  📌 Clic Derecho: Clavar Alfiler",
                text_color=THEME["accent_yellow"]
            )

    def _refresh_map_layers(self):
        if not self._map_name:
            return
        self._layer_render_token += 1
        token = self._layer_render_token
        map_name = self._map_name
        markers = get_datastore().get_markers(map_name)
        s_pins = self.show_pins.get()
        s_pmc = self.show_pmc.get()
        s_scav = self.show_scav.get()
        s_boss = self.show_boss.get()
        s_keys = self.show_keys.get()
        s_loot = self.show_loot.get()

        def worker():
            rendered = render_map_with_user_markers(
                map_name,
                markers,
                high_res=True,
                show_pins=s_pins,
                show_pmc=s_pmc,
                show_scav=s_scav,
                show_boss=s_boss,
                show_keys=s_keys,
                show_loot=s_loot
            )

            def apply_img():
                if not self.winfo_exists() or token != self._layer_render_token:
                    return
                self._orig_img = rendered
                self._render_scaled_image(center=False)

            self.after(0, apply_img)

        threading.Thread(target=worker, daemon=True).start()

    def _prompt_move_marker(self):
        if not self._map_name:
            return
        markers = get_datastore().get_markers(self._map_name)
        if not markers:
            self.hint_lbl.configure(text="⚠️ No tienes alfileres guardados en este mapa para mover.", text_color=C_RED)
            return
        if len(markers) == 1:
            self._start_moving_marker(markers[0])
            return

        dlg = ctk.CTkToplevel(self)
        dlg.title("Seleccionar Alfiler para Mover")
        dlg.geometry("440x360")
        dlg.transient(self)
        dlg.grab_set()
        dlg.configure(fg_color=C_BG_DEEP)

        ctk.CTkLabel(dlg, text="¿Qué alfiler quieres reubicar en el mapa?", font=ui_font(14, "bold"), text_color=C_TEXT).pack(padx=16, pady=(16, 8))
        scroll = ctk.CTkScrollableFrame(dlg, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=14, pady=8)

        for idx, m in enumerate(markers, start=1):
            btn = ctk.CTkButton(
                scroll,
                text=f"Alfiler #{idx} — {m.get('title', 'Nota')} ({clean_category_label(m.get('category', 'Nota'))})",
                font=ui_font(12, "bold"),
                fg_color="#1E2534",
                hover_color=THEME["accent_gold"],
                text_color=C_WHITE,
                anchor="w",
                height=34,
                command=lambda mk=m: (dlg.destroy(), self._start_moving_marker(mk))
            )
            btn.pack(fill="x", pady=3)

    def _start_moving_marker(self, marker: Dict[str, Any]):
        self._moving_marker_id = marker["id"]
        self.canvas.configure(cursor="tcross")
        if hasattr(self, "btn_move_marker"):
            self.btn_move_marker.configure(
                text="📍 Hacé Clic en Nuevo Punto...",
                fg_color=THEME["accent_green"],
                text_color="#0F1115"
            )
        self.hint_lbl.configure(
            text=f"🎯 REUBICACIÓN: Hacé Clic en la nueva posición para '{marker.get('title', 'Alfiler')}'",
            text_color=THEME["accent_green"]
        )

    def _on_finish_move_marker(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        iw, ih = self._orig_img.size
        nw = max(1, iw * self._zoom)
        nh = max(1, ih * self._zoom)
        x_pct = max(0.01, min(0.99, cx / nw))
        y_pct = max(0.01, min(0.99, cy / nh))

        get_datastore().update_marker_pos(self._moving_marker_id, x_pct, y_pct)
        self._moving_marker_id = None
        self.canvas.configure(cursor="fleur")
        if hasattr(self, "btn_move_marker"):
            self.btn_move_marker.configure(
                text="📍 Mover Alfiler",
                fg_color=C_SLATE_800,
                text_color=C_WHITE
            )
        self.hint_lbl.configure(
            text="✓ Alfiler reubicado con éxito. 🖱️ Rueda: Zoom | Arrastrar: Mover",
            text_color=THEME["accent_green"]
        )
        self._refresh_map_layers()
        if self._on_markers_changed:
            self._on_markers_changed()

    def _on_left_press(self, event):
        if self._moving_marker_id is not None and self._map_name:
            self._on_finish_move_marker(event)
            return
        if self._placing_marker_mode and self._map_name:
            self._on_place_marker_at_event(event)
            return
        self.canvas.scan_mark(event.x, event.y)

    def _on_place_marker_at_event(self, event):
        if not self._map_name:
            return
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        iw, ih = self._orig_img.size
        nw = max(1, iw * self._zoom)
        nh = max(1, ih * self._zoom)
        x_pct = max(0.01, min(0.99, cx / nw))
        y_pct = max(0.01, min(0.99, cy / nh))

        def _after_save():
            self._refresh_map_layers()
            if self._placing_marker_mode:
                self._toggle_place_mode()
            if self._on_markers_changed:
                self._on_markers_changed()

        AddMarkerDialog(self, self._map_name, x_pct, y_pct, on_saved=_after_save)

    def _fit_to_window(self):
        if not self.winfo_exists():
            return
        cw = max(800, self.canvas.winfo_width())
        ch = max(520, self.canvas.winfo_height())
        iw, ih = self._orig_img.size
        scale = min((cw - 40) / max(1, iw), (ch - 40) / max(1, ih))
        self._zoom = max(self._min_zoom, min(self._max_zoom, scale))
        self._render_scaled_image(center=True)

    def _step_zoom(self, factor: float, debounce: bool = False):
        new_z = max(self._min_zoom, min(self._max_zoom, self._zoom * factor))
        if abs(new_z - self._zoom) < 0.01:
            return
        self._zoom = new_z
        self.zoom_lbl.configure(text=f"{int(self._zoom * 100)}%")
        if self._zoom_job is not None:
            try:
                self.after_cancel(self._zoom_job)
            except Exception:
                pass
            self._zoom_job = None

        if debounce:
            self._zoom_job = self.after(25, self._flush_debounced_zoom)
        else:
            self._render_scaled_image(center=False)

    def _flush_debounced_zoom(self):
        self._zoom_job = None
        self._render_scaled_image(center=False)

    def _on_mouse_wheel(self, event):
        factor = 1.18 if event.delta > 0 else 0.85
        self._step_zoom(factor, debounce=True)

    def _on_pan_move(self, event):
        if self._placing_marker_mode:
            return
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _render_scaled_image(self, center: bool = False):
        if not self.winfo_exists():
            return
        iw, ih = self._orig_img.size
        nw = max(100, int(iw * self._zoom))
        nh = max(100, int(ih * self._zoom))

        resized = self._orig_img.resize((nw, nh), Image.Resampling.BILINEAR)
        self._tk_img = ImageTk.PhotoImage(resized)

        if self._img_id is None:
            self._img_id = self.canvas.create_image(0, 0, image=self._tk_img, anchor="nw")
        else:
            self.canvas.itemconfig(self._img_id, image=self._tk_img)
            self.canvas.coords(self._img_id, 0, 0)

        self.canvas.config(scrollregion=(0, 0, nw, nh))
        self.zoom_lbl.configure(text=f"{int(self._zoom * 100)}%")


def open_map_viewer_modal(
    parent,
    map_name: str,
    on_markers_changed: Optional[Callable[[], None]] = None
):
    """Abre el visor interactivo en alta resolución con los alfileres del usuario."""
    markers = get_datastore().get_markers(map_name)
    pil_img = render_map_with_user_markers(
        map_name,
        markers,
        high_res=True,
        show_pins=True,
        show_pmc=True,
        show_scav=True,
        show_boss=True
    )
    MapViewerModal(
        parent,
        f"Plano Táctico HD: {map_name}",
        pil_img,
        map_name_for_markers=map_name,
        on_markers_changed=on_markers_changed
    )


def open_boss_map_viewer_modal(parent, boss: Dict[str, Any], map_name: str):
    """Abre el visor interactivo en alta resolución para los spawns de un Boss en un mapa."""
    pil_img = load_boss_spawn_map_image(boss, map_name, high_res=True)
    MapViewerModal(parent, f"Spawns de {boss.get('name', '')} en {map_name}", pil_img)
