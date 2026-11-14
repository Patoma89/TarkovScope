"""
TarkovScope - Pestaña de Armas, Builds Meta/Budget y Guías Gunsmith (Mechanic) con Imágenes Pre-Cacheadas
Muestra imágenes reales en caché de cada arma y de cada accesorio / pieza Gunsmith con 0 ms de espera.
"""
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from core.weapons_data import WEAPONS_ARSENAL_DATA, GUNSMITH_GUIDES_DATA
from ui.image_utils import get_weapon_or_part_ctk_image
from ui.tab_weapons_builder import WeaponBuilderMixin
from ui.theme import C_BG_DARKEST, C_BG_PANEL, C_BG_PANEL_ALT2, C_BORDER, C_EMERALD, C_GREEN_LIGHT, C_SLATE_800, C_TEXT, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE


class TabWeapons(ctk.CTkFrame, WeaponBuilderMixin):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.mode = "ARSENAL"  # "ARSENAL", "GUNSMITH" o "BUILDER"
        self.selected_category = "TODAS"
        self.selected_weapon: Dict[str, Any] = WEAPONS_ARSENAL_DATA[0]
        self.weapon_buttons: Dict[str, ctk.CTkButton] = {}

        self._init_builder_state()
        self._mode_views: Dict[str, ctk.CTkFrame] = {}
        self._gs_search_debounce: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_switcher()
        self._build_body_container()
        self._mode_views["ARSENAL"] = self._render_arsenal_view()

    def _build_top_switcher(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        bar.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            bar,
            text="🔫 ARSENAL TÁCTICO & GUNSMITH",
            font=ui_font(size=16, weight="bold"),
            text_color=THEME["accent_orange"]
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        btn_box = ctk.CTkFrame(bar, fg_color="transparent")
        btn_box.grid(row=0, column=1, padx=10, pady=8, sticky="e")

        self.btn_arsenal = ctk.CTkButton(
            btn_box,
            text="🔫 Arsenal & Builds Meta",
            width=165,
            height=32,
            fg_color=THEME["accent_orange"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._switch_mode("ARSENAL")
        )
        self.btn_arsenal.pack(side="left", padx=3)

        self.btn_gunsmith = ctk.CTkButton(
            btn_box,
            text="🔧 Guías Gunsmith (Mechanic)",
            width=185,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._switch_mode("GUNSMITH")
        )
        self.btn_gunsmith.pack(side="left", padx=3)

        self.btn_builder = ctk.CTkButton(
            btn_box,
            text="🛠️ Modding Studio Pro",
            width=175,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._switch_mode("BUILDER")
        )
        self.btn_builder.pack(side="left", padx=3)

    def _build_body_container(self):
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew")
        self.body_frame.grid_columnconfigure(0, weight=1)
        self.body_frame.grid_rowconfigure(0, weight=1)

    def _switch_mode(self, new_mode: str):
        if self.mode == new_mode:
            return
        prev_mode = self.mode
        self.mode = new_mode
        self.btn_arsenal.configure(fg_color=THEME["accent_orange"] if new_mode == "ARSENAL" else THEME["bg_dark"])
        self.btn_gunsmith.configure(fg_color=THEME["accent_orange"] if new_mode == "GUNSMITH" else THEME["bg_dark"])
        self.btn_builder.configure(fg_color=THEME["accent_orange"] if new_mode == "BUILDER" else THEME["bg_dark"])

        if prev_mode in self._mode_views:
            self._mode_views[prev_mode].grid_remove()

        if new_mode in self._mode_views:
            self._mode_views[new_mode].grid(row=0, column=0, sticky="nsew")
        else:
            if new_mode == "ARSENAL":
                self._mode_views["ARSENAL"] = self._render_arsenal_view()
            elif new_mode == "GUNSMITH":
                self._mode_views["GUNSMITH"] = self._render_gunsmith_view()
            elif new_mode == "BUILDER":
                self._mode_views["BUILDER"] = self._render_builder_view()

    # --- VISTA 1: ARSENAL & BUILDS META ---

    def _render_arsenal_view(self):
        container = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        container.grid(row=0, column=0, sticky="nsew")
        container.grid_columnconfigure(0, weight=0)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        sidebar = ctk.CTkFrame(
            container,
            width=310,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        sidebar.grid(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(2, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="Categoría de Arma:",
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["text_muted"]
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        cats = ["TODAS", "Rifles de Asalto", "DMR / Precisión", "Subfusiles (SMG)", "Escopetas & CQC", "Francotiradores"]
        self.cat_combo = ctk.CTkComboBox(
            sidebar,
            values=cats,
            height=34,
            font=ui_font(size=13, weight="bold"),
            state="readonly",
            command=self._on_category_change
        )
        self.cat_combo.set(self.selected_category)
        self.cat_combo.grid(row=1, column=0, padx=14, pady=(0, 8), sticky="ew")

        self.weapons_list_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.weapons_list_scroll.grid(row=2, column=0, padx=6, pady=(0, 10), sticky="nsew")
        self.weapons_list_scroll.grid_columnconfigure(0, weight=1)

        self.weapon_detail_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.weapon_detail_scroll.grid(row=0, column=1, sticky="nsew")
        self.weapon_detail_scroll.grid_columnconfigure(0, weight=1)
        self.weapon_detail_scroll.grid_columnconfigure(1, weight=1)

        self._populate_weapons_sidebar()
        self._select_weapon(self.selected_weapon)
        return container

    def _on_category_change(self, cat: str):
        self.selected_category = cat
        self._populate_weapons_sidebar()

    def _populate_weapons_sidebar(self):
        for w in self.weapons_list_scroll.winfo_children():
            w.destroy()
        self.weapon_buttons.clear()

        filtered = [
            w for w in WEAPONS_ARSENAL_DATA
            if self.selected_category == "TODAS" or w["category"] == self.selected_category
        ]

        for idx, wp in enumerate(filtered):
            wp_thumb = get_weapon_or_part_ctk_image(wp["id"], size=(66, 36), label_fallback=wp["name"])
            btn = ctk.CTkButton(
                self.weapons_list_scroll,
                text=f"  {wp['name']}\n  [{wp['tier']} • {wp['rpm']} RPM]",
                image=wp_thumb,
                compound="left",
                anchor="w",
                height=56,
                corner_radius=8,
                font=ui_font(size=12, weight="bold"),
                fg_color="transparent",
                text_color=THEME["text_main"],
                hover_color=THEME["bg_card_hover"],
                command=lambda item=wp: self._select_weapon(item)
            )
            btn.grid(row=idx, column=0, padx=4, pady=3, sticky="ew")
            self.weapon_buttons[wp["id"]] = btn

        if filtered and self.selected_weapon not in filtered:
            self._select_weapon(filtered[0])
        elif filtered:
            self._select_weapon(self.selected_weapon)

    def _select_weapon(self, wp: Dict[str, Any]):
        self.selected_weapon = wp
        for wid, btn in self.weapon_buttons.items():
            if wid == wp["id"]:
                btn.configure(fg_color=THEME["accent_orange"], text_color=C_WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_main"])

        for w in self.weapon_detail_scroll.winfo_children():
            w.destroy()

        # 1. Header del Arma con Imagen Grande del Rifle
        hdr = ctk.CTkFrame(
            self.weapon_detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        hdr.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 12), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        wp_big_img = get_weapon_or_part_ctk_image(wp["id"], size=(240, 108), label_fallback=wp["name"])
        img_lbl = ctk.CTkLabel(hdr, text="", image=wp_big_img)
        img_lbl.grid(row=0, column=0, padx=(16, 10), pady=14, sticky="w")

        title_box = ctk.CTkFrame(hdr, fg_color="transparent")
        title_box.grid(row=0, column=1, padx=8, pady=14, sticky="w")

        ctk.CTkLabel(
            title_box,
            text=wp["name"],
            font=ui_font(size=22, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text=f"Categoría: {wp['category']}   |   Calibre: {wp['caliber']}\nCadencia: {wp['rpm']} RPM   |   Modos: {wp['fire_modes']}",
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["text_muted"],
            justify="left"
        ).pack(anchor="w", pady=(6, 0))

        tier_badge = ctk.CTkLabel(
            hdr,
            text=f" 🏆 {wp['tier']} ",
            font=ui_font(size=15, weight="bold"),
            fg_color=THEME["accent_green"] if "S+" in wp["tier"] else THEME["accent_orange"],
            text_color="#0F1115" if "S+" in wp["tier"] else C_WHITE,
            corner_radius=8,
            height=38
        )
        tier_badge.grid(row=0, column=2, padx=18, pady=14, sticky="e")

        # 2. Galería Visual de Piezas Clave del Arma
        featured_parts = wp.get("featured_parts", [])
        if featured_parts:
            parts_gallery = ctk.CTkFrame(
                self.weapon_detail_scroll,
                fg_color=THEME["bg_dark"],
                corner_radius=8,
                border_width=1,
                border_color=THEME["border"]
            )
            parts_gallery.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")

            ctk.CTkLabel(
                parts_gallery,
                text="🧩 PIEZAS Y ACCESORIOS CLAVE DE LA BUILD META:",
                font=ui_font(size=13, weight="bold"),
                text_color=THEME["accent_yellow"]
            ).pack(anchor="w", padx=16, pady=(10, 6))

            cards_row = ctk.CTkFrame(parts_gallery, fg_color="transparent")
            cards_row.pack(fill="x", padx=12, pady=(0, 12))

            for idx, (p_key, p_lbl) in enumerate(featured_parts):
                cards_row.grid_columnconfigure(idx, weight=1)
                p_card = ctk.CTkFrame(
                    cards_row,
                    fg_color=THEME["bg_card"],
                    corner_radius=6,
                    border_width=1,
                    border_color=THEME["border"]
                )
                p_card.grid(row=0, column=idx, padx=5, pady=2, sticky="ew")

                p_img = get_weapon_or_part_ctk_image(p_key, size=(92, 54), label_fallback=p_lbl)
                ctk.CTkLabel(p_card, text="", image=p_img).pack(padx=8, pady=(8, 4))
                ctk.CTkLabel(
                    p_card,
                    text=p_lbl,
                    font=ui_font(size=12, weight="bold"),
                    text_color=THEME["text_main"]
                ).pack(padx=6, pady=(0, 6))

        # 3. Estadísticas y Munición Recomendada
        stats_box = ctk.CTkFrame(
            self.weapon_detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        stats_box.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        stats_box.grid_columnconfigure(0, weight=1)

        st = wp["stats"]
        ctk.CTkLabel(
            stats_box,
            text=f"📊 Estadísticas Modificadas:   ⚡ Ergonomía: {st['ergo']}   |   📉 Retroceso Vertical: {st['recoil_v']}   |   🔭 Alcance Efectivo: {st['range']}",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_yellow"]
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            stats_box,
            text=f"🎯 Munición Recomendada: {wp['best_ammo']}",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_green"]
        ).pack(anchor="w", padx=16, pady=(2, 12))

        # 4. Build Meta (Izquierda) vs Build Económica (Derecha)
        meta_card = ctk.CTkFrame(
            self.weapon_detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["accent_orange"]
        )
        meta_card.grid(row=3, column=0, padx=(16, 8), pady=(0, 12), sticky="nsew")

        ctk.CTkLabel(
            meta_card,
            text="🔥 CONFIGURACIÓN META (MÍNIMO RETROCESO)",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        for part in wp["meta_build"]:
            ctk.CTkLabel(
                meta_card,
                text=f"• {part}",
                font=ui_font(size=13),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=4)
        ctk.CTkLabel(meta_card, text="", height=8).pack()

        budget_card = ctk.CTkFrame(
            self.weapon_detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        budget_card.grid(row=3, column=1, padx=(8, 16), pady=(0, 12), sticky="nsew")

        ctk.CTkLabel(
            budget_card,
            text="💰 CONFIGURACIÓN ECONÓMICA (TRADERS LL2/LL3)",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_green"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        for b_part in wp["budget_build"]:
            ctk.CTkLabel(
                budget_card,
                text=f"• {b_part}",
                font=ui_font(size=13),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=4)

        ctk.CTkLabel(
            budget_card,
            text="🧠 Análisis Táctico:",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_blue"]
        ).pack(anchor="w", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            budget_card,
            text=wp["notes"],
            font=ui_font(size=13),
            text_color=THEME["text_muted"],
            justify="left",
            wraplength=420
        ).pack(anchor="w", padx=16, pady=(0, 12))

    # --- VISTA 2: GUÍAS GUNSMITH (MECHANIC) CON IMAGEN DE ARMA, CHECKLIST Y FILTROS ---

    def _render_gunsmith_view(self):
        self._gs_search_query = getattr(self, "_gs_search_query", "")
        self._gs_only_pending = getattr(self, "_gs_only_pending", ctk.BooleanVar(value=False))

        outer = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(1, weight=1)

        # Barra de Progreso y Búsqueda de Gunsmith (Partes 1 a 25)
        ctrl_bar = ctk.CTkFrame(
            outer,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        ctrl_bar.grid(row=0, column=0, padx=0, pady=(0, 8), sticky="ew")
        ctrl_bar.grid_columnconfigure(1, weight=1)

        self.gs_progress_lbl = ctk.CTkLabel(
            ctrl_bar,
            text="",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_green"]
        )
        self.gs_progress_lbl.grid(row=0, column=0, padx=(16, 12), pady=10, sticky="w")

        self.gs_search_entry = ctk.CTkEntry(
            ctrl_bar,
            placeholder_text="Buscar Gunsmith (ej: Part 6, Part 14, MP5, RSASS, M4A1, PKP, B-30)...",
            height=34,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(size=13)
        )
        self.gs_search_entry.grid(row=0, column=1, padx=8, pady=10, sticky="ew")
        if self._gs_search_query:
            self.gs_search_entry.insert(0, self._gs_search_query)
        self.gs_search_entry.bind("<KeyRelease>", self._on_gs_search_debounced)

        ctk.CTkCheckBox(
            ctrl_bar,
            text="Solo pendientes",
            variable=self._gs_only_pending,
            font=ui_font(size=12, weight="bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_green"],
            command=self._refresh_gunsmith_list
        ).grid(row=0, column=2, padx=10, pady=10)

        self.gs_scroll = ctk.CTkScrollableFrame(
            outer,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.gs_scroll.grid(row=1, column=0, sticky="nsew")
        self.gs_scroll.grid_columnconfigure(0, weight=1)

        self._refresh_gunsmith_list()
        return outer

    def _on_gs_search_debounced(self, _=None):
        self._gs_limit = 8
        if self._gs_search_debounce is not None:
            self.after_cancel(self._gs_search_debounce)
        self._gs_search_debounce = self.after(150, self._refresh_gunsmith_list)

    def _refresh_gunsmith_list(self, reset_limit: bool = False):
        if reset_limit:
            self._gs_limit = 8
        self._render_token_gunsmith = getattr(self, "_render_token_gunsmith", 0) + 1
        token = self._render_token_gunsmith

        if hasattr(self, "gs_search_entry") and self.gs_search_entry.winfo_exists():
            self._gs_search_query = self.gs_search_entry.get().strip()

        ds = get_datastore()
        total_gs = len(GUNSMITH_GUIDES_DATA)
        done_gs = sum(1 for g in GUNSMITH_GUIDES_DATA if ds.get_stash_count(f"gunsmith:{g['part']}") >= 1)
        pct_gs = int((done_gs / total_gs) * 100) if total_gs > 0 else 0
        if hasattr(self, "gs_progress_lbl") and self.gs_progress_lbl.winfo_exists():
            self.gs_progress_lbl.configure(
                text=f"🔧 Progreso Gunsmith: {done_gs} / {total_gs} Completadas ({pct_gs}%)"
            )

        for w in self.gs_scroll.winfo_children():
            w.destroy()

        q = self._gs_search_query.lower()
        only_pend = self._gs_only_pending.get()

        filtered_gs = []
        for g in GUNSMITH_GUIDES_DATA:
            is_done = ds.get_stash_count(f"gunsmith:{g['part']}") >= 1
            if only_pend and is_done:
                continue
            if q:
                haystack = f"{g['title']} {g['weapon']} {g['reqs']} " + " ".join(p[1] for p in g.get("parts_detailed", []))
                if q not in haystack.lower():
                    continue
            filtered_gs.append(g)

        if not filtered_gs:
            ctk.CTkLabel(
                self.gs_scroll,
                text="No hay misiones de Gunsmith que coincidan con ese filtro.",
                font=ui_font(size=14, weight="bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=0, column=0, pady=40)
            return

        limit_n = getattr(self, "_gs_limit", 8)
        shown_gs = filtered_gs[:limit_n]
        remaining_gs = len(filtered_gs) - len(shown_gs)

        def _render_batch(start_idx: int = 0, batch_size: int = 4):
            if not self.winfo_exists() or token != self._render_token_gunsmith:
                return
            end_idx = min(start_idx + batch_size, len(shown_gs))
            for idx in range(start_idx, end_idx):
                self._create_gunsmith_card(self.gs_scroll, idx, shown_gs[idx])
            if end_idx < len(shown_gs):
                self.after(6, lambda: _render_batch(end_idx, batch_size))
            elif remaining_gs > 0:
                def _load_more_gs():
                    self._gs_limit = getattr(self, "_gs_limit", 8) + 10
                    self._refresh_gunsmith_list()

                ctk.CTkButton(
                    self.gs_scroll,
                    text=f"⬇ Cargar más misiones Gunsmith ({remaining_gs} restantes)",
                    height=34,
                    fg_color=C_BG_PANEL,
                    hover_color=THEME["accent_orange"],
                    border_width=1,
                    border_color=C_BORDER,
                    text_color=C_WHITE,
                    font=ui_font(size=12, weight="bold"),
                    command=_load_more_gs,
                ).grid(row=len(shown_gs), column=0, padx=14, pady=10, sticky="ew")

        _render_batch(0, 4)

    def _create_gunsmith_card(self, scroll: ctk.CTkScrollableFrame, idx: int, gs: Dict[str, Any]):
        ds = get_datastore()
        gs_key = f"gunsmith:{gs['part']}"
        is_done = ds.get_stash_count(gs_key) >= 1
        card_bg = "#0D1713" if is_done else THEME["bg_dark"]
        hdr_bg = "#11221B" if is_done else C_BG_PANEL_ALT2

        card = tk.Frame(
            scroll,
            bg=card_bg,
            highlightbackground=C_EMERALD if is_done else THEME["border"],
            highlightthickness=1,
            bd=0,
        )
        card.grid(row=idx, column=0, padx=12, pady=7, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        hdr_frame = tk.Frame(card, bg=hdr_bg, bd=0)
        hdr_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 6), sticky="ew")
        hdr_frame.grid_columnconfigure(0, weight=1)

        lbl_title = tk.Label(
            hdr_frame,
            text=f"🔧 {gs['title']}  —  {gs['weapon']}",
            font=ui_font(size=15, weight="bold"),
            bg=hdr_bg,
            fg=C_GREEN_LIGHT if is_done else THEME["accent_orange"],
            anchor="w",
            bd=0,
        )
        lbl_title.grid(row=0, column=0, padx=12, pady=8, sticky="w")

        tk.Label(
            hdr_frame,
            text=f" Nivel {gs['level']} Requerido  •  KAPPA ",
            font=ui_font(size=11, weight="bold"),
            bg=THEME["accent_blue"],
            fg=C_WHITE,
            padx=6,
            pady=4,
            bd=0,
        ).grid(row=0, column=1, padx=4, pady=8)

        btn_done = ctk.CTkButton(
            hdr_frame,
            text="✓ Completada" if is_done else "Marcar Completada",
            width=145,
            height=28,
            corner_radius=6,
            fg_color=C_EMERALD if is_done else C_SLATE_800,
            hover_color="#059669" if is_done else THEME["accent_orange"],
            text_color=C_BG_DARKEST if is_done else C_WHITE,
            font=ui_font(size=12, weight="bold"),
        )

        def toggle_gs(k=gs_key):
            cur = ds.get_stash_count(k)
            new_done = cur < 1
            ds.set_stash_count(k, 1 if new_done else 0)
            total_gs = len(GUNSMITH_GUIDES_DATA)
            done_gs = sum(1 for g in GUNSMITH_GUIDES_DATA if ds.get_stash_count(f"gunsmith:{g['part']}") >= 1)
            pct_gs = int((done_gs / total_gs) * 100) if total_gs > 0 else 0
            if hasattr(self, "gs_progress_lbl") and self.gs_progress_lbl.winfo_exists():
                self.gs_progress_lbl.configure(
                    text=f"🔧 Progreso Gunsmith: {done_gs} / {total_gs} Completadas ({pct_gs}%)"
                )
            if self._gs_only_pending.get() and new_done:
                if card.winfo_exists():
                    card.destroy()
                return
            nb = "#0D1713" if new_done else THEME["bg_dark"]
            nh = "#11221B" if new_done else C_BG_PANEL_ALT2
            card.configure(bg=nb, highlightbackground=C_EMERALD if new_done else THEME["border"])
            hdr_frame.configure(bg=nh)
            lbl_title.configure(bg=nh, fg=C_GREEN_LIGHT if new_done else THEME["accent_orange"])
            btn_done.configure(
                text="✓ Completada" if new_done else "Marcar Completada",
                fg_color=C_EMERALD if new_done else C_SLATE_800,
                hover_color="#059669" if new_done else THEME["accent_orange"],
                text_color=C_BG_DARKEST if new_done else C_WHITE,
            )

        btn_done.configure(command=toggle_gs)
        btn_done.grid(row=0, column=2, padx=(4, 10), pady=8)

        reqs_bar = tk.Frame(card, bg="#141A26", highlightbackground="#273142", highlightthickness=1, bd=0)
        reqs_bar.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 8), sticky="ew")

        tk.Label(
            reqs_bar,
            text=f"📐 REQUISITOS OBLIGATORIOS: {gs['reqs']}",
            font=ui_font(size=12, weight="bold"),
            bg="#141A26",
            fg=THEME["accent_yellow"],
            anchor="w",
            justify="left",
            wraplength=820,
            bd=0,
        ).pack(anchor="w", padx=10, pady=6)

        wp_box = tk.Frame(card, width=250, bg="#10141E", highlightbackground="#242C3B", highlightthickness=1, bd=0)
        wp_box.grid(row=2, column=0, padx=(10, 8), pady=(0, 10), sticky="nsew")
        wp_box.grid_propagate(False)

        wp_img = get_weapon_or_part_ctk_image(
            gs.get("image_key", f"gs_{gs['part']}"),
            size=(228, 96),
            label_fallback=gs["weapon"]
        )
        ctk.CTkLabel(wp_box, text="", image=wp_img, fg_color="#10141E").pack(padx=8, pady=(10, 4))

        tk.Label(
            wp_box,
            text=gs["weapon"],
            font=ui_font(size=12, weight="bold"),
            bg="#10141E",
            fg=THEME["text_main"],
            wraplength=230,
            justify="center",
            bd=0,
        ).pack(padx=8, pady=(0, 6))

        parts_box = tk.Frame(card, bg="#10141E", highlightbackground="#242C3B", highlightthickness=1, bd=0)
        parts_box.grid(row=2, column=1, padx=(0, 10), pady=(0, 10), sticky="nsew")
        parts_box.grid_columnconfigure(1, weight=1)

        parts_list = gs.get("parts_detailed", [])
        for p_idx, (part_icon_key, p_line) in enumerate(parts_list):
            is_warn = "IMPORTANTE" in p_line
            part_img = get_weapon_or_part_ctk_image(part_icon_key, size=(58, 34), label_fallback="MOD")

            ctk.CTkLabel(
                parts_box,
                text="",
                image=part_img,
                fg_color="#10141E",
            ).grid(row=p_idx, column=0, padx=(10, 8), pady=3, sticky="w")

            tk.Label(
                parts_box,
                text=p_line,
                font=ui_font(size=11, weight="bold" if is_warn else "normal"),
                bg="#10141E",
                fg=THEME["accent_green"] if is_warn else C_TEXT_SOFT,
                wraplength=460,
                justify="left",
                anchor="w",
                bd=0,
            ).grid(row=p_idx, column=1, padx=4, pady=3, sticky="w")
