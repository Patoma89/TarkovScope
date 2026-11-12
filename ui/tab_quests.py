"""
TarkovScope - Pestaña de Quests & Traders
Diseño de Tabla estilo Escape from Tarkov Wiki con sub-pestañas:
1) [ 📜 Misiones & Quests ]:
   - Galería superior con los 11 Traders oficiales (Prapor, Therapist, Fence, Skier, Peacekeeper,
     Mechanic, Ragman, Jaeger, Lightkeeper, BTR Driver, Ref).
   - Tabla interactiva estilo Wiki (✓ | Quest | Objectives | Rewards) con alto contraste.
   - Modos: 'Progresión Correlativa', 'Requeridas para KAPPA', 'Ruta LIGHTKEEPER' y 'Todas las Misiones'.
2) [ 🛒 Inventario & Barters (LL1 a LL4) ]:
   - Catálogo oficial por comerciante (Prapor, Therapist, Skier, Peacekeeper, Mechanic, Ragman, Jaeger, Ref, Fence).
   - Selector de nivel de lealtad (LL1, LL2, LL3, LL4 Corona) con desglose de requisitos (Nivel, Reputación, Gasto).
   - Tarjetas de armamento, munición, blindajes y recetas de trueque (barters) con imágenes oficiales.
"""
import webbrowser
import customtkinter as ctk
from typing import List, Dict, Any, Optional
from core.config import THEME
from core.datastore import get_datastore
from ui.theme import ui_font
from ui.image_utils import get_trader_ctk_image
from ui.map_viewer_modal import open_map_viewer_modal
from ui.theme import C_AMBER, C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL, C_BG_ROW, C_BG_ROW_ALT, C_BORDER, C_BORDER_ALT, C_BORDER_SOFT, C_GREEN, C_GREEN_LIGHT, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE
from ui.quest_guide_modal import QuestGuideModal, extract_required_keys
from ui.tab_quests_assortment import AssortmentViewMixin


WIKI_TRADERS_ORDER = [
    "Prapor",
    "Therapist",
    "Fence",
    "Skier",
    "Peacekeeper",
    "Mechanic",
    "Ragman",
    "Jaeger",
    "Lightkeeper",
    "BTR Driver",
    "Ref",
]


TRADER_NOTES: Dict[str, str] = {
    "TODOS": "Nota: Mostrando las misiones de Escape from Tarkov de los 11 Traders. Haz clic en cualquier retrato arriba para filtrar por Trader.",
    "Prapor": "Nota: Prapor se desbloquea progresando en el capítulo inicial Tour y provee armamento del Pacto de Varsovia y munición rusa.",
    "Therapist": "Nota: Therapist está disponible desde el inicio; se especializa en suministros médicos, llaves, contenedores y misiones humanitarias.",
    "Fence": "Nota: Fence ofrece encargos de Karma Scav y desbloquea la misión final 'Collector' (Contenedor Seguro Kappa) al completar todas las misiones Kappa.",
    "Skier": "Nota: Skier se desbloquea avanzando por las primeras misiones en Ground Zero; comercializa accesorios occidentales, armas y divisas.",
    "Peacekeeper": "Nota: Para desbloquear las misiones de Peacekeeper debes completar primero la misión de Skier 'Friend From the West - Part 2'.",
    "Mechanic": "Nota: Mechanic ofrece la serie de armería 'Gunsmith' (Partes 1 a 25), tareas electrónicas y la cadena 'Network Provider' hacia Lightkeeper.",
    "Ragman": "Nota: Ragman se especializa en chalecos tácticos, blindajes corporales, cascos, mochilas y operaciones en Interchange.",
    "Jaeger": "Nota: Para desbloquear a Jaeger debes completar la misión de Mechanic 'Introduction' en Woods.",
    "Lightkeeper": "Nota: Para acceder a Lightkeeper en la isla del faro (Lighthouse) debes completar la cadena 'Network Provider' y 'Getting Acquainted' de Mechanic.",
    "BTR Driver": "Nota: El Conductor del BTR ofrece transporte blindado, extracción de botín y su propia cadena de misiones en Streets of Tarkov y Woods.",
    "Ref": "Nota: Para desbloquear a Ref (The Host) debes completar la misión de Skier 'Easy Money - Part 1'; acepta monedas GP.",
}

MAP_FILTER_OPTIONS = [
    "TODOS LOS MAPAS",
    "Ground Zero",
    "Customs",
    "Woods",
    "Factory",
    "Interchange",
    "Shoreline",
    "Reserve",
    "Lighthouse",
    "Streets of Tarkov",
    "The Lab",
]

COL_CHECK_W = 50
COL_QUEST_W = 285
COL_OBJ_W = 470
COL_REW_W = 280


class TabQuests(AssortmentViewMixin, ctk.CTkFrame):
    PAGE_SIZE = 20

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        # Estado Sub-Pestaña Activa ('quests' o 'assortment')
        self._active_subtab = "quests"

        # Estado Vista 1: Quests
        self.filtered_quests: List[Dict[str, Any]] = []
        self.selected_trader = "TODOS"  # por defecto: todos los traders marcados
        self.selected_map = "TODOS LOS MAPAS"
        self.progression_mode = "CORRELATIVE"  # "CORRELATIVE", "KAPPA", "LIGHTKEEPER", "ALL"
        self.trader_cards: Dict[str, ctk.CTkFrame] = {}
        self.trader_name_labels: Dict[str, ctk.CTkLabel] = {}
        self.mode_buttons: Dict[str, ctk.CTkButton] = {}
        self.current_page = 0
        self._render_token = 0
        self._debounce_job: Optional[str] = None

        # Estado Vista 2: Assortment & Barters
        self.selected_assort_trader = "Prapor"
        self.selected_ll = 1
        self.assort_view_mode = "GRID"  # "GRID" (cuadrícula auténtica in-game de la wiki) o "LIST"
        self.assort_category_filter = "TODAS LAS CATEGORÍAS"
        self.assort_trader_cards: Dict[str, ctk.CTkFrame] = {}
        self.assort_trader_name_lbls: Dict[str, ctk.CTkLabel] = {}
        self.ll_buttons: Dict[int, ctk.CTkButton] = {}
        self._assort_debounce_job: Optional[str] = None
        self._assort_render_token = 0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Selector Superior de Sub-Pestañas
        self._build_subtab_header()

        # 2. Contenedor de Vistas
        self.views_container = ctk.CTkFrame(self, fg_color="transparent")
        self.views_container.grid(row=1, column=0, sticky="nsew")
        self.views_container.grid_columnconfigure(0, weight=1)
        self.views_container.grid_rowconfigure(0, weight=1)

        # Vista 1: Misiones
        self.quests_view = ctk.CTkFrame(self.views_container, fg_color="transparent")
        self.quests_view.grid(row=0, column=0, sticky="nsew")
        self.quests_view.grid_columnconfigure(0, weight=1)
        self.quests_view.grid_rowconfigure(3, weight=1)

        # Vista 2: Assortment
        self.assortment_view = ctk.CTkFrame(self.views_container, fg_color="transparent")
        self.assortment_view.grid(row=0, column=0, sticky="nsew")
        self.assortment_view.grid_columnconfigure(0, weight=1)
        self.assortment_view.grid_rowconfigure(3, weight=1)

        # Construir ambas vistas
        self._setup_quests_view()
        self._setup_assortment_view()

        # Mostrar por defecto Quests
        self._switch_subtab("quests")
        self.reload_data()

    # =========================================================================
    # BARRA SUPERIOR DE SUB-PESTAÑAS
    # =========================================================================
    def _build_subtab_header(self):
        switcher_bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT,
            height=46
        )
        switcher_bar.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        switcher_bar.grid_columnconfigure(2, weight=1)

        self.btn_subtab_quests = ctk.CTkButton(
            switcher_bar,
            text="📜  Misiones & Quests",
            font=ui_font(13, "bold"),
            height=34,
            corner_radius=6,
            border_width=1,
            border_color=THEME["accent_gold"],
            fg_color="#1E2536",
            hover_color="#273147",
            text_color=C_WHITE,
            command=lambda: self._switch_subtab("quests")
        )
        self.btn_subtab_quests.grid(row=0, column=0, padx=(8, 4), pady=5)

        self.btn_subtab_assort = ctk.CTkButton(
            switcher_bar,
            text="🛒  Inventario & Barters (LL1 a LL4)",
            font=ui_font(13, "bold"),
            height=34,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER,
            fg_color="transparent",
            hover_color="#1F2637",
            text_color=C_TEXT_DIM,
            command=lambda: self._switch_subtab("assortment")
        )
        self.btn_subtab_assort.grid(row=0, column=1, padx=4, pady=5)

        self.subtab_info_lbl = ctk.CTkLabel(
            switcher_bar,
            text="Escape from Tarkov Wiki Database",
            font=ui_font(11, "bold"),
            text_color="#64748B"
        )
        self.subtab_info_lbl.grid(row=0, column=2, padx=14, pady=5, sticky="e")

    def _switch_subtab(self, subtab_key: str):
        self._active_subtab = subtab_key
        if subtab_key == "quests":
            self.quests_view.tkraise()
            self.btn_subtab_quests.configure(
                fg_color="#1E2536",
                border_color=THEME["accent_gold"],
                text_color=C_WHITE
            )
            self.btn_subtab_assort.configure(
                fg_color="transparent",
                border_color=C_BORDER,
                text_color=C_TEXT_DIM
            )
            self.subtab_info_lbl.configure(text="Escape from Tarkov Official Quests")
        else:
            self.assortment_view.tkraise()
            self.btn_subtab_assort.configure(
                fg_color="#1E2536",
                border_color=THEME["accent_gold"],
                text_color=C_WHITE
            )
            self.btn_subtab_quests.configure(
                fg_color="transparent",
                border_color=C_BORDER,
                text_color=C_TEXT_DIM
            )
            self.subtab_info_lbl.configure(text="Trader Assortment & Loyalty Levels (LL1-LL4)")
            self._apply_assortment_filters()

    # =========================================================================
    # VISTA 1: MISIONES & QUESTS
    # =========================================================================
    def _setup_quests_view(self):
        self._build_traders_gallery()
        self._build_search_and_filters()
        self._build_wiki_table_header()
        self._build_quest_list_area()
        self._build_pagination_bar()

    def _build_traders_gallery(self):
        gallery_outer = ctk.CTkFrame(
            self.quests_view,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        gallery_outer.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        gallery_outer.grid_columnconfigure(0, weight=1)

        # Cabecera estilo Wiki ("List of Quests" + Botón Todos + Contadores)
        header_row = ctk.CTkFrame(gallery_outer, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=14, pady=(8, 4), sticky="ew")
        header_row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            header_row,
            text="Listado de Misiones (Quests)",
            font=ui_font(18, "bold"),
            text_color=C_TEXT
        ).grid(row=0, column=0, padx=(0, 12), sticky="w")

        self.all_traders_btn = ctk.CTkButton(
            header_row,
            text="Todos los Traders",
            height=28,
            width=150,
            corner_radius=5,
            fg_color="#252F42" if self.selected_trader == "TODOS" else C_BG_ROW,
            hover_color=C_BORDER_ALT,
            border_width=1,
            border_color=C_WHITE if self.selected_trader == "TODOS" else "#384152",
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=lambda: self._select_trader("TODOS")
        )
        self.all_traders_btn.grid(row=0, column=1, sticky="w")

        self.unlock_notice_lbl = ctk.CTkLabel(
            header_row,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"]
        )
        self.unlock_notice_lbl.grid(row=0, column=2, padx=12)

        self.stats_lbl = ctk.CTkLabel(
            header_row,
            text="Total: 0 completadas (0%)",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_green"]
        )
        self.stats_lbl.grid(row=0, column=3, sticky="e")

        # Galería horizontal de los 11 Traders con retratos cuadrados como en la Wiki
        traders_row = ctk.CTkFrame(gallery_outer, fg_color="transparent")
        traders_row.grid(row=1, column=0, padx=10, pady=(2, 4), sticky="ew")

        for idx, t_name in enumerate(WIKI_TRADERS_ORDER):
            traders_row.grid_columnconfigure(idx, weight=1)
            is_sel = self.selected_trader == "TODOS" or t_name == self.selected_trader

            card = ctk.CTkFrame(
                traders_row,
                fg_color="#141820",
                corner_radius=4,
                border_width=2,
                border_color=C_WHITE if is_sel else "#2A303C",
                cursor="hand2"
            )
            card.grid(row=0, column=idx, padx=3, pady=2, sticky="nsew")
            self.trader_cards[t_name] = card

            img_lbl = ctk.CTkLabel(card, text="")
            img_lbl.pack(padx=3, pady=(3, 1))

            def make_cb(label_widget):
                def _cb(new_img):
                    if label_widget.winfo_exists():
                        self.after(0, lambda: label_widget.configure(image=new_img))
                return _cb

            ctk_img = get_trader_ctk_image(t_name, size=(68, 68), widget_callback=make_cb(img_lbl))
            img_lbl.configure(image=ctk_img)

            name_lbl = ctk.CTkLabel(
                card,
                text=t_name,
                font=ui_font(11, "bold"),
                text_color=C_WHITE if is_sel else C_TEXT_MUTED
            )
            name_lbl.pack(padx=2, pady=(0, 3))
            self.trader_name_labels[t_name] = name_lbl

            for w in (card, img_lbl, name_lbl):
                w.bind("<Button-1>", lambda e, tr=t_name: self._select_trader(tr))

        # Nota contextual del Trader debajo de los retratos
        self.trader_note_lbl = ctk.CTkLabel(
            gallery_outer,
            text=TRADER_NOTES.get(self.selected_trader, ""),
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            anchor="w"
        )
        self.trader_note_lbl.grid(row=2, column=0, padx=14, pady=(2, 8), sticky="ew")

    def _build_search_and_filters(self):
        bar = ctk.CTkFrame(
            self.quests_view,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        bar.grid_columnconfigure(2, weight=1)

        modes_row = ctk.CTkFrame(bar, fg_color="transparent")
        modes_row.grid(row=0, column=0, columnspan=4, padx=12, pady=(7, 5), sticky="ew")

        modes_spec = [
            ("CORRELATIVE", "Progresión Correlativa"),
            ("KAPPA", "Requeridas para KAPPA"),
            ("LIGHTKEEPER", "Ruta LIGHTKEEPER"),
            ("ALL", "Todas las Misiones"),
        ]
        for m_key, m_label in modes_spec:
            is_act = (m_key == self.progression_mode)
            btn = ctk.CTkButton(
                modes_row,
                text=m_label,
                height=30,
                corner_radius=5,
                border_width=1,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
                fg_color=C_BG_ROW_ALT if is_act else C_BG_PANEL,
                hover_color="#2A3244",
                text_color=C_WHITE if is_act else C_TEXT_MUTED,
                font=ui_font(12, "bold"),
                command=lambda mk=m_key: self._set_progression_mode(mk)
            )
            btn.pack(side="left", padx=(0, 6))
            self.mode_buttons[m_key] = btn

        self.hide_completed_var = ctk.BooleanVar(value=False)
        hide_chk = ctk.CTkCheckBox(
            modes_row,
            text="Ocultar completadas",
            variable=self.hide_completed_var,
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_green"],
            command=self._reset_and_apply_filters
        )
        hide_chk.pack(side="right", padx=6)

        self.search_entry = ctk.CTkEntry(
            modes_row,
            placeholder_text="Buscar misión, objetivo o recompensa...",
            width=260,
            height=30,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12)
        )
        self.search_entry.pack(side="right", padx=6)
        self.search_entry.bind("<KeyRelease>", self._on_search_key_debounced)

        self.map_combo = ctk.CTkComboBox(
            modes_row,
            values=MAP_FILTER_OPTIONS,
            width=170,
            height=30,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            state="readonly",
            command=self._on_map_filter_change
        )
        self.map_combo.set("TODOS LOS MAPAS")
        self.map_combo.pack(side="right", padx=6)

    def _build_wiki_table_header(self):
        hdr = ctk.CTkFrame(
            self.quests_view,
            fg_color="#141821",
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER,
            height=36
        )
        hdr.grid(row=2, column=0, padx=0, pady=(0, 2), sticky="ew")
        hdr.grid_columnconfigure(0, minsize=COL_CHECK_W, weight=0)
        hdr.grid_columnconfigure(1, minsize=COL_QUEST_W, weight=0)
        hdr.grid_columnconfigure(2, minsize=COL_OBJ_W, weight=3)
        hdr.grid_columnconfigure(3, minsize=COL_REW_W, weight=2)

        cols = [
            (0, "✓", COL_CHECK_W, "center"),
            (1, "Misión (Quest)  ▴▾", COL_QUEST_W, "center"),
            (2, "Objetivos Tácticos  ▴▾", COL_OBJ_W, "center"),
            (3, "Recompensas & Guía  ▴▾", COL_REW_W, "center"),
        ]
        for col_idx, text, min_w, anchor in cols:
            cell = ctk.CTkFrame(
                hdr,
                fg_color="transparent",
                corner_radius=0
            )
            cell.grid(row=0, column=col_idx, padx=2, pady=4, sticky="nsew")
            ctk.CTkLabel(
                cell,
                text=text,
                width=min_w - 10,
                font=ui_font(13, "bold"),
                text_color=C_WHITE,
                anchor=anchor
            ).pack(fill="both", expand=True, padx=4, pady=2)

    def _build_quest_list_area(self):
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.quests_view,
            fg_color=C_BG_DARKEST,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.scroll_frame.grid(row=3, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _build_pagination_bar(self):
        pager = ctk.CTkFrame(
            self.quests_view,
            fg_color=C_BG_DEEP,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER_SOFT,
            height=40
        )
        pager.grid(row=4, column=0, pady=(5, 0), sticky="ew")
        pager.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            pager,
            text="◀ Anterior",
            width=110,
            height=28,
            fg_color="#161B24",
            hover_color="#262F3F",
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=self._prev_page
        )
        self.prev_btn.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.page_info_lbl = ctk.CTkLabel(
            pager,
            text="Página 1 de 1",
            font=ui_font(12, "bold"),
            text_color=C_TEXT
        )
        self.page_info_lbl.grid(row=0, column=1, pady=5)

        self.next_btn = ctk.CTkButton(
            pager,
            text="Siguiente ▶",
            width=110,
            height=28,
            fg_color="#161B24",
            hover_color="#262F3F",
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=self._next_page
        )
        self.next_btn.grid(row=0, column=2, padx=10, pady=5, sticky="e")

    def _set_progression_mode(self, mode: str):
        self.progression_mode = mode
        for mk, btn in self.mode_buttons.items():
            is_act = (mk == mode)
            btn.configure(
                fg_color=C_BG_ROW_ALT if is_act else C_BG_PANEL,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
                text_color=C_WHITE if is_act else C_TEXT_MUTED
            )
        self._reset_and_apply_filters()

    def _select_trader(self, trader_name: str):
        self.selected_trader = trader_name
        for t_key, card in self.trader_cards.items():
            is_sel = trader_name == "TODOS" or t_key == trader_name
            card.configure(border_color=C_WHITE if is_sel else "#2A303C")
            if t_key in self.trader_name_labels:
                self.trader_name_labels[t_key].configure(
                    text_color=C_WHITE if is_sel else C_TEXT_MUTED
                )
        self.all_traders_btn.configure(
            border_color=C_WHITE if trader_name == "TODOS" else "#384152",
            fg_color="#252F42" if trader_name == "TODOS" else C_BG_ROW
        )
        self.trader_note_lbl.configure(text=TRADER_NOTES.get(trader_name, ""))
        self._reset_and_apply_filters()

    def _on_map_filter_change(self, choice: str):
        self.selected_map = choice
        self._reset_and_apply_filters()

    def _on_search_key_debounced(self, event=None):
        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(180, self._reset_and_apply_filters)

    def reload_data(self):
        self._reset_and_apply_filters()

    def _reset_and_apply_filters(self):
        self._debounce_job = None
        self.current_page = 0
        self._apply_filters()

    def _apply_filters(self):
        ds = get_datastore()
        all_quests_global = ds.get_quests(trader_filter="TODOS", progression_mode="ALL")
        total_global = len(all_quests_global)
        done_global = sum(1 for q in all_quests_global if q.get("is_completed") == 1)

        if self.selected_trader == "TODOS":
            pct = int((done_global / total_global) * 100) if total_global > 0 else 0
            self.stats_lbl.configure(text=f"Total Quests: {done_global} / {total_global} ({pct}%)")
        else:
            tr_quests = ds.get_quests(trader_filter=self.selected_trader, progression_mode="ALL")
            tr_tot = len(tr_quests)
            tr_done = sum(1 for q in tr_quests if q.get("is_completed") == 1)
            self.stats_lbl.configure(
                text=f"{self.selected_trader}: {tr_done}/{tr_tot}  •  Total Juego: {done_global}/{total_global}"
            )

        map_arg = "TODOS" if self.selected_map == "TODOS LOS MAPAS" else self.selected_map
        query = self.search_entry.get()
        hide_done = self.hide_completed_var.get()

        self.filtered_quests = ds.get_quests(
            trader_filter=self.selected_trader,
            map_filter=map_arg,
            search_query=query,
            hide_completed=hide_done,
            progression_mode=self.progression_mode
        )
        self._render_current_page()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._render_current_page()

    def _next_page(self):
        total_pages = max(1, (len(self.filtered_quests) + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.current_page + 1 < total_pages:
            self.current_page += 1
            self._render_current_page()

    def _render_current_page(self):
        self._render_token += 1
        token = self._render_token

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        total_items = len(self.filtered_quests)
        total_pages = max(1, (total_items + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.current_page = min(self.current_page, total_pages - 1)

        start = self.current_page * self.PAGE_SIZE
        end = min(start + self.PAGE_SIZE, total_items)
        page_slice = self.filtered_quests[start:end]

        mode_names = {
            "CORRELATIVE": "Progresión Correlativa",
            "KAPPA": "Requeridas para Kappa",
            "LIGHTKEEPER": "Ruta Lightkeeper",
            "ALL": "Todas las Misiones",
        }
        m_tag = mode_names.get(self.progression_mode, "")
        self.page_info_lbl.configure(
            text=f"{m_tag}  •  Página {self.current_page + 1} de {total_pages}  •  Mostrando {len(page_slice)} de {total_items} quests"
        )
        self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_btn.configure(state="normal" if (self.current_page + 1) < total_pages else "disabled")

        if not page_slice:
            ctk.CTkLabel(
                self.scroll_frame,
                text="No hay misiones visibles con estos filtros (completá las misiones previas o seleccioná 'Todas las Misiones').",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=0, column=0, pady=40)
            return

        def render_batch(idx: int):
            if not self.winfo_exists() or token != self._render_token:
                return
            limit = min(idx + 8, len(page_slice))
            for i in range(idx, limit):
                self._create_wiki_quest_row(i, page_slice[i])
            if limit < len(page_slice):
                self.after(4, lambda: render_batch(limit))

        render_batch(0)

    def _create_wiki_quest_row(self, row_idx: int, q: Dict[str, Any]):
        is_done = bool(q.get("is_completed"))
        row_bg = "#0E1C16" if is_done else ("#0C0E13" if row_idx % 2 == 0 else "#10141B")
        border_col = C_GREEN if is_done else "#232936"

        row_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=row_bg,
            corner_radius=0,
            border_width=1,
            border_color=border_col
        )
        row_frame.grid(row=row_idx, column=0, padx=0, pady=0, sticky="ew")
        row_frame.grid_columnconfigure(0, minsize=COL_CHECK_W, weight=0)
        row_frame.grid_columnconfigure(1, minsize=COL_QUEST_W, weight=0)
        row_frame.grid_columnconfigure(2, minsize=COL_OBJ_W, weight=3)
        row_frame.grid_columnconfigure(3, minsize=COL_REW_W, weight=2)

        # Columna 0: Checkbox centrado
        chk_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
        chk_cell.grid(row=0, column=0, padx=4, pady=10, sticky="nsew")
        chk_var = ctk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            chk_cell,
            text="",
            variable=chk_var,
            width=22,
            height=22,
            checkbox_width=20,
            checkbox_height=20,
            corner_radius=3,
            border_width=2,
            border_color=C_TEXT_DIM,
            fg_color=THEME["accent_green"],
            hover_color="#16A34A",
            command=lambda q_obj=q: self._on_toggle_quest(q_obj)
        )
        chk.pack(expand=True, padx=(12, 4), pady=8)

        # Columna 1: Quest Title + Badges + Cadena Correlativa
        quest_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
        quest_cell.grid(row=0, column=1, padx=8, pady=10, sticky="nsew")

        title_lbl = ctk.CTkLabel(
            quest_cell,
            text=q["title"],
            font=ui_font(14, "bold"),
            text_color=C_GREEN_LIGHT if is_done else THEME["accent_gold"],
            anchor="w",
            justify="left",
            wraplength=COL_QUEST_W - 24
        )
        title_lbl.pack(fill="x", anchor="w")

        badges_row = ctk.CTkFrame(quest_cell, fg_color="transparent")
        badges_row.pack(fill="x", anchor="w", pady=(4, 2))

        if self.selected_trader == "TODOS":
            ctk.CTkLabel(
                badges_row,
                text=f" {q['trader_name']} ",
                font=ui_font(11, "bold"),
                fg_color=C_SLATE_800,
                text_color=C_TEXT,
                corner_radius=3
            ).pack(side="left", padx=(0, 4))

        if q.get("is_kappa"):
            ctk.CTkLabel(
                badges_row,
                text=" KAPPA ",
                font=ui_font(10, "bold"),
                fg_color=C_AMBER,
                text_color=C_BG_DARKEST,
                corner_radius=3
            ).pack(side="left", padx=(0, 4))

        if q.get("is_lightkeeper"):
            ctk.CTkLabel(
                badges_row,
                text=" LIGHTKEEPER ",
                font=ui_font(10, "bold"),
                fg_color="#06B6D4",
                text_color=C_BG_DARKEST,
                corner_radius=3
            ).pack(side="left", padx=(0, 4))

        primary_map = q.get("primary_map", "Cualquier Mapa")
        if primary_map and primary_map != "Cualquier Mapa":
            ctk.CTkButton(
                badges_row,
                text=f"📍 {primary_map}",
                height=20,
                width=70,
                corner_radius=3,
                fg_color="#1E3A8A",
                hover_color="#2563EB",
                text_color=C_WHITE,
                font=ui_font(10, "bold"),
                command=lambda mp=primary_map: open_map_viewer_modal(self, mp)
            ).pack(side="left", padx=(0, 4))

        req_keys = extract_required_keys(q)
        for r_key in req_keys:
            ctk.CTkLabel(
                badges_row,
                text=f" 🔑 Llave: {r_key} ",
                font=ui_font(10, "bold"),
                fg_color="#854D0E",
                text_color="#FEF08A",
                corner_radius=3
            ).pack(side="left", padx=(0, 4))

        unlocks = q.get("unlocks_titles", [])
        prereqs = q.get("prereq_titles", [])
        if unlocks:
            u_txt = ", ".join(unlocks[:2]) + (f" (+{len(unlocks)-2})" if len(unlocks) > 2 else "")
            ctk.CTkLabel(
                quest_cell,
                text=f"↳ Desbloquea: {u_txt}",
                font=ui_font(11, "bold"),
                text_color="#60A5FA",
                anchor="w",
                justify="left",
                wraplength=COL_QUEST_W - 24
            ).pack(fill="x", anchor="w", pady=(2, 0))
        elif prereqs:
            p_txt = ", ".join(prereqs[:2])
            ctk.CTkLabel(
                quest_cell,
                text=f"🔗 Previa: {p_txt}",
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                anchor="w",
                justify="left",
                wraplength=COL_QUEST_W - 24
            ).pack(fill="x", anchor="w", pady=(2, 0))

        # Columna 2: Objectives
        obj_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
        obj_cell.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        obj_lines = q.get("objectives_lines") or ["• Consultar detalles en la Wiki."]
        ctk.CTkLabel(
            obj_cell,
            text="\n".join(obj_lines[:8]),
            font=ui_font(13),
            text_color=C_TEXT,
            anchor="w",
            justify="left",
            wraplength=COL_OBJ_W + 40
        ).pack(fill="both", expand=True, anchor="w")

        # Columna 3: Rewards
        rew_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
        rew_cell.grid(row=0, column=3, padx=10, pady=10, sticky="nsew")

        rew_lines = q.get("rewards_lines") or [f"• +{q.get('exp', 0):,} EXP"]
        ctk.CTkLabel(
            rew_cell,
            text="\n".join(rew_lines[:7]),
            font=ui_font(13),
            text_color=C_TEXT_SOFT,
            anchor="w",
            justify="left",
            wraplength=COL_REW_W - 20
        ).pack(fill="x", anchor="w")

        actions_row = ctk.CTkFrame(rew_cell, fg_color="transparent")
        actions_row.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(
            actions_row,
            text="📖 Guía Táctica",
            width=116,
            height=24,
            corner_radius=4,
            fg_color="#1E3A8A",
            hover_color=THEME["accent_gold"],
            text_color=C_WHITE,
            font=ui_font(11, "bold"),
            command=lambda quest_obj=q: self._open_quest_guide_modal(quest_obj)
        ).pack(side="left", padx=(0, 4))

        if q.get("wiki_url"):
            ctk.CTkButton(
                actions_row,
                text="Wiki ↗",
                width=62,
                height=24,
                corner_radius=4,
                fg_color=C_BG_ROW,
                hover_color=C_BORDER_ALT,
                text_color=THEME["accent_gold"],
                font=ui_font(11, "bold"),
                command=lambda u=q["wiki_url"]: webbrowser.open(u)
            ).pack(side="right")

    def _open_quest_guide_modal(self, q: Dict[str, Any]):
        QuestGuideModal(self, q, on_toggle_callback=self._on_toggle_quest)

    def _on_toggle_quest(self, q: Dict[str, Any]):
        new_state = get_datastore().toggle_quest(q["id"])
        unlocks = q.get("unlocks_titles", [])
        if new_state and unlocks:
            self.unlock_notice_lbl.configure(
                text=f"✓ '{q['title']}' completada → Desbloqueó: {', '.join(unlocks[:2])}",
                text_color=THEME["accent_green"]
            )
        elif not new_state:
            self.unlock_notice_lbl.configure(
                text=f"↩ '{q['title']}' desmarcada",
                text_color=THEME["accent_gold"]
            )
        self._apply_filters()
