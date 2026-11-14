"""
TarkovScope - Armador Interactivo Pro de Builds (Gunsmith Studio)
Simulador dinámico de banco de trabajo militar estilo Escape from Tarkov.
Permite seleccionar armas, ver cómo cambia el plano esquemático del arma en tiempo real
al instalar cada silenciador, mira óptica, culata, empuñadura y cargador de tambor.
Ofrece selección rápida de ranuras (Quick Slots), catálogo visual con equipamiento en 1-clic,
presets meta directos y exportación a JSON (EFT/SPT), lista de compra y Base64.
"""
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, Optional, List

from core.config import THEME
from core.weapon_modding_data import (
    MODDABLE_WEAPONS,
    ATTACHMENTS_CATALOG,
    MOD_SLOTS,
    get_available_attachments_for_slot,
    get_attachment_image_key
)
from core.weapon_modding_engine import (
    calculate_build_stats,
    export_build_to_json,
    export_shopping_list_text,
    export_build_to_base64,
    import_build_from_base64,
    import_build_from_json
)
from ui.theme import (
    C_AMBER, C_BG_DARKEST, C_BG_DEEP, C_BG_INSET, C_BG_PANEL, C_BG_PANEL_ALT,
    C_BG_PANEL_ALT2, C_BORDER, C_BORDER_ALT, C_EMERALD, C_GREEN, C_GREEN_LIGHT,
    C_RED, C_RED_DARK, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED,
    C_TEXT_SOFT, C_WHITE, ui_font
)
from ui.image_utils import get_dynamic_weapon_composite_ctk_image, get_weapon_or_part_ctk_image


SLOT_ICONS = {
    "barrel": "🔩",
    "muzzle": "🔇",
    "handguard": "🛡️",
    "foregrip": "✊",
    "pistol_grip": "🫲",
    "stock": "🪖",
    "optic": "🎯",
    "magazine": "🔋",
    "tactical": "🔦",
}

WEAPON_CATEGORY_ORDER = [
    "Rifles de Asalto",
    "Carabinas",
    "Subfusiles (SMG)",
    "Rifles de Tirador (DMR)",
    "Francotirador (Bolt)",
    "Escopetas",
    "Ametralladoras (LMG)",
    "Pistolas",
]


def get_ordered_weapon_categories() -> List[str]:
    """Devuelve las categorías de armas ordenadas incluyendo 'Todas' al inicio."""
    present = {w.get("category", "Otros") for w in MODDABLE_WEAPONS.values()}
    ordered = [cat for cat in WEAPON_CATEGORY_ORDER if cat in present]
    extras = sorted(cat for cat in present if cat not in ordered)
    return ["Todas"] + ordered + extras


class WeaponPickerModal(ctk.CTkToplevel):
    """Selector moderno de armas con filtros por categoría, búsqueda instantánea y tarjetas tácticas."""

    def __init__(
        self,
        parent,
        current_weapon_id: str,
        initial_category: str = "Todas",
        on_select=None,
    ):
        super().__init__(parent)
        self.title("TarkovScope — Selector de Arma")
        self.geometry("920x640")
        self.minsize(740, 500)
        self.configure(fg_color=C_BG_DARKEST)
        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self._current_weapon_id = current_weapon_id
        self._active_category = initial_category or "Todas"
        self._on_select = on_select
        self._search_after_id: Optional[str] = None
        self._render_token = 0
        self._cat_buttons: Dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_category_pills()
        self._build_search_bar()
        self._build_results_grid()

        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(60, self._focus_search)
        self._schedule_render_weapons()

    def _focus_search(self):
        if self.winfo_exists():
            self.entry_search.focus_set()

    def _build_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=C_BG_PANEL,
            corner_radius=0,
            border_width=1,
            border_color=C_BORDER,
        )
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(hdr, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w", padx=16, pady=10)

        ctk.CTkLabel(
            title_box,
            text="🔫 SELECTOR DE ARMA — GUNSMITH STUDIO",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"],
        ).pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            title_box,
            text="",
            font=ui_font(12),
            text_color=C_TEXT_MUTED,
        )
        self.lbl_count.pack(side="left", padx=(12, 0))

        ctk.CTkButton(
            hdr,
            text="✕ Cerrar",
            width=84,
            height=28,
            fg_color=C_SLATE_800,
            hover_color=C_RED_DARK,
            text_color=C_TEXT_SOFT,
            font=ui_font(11, "bold"),
            command=self.destroy,
        ).grid(row=0, column=1, padx=14, pady=10)

    def _build_category_pills(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_PANEL_ALT,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        bar.grid(row=1, column=0, sticky="ew", padx=14, pady=(10, 6))

        counts: Dict[str, int] = {}
        for w in MODDABLE_WEAPONS.values():
            cat = w.get("category", "Otros")
            counts[cat] = counts.get(cat, 0) + 1
        counts["Todas"] = len(MODDABLE_WEAPONS)

        cats = get_ordered_weapon_categories()
        cols_per_row = 5
        for c in range(cols_per_row):
            bar.grid_columnconfigure(c, weight=1, uniform="catcol")

        for idx, cat in enumerate(cats):
            cnt = counts.get(cat, 0)
            r = idx // cols_per_row
            c = idx % cols_per_row
            btn = ctk.CTkButton(
                bar,
                text=f"{cat} ({cnt})",
                height=32,
                corner_radius=6,
                font=ui_font(11, "bold"),
                command=lambda cat_name=cat: self._select_category(cat_name),
            )
            btn.grid(row=r, column=c, sticky="ew", padx=4, pady=4)
            self._cat_buttons[cat] = btn

        self._update_category_pill_styles()

    def _update_category_pill_styles(self):
        for cat, btn in self._cat_buttons.items():
            is_active = cat == self._active_category
            btn.configure(
                fg_color=THEME["accent_gold"] if is_active else C_BG_DEEP,
                hover_color=THEME["accent_gold"] if is_active else C_SLATE_700,
                text_color=C_BG_DARKEST if is_active else C_TEXT_SOFT,
                border_width=1,
                border_color=THEME["accent_gold"] if is_active else C_BORDER,
            )

    def _select_category(self, category: str):
        self._active_category = category
        self._update_category_pill_styles()
        self._schedule_render_weapons()

    def _build_search_bar(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=14, pady=(2, 6))
        row.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(
            row,
            height=36,
            placeholder_text="🔍 Buscar arma por nombre o calibre (ej: M4A1, 7.62x39, MP5, .338, AK-74)...",
            font=ui_font(13),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
            text_color=C_WHITE,
        )
        self.entry_search.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_search.bind("<KeyRelease>", self._on_search_key)

        ctk.CTkButton(
            row,
            text="Limpiar",
            width=76,
            height=36,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_TEXT_SOFT,
            font=ui_font(11, "bold"),
            command=self._clear_search,
        ).grid(row=0, column=1)

    def _on_search_key(self, _event=None):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(110, self._schedule_render_weapons)

    def _clear_search(self):
        self.entry_search.delete(0, "end")
        self._schedule_render_weapons()

    def _build_results_grid(self):
        self.scroll_weapons = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        self.scroll_weapons.grid(row=3, column=0, sticky="nsew", padx=14, pady=(0, 14))
        self.scroll_weapons.grid_columnconfigure(0, weight=1, uniform="wcol")
        self.scroll_weapons.grid_columnconfigure(1, weight=1, uniform="wcol")

    def _get_filtered_weapons(self) -> List[Dict[str, Any]]:
        query = self.entry_search.get().strip().lower()
        results: List[Dict[str, Any]] = []
        for w in MODDABLE_WEAPONS.values():
            if self._active_category != "Todas" and w.get("category") != self._active_category:
                continue
            if query:
                haystack = f"{w.get('name', '')} {w.get('caliber', '')} {w.get('category', '')}".lower()
                if query not in haystack:
                    continue
            results.append(w)
        return results

    def _schedule_render_weapons(self):
        self._render_token += 1
        token = self._render_token

        for child in self.scroll_weapons.winfo_children():
            child.destroy()

        weapons = self._get_filtered_weapons()
        self.lbl_count.configure(text=f"({len(weapons)} armas)")

        if not weapons:
            empty = ctk.CTkLabel(
                self.scroll_weapons,
                text="No se encontraron armas con ese filtro o búsqueda.",
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
            )
            empty.grid(row=0, column=0, columnspan=2, pady=40)
            return

        self._render_weapon_batch(weapons, 0, token)

    def _render_weapon_batch(self, weapons: List[Dict[str, Any]], start_idx: int, token: int):
        if not self.winfo_exists() or token != self._render_token:
            return

        batch_size = 16
        end_idx = min(start_idx + batch_size, len(weapons))

        for idx in range(start_idx, end_idx):
            w = weapons[idx]
            row = idx // 2
            col = idx % 2
            self._create_weapon_card(w, row, col)

        if end_idx < len(weapons):
            self.after(4, lambda: self._render_weapon_batch(weapons, end_idx, token))

    def _create_weapon_card(self, w: Dict[str, Any], row: int, col: int):
        w_id = w["id"]
        is_current = w_id == self._current_weapon_id
        card_fg = C_BG_PANEL if is_current else C_BG_DEEP
        border_c = THEME["accent_gold"] if is_current else C_BORDER

        card = ctk.CTkFrame(
            self.scroll_weapons,
            fg_color=card_fg,
            corner_radius=8,
            border_width=2 if is_current else 1,
            border_color=border_c,
        )
        card.grid(row=row, column=col, sticky="ew", padx=6, pady=5)
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(9, 2))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text=w["name"],
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"] if is_current else C_WHITE,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top,
            text=w.get("caliber", ""),
            font=ui_font(11, "bold"),
            text_color=C_EMERALD,
            anchor="e",
        ).grid(row=0, column=1, sticky="e", padx=(8, 0))

        meta = (
            f"{w.get('category', '')}  •  "
            f"RPM: {w.get('fire_rate', 0)}  •  "
            f"Ergo: {w.get('base_ergo', 0)}  •  "
            f"V.Rec: {w.get('base_recoil_v', 0)}"
        )
        ctk.CTkLabel(
            card,
            text=meta,
            font=ui_font(11),
            text_color=C_TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 9))

        select_btn = ctk.CTkButton(
            card,
            text="✓ Activa" if is_current else "Seleccionar",
            width=92,
            height=28,
            fg_color=THEME["accent_gold"] if is_current else C_SLATE_800,
            hover_color=THEME["accent_gold"],
            text_color=C_BG_DARKEST if is_current else C_WHITE,
            font=ui_font(11, "bold"),
            command=lambda wid=w_id: self._pick(wid),
        )
        select_btn.grid(row=0, column=1, rowspan=2, padx=(4, 12), pady=8)

        for widget in (card, top):
            widget.bind("<Button-1>", lambda _e, wid=w_id: self._pick(wid))

    def _pick(self, weapon_id: str):
        if self._on_select:
            self._on_select(weapon_id)
        self.destroy()


class BuildExportDialog(ctk.CTkToplevel):
    """Modal CustomTkinter para visualizar y copiar el preset exportado (JSON o Base64)."""

    def __init__(self, parent, content: str, title_text: str = "Exportar Preset", is_json: bool = True):
        super().__init__(parent)
        self.title(f"TarkovScope — {title_text}")
        self.geometry("720x520")
        self.minsize(600, 400)
        self.configure(fg_color=C_BG_DARKEST)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Encabezado
        hdr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, height=50, corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            hdr,
            text=f"📋 {title_text.upper()}",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left", padx=16, pady=12)

        fmt_desc = "Formato weaponbuilds (SPT-AKI / herramientas EFT)" if is_json else "Código Base64 portable para compartir"
        ctk.CTkLabel(
            hdr,
            text=fmt_desc,
            font=ui_font(11),
            text_color=C_TEXT_MUTED
        ).pack(side="right", padx=16, pady=12)

        # Contenedor de texto
        txt_frame = ctk.CTkFrame(self, fg_color="transparent")
        txt_frame.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)
        txt_frame.grid_columnconfigure(0, weight=1)
        txt_frame.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(
            txt_frame,
            fg_color=C_BG_DEEP,
            text_color=C_TEXT,
            border_width=1,
            border_color=C_BORDER,
            font=ui_font(12),
            wrap="none"
        )
        self.textbox.grid(row=0, column=0, sticky="nsew")
        self.textbox.insert("1.0", content)

        # Barra inferior
        ftr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, height=48, corner_radius=0)
        ftr.grid(row=2, column=0, sticky="ew")

        self.copy_btn = ctk.CTkButton(
            ftr,
            text="📋 Copiar al Portapapeles",
            width=200,
            height=32,
            fg_color="#1E3A8A",
            hover_color="#2563EB",
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._copy_to_clipboard
        )
        self.copy_btn.pack(side="left", padx=16, pady=8)

        ctk.CTkButton(
            ftr,
            text="Cerrar",
            width=100,
            height=32,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self.destroy
        ).pack(side="right", padx=16, pady=8)

    def _copy_to_clipboard(self):
        text = self.textbox.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.copy_btn.configure(text="✓ ¡Copiado con Éxito!", fg_color="#16A34A")
        self.after(2000, lambda: self.copy_btn.configure(text="📋 Copiar al Portapapeles", fg_color="#1E3A8A"))


class BuildImportDialog(ctk.CTkToplevel):
    """Modal CustomTkinter para importar presets mediante JSON o cadena Base64."""

    def __init__(self, parent, on_import_callback):
        super().__init__(parent)
        self.on_import_callback = on_import_callback
        self.title("TarkovScope — Importar Preset de Armería")
        self.geometry("640x440")
        self.minsize(540, 360)
        self.configure(fg_color=C_BG_DARKEST)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, height=50, corner_radius=0)
        hdr.grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            hdr,
            text="📥 IMPORTAR PRESET DE ARMERÍA",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left", padx=16, pady=12)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=16, pady=10)
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            body,
            text="Pega abajo el código Base64 (ej: TTCBUILD:...) o el JSON exportado de la build:",
            font=ui_font(12),
            text_color=C_TEXT_SOFT
        ).grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.textbox = ctk.CTkTextbox(
            body,
            fg_color=C_BG_DEEP,
            text_color=C_TEXT,
            border_width=1,
            border_color=C_BORDER,
            font=ui_font(12),
            wrap="char"
        )
        self.textbox.grid(row=1, column=0, sticky="nsew")

        self.lbl_error = ctk.CTkLabel(
            body,
            text="",
            font=ui_font(12, "bold"),
            text_color="#F87171"
        )
        self.lbl_error.grid(row=2, column=0, sticky="w", pady=(4, 0))

        ftr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, height=48, corner_radius=0)
        ftr.grid(row=2, column=0, sticky="ew")

        ctk.CTkButton(
            ftr,
            text="📥 Cargar Preset en el Taller",
            width=210,
            height=32,
            fg_color="#16A34A",
            hover_color="#15803D",
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._do_import
        ).pack(side="left", padx=16, pady=8)

        ctk.CTkButton(
            ftr,
            text="Cancelar",
            width=100,
            height=32,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self.destroy
        ).pack(side="right", padx=16, pady=8)

    def _do_import(self):
        raw_text = self.textbox.get("1.0", "end-1c").strip()
        if not raw_text:
            self.lbl_error.configure(text="⚠️ Por favor pega el código o JSON de la build.")
            return

        parsed = None
        if raw_text.startswith("TTCBUILD:") or not raw_text.startswith("{"):
            parsed = import_build_from_base64(raw_text)
        if not parsed and raw_text.startswith("{"):
            parsed = import_build_from_json(raw_text)

        if parsed:
            self.on_import_callback(parsed)
            self.destroy()
        else:
            self.lbl_error.configure(text="❌ Formato inválido o arma desconocida en el código.")


class WeaponBuilderMixin:
    """
    Mixin para la pestaña de armas que implementa el Gunsmith Studio Interactivo Pro.
    Visualiza el arma cambiando en tiempo real mediante planos esquemáticos militares dinámicos,
    ofrece conmutación rápida de ranuras y catálogo visual con instalación en 1-clic.
    """

    def _init_builder_state(self):
        """Inicializa las variables de estado del Gunsmith Studio Pro."""
        self.builder_weapon_id = "m4a1"
        self.builder_weapon_category = MODDABLE_WEAPONS["m4a1"].get("category", "Rifles de Asalto")
        self.builder_slots = dict(MODDABLE_WEAPONS["m4a1"]["default_slots"])
        self.builder_active_slot = "muzzle"  # Ranura activa por defecto
        self.builder_slot_buttons: Dict[str, ctk.CTkButton] = {}
        self.builder_preset_buttons: Dict[str, ctk.CTkButton] = {}
        self.builder_stat_labels: Dict[str, ctk.CTkLabel] = {}
        self.builder_stat_bars: Dict[str, ctk.CTkProgressBar] = {}

    def _render_builder_view(self):
        """Construye y renderiza el banco de trabajo interactivo Pro."""
        if not hasattr(self, "builder_weapon_id"):
            self._init_builder_state()

        container = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=3)
        container.grid_rowconfigure(2, weight=2)

        # 1. Barra de Herramientas Superior: Selector de Arma + Presets Rápidos + Acciones
        self._build_pro_top_bar(container)

        # 2. Escenario Superior: Blueprint Esquemático Dinámico + Telemetría Balística
        self._build_pro_blueprint_stage(container)

        # 3. Escenario Inferior: Selector Rápido de Ranuras + Catálogo Visual 1-Clic
        self._build_pro_parts_shelf(container)

        # Refrescar todo el estado visual inicial
        self._refresh_pro_builder_ui()
        return container

    # -------------------------------------------------------------
    # 1. BARRA SUPERIOR PRO (SELECTOR, PRESETS DIRECTOS Y ACCIONES)
    # -------------------------------------------------------------
    def _build_pro_top_bar(self, parent):
        top_bar = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        top_bar.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 6))
        top_bar.grid_columnconfigure(0, weight=1)

        row_top = ctk.CTkFrame(top_bar, fg_color="transparent")
        row_top.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 3))

        # Selector de Arma (Botón limpio que abre la ventana con categorías y listado)
        w_box = ctk.CTkFrame(row_top, fg_color="transparent")
        w_box.pack(side="left")

        ctk.CTkLabel(
            w_box,
            text="Arma Base:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left", padx=(0, 6))

        cur_w = MODDABLE_WEAPONS[self.builder_weapon_id]
        if not getattr(self, "builder_weapon_category", None):
            self.builder_weapon_category = cur_w.get("category", "Todas")

        self.btn_weapon_picker = ctk.CTkButton(
            w_box,
            text=f"🔫 {cur_w['name']}  •  {self.builder_weapon_category}  ▾",
            width=290,
            height=30,
            anchor="w",
            fg_color=C_BG_DEEP,
            hover_color=C_SLATE_800,
            border_width=1,
            border_color=THEME["accent_gold"],
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._open_weapon_picker
        )
        self.btn_weapon_picker.pack(side="left")

        # Botones de Acción (Lista, Exportar, Importar)
        act_box = ctk.CTkFrame(row_top, fg_color="transparent")
        act_box.pack(side="right")

        ctk.CTkButton(
            act_box,
            text="📋 Lista Compras",
            width=110,
            height=28,
            fg_color="#1E3A8A",
            hover_color="#2563EB",
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._copy_shopping_list
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            act_box,
            text="💾 JSON EFT/SPT",
            width=110,
            height=28,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._open_export_json_dialog
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            act_box,
            text="🔗 B64",
            width=62,
            height=28,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=THEME["accent_gold"],
            font=ui_font(11, "bold"),
            command=self._open_export_b64_dialog
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            act_box,
            text="📥 Importar",
            width=82,
            height=28,
            fg_color=C_SLATE_800,
            hover_color="#16A34A",
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._open_import_dialog
        ).pack(side="left", padx=2)

        # Barra de Presets Meta Rápidos en fila dedicada
        self.presets_bar = ctk.CTkFrame(top_bar, fg_color="transparent")
        self.presets_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 6))
        self._rebuild_preset_buttons()

    def _rebuild_preset_buttons(self):
        """Crea botones directos para los presets meta del arma activa."""
        for w in self.presets_bar.winfo_children():
            w.destroy()
        self.builder_preset_buttons.clear()

        w = MODDABLE_WEAPONS.get(self.builder_weapon_id, MODDABLE_WEAPONS["m4a1"])
        presets = w.get("presets", {})

        ctk.CTkLabel(
            self.presets_bar,
            text="Presets Meta:",
            font=ui_font(11, "bold"),
            text_color=C_TEXT_MUTED
        ).pack(side="left", padx=(0, 4))

        for p_name in presets.keys():
            # Icono y estilo según nombre
            color = "#047857" if "Meta" in p_name or "Laser" in p_name else (
                "#B45309" if "Budget" in p_name else "#1D4ED8"
            )
            btn = ctk.CTkButton(
                self.presets_bar,
                text=p_name,
                height=26,
                corner_radius=4,
                fg_color=color,
                hover_color=THEME["accent_gold"],
                text_color=C_WHITE,
                font=ui_font(11, "bold"),
                command=lambda pn=p_name: self._apply_preset_direct(pn)
            )
            btn.pack(side="left", padx=3)
            self.builder_preset_buttons[p_name] = btn

        # Botón Reset Fábrica
        ctk.CTkButton(
            self.presets_bar,
            text="🔄 Fábrica",
            height=26,
            corner_radius=4,
            fg_color=C_SLATE_800,
            hover_color=C_RED_DARK,
            text_color=C_TEXT_SOFT,
            font=ui_font(11, "bold"),
            command=self._reset_to_factory_defaults
        ).pack(side="left", padx=3)

    def _on_category_changed(self, selected_category: str):
        self.builder_weapon_category = selected_category
        cur_w = MODDABLE_WEAPONS.get(self.builder_weapon_id, {})
        if selected_category != "Todas" and cur_w.get("category") != selected_category:
            for w_id, w_data in MODDABLE_WEAPONS.items():
                if w_data.get("category") == selected_category:
                    self._select_weapon_by_id(w_id)
                    break

    def _open_weapon_picker(self):
        WeaponPickerModal(
            self,
            current_weapon_id=self.builder_weapon_id,
            initial_category=getattr(self, "builder_weapon_category", "Todas"),
            on_select=self._select_weapon_by_id,
        )

    def _select_weapon_by_id(self, w_id: str):
        w_data = MODDABLE_WEAPONS.get(w_id)
        if not w_data:
            return
        self.builder_weapon_id = w_id
        self.builder_weapon_category = w_data.get("category", "Todas")
        self.builder_slots = dict(w_data["default_slots"])

        if hasattr(self, "btn_weapon_picker"):
            self.btn_weapon_picker.configure(
                text=f"🔫 {w_data['name']}  •  {self.builder_weapon_category}  ▾"
            )

        self._rebuild_preset_buttons()
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()
        self._refresh_pro_builder_ui()

    def _on_weapon_changed(self, selected_name: str):
        for w_id, w_data in MODDABLE_WEAPONS.items():
            if selected_name == w_data["name"]:
                self._select_weapon_by_id(w_id)
                break

    def _apply_preset_direct(self, preset_name: str):
        w = MODDABLE_WEAPONS[self.builder_weapon_id]
        if preset_name in w.get("presets", {}):
            self.builder_slots = dict(w["presets"][preset_name])
            self._rebuild_slot_selector_bar()
            self._render_parts_for_active_slot()
            self._refresh_pro_builder_ui()

    def _reset_to_factory_defaults(self):
        w = MODDABLE_WEAPONS[self.builder_weapon_id]
        self.builder_slots = dict(w["default_slots"])
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()
        self._refresh_pro_builder_ui()

    # -------------------------------------------------------------
    # 2. ESCENARIO CENTRAL: BLUEPRINT ESQUEMÁTICO DINÁMICO & STATS
    # -------------------------------------------------------------
    def _build_pro_blueprint_stage(self, parent):
        stage = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        stage.grid(row=1, column=0, sticky="nsew", padx=2, pady=(0, 6))
        stage.grid_columnconfigure(0, weight=1)
        stage.grid_rowconfigure(0, weight=1)

        # Fila Superior: Contenedor del Blueprint Táctico Dinámico
        bp_box = ctk.CTkFrame(stage, fg_color="#090D14", corner_radius=6)
        bp_box.grid(row=0, column=0, sticky="nsew", padx=8, pady=(8, 4))
        bp_box.grid_columnconfigure(0, weight=1)

        self.lbl_blueprint_img = ctk.CTkLabel(bp_box, text="")
        self.lbl_blueprint_img.pack(fill="both", expand=True, pady=4)

        # Fila Inferior del Escenario: Telemetría Balística en Barras Horizontales
        telemetry = ctk.CTkFrame(stage, fg_color=C_BG_PANEL, corner_radius=6)
        telemetry.grid(row=1, column=0, sticky="ew", padx=8, pady=(2, 8))
        telemetry.grid_columnconfigure((0, 1, 2, 3), weight=1)

        # Col 0: Ergonomía
        c0 = ctk.CTkFrame(telemetry, fg_color="transparent")
        c0.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        ctk.CTkLabel(c0, text="Ergonomía (ADS):", font=ui_font(11, "bold"), text_color=C_TEXT).pack(anchor="w")
        self.lbl_stat_ergo = ctk.CTkLabel(c0, text="—", font=ui_font(13, "bold"), text_color=C_WHITE)
        self.lbl_stat_ergo.pack(anchor="w")
        self.bar_stat_ergo = ctk.CTkProgressBar(c0, height=6, corner_radius=3, fg_color=C_SLATE_800)
        self.bar_stat_ergo.pack(fill="x", pady=(2, 0))

        # Col 1: Retroceso Vertical
        c1 = ctk.CTkFrame(telemetry, fg_color="transparent")
        c1.grid(row=0, column=1, padx=8, pady=6, sticky="ew")
        ctk.CTkLabel(c1, text="Retroceso Vertical:", font=ui_font(11, "bold"), text_color=C_TEXT).pack(anchor="w")
        self.lbl_stat_recoil_v = ctk.CTkLabel(c1, text="—", font=ui_font(13, "bold"), text_color="#38BDF8")
        self.lbl_stat_recoil_v.pack(anchor="w")
        self.bar_stat_recoil_v = ctk.CTkProgressBar(c1, height=6, corner_radius=3, fg_color=C_SLATE_800)
        self.bar_stat_recoil_v.pack(fill="x", pady=(2, 0))

        # Col 2: Retroceso Horizontal y Peso
        c2 = ctk.CTkFrame(telemetry, fg_color="transparent")
        c2.grid(row=0, column=2, padx=8, pady=6, sticky="ew")
        ctk.CTkLabel(c2, text="Retroceso H. / Masa:", font=ui_font(11, "bold"), text_color=C_TEXT).pack(anchor="w")
        self.lbl_stat_recoil_h_weight = ctk.CTkLabel(c2, text="—", font=ui_font(13, "bold"), text_color=C_WHITE)
        self.lbl_stat_recoil_h_weight.pack(anchor="w")
        self.bar_stat_weight = ctk.CTkProgressBar(c2, height=6, corner_radius=3, fg_color=C_SLATE_800)
        self.bar_stat_weight.pack(fill="x", pady=(2, 0))

        # Col 3: Costo de Piezas y Traders
        c3 = ctk.CTkFrame(telemetry, fg_color="transparent")
        c3.grid(row=0, column=3, padx=8, pady=6, sticky="ew")
        self.lbl_stat_cost = ctk.CTkLabel(c3, text="💰 ~0 ₽", font=ui_font(13, "bold"), text_color=C_GREEN_LIGHT)
        self.lbl_stat_cost.pack(anchor="w")
        self.lbl_stat_traders = ctk.CTkLabel(c3, text="🔑 Traders: —", font=ui_font(11), text_color=C_TEXT_SOFT)
        self.lbl_stat_traders.pack(anchor="w")

    # -------------------------------------------------------------
    # 3. ESCENARIO INFERIOR: INSPECTOR DE RANURAS + CATÁLOGO DE PIEZAS
    # -------------------------------------------------------------
    def _build_pro_parts_shelf(self, parent):
        shelf_frame = ctk.CTkFrame(
            parent,
            fg_color=C_BG_DARKEST,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        shelf_frame.grid(row=2, column=0, sticky="nsew", padx=2, pady=0)
        shelf_frame.grid_columnconfigure(0, weight=0)
        shelf_frame.grid_columnconfigure(1, weight=1)
        shelf_frame.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo: Inspector Vertical de Ranuras (todas visibles sin scroll horizontal)
        left_panel = ctk.CTkFrame(
            shelf_frame,
            width=285,
            fg_color=C_BG_PANEL,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER
        )
        left_panel.grid(row=0, column=0, sticky="nsw", padx=(6, 4), pady=6)
        left_panel.grid_propagate(False)
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            left_panel,
            text="🔧 RANURAS DEL ARMA",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w"
        ).grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))

        self.slot_nav_frame = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent"
        )
        self.slot_nav_frame.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 6))
        self.slot_nav_frame.grid_columnconfigure(0, weight=1)

        # Panel Derecho: Encabezado + Buscador de Piezas + Catálogo Compatible
        right_panel = ctk.CTkFrame(
            shelf_frame,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER
        )
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 6), pady=6)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        parts_hdr = ctk.CTkFrame(right_panel, fg_color=C_BG_PANEL, corner_radius=6)
        parts_hdr.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))
        parts_hdr.grid_columnconfigure(0, weight=1)

        self.lbl_active_slot_hdr = ctk.CTkLabel(
            parts_hdr,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w"
        )
        self.lbl_active_slot_hdr.grid(row=0, column=0, sticky="w", padx=10, pady=6)

        self.entry_part_search = ctk.CTkEntry(
            parts_hdr,
            width=220,
            height=28,
            placeholder_text="🔍 Filtrar pieza...",
            font=ui_font(11),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
            text_color=C_WHITE
        )
        self.entry_part_search.grid(row=0, column=1, padx=4, pady=6)
        self.entry_part_search.bind("<KeyRelease>", self._on_part_search_key)

        self.btn_unequip_slot = ctk.CTkButton(
            parts_hdr,
            text="✕ Quitar",
            width=74,
            height=28,
            fg_color=C_SLATE_800,
            hover_color=C_RED_DARK,
            text_color=C_TEXT_SOFT,
            font=ui_font(11, "bold"),
            command=lambda: self._equip_part_in_active_slot("none")
        )
        self.btn_unequip_slot.grid(row=0, column=2, padx=(4, 8), pady=6)

        self.parts_palette_scroll = ctk.CTkScrollableFrame(
            right_panel,
            fg_color=C_BG_DARKEST,
            corner_radius=6
        )
        self.parts_palette_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.parts_palette_scroll.grid_columnconfigure(0, weight=1)

        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()

    def _on_part_search_key(self, _event=None):
        if getattr(self, "_part_search_after_id", None) is not None:
            self.after_cancel(self._part_search_after_id)
        self._part_search_after_id = self.after(110, self._render_parts_for_active_slot)

    def _rebuild_slot_selector_bar(self):
        """Genera tarjetas limpias para cada ranura soportada por el arma activa."""
        for w in self.slot_nav_frame.winfo_children():
            w.destroy()
        self.builder_slot_buttons.clear()

        weapon = MODDABLE_WEAPONS.get(self.builder_weapon_id, {})
        supported = weapon.get("supported_slots") or [sk for sk, _ in MOD_SLOTS]
        if self.builder_active_slot not in supported and supported:
            self.builder_active_slot = supported[0]

        for slot_key, slot_name in MOD_SLOTS:
            if slot_key not in supported:
                continue
            icon = SLOT_ICONS.get(slot_key, "🔩")
            cur_part_id = self.builder_slots.get(slot_key, "none")
            cur_part = ATTACHMENTS_CATALOG.get(cur_part_id, ATTACHMENTS_CATALOG["none"])

            is_active = (slot_key == self.builder_active_slot)
            clean_slot = slot_name.split(" (")[0]
            part_name = cur_part["name"] if cur_part_id != "none" else "— Vacío / Estándar —"

            card = ctk.CTkFrame(
                self.slot_nav_frame,
                fg_color=C_BG_DEEP if is_active else C_BG_PANEL_ALT2,
                corner_radius=6,
                border_width=2 if is_active else 1,
                border_color=THEME["accent_gold"] if is_active else C_BORDER
            )
            card.pack(fill="x", padx=2, pady=3)
            card.grid_columnconfigure(0, weight=1)

            lbl_slot = ctk.CTkLabel(
                card,
                text=f"{icon}  {clean_slot}",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"] if is_active else C_WHITE,
                anchor="w"
            )
            lbl_slot.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 1))

            lbl_part = ctk.CTkLabel(
                card,
                text=f"✓ {part_name}" if cur_part_id != "none" else part_name,
                font=ui_font(11),
                text_color=C_EMERALD if cur_part_id != "none" else C_TEXT_DIM,
                anchor="w"
            )
            lbl_part.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 6))

            for widget in (card, lbl_slot, lbl_part):
                widget.bind("<Button-1>", lambda _e, sk=slot_key: self._on_slot_button_clicked(sk))

            self.builder_slot_buttons[slot_key] = card

    def _on_slot_button_clicked(self, slot_key: str):
        self.builder_active_slot = slot_key
        if hasattr(self, "entry_part_search"):
            self.entry_part_search.delete(0, "end")
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()

    def _render_parts_for_active_slot(self):
        """Renderiza los accesorios compatibles en lotes (batch rendering) con filtro instantáneo."""
        self._parts_render_token = getattr(self, "_parts_render_token", 0) + 1
        token = self._parts_render_token

        for w in self.parts_palette_scroll.winfo_children():
            w.destroy()

        slot_key = self.builder_active_slot
        all_parts = get_available_attachments_for_slot(slot_key, self.builder_weapon_id)
        query = self.entry_part_search.get().strip().lower() if hasattr(self, "entry_part_search") else ""
        if query:
            parts = [
                p for p in all_parts
                if query in p.get("name", "").lower() or query in p.get("trader", "").lower()
            ]
        else:
            parts = all_parts

        cur_equipped_id = self.builder_slots.get(slot_key, "none")

        slot_label = dict(MOD_SLOTS).get(slot_key, slot_key)
        icon = SLOT_ICONS.get(slot_key, "🔩")
        if hasattr(self, "lbl_active_slot_hdr"):
            self.lbl_active_slot_hdr.configure(
                text=f"{icon}  {slot_label.upper()}  —  {len(parts)} piezas"
            )

        if not parts:
            ctk.CTkLabel(
                self.parts_palette_scroll,
                text="No hay piezas que coincidan con el filtro.",
                font=ui_font(12),
                text_color=C_TEXT_MUTED
            ).pack(pady=30)
            return

        def _render_batch(start_idx: int = 0, batch_size: int = 8):
            if not self.winfo_exists() or token != self._parts_render_token:
                return
            end_idx = min(start_idx + batch_size, len(parts))
            for part in parts[start_idx:end_idx]:
                self._create_builder_part_row(part, cur_equipped_id)
            if end_idx < len(parts):
                self.after(6, lambda: _render_batch(end_idx, batch_size))

        _render_batch(0, 8)

    def _create_builder_part_row(self, part: Dict[str, Any], cur_equipped_id: str):
        p_id = part["id"]
        is_equipped = (p_id == cur_equipped_id)
        row_bg = "#121A26" if is_equipped else C_BG_PANEL

        row_card = tk.Frame(
            self.parts_palette_scroll,
            bg=row_bg,
            highlightbackground=THEME["accent_gold"] if is_equipped else "#1E293B",
            highlightthickness=2 if is_equipped else 1,
            bd=0,
            cursor="hand2",
        )
        row_card.pack(fill="x", padx=6, pady=3)
        row_card.grid_columnconfigure(1, weight=1)

        img_box = tk.Frame(
            row_card,
            width=78,
            height=50,
            bg="#080C14",
            highlightbackground="#1F2937",
            highlightthickness=1,
            bd=0,
        )
        img_box.grid(row=0, column=0, rowspan=2, padx=(8, 10), pady=6)
        img_box.grid_propagate(False)

        img_key = get_attachment_image_key(p_id)
        thumb_lbl = ctk.CTkLabel(img_box, text="", fg_color="#080C14")
        ctk_img = get_weapon_or_part_ctk_image(img_key, size=(70, 42), label_fallback=part["name"])
        if ctk_img:
            thumb_lbl.configure(image=ctk_img)
        thumb_lbl.pack(expand=True, fill="both")

        name_lbl = tk.Label(
            row_card,
            text=part["name"],
            font=ui_font(12, "bold"),
            bg=row_bg,
            fg=THEME["accent_gold"] if is_equipped else C_WHITE,
            anchor="w",
            bd=0,
        )
        name_lbl.grid(row=0, column=1, sticky="w", padx=2, pady=(6, 1))

        badges_row = tk.Frame(row_card, bg=row_bg, bd=0)
        badges_row.grid(row=1, column=1, sticky="w", padx=2, pady=(0, 6))

        if p_id != "none":
            e_d = part.get("ergo_delta", 0.0)
            r_d = part.get("recoil_pct_delta", 0.0)
            w_d = part.get("weight_delta_kg", 0.0)
            cost = part.get("price_rubles", 0)
            trader = part.get("trader", "—")
            ll = part.get("loyalty_level", 1)

            if e_d != 0:
                tk.Label(
                    badges_row,
                    text=f" {e_d:+g} Ergo ",
                    font=ui_font(9, "bold"),
                    bg="#166534" if e_d > 0 else "#991B1B",
                    fg=C_WHITE,
                    padx=3,
                    pady=1,
                    bd=0,
                ).pack(side="left", padx=(0, 4))

            if r_d != 0:
                tk.Label(
                    badges_row,
                    text=f" {r_d:+g}% Recoil ",
                    font=ui_font(9, "bold"),
                    bg="#0369A1" if r_d < 0 else "#991B1B",
                    fg=C_WHITE,
                    padx=3,
                    pady=1,
                    bd=0,
                ).pack(side="left", padx=2)

            if w_d != 0:
                tk.Label(
                    badges_row,
                    text=f" {w_d:+.2f} kg ",
                    font=ui_font(9),
                    bg="#1E293B",
                    fg=C_TEXT_SOFT,
                    padx=3,
                    pady=1,
                    bd=0,
                ).pack(side="left", padx=2)

            t_txt = f"🛡️ {trader} LL{ll}" if trader != "—" else "🛒 Flea Market"
            tk.Label(
                badges_row,
                text=t_txt,
                font=ui_font(10, "bold"),
                bg=row_bg,
                fg="#38BDF8",
                bd=0,
            ).pack(side="left", padx=(6, 4))

            cost_txt = f"💰 ~{cost:,} ₽".replace(",", ".") if cost > 0 else "0 ₽"
            tk.Label(
                badges_row,
                text=cost_txt,
                font=ui_font(10, "bold"),
                bg=row_bg,
                fg=C_GREEN_LIGHT,
                bd=0,
            ).pack(side="left", padx=4)
        else:
            tk.Label(
                badges_row,
                text="Desmontar accesorio (deja la ranura vacía o con pieza estándar)",
                font=ui_font(10),
                bg=row_bg,
                fg=C_TEXT_DIM,
                bd=0,
            ).pack(side="left", padx=2)

        btn_state = ctk.CTkButton(
            row_card,
            text="✓ INSTALADO" if is_equipped else "Equipar",
            width=105,
            height=28,
            corner_radius=5,
            fg_color="#15803D" if is_equipped else C_SLATE_800,
            hover_color="#16A34A" if is_equipped else THEME["accent_gold"],
            text_color=C_WHITE if is_equipped else C_TEXT,
            font=ui_font(11, "bold"),
            command=lambda pid=p_id: self._equip_part_in_active_slot(pid)
        )
        btn_state.grid(row=0, column=2, rowspan=2, padx=10, pady=6)

        for w in (row_card, name_lbl, img_box, thumb_lbl):
            w.bind("<Button-1>", lambda e, pid=p_id: self._equip_part_in_active_slot(pid))

    def _equip_part_in_active_slot(self, part_id: str):
        """Instala la pieza seleccionada y actualiza instantáneamente el blueprint y los stats."""
        self.builder_slots[self.builder_active_slot] = part_id
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()
        self._refresh_pro_builder_ui()

    # -------------------------------------------------------------
    # ACTUALIZACIÓN VISUAL INTEGRAL (BLUEPRINT + TELEMETRÍA)
    # -------------------------------------------------------------
    def _refresh_pro_builder_ui(self):
        """Actualiza el blueprint esquemático interactivo y los medidores balísticos."""
        from core.weapon_visual_compositor import ensure_factory_weapon_image_async
        w_id_cur = self.builder_weapon_id

        def _on_factory_ready():
            def _ui_refresh():
                if not self.winfo_exists() or self.builder_weapon_id != w_id_cur:
                    return
                bp_new = get_dynamic_weapon_composite_ctk_image(
                    self.builder_weapon_id,
                    self.builder_slots,
                    target_size=(920, 310)
                )
                self.lbl_blueprint_img.configure(image=bp_new)
            self.after(0, _ui_refresh)

        ensure_factory_weapon_image_async(w_id_cur, on_ready=_on_factory_ready)

        # 1. Blueprint Dinámico Militar (<1 ms)
        bp_ctk = get_dynamic_weapon_composite_ctk_image(
            self.builder_weapon_id,
            self.builder_slots,
            target_size=(920, 310)
        )
        self.lbl_blueprint_img.configure(image=bp_ctk)

        # 2. Stats Balísticos Dinámicos
        stats = calculate_build_stats(self.builder_weapon_id, self.builder_slots)

        # Ergonomía
        e_val = stats["final_ergo"]
        e_del = stats["ergo_delta_total"]
        del_str = f" ({e_del:+d})" if e_del != 0 else ""
        self.lbl_stat_ergo.configure(text=f"{e_val} / 100{del_str}")
        self.bar_stat_ergo.set(min(1.0, max(0.0, e_val / 100.0)))
        self.bar_stat_ergo.configure(progress_color="#16A34A" if e_val >= 60 else (C_AMBER if e_val >= 40 else "#DC2626"))

        # Retroceso Vertical
        rv_val = stats["final_recoil_v"]
        rv_base = stats["base_recoil_v"]
        r_pct = stats["recoil_reduction_pct"]
        self.lbl_stat_recoil_v.configure(text=f"{rv_val}  ({r_pct:+g}%)  [Base: {rv_base}]")
        self.bar_stat_recoil_v.set(max(0.0, min(1.0, rv_val / (rv_base * 1.4))))
        self.bar_stat_recoil_v.configure(progress_color="#16A34A" if rv_val <= 70 else (C_AMBER if rv_val <= 130 else "#DC2626"))

        # Retroceso Horizontal y Peso
        rh_val = stats["final_recoil_h"]
        w_val = stats["final_weight_kg"]
        self.lbl_stat_recoil_h_weight.configure(text=f"Horiz: {rh_val}  •  {w_val:.2f} kg")
        self.bar_stat_weight.set(min(1.0, w_val / 8.0))

        # Costo y Comerciantes
        cost_str = f"{stats['total_cost_rubles']:,} ₽".replace(",", ".")
        self.lbl_stat_cost.configure(text=f"💰 ~{cost_str}")
        traders_str = ", ".join(f"{t} LL{lvl}" for t, lvl in sorted(stats["traders_needed"].items())) or "Sin requisitos"
        self.lbl_stat_traders.configure(text=f"🔑 {traders_str}")

    # -------------------------------------------------------------
    # EXPORTACIÓN / IMPORTACIÓN / COPIAR AL PORTAPAPELES
    # -------------------------------------------------------------
    def _copy_shopping_list(self):
        text = export_shopping_list_text(self.builder_weapon_id, self.builder_slots)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()

    def _open_export_json_dialog(self):
        json_content = export_build_to_json(self.builder_weapon_id, self.builder_slots)
        BuildExportDialog(self, json_content, title_text="Exportar JSON EFT/SPT", is_json=True)

    def _open_export_b64_dialog(self):
        b64_code = export_build_to_base64(self.builder_weapon_id, self.builder_slots)
        BuildExportDialog(self, b64_code, title_text="Código Preset Portable (Base64)", is_json=False)

    def _open_import_dialog(self):
        BuildImportDialog(self, on_import_callback=self._apply_imported_build)

    def _apply_imported_build(self, build_data: Dict[str, Any]):
        w_id = build_data.get("weapon_id")
        if w_id in MODDABLE_WEAPONS:
            self.builder_weapon_id = w_id
            cur_w = MODDABLE_WEAPONS[w_id]
            self.builder_weapon_category = cur_w.get("category", "Todas")
            if hasattr(self, "btn_weapon_picker"):
                self.btn_weapon_picker.configure(
                    text=f"🔫 {cur_w['name']}  •  {self.builder_weapon_category}  ▾"
                )

            new_slots = dict(cur_w["default_slots"])
            new_slots.update(build_data.get("slots", {}))
            self.builder_slots = new_slots

            self._rebuild_preset_buttons()
            self._rebuild_slot_selector_bar()
            self._render_parts_for_active_slot()
            self._refresh_pro_builder_ui()
