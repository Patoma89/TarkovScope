"""
TarkovScope - Pestaña de Quests de la Historia (Wiki-Grade Interactive Story Chapters Viewer)
Réplica e integración completa de los 10 Capítulos Oficiales de la Historia de Escape from Tarkov
(Tour, Batya, Falling Skies, Accidental Witness, They Are Already Here, The Unheard,
Blue Fire, Boreas, The Ticket y The Labyrinth), con:
- Banners e íconos oficiales de cada capítulo
- Requisitos de desbloqueo y árbol completo de objetivos interactivos (persistidos en SQLite)
- Guía Paso a Paso exhaustiva con tablas de Related Quest Items, códigos, condiciones de rutas
  y las 498 capturas y mapas oficiales integrados offline con visor Zoom HD al hacer clic.
"""
import webbrowser
import customtkinter as ctk
from typing import Dict, Any, List, Optional
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from ui.image_utils import get_story_chapter_icon_ctk, get_story_chapter_banner_ctk
from ui.theme import C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL_ALT, C_BLUE, C_BORDER, C_BORDER_SOFT, C_GREEN, C_GREEN_LIGHT, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE
from ui.tab_story_guide import StoryGuideMixin

CHAPTER_SELECTOR_SPECS = [
    (1, "Tour", "tour_icon.png"),
    (2, "Batya", "batya_icon.png"),
    (3, "Falling Skies", "falling_skies_icon.png"),
    (4, "Accidental Witness", "accidental_witness_icon.png"),
    (5, "They Are Already Here", "they_are_already_here_icon.png"),
    (6, "The Unheard", "the_unheard_icon.png"),
    (7, "Blue Fire", "blue_fire_icon.png"),
    (8, "Boreas", "boreas_icon.png"),
    (9, "The Ticket", "the_ticket_icon.png"),
    (10, "The Labyrinth", "the_labyrinth_icon.png"),
]


class TabStoryQuests(StoryGuideMixin, ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.selected_chapter: int = 1
        self.active_subview: str = "GUIDE"  # "GUIDE" (Guía Paso a Paso + Objetivos) o "OBJECTIVES" (Solo Checklist) o "MISSIONS" (Resumen 71 misiones)
        self.lang_mode: str = "ES"  # "ES" o "EN"
        self.ticket_branch: str = "ALL"
        self.guide_page: int = 0
        self._objectives_summary_expanded: bool = False
        self.hide_completed_var = ctk.BooleanVar(value=False)

        self._debounce_job: Optional[str] = None
        self._render_token: int = 0
        self.chapter_buttons: Dict[int, ctk.CTkButton] = {}
        self.subview_buttons: Dict[str, ctk.CTkButton] = {}
        self.branch_buttons: Dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_top_header()
        self._build_chapter_selector_bar()
        self._build_main_scroll_area()
        self.reload_data()

    # =========================================================================
    # CABECERA SUPERIOR: TÍTULO, MODOS DE VISTA, IDIOMA Y BUSCADOR
    # =========================================================================
    def _build_top_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        hdr.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        # Fila 0: Título + Botones de Subvista + Progreso Global
        row0 = ctk.CTkFrame(hdr, fg_color="transparent")
        row0.grid(row=0, column=0, padx=14, pady=(8, 4), sticky="ew")
        row0.grid_columnconfigure(1, weight=1)

        title_box = ctk.CTkFrame(row0, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_box,
            text="📖 CAPÍTULOS DE LA HISTORIA — GUÍA INTERACTIVA WIKI OFICIAL",
            font=ui_font(16, "bold"),
            text_color=C_TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_box,
            text="10 Capítulos Oficiales • Guía Paso a Paso Completa • 498 Mapas y Capturas HD Offline • Tablas de Ítems y Códigos",
            font=ui_font(11),
            text_color=C_TEXT_DIM
        ).pack(anchor="w")

        # Selector de Subvistas en el centro-derecha
        subview_box = ctk.CTkFrame(row0, fg_color="transparent")
        subview_box.grid(row=0, column=1, padx=14)

        subviews = [
            ("GUIDE", "📖 Guía Completa Wiki (Paso a Paso + Fotos)"),
            ("OBJECTIVES", "☑️ Árbol de Objetivos & Ramas"),
            ("MISSIONS", "🗂️ Resumen de Misiones (71)"),
        ]
        for sv_key, sv_label in subviews:
            is_act = (sv_key == self.active_subview)
            btn = ctk.CTkButton(
                subview_box,
                text=sv_label,
                height=30,
                corner_radius=5,
                border_width=1,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
                fg_color="#1E2536" if is_act else C_BG_PANEL_ALT,
                hover_color="#273147",
                text_color=C_WHITE if is_act else C_TEXT_MUTED,
                font=ui_font(12, "bold"),
                command=lambda k=sv_key: self._set_subview(k)
            )
            btn.pack(side="left", padx=3)
            self.subview_buttons[sv_key] = btn

        self.stats_lbl = ctk.CTkLabel(
            row0,
            text="Progreso: 0 / 437 (0%)",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_green"]
        )
        self.stats_lbl.grid(row=0, column=2, sticky="e", padx=4)

        # Fila 1: Buscador + Botón Idioma (ES/EN) + Ocultar completadas
        bar_row = ctk.CTkFrame(hdr, fg_color="transparent")
        bar_row.grid(row=1, column=0, padx=14, pady=(2, 8), sticky="ew")
        bar_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar_row,
            placeholder_text="🔍 Buscar paso, llave, código, ítem requerido, mapa o instrucción en el capítulo...",
            height=32,
            corner_radius=6,
            fg_color=C_BG_PANEL_ALT,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12)
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_key)

        self.lang_btn = ctk.CTkButton(
            bar_row,
            text="🌐 Idioma: Español / Wiki Original",
            width=210,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BLUE,
            fg_color="#141C2B",
            hover_color=C_SLATE_800,
            text_color=C_BLUE,
            font=ui_font(11, "bold"),
            command=self._toggle_language
        )
        self.lang_btn.grid(row=0, column=1, padx=(0, 10))

        ctk.CTkCheckBox(
            bar_row,
            text="Ocultar completados",
            variable=self.hide_completed_var,
            font=ui_font(12, "bold"),
            text_color=C_TEXT_MUTED,
            fg_color=THEME["accent_green"],
            command=self.reload_data
        ).grid(row=0, column=2, sticky="e")

    # =========================================================================
    # BARRA DE LOS 10 CAPÍTULOS CON ICONOS OFICIALES EN INGLÉS
    # =========================================================================
    def _build_chapter_selector_bar(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=6, pady=5)

        for idx, (ch_id, ch_title, icon_fn) in enumerate(CHAPTER_SELECTOR_SPECS):
            inner.grid_columnconfigure(idx, weight=1)
            is_sel = (ch_id == self.selected_chapter)
            icon_ctk = get_story_chapter_icon_ctk(icon_fn, size=(22, 22))

            btn = ctk.CTkButton(
                inner,
                text=f"{ch_id}. {ch_title}",
                image=icon_ctk,
                compound="left",
                height=34,
                corner_radius=6,
                fg_color="#222B3D" if is_sel else C_BG_PANEL_ALT,
                hover_color="#2C374E",
                border_width=2 if is_sel else 1,
                border_color=THEME["accent_gold"] if is_sel else "#262E3D",
                text_color=C_WHITE if is_sel else C_TEXT_MUTED,
                font=ui_font(11, "bold"),
                command=lambda cid=ch_id: self._select_chapter(cid)
            )
            btn.grid(row=0, column=idx, padx=2, pady=1, sticky="ew")
            self.chapter_buttons[ch_id] = btn

    def _build_main_scroll_area(self):
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG_DARKEST,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.results_scroll.grid(row=2, column=0, sticky="nsew")
        self.results_scroll.grid_columnconfigure(0, weight=1)

    # =========================================================================
    # NAVEGACIÓN Y ACCIONES DE FILTRADO
    # =========================================================================
    def _set_subview(self, sv_key: str):
        self.active_subview = sv_key
        self.guide_page = 0
        for k, btn in self.subview_buttons.items():
            is_act = (k == sv_key)
            btn.configure(
                fg_color="#1E2536" if is_act else C_BG_PANEL_ALT,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
                text_color=C_WHITE if is_act else C_TEXT_MUTED
            )
        self.reload_data()

    def _toggle_language(self):
        self.lang_mode = "EN" if self.lang_mode == "ES" else "ES"
        if self.lang_mode == "ES":
            self.lang_btn.configure(text="🌐 Idioma: Español / Wiki Original", text_color=C_BLUE, border_color=C_BLUE)
        else:
            self.lang_btn.configure(text="🌐 Language: Original English Wiki", text_color="#FDE047", border_color="#EAB308")
        self.reload_data()

    def _select_chapter(self, ch_id: int):
        self.selected_chapter = ch_id
        self.guide_page = 0
        for cid, btn in self.chapter_buttons.items():
            is_sel = (cid == ch_id)
            btn.configure(
                fg_color="#222B3D" if is_sel else C_BG_PANEL_ALT,
                border_width=2 if is_sel else 1,
                border_color=THEME["accent_gold"] if is_sel else "#262E3D",
                text_color=C_WHITE if is_sel else C_TEXT_MUTED
            )
        self.reload_data()

    def _select_ticket_branch(self, branch_key: str):
        self.ticket_branch = branch_key
        self.guide_page = 0
        self.reload_data()

    def _on_search_key(self, event=None):
        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self.guide_page = 0
        self._debounce_job = self.after(160, self.reload_data)

    # =========================================================================
    # RENDERIZADO PRINCIPAL
    # =========================================================================
    def reload_data(self):
        self._debounce_job = None
        self._render_token += 1
        token = self._render_token

        try:
            self.results_scroll._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

        for w in self.results_scroll.winfo_children():
            w.destroy()

        ds = get_datastore()
        chapters = ds.get_wiki_story_chapters()
        if not chapters:
            ctk.CTkLabel(
                self.results_scroll,
                text="Cargando base de datos de capítulos de la historia...",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_DIM
            ).grid(row=0, column=0, pady=40)
            return

        # Actualizar contador global
        total_objs = sum(c.get("total_objectives", 0) for c in chapters)
        done_objs = sum(c.get("completed_objectives", 0) for c in chapters)
        pct_global = int((done_objs / total_objs) * 100) if total_objs > 0 else 0
        self.stats_lbl.configure(text=f"Objetivos Historia: {done_objs} / {total_objs} ({pct_global}%)")

        # Buscar capítulo activo
        chapter = next((c for c in chapters if c.get("chapter_number") == self.selected_chapter), chapters[0])

        if self.active_subview == "MISSIONS":
            self._render_legacy_missions_view(token)
            return

        # 1. Renderizar Hero Banner Card del Capítulo (con Banner Oficial, Requisitos y Recompensas)
        self._render_chapter_hero_card(self.results_scroll, chapter, row_idx=0)

        if self.active_subview == "OBJECTIVES":
            self._render_objectives_full_tree(self.results_scroll, chapter, row_idx=1)
        else:
            # Vista principal tipo Wiki: Panel colapsable/compacto de Objetivos + Guía Paso a Paso con Galerías
            self._render_objectives_summary_box(self.results_scroll, chapter, row_idx=1)
            self._render_wiki_guide_section(self.results_scroll, chapter, row_idx=2, token=token)

    # =========================================================================
    # COMPONENTE 1: HERO BANNER CARD DEL CAPÍTULO (ESTILO WIKI)
    # =========================================================================
    def _render_chapter_hero_card(self, parent, chapter: Dict[str, Any], row_idx: int):
        card = ctk.CTkFrame(
            parent,
            fg_color="#0D1119",
            corner_radius=10,
            border_width=1,
            border_color="#2D3648"
        )
        card.grid(row=row_idx, column=0, padx=8, pady=(6, 8), sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Banner panorámico superior + Información lateral
        top_split = ctk.CTkFrame(card, fg_color="transparent")
        top_split.grid(row=0, column=0, padx=12, pady=(10, 8), sticky="ew")
        top_split.grid_columnconfigure(1, weight=1)

        banner_img = get_story_chapter_banner_ctk(chapter.get("banner_file", ""), target_width=560)
        if banner_img:
            b_lbl = ctk.CTkLabel(top_split, text="", image=banner_img)
            b_lbl.grid(row=0, column=0, padx=(0, 14), pady=2, sticky="w")

        right_info = ctk.CTkFrame(top_split, fg_color="transparent")
        right_info.grid(row=0, column=1, sticky="nsew")
        right_info.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(right_info, fg_color="transparent")
        title_row.pack(fill="x", anchor="w")

        icon_img = get_story_chapter_icon_ctk(chapter.get("icon_file", ""), size=(34, 34))
        if icon_img:
            ctk.CTkLabel(title_row, text="", image=icon_img).pack(side="left", padx=(0, 8))

        ch_num = chapter.get("chapter_number", 1)
        ch_title = chapter.get("title", "")
        ctk.CTkLabel(
            title_row,
            text=f"CHAPTER {ch_num}: {ch_title.upper()}",
            font=ui_font(20, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left")

        wiki_url = chapter.get("wiki_url", "")
        if wiki_url:
            ctk.CTkButton(
                title_row,
                text="🌐 Wiki Oficial",
                width=110,
                height=26,
                corner_radius=5,
                fg_color="#1A2232",
                hover_color="#29354D",
                border_width=1,
                border_color="#3B4963",
                text_color=C_TEXT_SOFT,
                font=ui_font(11, "bold"),
                command=lambda u=wiki_url: webbrowser.open(u)
            ).pack(side="right", padx=4)

        # Barra de progreso del capítulo
        c_done = chapter.get("completed_objectives", 0)
        c_tot = chapter.get("total_objectives", 1)
        c_pct = int((c_done / c_tot) * 100) if c_tot > 0 else 0
        steps_cnt = len(chapter.get("guide_steps", []))
        imgs_cnt = sum(len(s.get("gallery", [])) for s in chapter.get("guide_steps", []))

        ctk.CTkLabel(
            right_info,
            text=f"📊 Objetivos del Capítulo: {c_done}/{c_tot} ({c_pct}%)   •   📖 {steps_cnt} Pasos de Guía   •   🖼️ {imgs_cnt} Mapas/Capturas",
            font=ui_font(12, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w", pady=(4, 4))

        # Requisitos y Recompensas en 2 columnas
        req_rew_grid = ctk.CTkFrame(card, fg_color="#111622", corner_radius=8, border_width=1, border_color="#232B3B")
        req_rew_grid.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        req_rew_grid.grid_columnconfigure(0, weight=3)
        req_rew_grid.grid_columnconfigure(1, weight=2)

        # Col 0: Requirements
        req_box = ctk.CTkFrame(req_rew_grid, fg_color="transparent")
        req_box.grid(row=0, column=0, padx=12, pady=8, sticky="nsew")

        ctk.CTkLabel(
            req_box,
            text="🔓 REQUISITOS DE DESBLOQUEO:",
            font=ui_font(11, "bold"),
            text_color="#FDE047"
        ).pack(anchor="w")

        req_txt = chapter.get("requirements_es" if self.lang_mode == "ES" else "requirements_en", "") or chapter.get("requirements_en", "")
        ctk.CTkLabel(
            req_box,
            text=req_txt,
            font=ui_font(12),
            text_color="#F1F5F9",
            justify="left",
            wraplength=560,
            anchor="w"
        ).pack(anchor="w", pady=(2, 0))

        # Col 1: Chapter Rewards
        rew_box = ctk.CTkFrame(req_rew_grid, fg_color="transparent")
        rew_box.grid(row=0, column=1, padx=12, pady=8, sticky="nsew")

        ctk.CTkLabel(
            rew_box,
            text="🏆 RECOMPENSAS DEL CAPÍTULO:",
            font=ui_font(11, "bold"),
            text_color=C_GREEN_LIGHT
        ).pack(anchor="w")

        rewards_list = chapter.get("rewards_es" if self.lang_mode == "ES" else "rewards", []) or chapter.get("rewards", [])
        if rewards_list:
            shown_rews = rewards_list[:5]
            rew_summary = "  •  ".join(shown_rews)
            if len(rewards_list) > 5:
                rew_summary += f"  (+{len(rewards_list) - 5} más)"
            ctk.CTkLabel(
                rew_box,
                text=rew_summary,
                font=ui_font(12, "bold"),
                text_color=C_TEXT_SOFT,
                justify="left",
                wraplength=420,
                anchor="w"
            ).pack(anchor="w", pady=(2, 0))

    # =========================================================================
    # COMPONENTE 2: CAJA COMPACTA DE OBJETIVOS (EN LA VISTA DE GUÍA)
    # =========================================================================
    def _render_objectives_summary_box(self, parent, chapter: Dict[str, Any], row_idx: int):
        box = ctk.CTkFrame(
            parent,
            fg_color="#0D1118",
            corner_radius=8,
            border_width=1,
            border_color="#252D3D"
        )
        box.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(box, fg_color="#141A26", corner_radius=6)
        hdr.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        objs = chapter.get("objectives", [])
        c_done = chapter.get("completed_objectives", 0)
        c_tot = chapter.get("total_objectives", 0)

        ctk.CTkLabel(
            hdr,
            text=f"🎯 ÁRBOL OFICIAL DE OBJETIVOS ({c_done} / {c_tot} completados) — Marca tus objetivos mientras avanzas",
            font=ui_font(13, "bold"),
            text_color=C_TEXT
        ).grid(row=0, column=0, padx=10, pady=6, sticky="w")

        btn_toggle_txt = "▲ Ocultar Checklist Rápido" if self._objectives_summary_expanded else "▼ Desplegar Checklist Rápido aquí"
        ctk.CTkButton(
            hdr,
            text=btn_toggle_txt,
            height=26,
            corner_radius=5,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            border_width=1,
            border_color=C_BLUE,
            text_color=C_BLUE,
            font=ui_font(11, "bold"),
            command=self._toggle_objectives_summary_box
        ).grid(row=0, column=1, padx=4, pady=5, sticky="e")

        ctk.CTkButton(
            hdr,
            text="Ver Árbol en Pantalla Completa ➔",
            height=26,
            corner_radius=5,
            fg_color="#1F293D",
            hover_color="#2D3B56",
            border_width=1,
            border_color=THEME["accent_gold"],
            text_color=THEME["accent_gold"],
            font=ui_font(11, "bold"),
            command=lambda: self._set_subview("OBJECTIVES")
        ).grid(row=0, column=2, padx=(4, 8), pady=5, sticky="e")

        if self._objectives_summary_expanded:
            obj_scroll = ctk.CTkScrollableFrame(
                box,
                fg_color="#0A0D13",
                corner_radius=6,
                height=175
            )
            obj_scroll.grid(row=1, column=0, padx=8, pady=(0, 8), sticky="ew")
            obj_scroll.grid_columnconfigure(0, weight=1)
            self._populate_objectives_rows(obj_scroll, objs)

    def _toggle_objectives_summary_box(self):
        self._objectives_summary_expanded = not self._objectives_summary_expanded
        self.reload_data()

    def _render_objectives_full_tree(self, parent, chapter: Dict[str, Any], row_idx: int):
        box = ctk.CTkFrame(
            parent,
            fg_color="#0D1118",
            corner_radius=8,
            border_width=1,
            border_color="#252D3D"
        )
        box.grid(row=row_idx, column=0, padx=8, pady=(0, 8), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(box, fg_color="#141A26", corner_radius=6)
        hdr.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text=f"☑️ LISTA COMPLETA DE OBJETIVOS Y RAMAS CONDICIONALES — {chapter.get('title', '').upper()}",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"]
        ).grid(row=0, column=0, padx=12, pady=8, sticky="w")

        ctk.CTkButton(
            hdr,
            text="📖 Volver a la Guía Paso a Paso con Imágenes",
            height=28,
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=lambda: self._set_subview("GUIDE")
        ).grid(row=0, column=1, padx=10, pady=6, sticky="e")

        list_container = ctk.CTkFrame(box, fg_color="transparent")
        list_container.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
        list_container.grid_columnconfigure(0, weight=1)

        self._populate_objectives_rows(list_container, chapter.get("objectives", []))

    def _populate_objectives_rows(self, container, objectives: List[Dict[str, Any]]):
        q = (self.search_entry.get() or "").strip().lower()
        hide_done = self.hide_completed_var.get()

        row_i = 0
        for obj in objectives:
            otype = obj.get("type", "objective")
            txt = obj.get("text_es" if self.lang_mode == "ES" else "text", "") or obj.get("text", "")

            if q and q not in txt.lower() and q not in obj.get("text", "").lower():
                continue

            if otype in ("branch_header", "condition_header"):
                hdr_frame = ctk.CTkFrame(
                    container,
                    fg_color="#1C2230" if otype == "branch_header" else "#231D15",
                    corner_radius=5,
                    border_width=1,
                    border_color=C_BLUE if otype == "branch_header" else "#CA8A04"
                )
                hdr_frame.grid(row=row_i, column=0, padx=4, pady=(8, 3), sticky="ew")
                ctk.CTkLabel(
                    hdr_frame,
                    text=f"⚡ {txt}",
                    font=ui_font(12, "bold"),
                    text_color=C_BLUE if otype == "branch_header" else "#FDE047",
                    anchor="w"
                ).pack(padx=10, pady=4, fill="x")
                row_i += 1
                continue

            is_done = bool(obj.get("is_completed"))
            if hide_done and is_done:
                continue

            indent = int(obj.get("indent", 0))
            left_pad = 8 + indent * 22

            item_row = ctk.CTkFrame(
                container,
                fg_color="#0D1914" if is_done else "transparent",
                corner_radius=4
            )
            item_row.grid(row=row_i, column=0, padx=(left_pad, 4), pady=1, sticky="ew")
            item_row.grid_columnconfigure(1, weight=1)

            chk_var = ctk.BooleanVar(value=is_done)
            chk = ctk.CTkCheckBox(
                item_row,
                text="",
                variable=chk_var,
                width=20,
                height=20,
                checkbox_width=18,
                checkbox_height=18,
                corner_radius=4,
                border_width=2,
                border_color="#64748B",
                fg_color=THEME["accent_green"],
                command=lambda o=obj, r=item_row: self._on_toggle_objective(o, r)
            )
            chk.grid(row=0, column=0, padx=(4, 6), pady=3, sticky="nw")

            lbl_color = C_GREEN_LIGHT if is_done else (C_TEXT_DIM if obj.get("optional") else "#F1F5F9")
            lbl = ctk.CTkLabel(
                item_row,
                text=txt,
                font=ui_font(12, "bold" if not obj.get("optional") else "normal"),
                text_color=lbl_color,
                justify="left",
                wraplength=860,
                anchor="w"
            )
            lbl.grid(row=0, column=1, padx=2, pady=2, sticky="w")

            if obj.get("fir"):
                ctk.CTkLabel(
                    item_row,
                    text=" FIR ",
                    font=ui_font(9, "bold"),
                    fg_color="#7F1D1D",
                    text_color="#FCA5A5",
                    corner_radius=3
                ).grid(row=0, column=2, padx=6, pady=2)

            row_i += 1

    def _on_toggle_objective(self, obj: Dict[str, Any], row_frame: ctk.CTkFrame):
        ds = get_datastore()
        new_state = ds.toggle_story_quest(obj["id"])
        obj["is_completed"] = 1 if new_state else 0
        if row_frame.winfo_exists():
            row_frame.configure(fg_color="#0D1914" if new_state else "transparent")
        # Actualizar contador global
        chapters = ds.get_wiki_story_chapters()
        total_objs = sum(c.get("total_objectives", 0) for c in chapters)
        done_objs = sum(c.get("completed_objectives", 0) for c in chapters)
        pct_global = int((done_objs / total_objs) * 100) if total_objs > 0 else 0
        self.stats_lbl.configure(text=f"Objetivos Historia: {done_objs} / {total_objs} ({pct_global}%)")

    # =========================================================================
    # VISTA SECUNDARIA: RESUMEN DE LAS 71 MISIONES (RETROCOMPATIBLE)
    # =========================================================================
    def _render_legacy_missions_view(self, token: int):
        ds = get_datastore()
        query = self.search_entry.get().strip()
        filtered = ds.get_story_quests(chapter_filter=self.selected_chapter, search_query=query)
        if self.hide_completed_var.get():
            filtered = [q for q in filtered if not q.get("is_completed")]

        if not filtered:
            ctk.CTkLabel(
                self.results_scroll,
                text="No hay misiones de resumen que coincidan con los filtros seleccionados.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=0, column=0, pady=40)
            return

        def render_batch(start_idx: int = 0, batch_size: int = 5):
            if not self.winfo_exists() or token != self._render_token:
                return
            end_idx = min(start_idx + batch_size, len(filtered))
            for idx in range(start_idx, end_idx):
                self._create_legacy_quest_card(self.results_scroll, idx, filtered[idx])
            if end_idx < len(filtered):
                self.after(8, lambda: render_batch(end_idx, batch_size))

        render_batch(0, 5)

    def _create_legacy_quest_card(self, parent, idx: int, sq: Dict[str, Any]):
        is_done = bool(sq.get("is_completed"))
        card = ctk.CTkFrame(
            parent,
            fg_color="#0D1612" if is_done else C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_GREEN if is_done else C_BORDER_SOFT
        )
        card.grid(row=idx, column=0, padx=8, pady=5, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        chk_box = ctk.CTkFrame(card, fg_color="transparent")
        chk_box.grid(row=0, column=0, rowspan=3, padx=(12, 6), pady=12, sticky="n")

        chk_var = ctk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            chk_box,
            text="",
            variable=chk_var,
            width=24,
            height=24,
            checkbox_width=22,
            checkbox_height=22,
            corner_radius=4,
            border_width=2,
            border_color=C_TEXT_DIM,
            fg_color=THEME["accent_green"],
            hover_color="#16A34A",
            command=lambda s=sq, c=card: self._on_toggle_legacy_quest(s, c)
        )
        chk.pack(pady=4)

        header_row = ctk.CTkFrame(card, fg_color="transparent")
        header_row.grid(row=0, column=1, padx=(6, 14), pady=(12, 4), sticky="ew")

        ctk.CTkLabel(
            header_row,
            text=f"{sq['chapter_name']}  •  👤 {sq['trader']}  •  📍 {sq['map']}  •  Nivel {sq['level_req']}+",
            font=ui_font(11, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_row,
            text=sq["title"],
            font=ui_font(15, "bold"),
            text_color=C_GREEN_LIGHT if is_done else THEME["accent_gold"],
            anchor="w"
        ).pack(anchor="w", pady=(2, 2))

        ctk.CTkLabel(
            card,
            text=sq["briefing"],
            font=ui_font(12),
            text_color=C_TEXT_MUTED,
            justify="left",
            wraplength=860,
            anchor="w"
        ).grid(row=1, column=1, padx=(6, 14), pady=(0, 8), sticky="w")

    def _on_toggle_legacy_quest(self, sq: Dict[str, Any], card_frame: ctk.CTkFrame):
        ds = get_datastore()
        new_state = ds.toggle_story_quest(sq["id"])
        sq["is_completed"] = 1 if new_state else 0
        if card_frame.winfo_exists():
            card_frame.configure(
                fg_color="#0D1612" if new_state else C_BG_DEEP,
                border_color=C_GREEN if new_state else C_BORDER_SOFT
            )
