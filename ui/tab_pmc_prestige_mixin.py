"""
TarkovScope - Mixin UI Lazy para PMC Systems:
  1. Prestige & Arena / Ref Sync
  2. Achievements Tracker (con checklist persistente)
  3. Tactical Clothing (Ragman / Ref USEC & BEAR)
"""
from typing import Any, Dict, List, Optional, Set
import customtkinter as ctk

from core.config import THEME
from core.i18n import get_active_lang, t_ui
from core.pmc_prestige_achievements_data import (
    ACHIEVEMENT_CATEGORIES,
    ACHIEVEMENTS_CATALOG,
    ARENA_REF_SYNC_GUIDE,
    CLOTHING_FACTIONS,
    CLOTHING_SLOTS,
    PRESTIGE_LEVELS_DATA,
    PRESTIGE_RESET_MATRIX,
    filter_achievements,
    filter_tactical_clothing,
)
from core.user_data import (
    get_prestige_level,
    get_unlocked_achievement_ids,
    set_prestige_level,
    toggle_achievement_unlocked,
)
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_PANEL_ALT,
    C_BG_ROW,
    C_BLUE,
    C_BORDER,
    C_EMERALD,
    C_GREEN,
    C_GREEN_LIGHT,
    C_RED,
    C_SLATE_700,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)

RARITY_COLORS: Dict[str, str] = {
    "Common": "#64748B",
    "Rare": "#0284C7",
    "Ultra Rare": "#9333EA",
    "Legendary": "#D97706",
}


class PMCPrestigeAchievementsMixin:
    """Mixin lazy para sub-vistas de Prestige/Arena, Achievements y Ropa Táctica."""

    def _init_prestige_ach_state(self):
        self._prestige_built = False
        self._achievements_built = False
        self._clothing_built = False
        self._selected_prestige_lvl: int = 1
        self._active_ach_cat: str = "Todos"
        self._ach_only_missing: bool = False
        self._ach_token: int = 0
        self._ach_search_job: Optional[str] = None
        self._ach_cat_btns: Dict[str, ctk.CTkButton] = {}
        self._active_cloth_faction: str = "Todas"
        self._active_cloth_slot: str = "Todos"
        self._cloth_token: int = 0
        self._cloth_search_job: Optional[str] = None
        self._cloth_faction_btns: Dict[str, ctk.CTkButton] = {}
        self._cloth_slot_btns: Dict[str, ctk.CTkButton] = {}

    # ------------------------------------------------------------------
    # Sub-vista 4: PRESTIGE & ARENA / REF
    # ------------------------------------------------------------------
    def _build_prestige_view(self):
        root = self.prestige_frame
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # Barra superior de estado Prestige del jugador
        top_bar = ctk.CTkFrame(
            root,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_bar,
            text=t_ui(
                "🏆 SISTEMA DE PRESTIGE & SINCRONIZACIÓN ARENA / REF",
                "🏆 PRESTIGE SYSTEM & ARENA / REF SYNCHRONIZATION",
            ),
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            top_bar,
            text=t_ui(
                "Registra tu rango actual de Prestige y revisa requisitos, retención de skills y llaves exclusivas de Ref.",
                "Track your current Prestige rank, requirements, skill retention, and Ref's exclusive keys.",
            ),
            font=ui_font(11),
            text_color=C_TEXT_DIM,
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        lvl_box = ctk.CTkFrame(top_bar, fg_color="transparent")
        lvl_box.grid(row=0, column=1, rowspan=2, padx=12, pady=8, sticky="e")

        ctk.CTkLabel(
            lvl_box,
            text=t_ui("Tu Prestige:", "Your Prestige:"),
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
        ).pack(side="left", padx=(0, 6))

        self._user_prestige_btns: Dict[int, ctk.CTkButton] = {}
        cur_p = get_prestige_level()
        for lvl, lbl in [(0, "0"), (1, "I"), (2, "II"), (3, "III"), (4, "IV"), (5, "V"), (6, "VI")]:
            b = ctk.CTkButton(
                lvl_box,
                text=lbl,
                height=30,
                width=36,
                corner_radius=7,
                font=ui_font(11, "bold"),
                border_width=1,
                command=lambda v=lvl: self._set_user_prestige(v),
            )
            b.pack(side="left", padx=2)
            self._user_prestige_btns[lvl] = b
        self._refresh_user_prestige_btns(cur_p)

        # Contenido scrolleable principal
        scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        scroll.grid_columnconfigure(1, weight=1)

        is_en = get_active_lang() == "en"

        # Tarjetas Prestige 1 a Prestige 6 (grilla 2x3)
        for idx, p_data in enumerate(PRESTIGE_LEVELS_DATA):
            p_row = idx // 2
            p_col = idx % 2
            card = ctk.CTkFrame(
                scroll,
                fg_color=C_BG_PANEL,
                corner_radius=10,
                border_width=1,
                border_color=THEME["accent_gold"] if idx == len(PRESTIGE_LEVELS_DATA) - 1 else C_BORDER,
            )
            card.grid(row=p_row, column=p_col, sticky="nsew", padx=8, pady=8)

            hdr_row = ctk.CTkFrame(card, fg_color="transparent")
            hdr_row.pack(fill="x", padx=14, pady=(12, 4))

            icon_lbl = ctk.CTkLabel(hdr_row, text="", width=52, height=52)
            icon_lbl.pack(side="left", padx=(0, 10))
            p_icon = get_gear_ctk_icon(
                p_data.get("icon_key", ""),
                p_data.get("icon_url", ""),
                max_size=(52, 52),
                on_ready=lambda img, lbl=icon_lbl: self._safe_set_label_icon(lbl, img),
            )
            if p_icon is not None:
                icon_lbl.configure(image=p_icon)

            title_box = ctk.CTkFrame(hdr_row, fg_color="transparent")
            title_box.pack(side="left", fill="x", expand=True)
            ctk.CTkLabel(
                title_box,
                text=p_data["title_en"] if is_en else p_data["title_es"],
                font=ui_font(14, "bold"),
                text_color=THEME["accent_gold"],
                anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                title_box,
                text=p_data["summary_en"] if is_en else p_data["summary_es"],
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                wraplength=415,
                justify="left",
                anchor="w",
            ).pack(anchor="w", pady=(2, 0))

            ctk.CTkLabel(
                card,
                text=t_ui("📋 Requisitos Exactos:", "📋 Exact Requirements:"),
                font=ui_font(12, "bold"),
                text_color=C_AMBER,
            ).pack(anchor="w", padx=14, pady=(4, 2))
            reqs = p_data["requirements_en"] if is_en else p_data["requirements_es"]
            for r_txt in reqs:
                ctk.CTkLabel(
                    card,
                    text=f"  • {r_txt}",
                    font=ui_font(11),
                    text_color=C_TEXT_SOFT,
                    wraplength=470,
                    justify="left",
                ).pack(anchor="w", padx=14, pady=1)

            ctk.CTkLabel(
                card,
                text=t_ui("🎁 Recompensas Permanentes:", "🎁 Permanent Rewards:"),
                font=ui_font(12, "bold"),
                text_color=C_GREEN_LIGHT,
            ).pack(anchor="w", padx=14, pady=(8, 2))
            rews = p_data["rewards_en"] if is_en else p_data["rewards_es"]
            for rw_txt in rews:
                ctk.CTkLabel(
                    card,
                    text=f"  ★ {rw_txt}",
                    font=ui_font(11),
                    text_color=C_GREEN_LIGHT,
                    wraplength=470,
                    justify="left",
                ).pack(anchor="w", padx=14, pady=1)

            ctk.CTkFrame(card, height=8, fg_color="transparent").pack()

        # Matriz Qué se Conserva vs Qué se Resetea
        matrix_row = (len(PRESTIGE_LEVELS_DATA) + 1) // 2
        kept_card = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_EMERALD,
        )
        kept_card.grid(row=matrix_row, column=0, sticky="nsew", padx=8, pady=6)
        ctk.CTkLabel(
            kept_card,
            text=t_ui("✅ LO QUE CONSERVÁS AL HACER PRESTIGE", "✅ WHAT YOU KEEP ON PRESTIGE"),
            font=ui_font(13, "bold"),
            text_color=C_GREEN_LIGHT,
        ).pack(anchor="w", padx=14, pady=(10, 6))
        for item in PRESTIGE_RESET_MATRIX["kept"]:
            ctk.CTkLabel(
                kept_card,
                text=f"  ✓ {item['en'] if is_en else item['es']}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                wraplength=470,
                justify="left",
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(kept_card, height=8, fg_color="transparent").pack()

        reset_card = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_RED,
        )
        reset_card.grid(row=matrix_row, column=1, sticky="nsew", padx=8, pady=6)
        ctk.CTkLabel(
            reset_card,
            text=t_ui("🔄 LO QUE SE REINICIA A NIVEL 1", "🔄 WHAT RESETS TO LEVEL 1"),
            font=ui_font(13, "bold"),
            text_color=C_RED,
        ).pack(anchor="w", padx=14, pady=(10, 6))
        for item in PRESTIGE_RESET_MATRIX["reset"]:
            ctk.CTkLabel(
                reset_card,
                text=f"  ✕ {item['en'] if is_en else item['es']}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                wraplength=470,
                justify="left",
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(reset_card, height=8, fg_color="transparent").pack()

        # Guía Tarkov: Arena & Ref Sync
        arena_card = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_BLUE,
        )
        arena_card.grid(row=matrix_row + 1, column=0, columnspan=2, sticky="ew", padx=8, pady=(6, 10))
        ctk.CTkLabel(
            arena_card,
            text=t_ui(
                "⚔️ GUÍA DE SINCRONIZACIÓN: TARKOV ↔ ARENA & COMERCIANTE REF",
                "⚔️ CROSS-PROGRESSION GUIDE: TARKOV ↔ ARENA & TRADER REF",
            ),
            font=ui_font(13, "bold"),
            text_color=C_BLUE,
        ).pack(anchor="w", padx=14, pady=(10, 6))

        for row in ARENA_REF_SYNC_GUIDE:
            box = ctk.CTkFrame(arena_card, fg_color=C_BG_ROW, corner_radius=8)
            box.pack(fill="x", padx=14, pady=4)
            ctk.CTkLabel(
                box,
                text=row["topic_en"] if is_en else row["topic_es"],
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"],
            ).pack(anchor="w", padx=12, pady=(6, 2))
            ctk.CTkLabel(
                box,
                text=row["detail_en"] if is_en else row["detail_es"],
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                wraplength=980,
                justify="left",
            ).pack(anchor="w", padx=12, pady=(0, 8))

        ctk.CTkFrame(arena_card, height=8, fg_color="transparent").pack()

    def _safe_set_label_icon(self, lbl: ctk.CTkLabel, img: ctk.CTkImage):
        if not self.winfo_exists():
            return
        try:
            self.after(0, lambda: lbl.winfo_exists() and lbl.configure(image=img))
        except Exception:
            pass

    def _set_user_prestige(self, level: int):
        saved = set_prestige_level(level)
        self._refresh_user_prestige_btns(saved)

    def _refresh_user_prestige_btns(self, active_lvl: int):
        for lvl, btn in getattr(self, "_user_prestige_btns", {}).items():
            is_act = lvl == active_lvl
            btn.configure(
                fg_color=THEME["accent_gold"] if is_act else C_SLATE_700,
                text_color="#0F172A" if is_act else C_TEXT_SOFT,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
            )

    # ------------------------------------------------------------------
    # Sub-vista 5: ACHIEVEMENTS TRACKER (CHECKLIST)
    # ------------------------------------------------------------------
    def _build_achievements_view(self):
        root = self.achievements_frame
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        ctrl = ctk.CTkFrame(
            root,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctrl.grid_columnconfigure(1, weight=1)

        cat_row = ctk.CTkFrame(ctrl, fg_color="transparent")
        cat_row.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        for cat in ACHIEVEMENT_CATEGORIES:
            btn = ctk.CTkButton(
                cat_row,
                text=cat,
                height=28,
                width=0,
                corner_radius=14,
                font=ui_font(11, "bold"),
                command=lambda c=cat: self._select_ach_cat(c),
            )
            btn.pack(side="left", padx=2)
            self._ach_cat_btns[cat] = btn

        self.ach_search_entry = ctk.CTkEntry(
            ctrl,
            height=30,
            placeholder_text=t_ui(
                "🔍 Buscar logro (Killer7, Snowball, Killa, Lightkeeper...)",
                "🔍 Search achievement (Killer7, Snowball, Killa, Lightkeeper...)",
            ),
            font=ui_font(11),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
        )
        self.ach_search_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.ach_search_entry.bind("<KeyRelease>", self._on_ach_search_key)

        right_ctrl = ctk.CTkFrame(ctrl, fg_color="transparent")
        right_ctrl.grid(row=0, column=2, padx=10, pady=8, sticky="e")

        self.ach_missing_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            right_ctrl,
            text=t_ui("Solo pendientes", "Only pending"),
            variable=self.ach_missing_var,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_gold"],
            command=self._toggle_ach_only_missing,
        ).pack(side="left", padx=(0, 10))

        self.ach_kpi_lbl = ctk.CTkLabel(
            right_ctrl,
            text="",
            font=ui_font(12, "bold"),
            fg_color=C_BG_DEEP,
            text_color=C_GREEN_LIGHT,
            corner_radius=6,
            padx=10,
            pady=5,
        )
        self.ach_kpi_lbl.pack(side="left")

        self.ach_scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        self.ach_scroll.grid(row=1, column=0, sticky="nsew")
        self.ach_scroll.grid_columnconfigure(0, weight=1)

        self._update_ach_cat_styles()
        self._schedule_ach_render()

    def _select_ach_cat(self, cat: str):
        self._active_ach_cat = cat
        self._update_ach_cat_styles()
        self._schedule_ach_render()

    def _toggle_ach_only_missing(self):
        self._ach_only_missing = bool(self.ach_missing_var.get())
        self._schedule_ach_render()

    def _on_ach_search_key(self, _event=None):
        if self._ach_search_job is not None:
            self.after_cancel(self._ach_search_job)
        self._ach_search_job = self.after(120, self._schedule_ach_render)

    def _update_ach_cat_styles(self):
        for cat, btn in self._ach_cat_btns.items():
            act = cat == self._active_ach_cat
            btn.configure(
                fg_color=THEME["accent_gold"] if act else C_SLATE_700,
                text_color="#0F172A" if act else C_TEXT_SOFT,
                hover_color=THEME["accent_gold"] if act else THEME["btn_hover"],
            )

    def _schedule_ach_render(self):
        self._ach_token += 1
        token = self._ach_token
        for w in self.ach_scroll.winfo_children():
            w.destroy()

        unlocked = get_unlocked_achievement_ids()
        total_all = len(ACHIEVEMENTS_CATALOG)
        done_cnt = sum(1 for a in ACHIEVEMENTS_CATALOG if a["id"] in unlocked)
        self.ach_kpi_lbl.configure(
            text=t_ui(f"🎖️ {done_cnt}/{total_all} Desbloqueados", f"🎖️ {done_cnt}/{total_all} Unlocked")
        )

        q = self.ach_search_entry.get() if hasattr(self, "ach_search_entry") else ""
        items = filter_achievements(
            category=self._active_ach_cat,
            query=q,
            only_missing=self._ach_only_missing,
            unlocked_ids=unlocked,
        )
        if not items:
            ctk.CTkLabel(
                self.ach_scroll,
                text=t_ui("No hay logros para este filtro.", "No achievements match this filter."),
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
            ).grid(row=0, column=0, pady=30)
            return

        self._render_ach_batch(items, 0, token, unlocked)

    def _render_ach_batch(self, items: List[Dict[str, Any]], start: int, token: int, unlocked: Set[str]):
        if not self.winfo_exists() or token != self._ach_token:
            return
        is_en = get_active_lang() == "en"
        end = min(start + 12, len(items))
        for idx in range(start, end):
            ach = items[idx]
            is_done = ach["id"] in unlocked
            rar_col = RARITY_COLORS.get(ach.get("rarity", "Common"), "#64748B")

            card = ctk.CTkFrame(
                self.ach_scroll,
                fg_color="#122B22" if is_done else C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_EMERALD if is_done else C_BORDER,
            )
            card.grid(row=idx, column=0, sticky="ew", padx=8, pady=4)
            card.grid_columnconfigure(1, weight=1)

            var = ctk.BooleanVar(value=is_done)
            cb = ctk.CTkCheckBox(
                card,
                text="",
                variable=var,
                width=26,
                fg_color=C_EMERALD,
                command=lambda aid=ach["id"]: self._on_toggle_achievement(aid),
            )
            cb.grid(row=0, column=0, rowspan=2, padx=(12, 6), pady=10)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=1, sticky="ew", padx=(2, 12), pady=(8, 2))
            ctk.CTkLabel(
                top,
                text=ach["name"],
                font=ui_font(13, "bold"),
                text_color=C_GREEN_LIGHT if is_done else THEME["accent_gold"],
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f" {ach['rarity']} • {ach['pct_players']:.1f}% ",
                font=ui_font(10, "bold"),
                fg_color=rar_col,
                text_color=C_WHITE,
                corner_radius=4,
            ).pack(side="left", padx=8)

            ctk.CTkLabel(
                top,
                text=ach["category"],
                font=ui_font(10, "bold"),
                text_color=C_TEXT_DIM,
            ).pack(side="right")

            cond = ach["condition_en"] if is_en else ach["condition_es"]
            tip = ach["tip_en"] if is_en else ach["tip_es"]
            ctk.CTkLabel(
                card,
                text=f"📋 {cond}\n💡 {tip}   |   🎁 {ach['reward']}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=900,
            ).grid(row=1, column=1, sticky="w", padx=(2, 12), pady=(0, 8))

        if end < len(items):
            self.after(4, lambda: self._render_ach_batch(items, end, token, unlocked))

    def _on_toggle_achievement(self, ach_id: str):
        toggle_achievement_unlocked(ach_id)
        self._schedule_ach_render()

    # ------------------------------------------------------------------
    # Sub-vista 6: TACTICAL CLOTHING (RAGMAN / REF)
    # ------------------------------------------------------------------
    def _build_clothing_view(self):
        root = self.clothing_frame
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        ctrl = ctk.CTkFrame(
            root,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctrl.grid_columnconfigure(2, weight=1)

        f_box = ctk.CTkFrame(ctrl, fg_color="transparent")
        f_box.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        for fac in CLOTHING_FACTIONS:
            btn = ctk.CTkButton(
                f_box,
                text=fac,
                height=28,
                width=0,
                corner_radius=14,
                font=ui_font(11, "bold"),
                command=lambda f=fac: self._select_cloth_faction(f),
            )
            btn.pack(side="left", padx=2)
            self._cloth_faction_btns[fac] = btn

        s_box = ctk.CTkFrame(ctrl, fg_color="transparent")
        s_box.grid(row=0, column=1, padx=6, pady=8, sticky="w")
        for sl in CLOTHING_SLOTS:
            short_lbl = sl.split(" (")[0]
            btn = ctk.CTkButton(
                s_box,
                text=short_lbl,
                height=28,
                width=0,
                corner_radius=8,
                font=ui_font(11, "bold"),
                command=lambda s=sl: self._select_cloth_slot(s),
            )
            btn.pack(side="left", padx=2)
            self._cloth_slot_btns[sl] = btn

        self.cloth_search_entry = ctk.CTkEntry(
            ctrl,
            height=30,
            placeholder_text=t_ui(
                "🔍 Buscar vestimenta (Gorka, Predator, Tracksuit, Woodland...)",
                "🔍 Search clothing (Gorka, Predator, Tracksuit, Woodland...)",
            ),
            font=ui_font(11),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
        )
        self.cloth_search_entry.grid(row=0, column=2, padx=(6, 12), pady=8, sticky="ew")
        self.cloth_search_entry.bind("<KeyRelease>", self._on_cloth_search_key)

        self.cloth_scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        self.cloth_scroll.grid(row=1, column=0, sticky="nsew")
        self.cloth_scroll.grid_columnconfigure((0, 1), weight=1)

        self._update_cloth_btn_styles()
        self._schedule_cloth_render()

    def _select_cloth_faction(self, fac: str):
        self._active_cloth_faction = fac
        self._update_cloth_btn_styles()
        self._schedule_cloth_render()

    def _select_cloth_slot(self, slot: str):
        self._active_cloth_slot = slot
        self._update_cloth_btn_styles()
        self._schedule_cloth_render()

    def _on_cloth_search_key(self, _event=None):
        if self._cloth_search_job is not None:
            self.after_cancel(self._cloth_search_job)
        self._cloth_search_job = self.after(120, self._schedule_cloth_render)

    def _update_cloth_btn_styles(self):
        for fac, btn in self._cloth_faction_btns.items():
            act = fac == self._active_cloth_faction
            btn.configure(
                fg_color=THEME["accent_gold"] if act else C_SLATE_700,
                text_color="#0F172A" if act else C_TEXT_SOFT,
            )
        for sl, btn in self._cloth_slot_btns.items():
            act = sl == self._active_cloth_slot
            btn.configure(
                fg_color=C_BLUE if act else C_SLATE_700,
                text_color=C_WHITE if act else C_TEXT_SOFT,
            )

    def _schedule_cloth_render(self):
        self._cloth_token += 1
        token = self._cloth_token
        for w in self.cloth_scroll.winfo_children():
            w.destroy()

        q = self.cloth_search_entry.get() if hasattr(self, "cloth_search_entry") else ""
        items = filter_tactical_clothing(
            faction=self._active_cloth_faction,
            slot=self._active_cloth_slot,
            query=q,
        )
        if not items:
            ctk.CTkLabel(
                self.cloth_scroll,
                text=t_ui("No hay ropa táctica con esos filtros.", "No clothing found for this filter."),
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
            ).grid(row=0, column=0, columnspan=2, pady=30)
            return

        self._render_cloth_batch(items, 0, token)

    def _render_cloth_batch(self, items: List[Dict[str, Any]], start: int, token: int):
        if not self.winfo_exists() or token != self._cloth_token:
            return
        is_en = get_active_lang() == "en"
        end = min(start + 14, len(items))
        for idx in range(start, end):
            item = items[idx]
            r, c = idx // 2, idx % 2
            fac = item["faction"]
            fac_col = "#0284C7" if fac == "USEC" else ("#DC2626" if fac == "BEAR" else "#D97706")

            card = ctk.CTkFrame(
                self.cloth_scroll,
                fg_color=C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=5)
            card.grid_columnconfigure(1, weight=1)

            icon_box = ctk.CTkFrame(
                card,
                width=74,
                height=74,
                fg_color=C_BG_DEEP,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            icon_box.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=10, sticky="nw")
            icon_box.grid_propagate(False)
            icon_lbl = ctk.CTkLabel(icon_box, text="")
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
            c_icon = get_gear_ctk_icon(
                item.get("icon_key", item["id"]),
                item.get("icon_url", ""),
                max_size=(64, 64),
                on_ready=lambda img, lbl=icon_lbl: self._safe_set_label_icon(lbl, img),
            )
            if c_icon is not None:
                icon_lbl.configure(image=c_icon)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(8, 2))
            ctk.CTkLabel(
                top,
                text=item["name"],
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).pack(side="left")
            ctk.CTkLabel(
                top,
                text=f" {fac} ",
                font=ui_font(10, "bold"),
                fg_color=fac_col,
                text_color=C_WHITE,
                corner_radius=4,
            ).pack(side="right")

            note = item["camo_notes_en"] if is_en else item["camo_notes_es"]
            ctk.CTkLabel(
                card,
                text=(
                    f"🏷️ {item['slot']}  |  📈 PMC Nv. {item['pmc_level']}  |  🤝 {item['trader_req']}\n"
                    f"💰 {item['price_text']}  |  📜 Quest: {item['quest_req']}\n"
                    f"🎨 {note}"
                ),
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=390,
            ).grid(row=1, column=1, sticky="w", padx=(0, 12), pady=(0, 8))

        if end < len(items):
            self.after(4, lambda: self._render_cloth_batch(items, end, token))
