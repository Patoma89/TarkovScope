"""
TarkovScope - Mixin UI Lazy para TabWeapons:
  Guía Táctica de Fallas de Arma (Malfunctions), Umbral 93% de Durabilidad y Repair Kits.
"""
import customtkinter as ctk

from core.config import THEME
from core.i18n import get_active_lang, t_ui
from core.weapon_malfunctions_data import (
    DURABILITY_AND_REPAIR_GUIDE,
    WEAPON_MALFUNCTIONS_CATALOG,
)
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_PANEL,
    C_BG_ROW,
    C_BLUE,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


class WeaponMalfunctionsMixin:
    """Mixin lazy para la sub-vista de Fallas de Arma, Sobrecalentamiento y Repair Kits."""

    def _render_malfunctions_view(self) -> ctk.CTkFrame:
        root = ctk.CTkFrame(self.body_frame, fg_color="transparent")
        root.grid(row=0, column=0, sticky="nsew")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)

        scroll = ctk.CTkScrollableFrame(
            root,
            fg_color=C_BG_DARKEST,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        is_en = get_active_lang() == "en"
        g = DURABILITY_AND_REPAIR_GUIDE

        # Banner de la Regla de Oro del 93%
        hero = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=THEME["accent_orange"],
        )
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(10, 8))
        ctk.CTkLabel(
            hero,
            text=f"⚠️ {g['threshold_93_title_en'] if is_en else g['threshold_93_title_es']}",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_orange"],
        ).pack(anchor="w", padx=14, pady=(10, 4))
        ctk.CTkLabel(
            hero,
            text=g["threshold_93_desc_en"] if is_en else g["threshold_93_desc_es"],
            font=ui_font(12),
            text_color=C_TEXT_SOFT,
            wraplength=980,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # 5 Fallas de Arma (2 columnas)
        for idx, m in enumerate(WEAPON_MALFUNCTIONS_CATALOG):
            r = 1 + (idx // 2)
            c = idx % 2
            card = ctk.CTkFrame(
                scroll,
                fg_color=C_BG_PANEL,
                corner_radius=10,
                border_width=1,
                border_color=C_BORDER,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=10, pady=6)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=14, pady=(10, 4))
            ctk.CTkLabel(
                top,
                text=m["name_en"] if is_en else m["name_es"],
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).pack(side="left")
            ctk.CTkLabel(
                top,
                text=f" {m['min_durability_threshold']} ",
                font=ui_font(10, "bold"),
                fg_color=C_RED,
                text_color=C_WHITE,
                corner_radius=4,
            ).pack(side="right")

            cause = m["causes_en"] if is_en else m["causes_es"]
            steps = "\n".join(m["fix_steps_en"] if is_en else m["fix_steps_es"])
            tip = m["pro_tip_en"] if is_en else m["pro_tip_es"]
            ctk.CTkLabel(
                card,
                text=f"🔍 {cause}\n\n🛠️ Solución:\n{steps}\n\n💡 {tip}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=470,
            ).pack(anchor="w", padx=14, pady=(2, 10))

        # Fases de Sobrecalentamiento + Repair Kits
        base_row = 1 + ((len(WEAPON_MALFUNCTIONS_CATALOG) + 1) // 2)

        heat_card = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_AMBER,
        )
        heat_card.grid(row=base_row, column=0, sticky="nsew", padx=10, pady=(6, 12))
        ctk.CTkLabel(
            heat_card,
            text=t_ui("🔥 FASES DE SOBRECALENTAMIENTO (OVERHEAT)", "🔥 OVERHEAT STAGES"),
            font=ui_font(13, "bold"),
            text_color=C_AMBER,
        ).pack(anchor="w", padx=14, pady=(10, 6))
        for st in g["overheat_stages"]:
            box = ctk.CTkFrame(heat_card, fg_color=C_BG_ROW, corner_radius=6)
            box.pack(fill="x", padx=14, pady=3)
            eff = st["effects_en"] if is_en else st["effects_es"]
            ctk.CTkLabel(
                box,
                text=f"{st['stage']} ({st['heat']})\n  • {eff}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=450,
            ).pack(anchor="w", padx=10, pady=5)
        ctk.CTkFrame(heat_card, height=8, fg_color="transparent").pack()

        rep_card = ctk.CTkFrame(
            scroll,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_EMERALD,
        )
        rep_card.grid(row=base_row, column=1, sticky="nsew", padx=10, pady=(6, 12))
        ctk.CTkLabel(
            rep_card,
            text=t_ui("🧰 REPAIR KITS & ENHANCEMENTS", "🧰 REPAIR KITS & ENHANCEMENTS"),
            font=ui_font(13, "bold"),
            text_color=C_GREEN_LIGHT,
        ).pack(anchor="w", padx=14, pady=(10, 6))
        for rk in g["repair_kits_guide"]:
            box = ctk.CTkFrame(rep_card, fg_color=C_BG_ROW, corner_radius=6)
            box.pack(fill="x", padx=14, pady=3)
            title = rk["title_en"] if is_en else rk["title_es"]
            det = rk["detail_en"] if is_en else rk["detail_es"]
            ctk.CTkLabel(
                box,
                text=f"★ {title}\n{det}",
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                justify="left",
                anchor="w",
                wraplength=450,
            ).pack(anchor="w", padx=10, pady=5)
        ctk.CTkFrame(rep_card, height=8, fg_color="transparent").pack()

        return root
