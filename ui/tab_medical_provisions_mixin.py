"""
TarkovScope - Mixin UI Lazy para TabMedical:
  1. Provisions & Buffs (Comida, Bebidas, Alcohol, FiR)
  2. Matriz del Sistema de Salud (Debuffs & Curas rápidas)
"""
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from core.config import THEME
from core.i18n import get_active_lang, t_ui
from core.provisions_health_data import (
    HEALTH_EFFECTS_CATALOG,
    PROVISION_CATEGORIES,
    PROVISIONS_CATALOG,
    filter_provisions,
)
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_ROW,
    C_BLUE,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED,
    C_SLATE_700,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)

SEVERITY_COLORS: Dict[str, str] = {
    "Crítico": "#DC2626",
    "Alto": "#EA580C",
    "Medio": "#D97706",
    "Buff": "#059669",
}

TIER_COLORS: Dict[str, str] = {
    "S": "#059669",
    "A": "#0284C7",
    "B": "#D97706",
    "C": "#64748B",
}


class MedicalProvisionsMixin:
    """Mixin lazy para Provisiones & Buffs y Matriz de Estados de Salud."""

    def _init_provisions_state(self):
        self._active_med_mode: str = "medical"
        self._provisions_built: bool = False
        self._health_effects_built: bool = False
        self._active_prov_cat: str = "Todas"
        self._prov_only_buffs: bool = False
        self._prov_only_fir: bool = False
        self._prov_token: int = 0
        self._prov_search_job: Optional[str] = None
        self._prov_cat_btns: Dict[str, ctk.CTkButton] = {}
        self._med_mode_btns: Dict[str, ctk.CTkButton] = {}

    def _switch_medical_mode(self, mode: str):
        self._active_med_mode = mode
        for key, btn in self._med_mode_btns.items():
            act = key == mode
            btn.configure(
                fg_color=THEME["accent_gold"] if act else C_SLATE_700,
                text_color="#0F172A" if act else C_TEXT_SOFT,
                border_color=THEME["accent_gold"] if act else C_BORDER,
            )

        for frame in (self.med_filters_bar, self.med_split_frame, self.provisions_frame, self.health_effects_frame):
            frame.grid_forget()

        if mode == "medical":
            self.med_filters_bar.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 8))
            self.med_split_frame.grid(row=2, column=0, sticky="nsew", padx=2, pady=0)
        elif mode == "provisions":
            if not self._provisions_built:
                self._provisions_built = True
                self._build_provisions_view()
            self.provisions_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=2, pady=0)
        elif mode == "health_effects":
            if not self._health_effects_built:
                self._health_effects_built = True
                self._build_health_effects_view()
            self.health_effects_frame.grid(row=1, column=0, rowspan=2, sticky="nsew", padx=2, pady=0)

    # ------------------------------------------------------------------
    # Sub-vista: PROVISIONS & BUFFS
    # ------------------------------------------------------------------
    def _build_provisions_view(self):
        root = self.provisions_frame
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        ctrl = ctk.CTkFrame(
            root,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        ctrl.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctrl.grid_columnconfigure(1, weight=1)

        cat_box = ctk.CTkFrame(ctrl, fg_color="transparent")
        cat_box.grid(row=0, column=0, padx=10, pady=8, sticky="w")
        for cat in PROVISION_CATEGORIES:
            btn = ctk.CTkButton(
                cat_box,
                text=cat,
                height=28,
                width=0,
                corner_radius=14,
                font=ui_font(11, "bold"),
                command=lambda c=cat: self._select_prov_cat(c),
            )
            btn.pack(side="left", padx=2)
            self._prov_cat_btns[cat] = btn

        self.prov_search_entry = ctk.CTkEntry(
            ctrl,
            height=30,
            placeholder_text=t_ui(
                "🔍 Buscar comida, bebida o buff (Aquamari, Moonshine, MRE, Tushonka...)",
                "🔍 Search food, drink or buff (Aquamari, Moonshine, MRE, Tushonka...)",
            ),
            font=ui_font(11),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
        )
        self.prov_search_entry.grid(row=0, column=1, padx=8, pady=8, sticky="ew")
        self.prov_search_entry.bind("<KeyRelease>", self._on_prov_search_key)

        toggles = ctk.CTkFrame(ctrl, fg_color="transparent")
        toggles.grid(row=0, column=2, padx=10, pady=8, sticky="e")

        self.prov_buffs_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            toggles,
            text=t_ui("Meta / Buffs", "Meta / Buffs"),
            variable=self.prov_buffs_var,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_gold"],
            command=self._schedule_prov_render,
        ).pack(side="left", padx=6)

        self.prov_fir_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            toggles,
            text=t_ui("Uso FiR / Quest", "FiR / Quest Use"),
            variable=self.prov_fir_var,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=C_EMERALD,
            command=self._schedule_prov_render,
        ).pack(side="left", padx=6)

        self.prov_scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        self.prov_scroll.grid(row=1, column=0, sticky="nsew")
        self.prov_scroll.grid_columnconfigure((0, 1), weight=1)

        self._update_prov_cat_styles()
        self._schedule_prov_render()

    def _select_prov_cat(self, cat: str):
        self._active_prov_cat = cat
        self._update_prov_cat_styles()
        self._schedule_prov_render()

    def _on_prov_search_key(self, _event=None):
        if self._prov_search_job is not None:
            self.after_cancel(self._prov_search_job)
        self._prov_search_job = self.after(120, self._schedule_prov_render)

    def _update_prov_cat_styles(self):
        for cat, btn in self._prov_cat_btns.items():
            act = cat == self._active_prov_cat
            btn.configure(
                fg_color=THEME["accent_gold"] if act else C_SLATE_700,
                text_color="#0F172A" if act else C_TEXT_SOFT,
            )

    def _schedule_prov_render(self):
        self._prov_token += 1
        token = self._prov_token
        for w in self.prov_scroll.winfo_children():
            w.destroy()

        q = self.prov_search_entry.get() if hasattr(self, "prov_search_entry") else ""
        items = filter_provisions(
            category=self._active_prov_cat,
            query=q,
            only_buffs=bool(self.prov_buffs_var.get()) if hasattr(self, "prov_buffs_var") else False,
            only_fir=bool(self.prov_fir_var.get()) if hasattr(self, "prov_fir_var") else False,
        )
        if not items:
            ctk.CTkLabel(
                self.prov_scroll,
                text=t_ui("No se encontraron provisiones con ese filtro.", "No provisions match this filter."),
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
            ).grid(row=0, column=0, columnspan=2, pady=30)
            return

        self._render_prov_batch(items, 0, token)

    def _safe_set_prov_icon(self, lbl: ctk.CTkLabel, img: ctk.CTkImage):
        if not self.winfo_exists():
            return
        try:
            self.after(0, lambda: lbl.winfo_exists() and lbl.configure(image=img))
        except Exception:
            pass

    def _render_prov_batch(self, items: List[Dict[str, Any]], start: int, token: int):
        if not self.winfo_exists() or token != self._prov_token:
            return
        is_en = get_active_lang() == "en"
        end = min(start + 14, len(items))
        for idx in range(start, end):
            p = items[idx]
            r, c = idx // 2, idx % 2
            tier = p.get("meta_tier", "B")
            t_col = TIER_COLORS.get(tier, "#64748B")

            card = ctk.CTkFrame(
                self.prov_scroll,
                fg_color=C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=5)
            card.grid_columnconfigure(1, weight=1)

            icon_box = ctk.CTkFrame(
                card,
                width=66,
                height=66,
                fg_color=C_BG_DEEP,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            icon_box.grid(row=0, column=0, rowspan=3, padx=(10, 8), pady=10, sticky="nw")
            icon_box.grid_propagate(False)
            icon_lbl = ctk.CTkLabel(icon_box, text="")
            icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
            p_icon = get_gear_ctk_icon(
                p.get("icon_key", p["id"]),
                p.get("icon_url", ""),
                max_size=(56, 56),
                on_ready=lambda img, lbl=icon_lbl: self._safe_set_prov_icon(lbl, img),
            )
            if p_icon is not None:
                icon_lbl.configure(image=p_icon)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(8, 4))
            ctk.CTkLabel(
                top,
                text=p["name"],
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).pack(side="left")

            ctk.CTkLabel(
                top,
                text=f" TIER {tier} ",
                font=ui_font(10, "bold"),
                fg_color=t_col,
                text_color=C_WHITE,
                corner_radius=4,
            ).pack(side="right")

            en_val = p["energy"]
            hy_val = p["hydration"]
            en_txt = f"+{en_val}" if en_val >= 0 else str(en_val)
            hy_txt = f"+{hy_val}" if hy_val >= 0 else str(hy_val)
            use_s = int(p.get("use_time", 3) or 3)
            barter_txt = t_ui("Sí", "Yes") if p.get("is_barter") else "No"
            craft_txt = t_ui("Sí", "Yes") if p.get("is_craft") else "No"

            stats_row = ctk.CTkFrame(card, fg_color=C_BG_ROW, corner_radius=6)
            stats_row.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(0, 4))
            ctk.CTkLabel(
                stats_row,
                text=(
                    f"⚡ {en_txt}   |   💧 {hy_txt}   |   ⏱ {use_s}s   |   "
                    f"🔄 Barter: {barter_txt} · ⚗️ Craft: {craft_txt}"
                ),
                font=ui_font(11, "bold"),
                text_color=C_GREEN_LIGHT if hy_val >= 0 else C_AMBER,
            ).pack(anchor="w", padx=10, pady=5)

            buff_txt = p["buffs_en"] if is_en else p["buffs_es"]
            fir_txt = p["fir_usage_en"] if is_en else p["fir_usage_es"]
            ctk.CTkLabel(
                card,
                text=f"✨ {buff_txt}\n📦 FiR / Quest: {fir_txt}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=390,
            ).grid(row=2, column=1, sticky="w", padx=(0, 12), pady=(2, 8))

        if end < len(items):
            self.after(4, lambda: self._render_prov_batch(items, end, token))

    # ------------------------------------------------------------------
    # Sub-vista: HEALTH SYSTEM & STATUS EFFECTS
    # ------------------------------------------------------------------
    def _build_health_effects_view(self):
        root = self.health_effects_frame
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        banner = ctk.CTkFrame(
            root,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        banner.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        ctk.CTkLabel(
            banner,
            text=t_ui(
                "🩺 MATRIZ DEL SISTEMA DE SALUD: ESTADOS ALTERADOS, DEBUFFS Y CURAS INMEDIATAS",
                "🩺 HEALTH SYSTEM MATRIX: STATUS EFFECTS, DEBUFFS & INSTANT CURES",
            ),
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"],
        ).pack(anchor="w", padx=14, pady=(8, 2))
        ctk.CTkLabel(
            banner,
            text=t_ui(
                "Consulta rápida de supervivencia: qué provoca cada estado, cómo impacta al PMC y qué medkit o stim lo elimina.",
                "Rapid survival reference: causes, PMC combat penalties, and optimal healing items.",
            ),
            font=ui_font(11),
            text_color=C_TEXT_DIM,
        ).pack(anchor="w", padx=14, pady=(0, 8))

        scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        is_en = get_active_lang() == "en"
        for idx, eff in enumerate(HEALTH_EFFECTS_CATALOG):
            r, c = idx // 2, idx % 2
            sev = eff.get("severity", "Medio")
            sev_col = SEVERITY_COLORS.get(sev, "#D97706")

            card = ctk.CTkFrame(
                scroll,
                fg_color=C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=6, pady=5)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=12, pady=(8, 4))
            ctk.CTkLabel(
                top,
                text=eff["name_en"] if is_en else eff["name_es"],
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).pack(side="left")
            ctk.CTkLabel(
                top,
                text=f" {sev.upper()} ",
                font=ui_font(10, "bold"),
                fg_color=sev_col,
                text_color=C_WHITE,
                corner_radius=4,
            ).pack(side="right")

            causes = eff["causes_en"] if is_en else eff["causes_es"]
            impact = eff["impact_en"] if is_en else eff["impact_es"]
            cures = " • ".join(eff["best_cures"])
            ctk.CTkLabel(
                card,
                text=f"⚡ Causa: {causes}\n⚠️ Impacto: {impact}\n💊 Cura óptima: {cures}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=470,
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def open_from_search(self, target: str):
        """Enruta resultados de Ctrl+K con prefijos PROV:, EFFECT: o búsqueda médica estándar."""
        raw = (target or "").strip()
        if raw.startswith("PROV:"):
            q = raw.split(":", 1)[1].strip()
            self._switch_medical_mode("provisions")
            if hasattr(self, "prov_search_entry"):
                self.prov_search_entry.delete(0, "end")
                self.prov_search_entry.insert(0, q)
                self._schedule_prov_render()
        elif raw.startswith("EFFECT:"):
            self._switch_medical_mode("health_effects")
        else:
            self._switch_medical_mode("medical")
            if hasattr(self, "entry_search"):
                self.entry_search.delete(0, "end")
                self.entry_search.insert(0, raw)
                self._schedule_render_items()
