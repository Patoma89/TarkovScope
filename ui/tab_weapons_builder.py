"""
TarkovScope - Armador Interactivo Pro de Builds (Gunsmith Studio)
Simulador dinámico de banco de trabajo militar estilo Escape from Tarkov.
Permite seleccionar armas, ver cómo cambia el plano esquemático del arma en tiempo real
al instalar cada silenciador, mira óptica, culata, empuñadura y cargador de tambor.
Ofrece selección rápida de ranuras (Quick Slots), catálogo visual con equipamiento en 1-clic,
presets meta directos y exportación a JSON (EFT/SPT), lista de compra y Base64.
"""
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
        container.grid_rowconfigure(2, weight=1)

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

        # Selector de Arma
        w_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        w_box.pack(side="left", padx=10, pady=6)

        ctk.CTkLabel(
            w_box,
            text="Arma Base:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left", padx=(0, 6))

        weapon_titles = [f"{w['name']}" for w in MODDABLE_WEAPONS.values()]
        self.opt_weapon = ctk.CTkOptionMenu(
            w_box,
            values=weapon_titles,
            width=230,
            height=30,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            fg_color=C_BG_DEEP,
            button_color=C_SLATE_800,
            button_hover_color=THEME["accent_gold"],
            command=self._on_weapon_changed
        )
        cur_w = MODDABLE_WEAPONS[self.builder_weapon_id]
        self.opt_weapon.set(cur_w["name"])
        self.opt_weapon.pack(side="left")

        # Barra de Presets Meta Rápidos con 1 Clic
        self.presets_bar = ctk.CTkFrame(top_bar, fg_color="transparent")
        self.presets_bar.pack(side="left", padx=10, pady=6)
        self._rebuild_preset_buttons()

        # Botones de Acción (Lista, Exportar, Importar)
        act_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        act_box.pack(side="right", padx=10, pady=6)

        ctk.CTkButton(
            act_box,
            text="📋 Lista Compras",
            width=115,
            height=30,
            fg_color="#1E3A8A",
            hover_color="#2563EB",
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._copy_shopping_list
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            act_box,
            text="💾 JSON EFT/SPT",
            width=115,
            height=30,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._open_export_json_dialog
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            act_box,
            text="🔗 B64",
            width=65,
            height=30,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=THEME["accent_gold"],
            font=ui_font(11, "bold"),
            command=self._open_export_b64_dialog
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            act_box,
            text="📥 Importar",
            width=85,
            height=30,
            fg_color=C_SLATE_800,
            hover_color="#16A34A",
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=self._open_import_dialog
        ).pack(side="left", padx=3)

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

    def _on_weapon_changed(self, selected_name: str):
        for w_id, w_data in MODDABLE_WEAPONS.items():
            if selected_name == w_data["name"]:
                self.builder_weapon_id = w_id
                self.builder_slots = dict(w_data["default_slots"])
                break
        self._rebuild_preset_buttons()
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()
        self._refresh_pro_builder_ui()

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
        stage.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 6))
        stage.grid_columnconfigure(0, weight=1)

        # Fila Superior: Contenedor del Blueprint Táctico Dinámico
        bp_box = ctk.CTkFrame(stage, fg_color="#090D14", corner_radius=6)
        bp_box.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        bp_box.grid_columnconfigure(0, weight=1)

        self.lbl_blueprint_img = ctk.CTkLabel(bp_box, text="")
        self.lbl_blueprint_img.pack(fill="x", expand=True, pady=4)

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
    # 3. ESCENARIO INFERIOR: SELECTOR RÁPIDO Y CATÁLOGO VISUAL 1-CLIC
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
        shelf_frame.grid_columnconfigure(0, weight=1)
        shelf_frame.grid_rowconfigure(1, weight=1)

        # Fila 0: Barra Horizontal de Botones de Ranura (Quick Slots Strip)
        self.slot_nav_frame = ctk.CTkScrollableFrame(
            shelf_frame,
            orientation="horizontal",
            height=46,
            fg_color=C_BG_PANEL,
            corner_radius=6
        )
        self.slot_nav_frame.grid(row=0, column=0, sticky="ew", padx=6, pady=(6, 4))

        self._rebuild_slot_selector_bar()

        # Fila 1: Lista Vertical Táctica de Accesorios con Imágenes
        self.parts_palette_scroll = ctk.CTkScrollableFrame(
            shelf_frame,
            fg_color=C_BG_DARKEST,
            corner_radius=6
        )
        self.parts_palette_scroll.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.parts_palette_scroll.grid_columnconfigure(0, weight=1)

        self._render_parts_for_active_slot()

    def _rebuild_slot_selector_bar(self):
        """Genera botones estilizados para cada ranura de accesorio."""
        for w in self.slot_nav_frame.winfo_children():
            w.destroy()
        self.builder_slot_buttons.clear()

        for slot_key, slot_name in MOD_SLOTS:
            icon = SLOT_ICONS.get(slot_key, "🔩")
            cur_part_id = self.builder_slots.get(slot_key, "none")
            cur_part = ATTACHMENTS_CATALOG.get(cur_part_id, ATTACHMENTS_CATALOG["none"])

            is_active = (slot_key == self.builder_active_slot)
            short_part_name = cur_part["name"].split(" (")[0][:16] if cur_part_id != "none" else "Sin pieza"

            btn_text = f"{icon} {slot_name.split(' (')[0]}: {short_part_name}"
            btn = ctk.CTkButton(
                self.slot_nav_frame,
                text=btn_text,
                height=32,
                corner_radius=5,
                fg_color=THEME["accent_gold"] if is_active else C_BG_DEEP,
                hover_color="#B89658" if is_active else C_SLATE_800,
                text_color=C_BG_DARKEST if is_active else C_WHITE,
                font=ui_font(11, "bold"),
                command=lambda sk=slot_key: self._on_slot_button_clicked(sk)
            )
            btn.pack(side="left", padx=3)
            self.builder_slot_buttons[slot_key] = btn

    def _on_slot_button_clicked(self, slot_key: str):
        self.builder_active_slot = slot_key
        self._rebuild_slot_selector_bar()
        self._render_parts_for_active_slot()

    def _render_parts_for_active_slot(self):
        """Renderiza los accesorios en lotes (batch rendering) con imágenes oficiales de alta definición."""
        self._parts_render_token = getattr(self, "_parts_render_token", 0) + 1
        token = self._parts_render_token

        for w in self.parts_palette_scroll.winfo_children():
            w.destroy()

        slot_key = self.builder_active_slot
        parts = get_available_attachments_for_slot(slot_key, self.builder_weapon_id)
        cur_equipped_id = self.builder_slots.get(slot_key, "none")

        # Encabezado informativo de la lista
        slot_label = dict(MOD_SLOTS).get(slot_key, slot_key)
        icon = SLOT_ICONS.get(slot_key, "🔩")

        hdr_row = ctk.CTkFrame(self.parts_palette_scroll, fg_color="transparent")
        hdr_row.pack(fill="x", padx=8, pady=(4, 6))

        ctk.CTkLabel(
            hdr_row,
            text=f"{icon} {slot_label.upper()} — LISTA DE ACCESORIOS COMPATIBLES ({len(parts)} piezas disponibles)",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left")

        ctk.CTkLabel(
            hdr_row,
            text="Haz clic en cualquier fila para equipar la pieza instantáneamente",
            font=ui_font(11),
            text_color=C_TEXT_MUTED
        ).pack(side="right")

        def _render_batch(start_idx: int = 0, batch_size: int = 6):
            if not self.winfo_exists() or token != self._parts_render_token:
                return
            end_idx = min(start_idx + batch_size, len(parts))
            for part in parts[start_idx:end_idx]:
                self._create_builder_part_row(part, cur_equipped_id)
            if end_idx < len(parts):
                self.after(6, lambda: _render_batch(end_idx, batch_size))

        _render_batch(0, 6)

    def _create_builder_part_row(self, part: Dict[str, Any], cur_equipped_id: str):
        p_id = part["id"]
        is_equipped = (p_id == cur_equipped_id)

        row_card = ctk.CTkFrame(
            self.parts_palette_scroll,
            fg_color="#121A26" if is_equipped else C_BG_PANEL,
            corner_radius=6,
            border_width=2 if is_equipped else 1,
            border_color=THEME["accent_gold"] if is_equipped else "#1E293B"
        )
        row_card.pack(fill="x", padx=6, pady=3)
        row_card.grid_columnconfigure(1, weight=1)

        # Col 0: Marco de Imagen con Miniatura Oficial de EFT
        img_box = ctk.CTkFrame(
            row_card,
            width=80,
            height=52,
            fg_color="#080C14",
            corner_radius=4,
            border_width=1,
            border_color="#1F2937"
        )
        img_box.grid(row=0, column=0, rowspan=2, padx=(8, 10), pady=6)
        img_box.grid_propagate(False)

        img_key = get_attachment_image_key(p_id)
        thumb_lbl = ctk.CTkLabel(img_box, text="")
        ctk_img = get_weapon_or_part_ctk_image(img_key, size=(72, 44), label_fallback=part["name"])
        if ctk_img:
            thumb_lbl.configure(image=ctk_img)
        thumb_lbl.pack(expand=True)

        # Col 1: Información Principal (Nombre + Badges de Stats + Comerciante + Costo)
        name_lbl = ctk.CTkLabel(
            row_card,
            text=part["name"],
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"] if is_equipped else C_WHITE,
            anchor="w"
        )
        name_lbl.grid(row=0, column=1, sticky="w", padx=2, pady=(7, 2))

        # Fila de Badges y Metadatos
        badges_row = ctk.CTkFrame(row_card, fg_color="transparent")
        badges_row.grid(row=1, column=1, sticky="w", padx=2, pady=(0, 7))

        if p_id != "none":
            e_d = part.get("ergo_delta", 0.0)
            r_d = part.get("recoil_pct_delta", 0.0)
            w_d = part.get("weight_delta_kg", 0.0)
            cost = part.get("price_rubles", 0)
            trader = part.get("trader", "—")
            ll = part.get("loyalty_level", 1)

            if e_d != 0:
                ctk.CTkLabel(
                    badges_row,
                    text=f" {e_d:+g} Ergo ",
                    font=ui_font(10, "bold"),
                    fg_color="#166534" if e_d > 0 else "#991B1B",
                    text_color=C_WHITE,
                    corner_radius=4
                ).pack(side="left", padx=(0, 4))

            if r_d != 0:
                ctk.CTkLabel(
                    badges_row,
                    text=f" {r_d:+g}% Recoil ",
                    font=ui_font(10, "bold"),
                    fg_color="#0369A1" if r_d < 0 else "#991B1B",
                    text_color=C_WHITE,
                    corner_radius=4
                ).pack(side="left", padx=2)

            if w_d != 0:
                ctk.CTkLabel(
                    badges_row,
                    text=f" {w_d:+.2f} kg ",
                    font=ui_font(10),
                    fg_color="#1E293B",
                    text_color=C_TEXT_SOFT,
                    corner_radius=4
                ).pack(side="left", padx=2)

            t_txt = f"🛡️ {trader} LL{ll}" if trader != "—" else "🛒 Flea Market"
            ctk.CTkLabel(
                badges_row,
                text=t_txt,
                font=ui_font(11, "bold"),
                text_color="#38BDF8"
            ).pack(side="left", padx=(6, 4))

            cost_txt = f"💰 ~{cost:,} ₽".replace(",", ".") if cost > 0 else "0 ₽"
            ctk.CTkLabel(
                badges_row,
                text=cost_txt,
                font=ui_font(11, "bold"),
                text_color=C_GREEN_LIGHT
            ).pack(side="left", padx=4)
        else:
            ctk.CTkLabel(
                badges_row,
                text="Desmontar accesorio (deja la ranura vacía o con pieza estándar)",
                font=ui_font(11),
                text_color=C_TEXT_DIM
            ).pack(side="left", padx=2)

        # Col 2: Botón de Estado / Instalación
        btn_state = ctk.CTkButton(
            row_card,
            text="✓ INSTALADO" if is_equipped else "Equipar",
            width=110,
            height=30,
            corner_radius=5,
            fg_color="#15803D" if is_equipped else C_SLATE_800,
            hover_color="#16A34A" if is_equipped else THEME["accent_gold"],
            text_color=C_WHITE if is_equipped else C_TEXT,
            font=ui_font(11, "bold"),
            command=lambda pid=p_id: self._equip_part_in_active_slot(pid)
        )
        btn_state.grid(row=0, column=2, rowspan=2, padx=12, pady=8)

        # Hacer que hacer clic en la fila también equipe la pieza
        row_card.bind("<Button-1>", lambda e, pid=p_id: self._equip_part_in_active_slot(pid))
        name_lbl.bind("<Button-1>", lambda e, pid=p_id: self._equip_part_in_active_slot(pid))
        img_box.bind("<Button-1>", lambda e, pid=p_id: self._equip_part_in_active_slot(pid))
        thumb_lbl.bind("<Button-1>", lambda e, pid=p_id: self._equip_part_in_active_slot(pid))

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
        # 1. Blueprint Dinámico Militar (<1 ms)
        bp_ctk = get_dynamic_weapon_composite_ctk_image(
            self.builder_weapon_id,
            self.builder_slots,
            target_size=(740, 240)
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
            self.opt_weapon.set(cur_w["name"])

            new_slots = dict(cur_w["default_slots"])
            new_slots.update(build_data.get("slots", {}))
            self.builder_slots = new_slots

            self._rebuild_preset_buttons()
            self._rebuild_slot_selector_bar()
            self._render_parts_for_active_slot()
            self._refresh_pro_builder_ui()
