"""
TarkovScope - Pestaña de Mapas Tácticos con Múltiples Marcadores y Notas Interactivas (Zero-Lag)
Permite:
- Ver planos 2D tácticos reales (Ground Zero, Customs, Reserve, Streets, etc.).
- Elegir dónde poner tantos marcadores/notas como el usuario quiera:
  * Activando el botón "📌 Elegir Punto en Mapa" y haciendo Clic Izquierdo en el punto deseado, o
  * Haciendo Clic Derecho directamente sobre cualquier punto del plano en cualquier momento.
"""
import webbrowser
import customtkinter as ctk
from typing import Dict, Any, List, Optional
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from core.maps_data import normalize_map_key
from core.image_cache import render_map_with_user_markers, get_pin_color_for_index
from ui.image_utils import get_map_ctk_image
from ui.map_viewer_modal import open_map_viewer_modal, AddMarkerDialog, get_pinhead_circle_ctk_image, clean_category_label
from ui.theme import C_AMBER, C_EMERALD, C_RED, C_SLATE_700, C_SLATE_800, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE


class TabMaps(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.maps_list: List[Dict[str, Any]] = []
        self.map_buttons: Dict[str, ctk.CTkButton] = {}
        self.selected_map: Dict[str, Any] = {}
        self._current_img_size = (780, 480)
        self.placing_marker_mode: bool = False
        self._moving_marker_id: Optional[int] = None
        self.layer_pins = ctk.BooleanVar(value=True)
        self.layer_pmc = ctk.BooleanVar(value=True)
        self.layer_scav = ctk.BooleanVar(value=True)
        self.layer_boss = ctk.BooleanVar(value=True)
        self.layer_keys = ctk.BooleanVar(value=True)
        self.layer_loot = ctk.BooleanVar(value=True)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_detail_panel()
        self.reload_data()

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=265,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        sidebar.grid(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(1, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            sidebar,
            text="🗺️ MAPAS DE TARKOV",
            font=ui_font(size=17, weight="bold"),
            text_color=THEME["accent_orange"]
        ).grid(row=0, column=0, padx=16, pady=(16, 10), sticky="w")

        self.list_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.list_scroll.grid(row=1, column=0, padx=8, pady=(0, 12), sticky="nsew")
        self.list_scroll.grid_columnconfigure(0, weight=1)

    def _build_detail_panel(self):
        self.detail_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.detail_frame.grid(row=0, column=1, sticky="nsew")
        self.detail_frame.grid_columnconfigure(0, weight=1)
        self.detail_frame.grid_columnconfigure(1, weight=1)

    def reload_data(self):
        for w in self.list_scroll.winfo_children():
            w.destroy()
        self.map_buttons.clear()

        self.maps_list = get_datastore().get_maps()
        if not self.maps_list:
            return

        for idx, m in enumerate(self.maps_list):
            m_key = m.get("key") or normalize_map_key(m["name"])
            dur_str = m.get("raid_duration_str", "40 min").split(" (")[0]
            btn = ctk.CTkButton(
                self.list_scroll,
                text=f"📍  {m['name']}  ({dur_str})",
                anchor="w",
                height=44,
                corner_radius=8,
                font=ui_font(size=14, weight="bold"),
                fg_color="transparent",
                text_color=THEME["text_main"],
                hover_color=THEME["bg_card_hover"],
                command=lambda mp=m: self._select_map(mp)
            )
            btn.grid(row=idx, column=0, padx=4, pady=3, sticky="ew")
            self.map_buttons[m_key] = btn

        gz = next((x for x in self.maps_list if x.get("key") == "groundzero"), self.maps_list[0])
        self._select_map(gz)

    def select_map_by_name(self, map_name: str):
        target_key = normalize_map_key(map_name)
        for m in self.maps_list:
            if m.get("key") == target_key:
                self._select_map(m)
                return

    def _refresh_active_map_view(self):
        if not self.selected_map:
            return
        if hasattr(self, "map_img_lbl") and self.map_img_lbl.winfo_exists() and hasattr(self, "markers_box") and self.markers_box.winfo_exists():
            active_key = self.selected_map.get("key") or normalize_map_key(self.selected_map["name"])
            markers = get_datastore().get_markers(active_key)
            pil_with_markers = render_map_with_user_markers(
                active_key,
                markers,
                target_size=(780, 480),
                high_res=False,
                show_pins=self.layer_pins.get(),
                show_pmc=self.layer_pmc.get(),
                show_scav=self.layer_scav.get(),
                show_boss=self.layer_boss.get(),
                show_keys=self.layer_keys.get(),
                show_loot=self.layer_loot.get()
            )
            self._current_img_size = pil_with_markers.size
            self._ctk_current_map = ctk.CTkImage(light_image=pil_with_markers, dark_image=pil_with_markers, size=pil_with_markers.size)
            self.map_img_lbl.configure(image=self._ctk_current_map)
            self._populate_markers_box(markers)
            return

        self._select_map(self.selected_map, keep_place_mode=self.placing_marker_mode)

    def _populate_markers_box(self, markers: list):
        for w in self.markers_box.winfo_children():
            w.destroy()

        m = self.selected_map
        self.markers_box.configure(border_color=THEME["accent_orange"] if markers else THEME["border"])

        mk_hdr = ctk.CTkFrame(self.markers_box, fg_color="transparent")
        mk_hdr.grid(row=0, column=0, padx=16, pady=(12, 6), sticky="ew")
        mk_hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            mk_hdr,
            text=f"📌 MIS NOTAS Y MARCADORES EN {m['name'].upper()} ({len(markers)} activos — podés agregar todos los que necesites)",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_orange"]
        ).grid(row=0, column=0, sticky="w")

        if len(markers) > 1:
            ctk.CTkButton(
                mk_hdr,
                text="🗑️ Borrar Todos",
                width=125,
                height=28,
                fg_color=THEME["bg_card"],
                hover_color=THEME["accent_red"],
                font=ui_font(size=12, weight="bold"),
                command=lambda mlist=markers: self._clear_all_markers(mlist)
            ).grid(row=0, column=1, sticky="e")

        if not markers:
            ctk.CTkLabel(
                self.markers_box,
                text="Todavía no pusiste marcadores en este mapa. Tocá el botón '📌 Elegir Punto y Poner Nota' y hacé clic donde quieras en el mapa (o usá Clic Derecho directo sobre el mapa) para poner 1, 2 o todos los marcadores que quieras.",
                font=ui_font(size=13),
                text_color=THEME["text_muted"],
                wraplength=880,
                justify="left"
            ).grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")
        else:
            used_cols = []
            for idx, mk in enumerate(markers, start=1):
                raw_c = (mk.get("color") or "").strip()
                if not raw_c or raw_c.upper() == "#E5732F" or (used_cols and raw_c.upper() == used_cols[-1]):
                    raw_c = get_pin_color_for_index(idx - 1)
                used_cols.append(raw_c.upper())

                mk_row = ctk.CTkFrame(self.markers_box, fg_color=THEME["bg_card"], corner_radius=6)
                mk_row.grid(row=idx, column=0, padx=16, pady=3, sticky="ew")
                mk_row.grid_columnconfigure(2, weight=1)

                ctk.CTkLabel(
                    mk_row,
                    text=f"  Alfiler #{idx} ",
                    image=get_pinhead_circle_ctk_image(raw_c, 16),
                    compound="left",
                    font=ui_font(size=12, weight="bold"),
                    fg_color="#161C28",
                    text_color=raw_c,
                    corner_radius=4
                ).grid(row=0, column=0, padx=10, pady=6)

                ctk.CTkLabel(
                    mk_row,
                    text=f"[{clean_category_label(mk.get('category', 'Nota'))}]",
                    font=ui_font(size=12, weight="bold"),
                    text_color=raw_c
                ).grid(row=0, column=1, padx=(0, 10), pady=6, sticky="w")

                ctk.CTkLabel(
                    mk_row,
                    text=f"{mk.get('title', '')}   (Posición: {float(mk['x_pct'])*100:.1f}%, {float(mk['y_pct'])*100:.1f}%)",
                    font=ui_font(size=13, weight="bold"),
                    text_color=THEME["text_main"],
                    anchor="w"
                ).grid(row=0, column=2, padx=4, pady=6, sticky="ew")

                ctk.CTkButton(
                    mk_row,
                    text="📍 Mover",
                    width=75,
                    height=26,
                    fg_color=C_SLATE_800,
                    hover_color=C_SLATE_700,
                    font=ui_font(size=12, weight="bold"),
                    command=lambda mid=mk["id"], title=mk.get("title", "Alfiler"): self._start_move_marker(mid, title)
                ).grid(row=0, column=3, padx=(4, 2), pady=6)

                ctk.CTkButton(
                    mk_row,
                    text="🗑️ Quitar",
                    width=75,
                    height=26,
                    fg_color=THEME["accent_red"],
                    hover_color="#B91C1C",
                    font=ui_font(size=12, weight="bold"),
                    command=lambda mid=mk["id"]: self._delete_marker(mid)
                ).grid(row=0, column=4, padx=(2, 10), pady=6)

            ctk.CTkLabel(self.markers_box, text="", height=4).grid(row=len(markers) + 1, column=0)

    def _toggle_place_marker_mode(self):
        self.placing_marker_mode = not self.placing_marker_mode
        self._update_place_mode_visuals()

    def _update_place_mode_visuals(self):
        if not hasattr(self, "btn_place_marker") or not self.btn_place_marker.winfo_exists():
            return
        if self.placing_marker_mode:
            self.btn_place_marker.configure(
                text="🎯 Hacé Clic en el Mapa... (Activo)",
                fg_color=THEME["accent_green"],
                text_color="#0F1115"
            )
            self.map_hint_lbl.configure(
                text="🎯 MODO COLOCAR MARCADOR ACTIVO: Hacé CLIC IZQUIERDO en el punto exacto del mapa donde quieras poner tu nota (podés agregar múltiples marcadores)",
                text_color=THEME["accent_green"]
            )
            self.map_canvas_box.configure(border_color=THEME["accent_green"], border_width=2)
            self.map_img_lbl.configure(cursor="tcross")
        else:
            self.btn_place_marker.configure(
                text="📌 Elegir Punto y Poner Nota",
                fg_color=THEME["accent_orange"],
                text_color=C_WHITE
            )
            self.map_hint_lbl.configure(
                text="📐 PLANO TÁCTICO 2D  —  📌 Clic Derecho (o botón 'Elegir Punto'): Poner Marcador donde hagas clic   |   🔍 Clic Izquierdo: Zoom HD",
                text_color=THEME["accent_yellow"]
            )
            self.map_canvas_box.configure(border_color=THEME["border"], border_width=1)
            self.map_img_lbl.configure(cursor="hand2")

    def _select_map(self, m: Dict[str, Any], keep_place_mode: bool = False):
        self.selected_map = m
        if not keep_place_mode:
            self.placing_marker_mode = False
        active_key = m.get("key") or normalize_map_key(m["name"])

        for m_key, btn in self.map_buttons.items():
            if m_key == active_key:
                btn.configure(fg_color=THEME["accent_orange"], text_color=C_WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_main"])

        for w in self.detail_frame.winfo_children():
            w.destroy()

        ds = get_datastore()
        markers = ds.get_markers(active_key)

        # 1. Encabezado Táctico del Mapa
        header = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        header.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=18, pady=14, sticky="w")

        ctk.CTkLabel(
            title_box,
            text=f"🗺️ {m['name'].upper()}",
            font=ui_font(size=24, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w")

        meta_str = f"⏱️ Duración: {m.get('raid_duration_str', '40 min')}   |   👥 Jugadores: {m.get('players', '10-12 PMCs')}"
        ctk.CTkLabel(
            title_box,
            text=meta_str,
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_green"]
        ).pack(anchor="w", pady=(4, 2))

        if m.get("level_note"):
            ctk.CTkLabel(
                title_box,
                text=f"ℹ️ {m['level_note']}",
                font=ui_font(size=13),
                text_color=THEME["accent_yellow"]
            ).pack(anchor="w")

        actions_box = ctk.CTkFrame(header, fg_color="transparent")
        actions_box.grid(row=0, column=1, padx=18, pady=14, sticky="e")

        self.btn_place_marker = ctk.CTkButton(
            actions_box,
            text="📌 Elegir Punto y Poner Nota",
            height=38,
            fg_color=THEME["accent_orange"],
            hover_color="#C2591A",
            font=ui_font(size=13, weight="bold"),
            command=self._toggle_place_marker_mode
        )
        self.btn_place_marker.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            actions_box,
            text="🔍 Abrir Plano en HD (Zoom / Pan)",
            height=38,
            fg_color=THEME["accent_blue"],
            hover_color="#2563EB",
            font=ui_font(size=13, weight="bold"),
            command=lambda: open_map_viewer_modal(self, m["name"], on_markers_changed=self._refresh_active_map_view)
        ).pack(side="left", padx=(0, 8))

        if m.get("wiki_url"):
            ctk.CTkButton(
                actions_box,
                text="🌐 Wiki",
                width=95,
                height=38,
                fg_color=THEME["bg_card"],
                hover_color=THEME["border"],
                font=ui_font(size=13, weight="bold"),
                command=lambda u=m["wiki_url"]: webbrowser.open(u)
            ).pack(side="left")

        # 2. Visor del Plano 2D Táctico (Soporta elegir punto exacto con Clic Izquierdo en Modo Pin o Clic Derecho directo)
        self.map_canvas_box = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.map_canvas_box.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        self.map_canvas_box.grid_columnconfigure(0, weight=1)

        self.map_hint_lbl = ctk.CTkLabel(
            self.map_canvas_box,
            text="📐 PLANO TÁCTICO 2D  —  📌 Clic Derecho (o botón 'Elegir Punto'): Poner Marcador donde hagas clic   |   🔍 Clic Izquierdo: Zoom HD",
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["accent_yellow"]
        )
        self.map_hint_lbl.grid(row=0, column=0, padx=16, pady=(12, 4), sticky="w")

        layers_row = ctk.CTkFrame(self.map_canvas_box, fg_color="transparent")
        layers_row.grid(row=1, column=0, padx=16, pady=(0, 6), sticky="w")
        ctk.CTkLabel(layers_row, text="Capas:", font=ui_font(12, "bold"), text_color=C_TEXT_DIM).pack(side="left", padx=(0, 6))
        ctk.CTkCheckBox(layers_row, text="Alfileres", variable=self.layer_pins, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color=THEME["accent_orange"], width=82, height=22).pack(side="left", padx=3)
        ctk.CTkCheckBox(layers_row, text="Extracciones PMC", variable=self.layer_pmc, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color=C_EMERALD, width=128, height=22).pack(side="left", padx=3)
        ctk.CTkCheckBox(layers_row, text="Extracciones Scav", variable=self.layer_scav, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color=C_AMBER, width=128, height=22).pack(side="left", padx=3)
        ctk.CTkCheckBox(layers_row, text="Spawns Boss", variable=self.layer_boss, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color=C_RED, width=105, height=22).pack(side="left", padx=3)
        ctk.CTkCheckBox(layers_row, text="🔑 Llaves / Marked", variable=self.layer_keys, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color="#A855F7", width=132, height=22).pack(side="left", padx=3)
        ctk.CTkCheckBox(layers_row, text="💎 Cajas Fuertes / Loot", variable=self.layer_loot, command=self._refresh_active_map_view, font=ui_font(11, "bold"), text_color=C_TEXT_MUTED, fg_color="#06B6D4", width=150, height=22).pack(side="left", padx=3)

        pil_with_markers = render_map_with_user_markers(
            active_key,
            markers,
            target_size=(780, 480),
            high_res=False,
            show_pins=self.layer_pins.get(),
            show_pmc=self.layer_pmc.get(),
            show_scav=self.layer_scav.get(),
            show_boss=self.layer_boss.get(),
            show_keys=self.layer_keys.get(),
            show_loot=self.layer_loot.get()
        )
        self._current_img_size = pil_with_markers.size
        ctk_map = ctk.CTkImage(light_image=pil_with_markers, dark_image=pil_with_markers, size=pil_with_markers.size)

        img_w, img_h = self._current_img_size
        self.map_img_lbl = ctk.CTkLabel(
            self.map_canvas_box,
            text="",
            image=ctk_map,
            width=img_w,
            height=img_h,
            cursor="hand2"
        )
        self.map_img_lbl.grid(row=2, column=0, padx=16, pady=(4, 14))

        def _open_marker_at_click(event):
            w_i, h_i = max(1, self._current_img_size[0]), max(1, self._current_img_size[1])
            x_pct = max(0.01, min(0.99, event.x / w_i))
            y_pct = max(0.01, min(0.99, event.y / h_i))
            AddMarkerDialog(self, m["name"], x_pct, y_pct, on_saved=self._refresh_active_map_view)

        def _on_left_click_map(event):
            if self._moving_marker_id is not None:
                w_i, h_i = max(1, self._current_img_size[0]), max(1, self._current_img_size[1])
                x_pct = max(0.01, min(0.99, event.x / w_i))
                y_pct = max(0.01, min(0.99, event.y / h_i))
                get_datastore().update_marker_pos(self._moving_marker_id, x_pct, y_pct)
                self._moving_marker_id = None
                self._refresh_active_map_view()
                return
            if self.placing_marker_mode:
                _open_marker_at_click(event)
            else:
                open_map_viewer_modal(self, m["name"], on_markers_changed=self._refresh_active_map_view)

        self.map_img_lbl.bind("<Button-1>", _on_left_click_map)
        self.map_img_lbl.bind("<Button-3>", _open_marker_at_click)

        self._update_place_mode_visuals()

        # 3. Panel de Marcadores y Notas Personalizadas del Usuario en este Mapa
        self.markers_box = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["accent_orange"] if markers else THEME["border"]
        )
        self.markers_box.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        self.markers_box.grid_columnconfigure(0, weight=1)
        self._populate_markers_box(markers)

        # 4. Extracciones del Mapa
        ext_box = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        ext_box.grid(row=3, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        ext_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ext_box,
            text="🚁 PUNTOS DE EXTRACCIÓN (PMC, SCAV, VEHÍCULO V-EX, CO-OP Y BENGALAS)",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_green"]
        ).grid(row=0, column=0, padx=16, pady=(12, 8), sticky="w")

        extractions = m.get("extractions", [])
        for idx, ex in enumerate(extractions, start=1):
            row_f = ctk.CTkFrame(ext_box, fg_color=THEME["bg_card"], corner_radius=6)
            row_f.grid(row=idx, column=0, padx=16, pady=3, sticky="ew")
            row_f.grid_columnconfigure(2, weight=1)

            fac = ex.get("faction", "PMC")
            badge_col = THEME["accent_green"]
            if "Vehículo" in fac or "Bengala" in fac:
                badge_col = THEME["accent_yellow"]
            elif "Co-Op" in fac:
                badge_col = THEME["accent_blue"]
            elif fac == "Scav":
                badge_col = THEME["accent_orange"]

            ctk.CTkLabel(
                row_f,
                text=f" {fac} ",
                width=115,
                font=ui_font(size=12, weight="bold"),
                fg_color=badge_col,
                text_color="#0F1115" if badge_col == THEME["accent_yellow"] else C_WHITE,
                corner_radius=4
            ).grid(row=0, column=0, padx=10, pady=7)

            ctk.CTkLabel(
                row_f,
                text=ex.get("name", ""),
                font=ui_font(size=14, weight="bold"),
                text_color=THEME["text_main"]
            ).grid(row=0, column=1, padx=(2, 12), pady=7, sticky="w")

            ctk.CTkLabel(
                row_f,
                text=ex.get("req", ""),
                font=ui_font(size=13),
                text_color=THEME["text_muted"],
                anchor="w"
            ).grid(row=0, column=2, padx=6, pady=7, sticky="ew")

        ctk.CTkLabel(ext_box, text="", height=4).grid(row=len(extractions) + 1, column=0)

        # 5. Llaves Recomendadas & Puntos Calientes (Izquierda) + Jefes y Transits (Derecha)
        left_col = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        left_col.grid(row=4, column=0, padx=(16, 8), pady=(0, 16), sticky="nsew")

        ctk.CTkLabel(
            left_col,
            text="🔑 LLAVES IMPRESCINDIBLES & ZONAS DE BOTÍN",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_yellow"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        for k_item in m.get("keys", []):
            ctk.CTkLabel(
                left_col,
                text=f"• {k_item}",
                font=ui_font(size=13),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=3)

        ctk.CTkLabel(
            left_col,
            text="🔥 Zonas Calientes (Hotspots):",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        for hs in m.get("hotspots", []):
            ctk.CTkLabel(
                left_col,
                text=f"  ▸ {hs}",
                font=ui_font(size=13),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=2)

        ctk.CTkLabel(left_col, text="", height=8).pack()

        right_col = ctk.CTkFrame(
            self.detail_frame,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        right_col.grid(row=4, column=1, padx=(8, 16), pady=(0, 16), sticky="nsew")

        ctk.CTkLabel(
            right_col,
            text="💀 JEFES, AMENAZAS Y TRANSITS",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_red"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        for enemy in m.get("enemies", []):
            ctk.CTkLabel(
                right_col,
                text=f"• {enemy}",
                font=ui_font(size=13, weight="bold"),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=3)

        ctk.CTkLabel(
            right_col,
            text="🔄 Conexiones Transit a otros mapas:",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_blue"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        for tr in m.get("transits", []):
            ctk.CTkLabel(
                right_col,
                text=f"  ⇄ {tr}",
                font=ui_font(size=13),
                text_color=THEME["text_main"],
                justify="left",
                wraplength=420
            ).pack(anchor="w", padx=16, pady=2)

        ctk.CTkLabel(
            right_col,
            text="📖 Resumen Táctico:",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w", padx=16, pady=(12, 4))

        ctk.CTkLabel(
            right_col,
            text=m.get("description", ""),
            font=ui_font(size=13),
            text_color=THEME["text_muted"],
            justify="left",
            wraplength=420
        ).pack(anchor="w", padx=16, pady=(0, 14))

    def _delete_marker(self, marker_id: int):
        get_datastore().delete_marker(marker_id)
        self._refresh_active_map_view()

    def _start_move_marker(self, marker_id: int, marker_title: str):
        self._moving_marker_id = marker_id
        if hasattr(self, "map_img_lbl"):
            self.map_img_lbl.configure(cursor="tcross")
        if hasattr(self, "map_hint_lbl"):
            self.map_hint_lbl.configure(
                text=f"🎯 REUBICACIÓN ACTIVA: Hacé clic sobre el mapa para mover '{marker_title}' a una nueva posición.",
                text_color=THEME["accent_green"]
            )

    def _clear_all_markers(self, markers_list: List[Dict[str, Any]]):
        ds = get_datastore()
        for mk in markers_list:
            ds.delete_marker(mk["id"])
        self._refresh_active_map_view()
