"""
TarkovScope - Pestaña Táctica: PMC, Skills, Scav Karma, BTR Driver & Transits
Presenta en 3 sub-vistas segmentadas:
  1. Skills & Leveo (catálogo filtrable, requisitos, perks Élite, fatiga e Hideout boosters)
  2. Scav Karma (Fence) (rangos BTR/Transit, efecto LL2, acciones positivas/negativas)
  3. BTR Driver & Red de Transits (tarifas USEC/BEAR/Scav, conexiones entre mapas y multiplicador EXP)
"""
from typing import Any, Dict, List, Optional
import tkinter as tk
import customtkinter as ctk

from core.config import THEME
from core.pmc_systems_data import (
    BTR_SERVICE_DATA,
    PMC_SKILLS_CATALOG,
    SCAV_KARMA_ACTIONS,
    SCAV_KARMA_BRACKETS,
    SKILL_CATEGORIES,
    SKILL_LEVELING_MECHANICS,
    TRANSITS_CATALOG,
    TRANSIT_EXP_MULTIPLIERS,
    filter_skills,
    filter_transits,
)
from ui.theme import (
    C_AMBER,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_ROW,
    C_BG_ROW_ALT,
    C_BLUE,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED,
    C_SLATE_700,
    C_TEXT,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


SKILL_CAT_COLORS: Dict[str, tuple] = {
    "Física": ("#059669", "#FFFFFF"),
    "Combate": ("#DC2626", "#FFFFFF"),
    "Práctica": ("#0284C7", "#FFFFFF"),
    "Mental": ("#7C3AED", "#FFFFFF"),
}

TRANSIT_MAP_FILTERS: List[str] = [
    "Todos",
    "Customs",
    "Factory",
    "Ground Zero",
    "Interchange",
    "Lighthouse",
    "Reserve",
    "Shoreline",
    "Streets of Tarkov",
    "The Lab",
    "Woods",
]


class TabPMCSystems(ctk.CTkFrame):
    """Pestaña unificada de Sistemas PMC: Skills & Fatiga, Scav Karma (Fence) y BTR/Transits."""

    def __init__(self, master, datastore=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.datastore = datastore
        self.active_view: str = "skills"
        self.active_skill_cat: str = "Todas"
        self.selected_skill_id: Optional[str] = (
            PMC_SKILLS_CATALOG[0]["id"] if PMC_SKILLS_CATALOG else None
        )
        self.active_transit_map: str = "Todos"
        self._skill_token: int = 0
        self._transit_token: int = 0
        self._skill_search_job: Optional[str] = None
        self._transit_search_job: Optional[str] = None

        self._view_btns: Dict[str, ctk.CTkButton] = {}
        self._skill_cat_btns: Dict[str, ctk.CTkButton] = {}
        self._skill_row_refs: Dict[str, ctk.CTkFrame] = {}
        self._transit_map_btns: Dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_views()
        self._switch_view("skills")

    # ------------------------------------------------------------------
    # Construcción de Cabecera & Sub-navegación
    # ------------------------------------------------------------------
    def _build_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        hdr.grid(row=0, column=0, padx=0, pady=(0, 8), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text="📈 SISTEMAS DE PMC: SKILLS, SCAV KARMA & BTR",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(8, 2), sticky="w")

        ctk.CTkLabel(
            hdr,
            text="Guía táctica de progresión: skills sin fatiga, Scav Karma (Fence), tarifas BTR y Transits.",
            font=ui_font(11),
            text_color=C_TEXT_DIM,
        ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

        seg_bar = ctk.CTkFrame(hdr, fg_color="transparent")
        seg_bar.grid(row=0, column=1, rowspan=2, padx=12, pady=8, sticky="e")

        views = [
            ("skills", "📈 Skills & Leveo"),
            ("karma", "⚖️ Scav Karma"),
            ("btr_transits", "🚐 BTR & Transits"),
        ]
        for key, label in views:
            btn = ctk.CTkButton(
                seg_bar,
                text=label,
                height=32,
                width=0,
                corner_radius=8,
                font=ui_font(12, "bold"),
                border_width=1,
                command=lambda k=key: self._switch_view(k),
            )
            btn.pack(side="left", padx=3)
            self._view_btns[key] = btn

    def _build_views(self):
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=1, column=0, sticky="nsew")
        self.view_container.grid_columnconfigure(0, weight=1)
        self.view_container.grid_rowconfigure(0, weight=1)

        self.skills_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.karma_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.btr_frame = ctk.CTkFrame(self.view_container, fg_color="transparent")

        self._karma_built = False
        self._btr_built = False
        self._build_skills_view()

    def _switch_view(self, view_key: str):
        self.active_view = view_key
        for k, btn in self._view_btns.items():
            active = k == view_key
            btn.configure(
                fg_color=THEME["accent_gold"] if active else C_SLATE_700,
                text_color="#0F172A" if active else C_TEXT_SOFT,
                border_color=THEME["accent_gold"] if active else THEME["border"],
                hover_color="#E5C992" if active else C_BG_ROW_ALT,
            )

        for frame in (self.skills_frame, self.karma_frame, self.btr_frame):
            frame.grid_forget()

        if view_key == "skills":
            self.skills_frame.grid(row=0, column=0, sticky="nsew")
            self._schedule_skills_render()
        elif view_key == "karma":
            if not self._karma_built:
                self._karma_built = True
                self._build_karma_view()
            self.karma_frame.grid(row=0, column=0, sticky="nsew")
        elif view_key == "btr_transits":
            if not self._btr_built:
                self._btr_built = True
                self._build_btr_transits_view()
            self.btr_frame.grid(row=0, column=0, sticky="nsew")
            self._schedule_transits_render()

    # ------------------------------------------------------------------
    # VISTA 1: SKILLS & LEVEO
    # ------------------------------------------------------------------
    def _build_skills_view(self):
        self.skills_frame.grid_columnconfigure(0, weight=1)
        self.skills_frame.grid_rowconfigure(1, weight=1)

        fbar = ctk.CTkFrame(
            self.skills_frame,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        fbar.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        fbar.grid_columnconfigure(1, weight=1)

        self.skill_search_entry = ctk.CTkEntry(
            fbar,
            width=260,
            height=34,
            placeholder_text="Buscar skill, quest o módulo Hideout...",
            font=ui_font(12),
            fg_color=C_BG_DEEP,
            border_color=THEME["border"],
        )
        self.skill_search_entry.grid(row=0, column=0, padx=(12, 8), pady=10, sticky="w")
        self.skill_search_entry.bind("<KeyRelease>", self._on_skill_search_key)

        cat_wrap = ctk.CTkFrame(fbar, fg_color="transparent")
        cat_wrap.grid(row=0, column=1, padx=4, pady=8, sticky="w")

        for cat in SKILL_CATEGORIES:
            btn = ctk.CTkButton(
                cat_wrap,
                text=cat,
                height=30,
                width=82,
                corner_radius=14,
                font=ui_font(12, "bold"),
                border_width=1,
                command=lambda c=cat: self._set_skill_category(c),
            )
            btn.pack(side="left", padx=3)
            self._skill_cat_btns[cat] = btn

        self.skill_count_lbl = ctk.CTkLabel(
            fbar,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        )
        self.skill_count_lbl.grid(row=0, column=2, padx=14, pady=10, sticky="e")

        body = ctk.CTkFrame(self.skills_frame, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=5)
        body.grid_columnconfigure(1, weight=4)
        body.grid_rowconfigure(0, weight=1)

        self.skill_list_scroll = ctk.CTkScrollableFrame(
            body,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.skill_list_scroll.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self.skill_list_scroll.grid_columnconfigure(0, weight=1)

        right_scroll = ctk.CTkScrollableFrame(
            body,
            fg_color="transparent",
            corner_radius=0,
        )
        right_scroll.grid(row=0, column=1, sticky="nsew")
        right_scroll.grid_columnconfigure(0, weight=1)

        self.skill_detail_card = ctk.CTkFrame(
            right_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.skill_detail_card.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        self.skill_detail_card.grid_columnconfigure(0, weight=1)

        self._build_mechanics_card(right_scroll)
        self._update_skill_cat_styles()

    def _build_mechanics_card(self, parent):
        mech = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        mech.grid(row=1, column=0, sticky="ew")
        mech.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            mech,
            text="⚡ FATIGA EN RAID (DIMINISHING RETURNS) & BOOSTERS",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(12, 4), sticky="w")

        ctk.CTkLabel(
            mech,
            text=f"Nivel Máximo: {SKILL_LEVELING_MECHANICS['max_level']}",
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            wraplength=430,
            justify="left",
        ).grid(row=1, column=0, padx=14, pady=(0, 6), sticky="w")

        dr_wrap = ctk.CTkFrame(mech, fg_color=C_BG_DEEP, corner_radius=8, border_width=1, border_color=C_BORDER)
        dr_wrap.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")
        dr_wrap.grid_columnconfigure(1, weight=1)

        for idx, (label, pct, color_hex) in enumerate(SKILL_LEVELING_MECHANICS["diminishing_returns"]):
            ctk.CTkLabel(
                dr_wrap,
                text=label,
                font=ui_font(11),
                text_color=C_TEXT_MUTED,
            ).grid(row=idx, column=0, padx=(10, 6), pady=3, sticky="w")

            ctk.CTkLabel(
                dr_wrap,
                text=f"Velocidad {pct}",
                font=ui_font(11, "bold"),
                text_color=color_hex,
            ).grid(row=idx, column=1, padx=10, pady=3, sticky="e")

        reset_box = ctk.CTkFrame(mech, fg_color="#10241D", corner_radius=6, border_width=1, border_color=C_EMERALD)
        reset_box.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="ew")
        ctk.CTkLabel(
            reset_box,
            text=f"⏱️ Reset de Fatiga: {SKILL_LEVELING_MECHANICS['reset_note']}",
            font=ui_font(11, "bold"),
            text_color=C_GREEN_LIGHT,
            wraplength=415,
            justify="left",
        ).pack(padx=10, pady=7, anchor="w")

        ctk.CTkLabel(
            mech,
            text="🏠 Módulos del Hideout que aceleran/afectan Skills:",
            font=ui_font(12, "bold"),
            text_color=C_BLUE,
        ).grid(row=4, column=0, padx=14, pady=(2, 4), sticky="w")

        boost_wrap = ctk.CTkFrame(mech, fg_color="transparent")
        boost_wrap.grid(row=5, column=0, padx=12, pady=(0, 12), sticky="ew")
        for item in SKILL_LEVELING_MECHANICS["hideout_boosters"]:
            is_penalty = "penalización" in item.lower() or "defective wall" in item.lower()
            ctk.CTkLabel(
                boost_wrap,
                text=f"• {item}",
                font=ui_font(11),
                text_color=C_RED if is_penalty else C_TEXT_SOFT,
                wraplength=425,
                justify="left",
            ).pack(anchor="w", pady=2)

    def _on_skill_search_key(self, _event=None):
        if self._skill_search_job:
            self.after_cancel(self._skill_search_job)
        self._skill_search_job = self.after(120, self._schedule_skills_render)

    def _set_skill_category(self, category: str):
        self.active_skill_cat = category
        self._update_skill_cat_styles()
        self._schedule_skills_render()

    def _update_skill_cat_styles(self):
        for cat, btn in self._skill_cat_btns.items():
            active = cat == self.active_skill_cat
            btn.configure(
                fg_color=THEME["accent_gold"] if active else C_SLATE_700,
                text_color="#0F172A" if active else C_TEXT_SOFT,
                border_color=THEME["accent_gold"] if active else THEME["border"],
                hover_color="#E5C992" if active else C_BG_ROW_ALT,
            )

    def _schedule_skills_render(self):
        self._skill_token += 1
        token = self._skill_token
        query = self.skill_search_entry.get() if hasattr(self, "skill_search_entry") else ""
        items = filter_skills(category=self.active_skill_cat, query=query)
        self.skill_count_lbl.configure(text=f"{len(items)} skills")

        for child in self.skill_list_scroll.winfo_children():
            child.destroy()
        self._skill_row_refs.clear()

        if not items:
            ctk.CTkLabel(
                self.skill_list_scroll,
                text="No se encontraron skills para ese filtro.",
                font=ui_font(13),
                text_color=C_TEXT_DIM,
            ).grid(row=0, column=0, padx=20, pady=30)
            self._render_skill_detail(None)
            return

        if not any(s["id"] == self.selected_skill_id for s in items):
            self.selected_skill_id = items[0]["id"]

        selected_item = next((s for s in items if s["id"] == self.selected_skill_id), items[0])
        self._render_skill_detail(selected_item)
        self._render_skills_batch(items, 0, token)

    def _render_skills_batch(self, items: List[Dict[str, Any]], start: int, token: int):
        if not self.winfo_exists() or token != self._skill_token:
            return
        batch_size = 8
        end = min(start + batch_size, len(items))
        for idx in range(start, end):
            sk = items[idx]
            is_sel = sk["id"] == self.selected_skill_id
            row = ctk.CTkFrame(
                self.skill_list_scroll,
                fg_color=C_BG_ROW_ALT if is_sel else C_BG_ROW,
                corner_radius=8,
                border_width=1,
                border_color=THEME["accent_gold"] if is_sel else C_BORDER,
                cursor="hand2",
            )
            row.grid(row=idx, column=0, padx=8, pady=4, sticky="ew")
            row.grid_columnconfigure(0, weight=1)
            self._skill_row_refs[sk["id"]] = row

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="ew")
            top.grid_columnconfigure(0, weight=1)

            name_lbl = ctk.CTkLabel(
                top,
                text=sk["name"],
                font=ui_font(13, "bold"),
                text_color=C_WHITE,
                anchor="w",
            )
            name_lbl.grid(row=0, column=0, sticky="w")

            bg_c, fg_c = SKILL_CAT_COLORS.get(sk["category"], (C_SLATE_700, C_WHITE))
            badge = ctk.CTkLabel(
                top,
                text=f" {sk['category']} ",
                font=ui_font(10, "bold"),
                fg_color=bg_c,
                text_color=fg_c,
                corner_radius=6,
                height=20,
            )
            badge.grid(row=0, column=1, padx=(8, 0), sticky="e")

            req_lbl = ctk.CTkLabel(
                row,
                text=f"Requisitos: {sk['requirements']}",
                font=ui_font(11, "bold"),
                text_color=C_AMBER if "Nv." in sk["requirements"] else C_TEXT_DIM,
                anchor="w",
                wraplength=470,
                justify="left",
            )
            req_lbl.grid(row=1, column=0, padx=10, pady=(0, 2), sticky="w")

            lvl_lbl = ctk.CTkLabel(
                row,
                text=sk["how_to_level"],
                font=ui_font(11),
                text_color=C_TEXT_MUTED,
                anchor="w",
                wraplength=470,
                justify="left",
            )
            lvl_lbl.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="w")

            for widget in (row, top, name_lbl, badge, req_lbl, lvl_lbl):
                widget.bind("<Button-1>", lambda _e, s=sk: self._select_skill(s))

        if end < len(items):
            self.after(4, lambda: self._render_skills_batch(items, end, token))

    def _select_skill(self, sk: Dict[str, Any]):
        prev_id = self.selected_skill_id
        new_id = sk["id"]
        if prev_id != new_id:
            self.selected_skill_id = new_id
            for sid, sel in ((prev_id, False), (new_id, True)):
                frame = self._skill_row_refs.get(sid or "")
                if frame and frame.winfo_exists():
                    frame.configure(
                        fg_color=C_BG_ROW_ALT if sel else C_BG_ROW,
                        border_color=THEME["accent_gold"] if sel else C_BORDER,
                    )
        self._render_skill_detail(sk)

    def _render_skill_detail(self, sk: Optional[Dict[str, Any]]):
        for child in self.skill_detail_card.winfo_children():
            child.destroy()
        if not sk:
            ctk.CTkLabel(
                self.skill_detail_card,
                text="Seleccioná una skill para ver efectos, perk élite y consejos.",
                font=ui_font(12),
                text_color=C_TEXT_DIM,
            ).pack(padx=16, pady=20)
            return

        bg_c, fg_c = SKILL_CAT_COLORS.get(sk["category"], (C_SLATE_700, C_WHITE))
        top = ctk.CTkFrame(self.skill_detail_card, fg_color="transparent")
        top.grid(row=0, column=0, padx=14, pady=(12, 4), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text=sk["name"],
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            top,
            text=f" {sk['category']} ",
            font=ui_font(11, "bold"),
            fg_color=bg_c,
            text_color=fg_c,
            corner_radius=6,
            height=22,
        ).grid(row=0, column=1, sticky="e")

        sections = [
            ("🔑 REQUISITOS EN QUESTS / HIDEOUT", sk["requirements"], C_AMBER),
            ("📊 EFECTOS POR NIVEL", sk["effects"], C_TEXT_SOFT),
            ("👑 PERK ÉLITE (NIVEL 51)", sk["elite_perk"], C_GREEN_LIGHT),
            ("🚀 MÉTODO ÓPTIMO DE LEVEO", sk["how_to_level"], C_BLUE),
        ]
        for idx, (title, body_text, color) in enumerate(sections, start=1):
            box = ctk.CTkFrame(
                self.skill_detail_card,
                fg_color=C_BG_DEEP,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            box.grid(row=idx, column=0, padx=12, pady=4, sticky="ew")
            ctk.CTkLabel(
                box,
                text=title,
                font=ui_font(11, "bold"),
                text_color=color,
            ).pack(padx=10, pady=(6, 1), anchor="w")
            ctk.CTkLabel(
                box,
                text=body_text,
                font=ui_font(12),
                text_color=C_TEXT_SOFT,
                wraplength=415,
                justify="left",
            ).pack(padx=10, pady=(0, 7), anchor="w")

        ctk.CTkFrame(self.skill_detail_card, fg_color="transparent", height=6).grid(
            row=len(sections) + 1, column=0
        )

    # ------------------------------------------------------------------
    # VISTA 2: SCAV KARMA (FENCE)
    # ------------------------------------------------------------------
    def _build_karma_view(self):
        self.karma_frame.grid_columnconfigure(0, weight=1)
        self.karma_frame.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(
            self.karma_frame,
            fg_color="transparent",
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)

        # Panel izquierdo: Rangos de Reputación con Fence
        left = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        left.grid(row=0, column=0, padx=(0, 6), pady=0, sticky="nsew")
        left.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left,
            text="⚖️ RANGOS DE REPUTACIÓN CON FENCE (SCAV KARMA)",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(12, 2), sticky="w")

        ctk.CTkLabel(
            left,
            text="Impacto en entregas del BTR, tamaño de caja de Transit, cooldown del Scav y desbloqueo de Fence LL2 (+6.0).",
            font=ui_font(11),
            text_color=C_TEXT_DIM,
            wraplength=520,
            justify="left",
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        for idx, br in enumerate(SCAV_KARMA_BRACKETS, start=2):
            k_txt = br["karma"]
            if k_txt.startswith("-5"):
                accent = C_RED
                row_bg = "#241317"
            elif "ÉLITE" in k_txt:
                accent = C_AMBER
                row_bg = "#221D10"
            elif k_txt.startswith("+"):
                accent = C_EMERALD
                row_bg = C_BG_ROW_ALT
            else:
                accent = C_TEXT_MUTED
                row_bg = C_BG_ROW

            card = ctk.CTkFrame(
                left,
                fg_color=row_bg,
                corner_radius=8,
                border_width=1,
                border_color=accent if ("-5" in k_txt or "ÉLITE" in k_txt) else C_BORDER,
            )
            card.grid(row=idx, column=0, padx=12, pady=5, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, padx=10, pady=(8, 3), sticky="ew")
            top.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top,
                text=f"Karma {k_txt}",
                font=ui_font(13, "bold"),
                text_color=accent,
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                top,
                text=f"BTR: {br['btr']}  |  Transit: {br['transit_grid']}",
                font=ui_font(11, "bold"),
                fg_color=C_BG_DEEP,
                text_color=C_TEXT_SOFT,
                corner_radius=6,
                height=22,
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            ctk.CTkLabel(
                card,
                text=br["effects"],
                font=ui_font(12),
                text_color=C_TEXT_MUTED,
                wraplength=500,
                justify="left",
            ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

        # Panel derecho: Acciones que suben o bajan Karma
        right = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        right.grid(row=0, column=1, padx=(6, 0), pady=0, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            right,
            text="📊 TABLA DE ACCIONES (GANANCIA & PENALIZACIONES)",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(12, 2), sticky="w")

        ctk.CTkLabel(
            right,
            text="Extracciones Co-Op y Vehículos (Car Extract) son el camino más rápido por cada mapa al inicio del wipe.",
            font=ui_font(11),
            text_color=C_TEXT_DIM,
            wraplength=520,
            justify="left",
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        for idx, act in enumerate(SCAV_KARMA_ACTIONS, start=2):
            chg = act["change"]
            if chg.startswith("+"):
                badge_bg, badge_fg = "#065F46", C_GREEN_LIGHT
            elif chg.startswith("-"):
                badge_bg, badge_fg = "#7F1D1D", "#FCA5A5"
            else:
                badge_bg, badge_fg = C_SLATE_700, C_TEXT_SOFT

            row = ctk.CTkFrame(
                right,
                fg_color=C_BG_ROW if idx % 2 == 0 else C_BG_ROW_ALT,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            row.grid(row=idx, column=0, padx=12, pady=3, sticky="ew")
            row.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.grid(row=0, column=0, padx=10, pady=(6, 1), sticky="ew")
            top.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top,
                text=act["action"],
                font=ui_font(12, "bold"),
                text_color=C_TEXT,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                top,
                text=f" {chg} ",
                font=ui_font(11, "bold"),
                fg_color=badge_bg,
                text_color=badge_fg,
                corner_radius=6,
                height=20,
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            ctk.CTkLabel(
                row,
                text=act["notes"],
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                wraplength=490,
                justify="left",
            ).grid(row=1, column=0, padx=10, pady=(0, 6), sticky="w")

    # ------------------------------------------------------------------
    # VISTA 3: BTR DRIVER & RED DE TRANSITS
    # ------------------------------------------------------------------
    def _build_btr_transits_view(self):
        self.btr_frame.grid_columnconfigure(0, weight=1)
        self.btr_frame.grid_rowconfigure(2, weight=1)

        # Bloque superior: BTR Driver
        btr_card = ctk.CTkFrame(
            self.btr_frame,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        btr_card.grid(row=0, column=0, pady=(0, 8), sticky="ew")
        btr_card.grid_columnconfigure(0, weight=1)
        btr_card.grid_columnconfigure(1, weight=1)

        left_btr = ctk.CTkFrame(btr_card, fg_color="transparent")
        left_btr.grid(row=0, column=0, padx=12, pady=10, sticky="nsew")

        maps_str = " · ".join(BTR_SERVICE_DATA["maps"])
        ctk.CTkLabel(
            left_btr,
            text=f"🚐 BTR DRIVER — MAPAS ACTIVOS: {maps_str}",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"],
            wraplength=420,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_btr,
            text=BTR_SERVICE_DATA["unlock_note"],
            font=ui_font(11),
            text_color=C_TEXT_SOFT,
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(4, 4))

        ctk.CTkLabel(
            left_btr,
            text=f"⚠️ {BTR_SERVICE_DATA['hostile_rule']}",
            font=ui_font(11, "bold"),
            text_color=C_AMBER,
            wraplength=420,
            justify="left",
        ).pack(anchor="w")

        # Tabla tarifas BTR
        tbl = ctk.CTkFrame(btr_card, fg_color=C_BG_DEEP, corner_radius=8, border_width=1, border_color=C_BORDER)
        tbl.grid(row=0, column=1, padx=12, pady=10, sticky="nsew")
        for c in range(4):
            tbl.grid_columnconfigure(c, weight=1 if c > 0 else 2)

        headers = ["Servicio BTR", "USEC", "BEAR (Desc.)", "Scav"]
        for c, h in enumerate(headers):
            ctk.CTkLabel(
                tbl,
                text=h,
                font=ui_font(11, "bold"),
                text_color=THEME["accent_gold"] if c == 0 else (C_GREEN_LIGHT if c == 2 else C_TEXT_MUTED),
            ).grid(row=0, column=c, padx=6, pady=(8, 4), sticky="w" if c == 0 else "")

        for r, srv in enumerate(BTR_SERVICE_DATA["services"], start=1):
            vals = [srv["service"], srv["usec"], srv["bear"], srv["scav"]]
            for c, val in enumerate(vals):
                ctk.CTkLabel(
                    tbl,
                    text=val,
                    font=ui_font(11, "bold" if c in (0, 2) else "normal"),
                    text_color=C_TEXT_SOFT if c == 0 else (C_GREEN_LIGHT if c == 2 else C_TEXT_MUTED),
                ).grid(row=r, column=c, padx=6, pady=3, sticky="w" if c == 0 else "")

        # Bloque medio: Filtro de Transits + Multiplicador EXP
        fbar = ctk.CTkFrame(
            self.btr_frame,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        fbar.grid(row=1, column=0, pady=(0, 8), sticky="ew")
        fbar.grid_columnconfigure(0, weight=1)

        top_f = ctk.CTkFrame(fbar, fg_color="transparent")
        top_f.grid(row=0, column=0, padx=12, pady=(8, 3), sticky="ew")
        top_f.grid_columnconfigure(0, weight=1)

        self.transit_search_entry = ctk.CTkEntry(
            top_f,
            height=30,
            placeholder_text="Buscar mapa origen, destino o ubicación...",
            font=ui_font(12),
            fg_color=C_BG_DEEP,
            border_color=THEME["border"],
        )
        self.transit_search_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.transit_search_entry.bind("<KeyRelease>", self._on_transit_search_key)

        self.transit_count_lbl = ctk.CTkLabel(
            top_f,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        )
        self.transit_count_lbl.grid(row=0, column=1, padx=(6, 0), sticky="e")

        exp_strip = "   ".join(f"{k}: {v}" for k, v in TRANSIT_EXP_MULTIPLIERS)
        ctk.CTkLabel(
            fbar,
            text=f"🔥 Bonus EXP por Tránsito Continuo:  {exp_strip}",
            font=ui_font(11, "bold"),
            text_color=C_EMERALD,
            anchor="w",
        ).grid(row=1, column=0, padx=12, pady=(0, 4), sticky="ew")

        pills_row = ctk.CTkFrame(fbar, fg_color="transparent")
        pills_row.grid(row=2, column=0, padx=10, pady=(2, 8), sticky="ew")

        ctk.CTkLabel(
            pills_row,
            text="Origen:",
            font=ui_font(11, "bold"),
            text_color=C_TEXT_DIM,
        ).grid(row=0, column=0, padx=(2, 6), pady=2, sticky="w")

        for m_idx, mname in enumerate(TRANSIT_MAP_FILTERS):
            r_pos = m_idx // 6
            c_pos = (m_idx % 6) + 1
            btn = ctk.CTkButton(
                pills_row,
                text=mname,
                height=26,
                width=118,
                corner_radius=12,
                font=ui_font(11, "bold"),
                border_width=1,
                command=lambda m=mname: self._set_transit_map(m),
            )
            btn.grid(row=r_pos, column=c_pos, padx=2, pady=2, sticky="w")
            self._transit_map_btns[mname] = btn

        self._update_transit_map_styles()

        # Listado batch-rendered de Transits
        self.transit_scroll = ctk.CTkScrollableFrame(
            self.btr_frame,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.transit_scroll.grid(row=2, column=0, sticky="nsew")
        self.transit_scroll.grid_columnconfigure(0, weight=1)
        self.transit_scroll.grid_columnconfigure(1, weight=1)

    def _on_transit_search_key(self, _event=None):
        if self._transit_search_job:
            self.after_cancel(self._transit_search_job)
        self._transit_search_job = self.after(120, self._schedule_transits_render)

    def _set_transit_map(self, map_name: str):
        self.active_transit_map = map_name
        self._update_transit_map_styles()
        self._schedule_transits_render()

    def _update_transit_map_styles(self):
        for mname, btn in self._transit_map_btns.items():
            active = mname == self.active_transit_map
            btn.configure(
                fg_color=THEME["accent_gold"] if active else C_SLATE_700,
                text_color="#0F172A" if active else C_TEXT_SOFT,
                border_color=THEME["accent_gold"] if active else THEME["border"],
                hover_color="#E5C992" if active else C_BG_ROW_ALT,
            )

    def _schedule_transits_render(self):
        self._transit_token += 1
        token = self._transit_token
        query = self.transit_search_entry.get() if hasattr(self, "transit_search_entry") else ""
        items = filter_transits(from_map=self.active_transit_map, query=query)
        self.transit_count_lbl.configure(text=f"{len(items)} rutas")

        for child in self.transit_scroll.winfo_children():
            child.destroy()

        if not items:
            ctk.CTkLabel(
                self.transit_scroll,
                text="No hay rutas de Transit que coincidan con ese filtro.",
                font=ui_font(13),
                text_color=C_TEXT_DIM,
            ).grid(row=0, column=0, columnspan=2, padx=20, pady=30)
            return

        self._render_transits_batch(items, 0, token)

    def _render_transits_batch(self, items: List[Dict[str, Any]], start: int, token: int):
        if not self.winfo_exists() or token != self._transit_token:
            return
        batch_size = 16
        end = min(start + batch_size, len(items))
        for idx in range(start, end):
            tr = items[idx]
            r = idx // 2
            c = idx % 2
            is_pmc_only = tr.get("faction") == "PMC"

            card = tk.Frame(
                self.transit_scroll,
                bg=C_BG_ROW,
                highlightbackground=C_AMBER if is_pmc_only else C_BORDER,
                highlightthickness=1,
                bd=0,
            )
            card.grid(row=r, column=c, padx=6, pady=4, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)

            top = tk.Frame(card, bg=C_BG_ROW, bd=0)
            top.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="ew")
            top.grid_columnconfigure(0, weight=1)

            tk.Label(
                top,
                text=f"{tr['from_map']}  ➔  {tr['to_map']}",
                font=ui_font(12, "bold"),
                bg=C_BG_ROW,
                fg=C_WHITE,
                anchor="w",
                bd=0,
            ).grid(row=0, column=0, sticky="w")

            tk.Label(
                top,
                text=f" {tr['faction']} ",
                font=ui_font(9, "bold"),
                bg="#B45309" if is_pmc_only else "#0F766E",
                fg=C_WHITE,
                padx=5,
                pady=2,
                bd=0,
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            tk.Label(
                card,
                text=f"📍 {tr['notes']}",
                font=ui_font(10),
                bg=C_BG_ROW,
                fg=C_TEXT_MUTED,
                wraplength=390,
                justify="left",
                anchor="w",
                bd=0,
            ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="w")

        if end < len(items):
            self.after(4, lambda: self._render_transits_batch(items, end, token))

    # ------------------------------------------------------------------
    # Integración con Búsqueda Global (Ctrl+K)
    # ------------------------------------------------------------------
    def open_from_search(self, target: str):
        """Enruta resultados de Ctrl+K con prefijos SKILL:, KARMA:, BTR:, TRANSIT:."""
        raw = (target or "").strip()
        if raw.startswith("SKILL:"):
            skill_name = raw.split(":", 1)[1].strip()
            self.active_skill_cat = "Todas"
            self._update_skill_cat_styles()
            self.skill_search_entry.delete(0, "end")
            self.skill_search_entry.insert(0, skill_name)
            matched = filter_skills(category="Todas", query=skill_name)
            if matched:
                self.selected_skill_id = matched[0]["id"]
            self._switch_view("skills")
        elif raw.startswith("KARMA:"):
            self._switch_view("karma")
        elif raw.startswith("BTR:"):
            self._switch_view("btr_transits")
            self.active_transit_map = "Todos"
            self._update_transit_map_styles()
            self.transit_search_entry.delete(0, "end")
            self._schedule_transits_render()
        elif raw.startswith("TRANSIT:"):
            self._switch_view("btr_transits")
            map_name = raw.split(":", 1)[1].strip()
            if map_name in TRANSIT_MAP_FILTERS:
                self.active_transit_map = map_name
                self.transit_search_entry.delete(0, "end")
            else:
                self.active_transit_map = "Todos"
                self.transit_search_entry.delete(0, "end")
                self.transit_search_entry.insert(0, map_name)
            self._update_transit_map_styles()
            self._schedule_transits_render()
        else:
            self._switch_view("skills")
