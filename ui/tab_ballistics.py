"""
TarkovScope - Pestaña de Balística, Munición y Matriz de Penetración Pro (Zero-Lag)
Diseño tabular de ingeniería con grilla unificada (100% de alineación vertical entre cabeceras
y celdas), nombres de calibres formateados prolijamente ("Calibre 5.56x45 NATO", "Calibre 7.62x39", etc.),
columnas compactas CLASS 1 a CLASS 6 con número único sobre celda sólida (estilo Wiki),
y renderizado directo sin contenedores anidados.
"""
import customtkinter as ctk
from typing import List, Dict, Any, Optional
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from core.ballistics import calculate_armor_effectiveness, simulate_shots_to_kill
from ui.theme import C_AMBER, C_BG_DARKEST, C_BG_INSET, C_BG_PANEL, C_RED_DARK, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_SOFT, C_WHITE
from ui.ballistics_common import CALIBER_CLEAN_MAP, format_caliber_dropdown, format_caliber_short, COLUMNS_SPEC, CLASS_SCORE_COLORS
from ui.tab_ballistics_duel import DuelMixin

# Mapa de nombres limpios y profesionales para cada código de calibre de la API
# Formato: raw_api_caliber -> (Etiqueta en el selector desplegable, Etiqueta corta en la tabla)


# Definición de las 12 columnas con columna CALIBRE más amplia (132 px) para que nunca se corte ni encime

# Colores sólidos de la matriz balística (estilo tabla oficial de efectividad 1 a 6)


class TabBallistics(DuelMixin, ctk.CTkFrame):
    PAGE_SIZE = 28

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.filtered_ammo: List[Dict[str, Any]] = []
        self.display_to_raw_caliber: Dict[str, str] = {"TODOS LOS CALIBRES": "TODOS"}
        self.sort_by: str = "penetration_power"
        self.sort_desc: bool = True
        self.preset_mode: str = "ALL"
        self.current_page: int = 0
        self.is_duel_mode: bool = False
        self.show_stk_in_table: bool = False
        self.duel_ammo_a: Optional[Dict[str, Any]] = None
        self.duel_ammo_b: Optional[Dict[str, Any]] = None
        self._render_token: int = 0
        self._debounce_job: Optional[str] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_filter_bar()
        self._build_legend_bar()
        self._build_table_area()
        self._build_pagination_bar()
        self._build_duel_area()
        self.reload_data()

    def _build_filter_bar(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        bar.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            bar,
            text="Calibre:",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_gold"]
        ).grid(row=0, column=0, padx=(14, 6), pady=10, sticky="w")

        self.caliber_combo = ctk.CTkComboBox(
            bar,
            values=["TODOS LOS CALIBRES"],
            width=240,
            height=34,
            fg_color=C_BG_PANEL,
            border_color="#2E3646",
            button_color="#252F42",
            button_hover_color=C_SLATE_700,
            dropdown_fg_color=C_BG_PANEL,
            dropdown_hover_color="#252F42",
            dropdown_text_color=C_TEXT,
            text_color=C_TEXT,
            font=ui_font(size=13, weight="bold"),
            dropdown_font=ui_font(size=13, weight="bold"),
            command=self._on_filter_change,
            state="readonly"
        )
        self.caliber_combo.set("TODOS LOS CALIBRES")
        self.caliber_combo.grid(row=0, column=1, padx=6, pady=10, sticky="w")

        self.search_entry = ctk.CTkEntry(
            bar,
            placeholder_text="Buscar proyectil (ej: Igolnik, M855A1, M61, BP, RIP, Flechette, Hybrid)...",
            height=34,
            fg_color=C_BG_PANEL,
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(size=13)
        )
        self.search_entry.grid(row=0, column=2, padx=8, pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_debounced)

        presets_frame = ctk.CTkFrame(bar, fg_color="transparent")
        presets_frame.grid(row=0, column=3, padx=12, pady=8, sticky="e")

        self.btn_all = ctk.CTkButton(
            presets_frame,
            text="Todos",
            width=78,
            height=32,
            fg_color=THEME["accent_orange"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._set_preset("ALL")
        )
        self.btn_all.pack(side="left", padx=3)

        self.btn_meta = ctk.CTkButton(
            presets_frame,
            text="Meta Perforante (Pen 40+)",
            width=175,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._set_preset("META_PEN")
        )
        self.btn_meta.pack(side="left", padx=3)

        self.btn_leg = ctk.CTkButton(
            presets_frame,
            text="Leg Meta (Daño 75+)",
            width=150,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=12, weight="bold"),
            command=lambda: self._set_preset("LEG_META")
        )
        self.btn_leg.pack(side="left", padx=3)

        self.btn_duel = ctk.CTkButton(
            presets_frame,
            text="⚔️ Comparador Versus",
            width=175,
            height=32,
            fg_color=C_SLATE_800,
            hover_color=THEME["accent_gold"],
            font=ui_font(size=12, weight="bold"),
            command=self._toggle_duel_mode
        )
        self.btn_duel.pack(side="left", padx=3)

    def _build_legend_bar(self):
        """Barra de referencia rápida de efectividad contra blindajes Clases 1 a 6."""
        self.legend_frame = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"],
            height=36
        )
        self.legend_frame.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")

        ctk.CTkLabel(
            self.legend_frame,
            text="ESCALA CLASS 1–6:",
            font=ui_font(size=12, weight="bold"),
            text_color=THEME["text_muted"]
        ).pack(side="left", padx=(14, 10), pady=6)

        tiers = [
            ("6 • Pasa (>90%)", "#34D359", C_BG_INSET),
            ("5 • Alta (80-90%)", "#78D637", C_BG_INSET),
            ("4 • Buena (50-75%)", "#B5BD2B", C_BG_INSET),
            ("3 • Media (Desgaste)", C_AMBER, C_BG_INSET),
            ("2 • Baja (Frena)", "#EA580C", C_WHITE),
            ("1 • Nula (Rebota)", C_RED_DARK, C_WHITE),
        ]
        for text_lbl, bg_c, fg_c in tiers:
            ctk.CTkLabel(
                self.legend_frame,
                text=f" {text_lbl} ",
                font=ui_font(size=11, weight="bold"),
                fg_color=bg_c,
                text_color=fg_c,
                corner_radius=4,
                height=22
            ).pack(side="left", padx=4, pady=6)

        self.btn_stk_toggle = ctk.CTkButton(
            self.legend_frame,
            text="🎯 Ver Tiros para Matar (STK Tórax 85 HP)",
            height=24,
            width=255,
            corner_radius=5,
            fg_color=C_SLATE_800,
            hover_color=THEME["accent_gold"],
            text_color=C_TEXT,
            font=ui_font(size=11, weight="bold"),
            command=self._toggle_stk_table_mode,
        )
        self.btn_stk_toggle.pack(side="right", padx=(6, 12), pady=5)

    def _toggle_stk_table_mode(self):
        self.show_stk_in_table = not self.show_stk_in_table
        if self.show_stk_in_table:
            self.btn_stk_toggle.configure(
                text="📊 Ver Escala de Penetración (1–6)",
                fg_color=THEME["accent_gold"],
                text_color=C_BG_DARKEST,
            )
        else:
            self.btn_stk_toggle.configure(
                text="🎯 Ver Tiros para Matar (STK Tórax 85 HP)",
                fg_color=C_SLATE_800,
                text_color=C_TEXT,
            )
        self._render_current_page()

    def _build_table_area(self):
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _build_pagination_bar(self):
        self.pager = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"],
            height=44
        )
        self.pager.grid(row=3, column=0, pady=(6, 0), sticky="ew")
        self.pager.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            self.pager,
            text="◀ Anterior",
            width=110,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=13, weight="bold"),
            command=self._prev_page
        )
        self.prev_btn.grid(row=0, column=0, padx=12, pady=6, sticky="w")

        self.page_info_lbl = ctk.CTkLabel(
            self.pager,
            text="Página 1 de 1",
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["text_main"]
        )
        self.page_info_lbl.grid(row=0, column=1, pady=6)

        self.next_btn = ctk.CTkButton(
            self.pager,
            text="Siguiente ▶",
            width=110,
            height=32,
            fg_color=THEME["bg_dark"],
            hover_color=THEME["border"],
            font=ui_font(size=13, weight="bold"),
            command=self._next_page
        )
        self.next_btn.grid(row=0, column=2, padx=12, pady=6, sticky="e")

    def reload_data(self):
        ds = get_datastore()
        raw_calibers = ds.get_calibers()
        self.display_to_raw_caliber = {"TODOS LOS CALIBRES": "TODOS"}
        display_values = ["TODOS LOS CALIBRES"]
        for rc in raw_calibers:
            disp = format_caliber_dropdown(rc)
            self.display_to_raw_caliber[disp] = rc
            display_values.append(disp)

        self.caliber_combo.configure(values=display_values)
        if self.caliber_combo.get() not in self.display_to_raw_caliber:
            self.caliber_combo.set("TODOS LOS CALIBRES")
        self._init_duel_dropdowns()
        if self.is_duel_mode:
            self._render_duel_content()
        self._reset_and_filter()

    def _set_preset(self, mode: str):
        self.preset_mode = mode
        self.btn_all.configure(fg_color=THEME["accent_orange"] if mode == "ALL" else THEME["bg_dark"])
        self.btn_meta.configure(fg_color=THEME["accent_orange"] if mode == "META_PEN" else THEME["bg_dark"])
        self.btn_leg.configure(fg_color=THEME["accent_orange"] if mode == "LEG_META" else THEME["bg_dark"])

        if mode == "META_PEN":
            self.sort_by = "penetration_power"
            self.sort_desc = True
        elif mode == "LEG_META":
            self.sort_by = "damage"
            self.sort_desc = True
        self._reset_and_filter()

    def _toggle_sort(self, field: str):
        if self.sort_by == field:
            self.sort_desc = not self.sort_desc
        else:
            self.sort_by = field
            self.sort_desc = True
        self._reset_and_filter()

    def _on_filter_change(self, _=None):
        self._reset_and_filter()

    def _on_search_debounced(self, event=None):
        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(150, self._reset_and_filter)

    def _reset_and_filter(self):
        self._debounce_job = None
        self.current_page = 0
        self._apply_filters()

    def _apply_filters(self):
        ds = get_datastore()
        selected_disp = self.caliber_combo.get()
        raw_caliber = self.display_to_raw_caliber.get(selected_disp, "TODOS")
        query = self.search_entry.get()

        raw_list = ds.get_ammo(
            caliber=raw_caliber,
            search_query=query,
            sort_by=self.sort_by,
            descending=self.sort_desc
        )

        if self.preset_mode == "META_PEN":
            raw_list = [a for a in raw_list if float(a.get("penetration_power", 0)) >= 40]
        elif self.preset_mode == "LEG_META":
            raw_list = [a for a in raw_list if int(a.get("damage", 0)) >= 75]

        self.filtered_ammo = raw_list
        self._render_current_page()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_current_page()

    def _next_page(self):
        total_pages = max(1, (len(self.filtered_ammo) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.current_page + 1 < total_pages:
            self.current_page += 1
            self._render_current_page()

    def _render_current_page(self):
        self._render_token += 1
        token = self._render_token

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        total_items = len(self.filtered_ammo)
        total_pages = max(1, (total_items + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.current_page = min(self.current_page, total_pages - 1)

        start = self.current_page * self.PAGE_SIZE
        end = min(start + self.PAGE_SIZE, total_items)
        page_slice = self.filtered_ammo[start:end]

        self.page_info_lbl.configure(
            text=f"Página {self.current_page + 1} de {total_pages}  •  Mostrando {len(page_slice)} de {total_items} proyectiles"
        )
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if (self.current_page + 1) < total_pages else "disabled")

        if not page_slice:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No se encontraron proyectiles con los criterios seleccionados.",
                font=ui_font(size=14),
                text_color=THEME["text_muted"]
            ).grid(row=0, column=0, pady=30, padx=20)
            return

        # Grilla unificada con bordes de 1px mediante el fondo de table_grid (#242A36)
        self.table_grid = ctk.CTkFrame(
            self.scroll_frame,
            fg_color="#242A36",
            corner_radius=6,
            border_width=1,
            border_color="#2E3646"
        )
        self.table_grid.grid(row=0, column=0, padx=4, pady=4, sticky="ew")

        for col_idx, (_, col_w, _, _) in enumerate(COLUMNS_SPEC):
            self.table_grid.grid_columnconfigure(col_idx, minsize=col_w, weight=1 if col_idx == 1 else 0)

        # Fila 0: Cabeceras compactas perfectamente alineadas
        for col_idx, (col_title, col_w, sort_field, align) in enumerate(COLUMNS_SPEC):
            is_sorted = (sort_field is not None and self.sort_by == sort_field)
            arrow = (" ▼" if self.sort_desc else " ▲") if is_sorted else ""
            hdr_bg = "#1B202B" if not is_sorted else "#252B3B"

            if sort_field:
                btn = ctk.CTkButton(
                    self.table_grid,
                    text=f"{col_title.replace(' ↕', '')}{arrow}",
                    width=col_w,
                    height=38,
                    corner_radius=0,
                    fg_color=hdr_bg,
                    hover_color=THEME["bg_card_hover"],
                    font=ui_font(size=11, weight="bold"),
                    text_color=THEME["accent_gold"] if is_sorted else C_TEXT_SOFT,
                    anchor=align,
                    command=lambda sf=sort_field: self._toggle_sort(sf)
                )
                btn.grid(row=0, column=col_idx, padx=(0, 1), pady=(0, 1), sticky="nsew")
            else:
                lbl = ctk.CTkLabel(
                    self.table_grid,
                    text=col_title,
                    width=col_w,
                    height=38,
                    fg_color="#181C24",
                    font=ui_font(size=11, weight="bold"),
                    text_color=C_TEXT,
                    justify="center"
                )
                lbl.grid(row=0, column=col_idx, padx=(0, 1), pady=(0, 1), sticky="nsew")

        def render_batch(idx: int):
            if not self.winfo_exists() or token != self._render_token:
                return
            limit = min(idx + 14, len(page_slice))
            for i in range(idx, limit):
                self._create_aligned_ammo_row(i + 1, page_slice[i])
            if limit < len(page_slice):
                self.after(4, lambda: render_batch(limit))

        render_batch(0)

    def _create_aligned_ammo_row(self, grid_row: int, a: Dict[str, Any]):
        row_bg = "#141820" if grid_row % 2 == 1 else "#0F1218"

        pen = float(a.get("penetration_power", 0))
        dmg = int(a.get("damage", 0))
        admg = int(a.get("armor_damage", 0))
        spd = int(a.get("initial_speed", 0))
        cal_clean = format_caliber_short(str(a.get("caliber", "")))
        tracer_str = " [T]" if a.get("tracer") else ""

        # Col 0: Calibre (formateado y separado prolijamente)
        ctk.CTkLabel(
            self.table_grid,
            text=f"  {cal_clean}  ",
            width=132,
            height=32,
            fg_color=row_bg,
            font=ui_font(size=12, weight="bold"),
            text_color=THEME["accent_gold"],
            anchor="w"
        ).grid(row=grid_row, column=0, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Col 1: Proyectil
        ctk.CTkLabel(
            self.table_grid,
            text=f"  {a['name']}{tracer_str}",
            height=32,
            fg_color=row_bg,
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["text_main"],
            anchor="w"
        ).grid(row=grid_row, column=1, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Col 2: Daño
        is_utility = (dmg <= 0 and pen <= 0)
        dmg_col = C_TEXT_DIM if is_utility else (THEME["accent_green"] if dmg >= 75 else THEME["text_main"])
        dmg_txt = "0 (Utilidad)" if is_utility else str(dmg)
        ctk.CTkLabel(
            self.table_grid,
            text=dmg_txt,
            height=32,
            fg_color=row_bg,
            font=ui_font(size=11 if is_utility else 13, weight="bold"),
            text_color=dmg_col
        ).grid(row=grid_row, column=2, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Col 3: Penetración
        pen_col = C_TEXT_DIM if is_utility else (THEME["accent_orange"] if pen >= 40 else (THEME["accent_yellow"] if pen >= 28 else THEME["text_main"]))
        pen_txt = "—" if is_utility else f"{pen:.0f}"
        ctk.CTkLabel(
            self.table_grid,
            text=pen_txt,
            height=32,
            fg_color=row_bg,
            font=ui_font(size=13, weight="bold"),
            text_color=pen_col
        ).grid(row=grid_row, column=3, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Col 4: Daño Armadura %
        ctk.CTkLabel(
            self.table_grid,
            text="—" if is_utility else f"{admg}%",
            height=32,
            fg_color=row_bg,
            font=ui_font(size=12),
            text_color=THEME["text_muted"]
        ).grid(row=grid_row, column=4, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Col 5: Velocidad m/s
        ctk.CTkLabel(
            self.table_grid,
            text=f"{spd}" if spd > 0 else "—",
            height=32,
            fg_color=row_bg,
            font=ui_font(size=12),
            text_color=THEME["text_muted"]
        ).grid(row=grid_row, column=5, padx=(0, 1), pady=(0, 1), sticky="nsew")

        # Cols 6..11: CLASS 1 a CLASS 6 — Celdas sólidas compactas mostrando Score (1..6) o STK (Tiros al Tórax)
        for ac in range(1, 7):
            if is_utility:
                bg_cell, fg_cell = "#181D26", C_TEXT_DIM
                cell_txt = "—"
                f_size = 12
            else:
                eff = calculate_armor_effectiveness(pen, ac)
                score = eff["score"]
                bg_cell, fg_cell = CLASS_SCORE_COLORS.get(score, (eff["color"], C_BG_INSET))

                if self.show_stk_in_table:
                    sim = simulate_shots_to_kill(dmg, pen, admg, ac)
                    stk_val = sim["stk"]
                    cell_txt = f"{stk_val}t" if stk_val < 30 else "30+"
                    f_size = 12
                else:
                    cell_txt = str(score)
                    f_size = 14

            ctk.CTkLabel(
                self.table_grid,
                text=cell_txt,
                width=44,
                height=32,
                fg_color=bg_cell,
                text_color=fg_cell,
                font=ui_font(size=f_size, weight="bold"),
                corner_radius=0
            ).grid(row=grid_row, column=5 + ac, padx=(0, 1), pady=(0, 1), sticky="nsew")
