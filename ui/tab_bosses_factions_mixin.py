"""
TarkovScope - Mixin UI Lazy para Facciones Hostiles de IA (Rogues, Raiders, Cultists, Black Division, RUAF, Scavs)
"""
from typing import Any, Dict
import customtkinter as ctk

from core.ai_factions_data import AI_FACTIONS_CATALOG
from core.config import THEME
from core.i18n import get_active_lang, t_ui
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_PANEL,
    C_BG_ROW,
    C_BORDER,
    C_GREEN_LIGHT,
    C_RED,
    C_SLATE_700,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


class BossesFactionsMixin:
    """Mixin lazy para alternar entre los 12 Bosses y los dossiers de Facciones de IA."""

    def _init_factions_state(self):
        self._bosses_view_mode: str = "BOSSES"  # "BOSSES" o "FACTIONS"
        self._factions_built: bool = False
        self._selected_faction: Dict[str, Any] = AI_FACTIONS_CATALOG[0]
        self._faction_btns: Dict[str, ctk.CTkButton] = {}

    def _switch_bosses_view_mode(self, mode: str):
        if mode == self._bosses_view_mode:
            return
        self._bosses_view_mode = mode
        is_bosses = mode == "BOSSES"

        self.btn_sub_bosses.configure(
            fg_color=THEME["accent_orange"] if is_bosses else C_SLATE_700,
            text_color=C_WHITE if is_bosses else C_TEXT_SOFT,
        )
        self.btn_sub_factions.configure(
            fg_color=THEME["accent_orange"] if not is_bosses else C_SLATE_700,
            text_color=C_WHITE if not is_bosses else C_TEXT_SOFT,
        )

        if is_bosses:
            if hasattr(self, "factions_scroll"):
                self.factions_scroll.grid_forget()
            if hasattr(self, "factions_detail"):
                self.factions_detail.grid_forget()
            self.boss_list_scroll.grid(row=4, column=0, padx=6, pady=(0, 10), sticky="nsew")
            self.detail_scroll.grid(row=0, column=1, sticky="nsew")
        else:
            self.boss_list_scroll.grid_forget()
            self.detail_scroll.grid_forget()
            if not self._factions_built:
                self._factions_built = True
                self._build_factions_ui()
            self.factions_scroll.grid(row=4, column=0, padx=6, pady=(0, 10), sticky="nsew")
            self.factions_detail.grid(row=0, column=1, sticky="nsew")
            self._select_faction(self._selected_faction)

    def _build_factions_ui(self):
        self.factions_scroll = ctk.CTkScrollableFrame(self.boss_sidebar, fg_color="transparent")
        self.factions_scroll.grid_columnconfigure(0, weight=1)

        for idx, fac in enumerate(AI_FACTIONS_CATALOG):
            btn = ctk.CTkButton(
                self.factions_scroll,
                text=f"☠️  {fac['name']}",
                anchor="w",
                height=48,
                corner_radius=8,
                font=ui_font(13, "bold"),
                fg_color="transparent",
                text_color=THEME["text_main"],
                hover_color=THEME["bg_card_hover"],
                command=lambda f=fac: self._select_faction(f),
            )
            btn.grid(row=idx, column=0, padx=4, pady=3, sticky="ew")
            self._faction_btns[fac["id"]] = btn

        self.factions_detail = ctk.CTkScrollableFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.factions_detail.grid_columnconfigure(0, weight=1)

    def _select_faction(self, fac: Dict[str, Any]):
        self._selected_faction = fac
        for fid, btn in self._faction_btns.items():
            act = fid == fac["id"]
            btn.configure(
                fg_color=THEME["accent_orange"] if act else "transparent",
                text_color=C_WHITE if act else THEME["text_main"],
            )
        self._render_faction_details()

    def _render_faction_details(self):
        for w in self.factions_detail.winfo_children():
            w.destroy()

        fac = self._selected_faction
        is_en = get_active_lang() == "en"

        hdr = ctk.CTkFrame(
            self.factions_detail,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        hdr.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 10))
        ctk.CTkLabel(
            hdr,
            text=f"☠️ {fac['name']}",
            font=ui_font(22, "bold"),
            text_color=THEME["accent_orange"],
        ).pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(
            hdr,
            text=fac["subtitle_en"] if is_en else fac["subtitle_es"],
            font=ui_font(13),
            text_color=C_TEXT_SOFT,
        ).pack(anchor="w", padx=16, pady=(0, 4))
        ctk.CTkLabel(
            hdr,
            text=f"⚠️ Peligro: {fac['danger_level']}   |   🗺️ Mapas: {', '.join(fac['maps'])}",
            font=ui_font(12, "bold"),
            text_color=C_RED,
        ).pack(anchor="w", padx=16, pady=(0, 12))

        sections = [
            (
                t_ui("🎯 REGLAS DE AGGRO & COMPORTAMIENTO", "🎯 AGGRO RULES & AI BEHAVIOR"),
                fac["aggro_rules_en"] if is_en else fac["aggro_rules_es"],
                C_AMBER,
            ),
            (
                t_ui("📍 TRIGGERS Y ZONAS DE SPAWN", "📍 SPAWN TRIGGERS & LOCATIONS"),
                fac["spawn_triggers_en"] if is_en else fac["spawn_triggers_es"],
                THEME["accent_gold"],
            ),
            (
                t_ui("💎 BOTÍN DESTACADO (LOOT)", "💎 NOTABLE LOOT"),
                "\n".join(f"  ★ {x}" for x in fac["top_loot"]),
                C_GREEN_LIGHT,
            ),
            (
                t_ui("🧭 RUTA SEGURA DE FARMEO (PASO A PASO)", "🧭 SAFE FARMING GUIDE (STEP-BY-STEP)"),
                "\n\n".join(fac["farming_guide_steps_en"] if is_en else fac["farming_guide_steps_es"]),
                THEME["accent_orange"],
            ),
        ]
        for idx, (title, body, col) in enumerate(sections, start=1):
            card = ctk.CTkFrame(
                self.factions_detail,
                fg_color=C_BG_PANEL,
                corner_radius=10,
                border_width=1,
                border_color=C_BORDER,
            )
            card.grid(row=idx, column=0, sticky="ew", padx=16, pady=6)
            ctk.CTkLabel(
                card,
                text=title,
                font=ui_font(13, "bold"),
                text_color=col,
            ).pack(anchor="w", padx=14, pady=(10, 4))
            ctk.CTkLabel(
                card,
                text=body,
                font=ui_font(12),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=880,
            ).pack(anchor="w", padx=14, pady=(0, 12))
