"""
TarkovScope - Sub-vistas de Trueques Clave (Barters), Cultist Circle & Semáforo FiR
Mixin integrado en TabFleaAndItems.
"""
from typing import Any, Dict, List
import customtkinter as ctk

from core.barters_data import (
    BARTER_CATEGORIES,
    BARTER_TRADERS,
    CULTIST_CIRCLE_INFO,
    CULTIST_REPEATABLE_SACRIFICES,
    CULTIST_UNIQUE_SACRIFICES,
    check_item_keep_status,
    filter_barters,
)
from core.config import THEME
from core.datastore import get_datastore
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BORDER,
    C_BORDER_SOFT,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED_DARK,
    C_TEXT,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


class FleaBartersMixin:
    """Mixin de Trueques, Cultist Circle y Semáforo FiR para TabFleaAndItems."""

    def _init_barters_state(self):
        self._barter_trader: str = "Todos"
        self._barter_category: str = "Todas"
        self._barter_max_ll: int = 4
        self._barter_only_essential = ctk.BooleanVar(value=True)
        self._barters_bar: ctk.CTkFrame | None = None

    def _build_barters_controls_bar(self):
        if self._barters_bar is not None:
            return
        self._barters_bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT,
        )
        self._barters_bar.grid_columnconfigure(6, weight=1)

        ctk.CTkLabel(
            self._barters_bar,
            text="Trader:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=(12, 4), pady=7, sticky="w")

        self._barter_trader_menu = ctk.CTkOptionMenu(
            self._barters_bar,
            values=BARTER_TRADERS,
            width=135,
            height=28,
            fg_color=C_BG_PANEL,
            button_color=C_BORDER,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._on_barter_trader_change,
        )
        self._barter_trader_menu.set("Todos")
        self._barter_trader_menu.grid(row=0, column=1, padx=4, pady=7, sticky="w")

        ctk.CTkLabel(
            self._barters_bar,
            text="Tipo:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=2, padx=(10, 4), pady=7, sticky="w")

        self._barter_cat_menu = ctk.CTkOptionMenu(
            self._barters_bar,
            values=BARTER_CATEGORIES,
            width=148,
            height=28,
            fg_color=C_BG_PANEL,
            button_color=C_BORDER,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._on_barter_cat_change,
        )
        self._barter_cat_menu.set("Todas")
        self._barter_cat_menu.grid(row=0, column=3, padx=4, pady=7, sticky="w")

        ctk.CTkLabel(
            self._barters_bar,
            text="Máx LL:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=4, padx=(10, 4), pady=7, sticky="w")

        self._barter_ll_menu = ctk.CTkOptionMenu(
            self._barters_bar,
            values=["LL1", "LL2", "LL3", "LL4 (Todos)"],
            width=118,
            height=28,
            fg_color=C_BG_PANEL,
            button_color=C_BORDER,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=self._on_barter_ll_change,
        )
        self._barter_ll_menu.set("LL4 (Todos)")
        self._barter_ll_menu.grid(row=0, column=5, padx=4, pady=7, sticky="w")

        ctk.CTkCheckBox(
            self._barters_bar,
            text="Solo Trueques Esenciales / Alto Valor",
            variable=self._barter_only_essential,
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_gold"],
            command=lambda: self._run_search(self.search_entry.get()),
        ).grid(row=0, column=6, padx=12, pady=7, sticky="w")

        self._barter_count_lbl = ctk.CTkLabel(
            self._barters_bar,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        )
        self._barter_count_lbl.grid(row=0, column=7, padx=14, pady=7, sticky="e")

    def _on_barter_trader_change(self, val: str):
        self._barter_trader = val
        self._run_search(self.search_entry.get())

    def _on_barter_cat_change(self, val: str):
        self._barter_category = val
        self._run_search(self.search_entry.get())

    def _on_barter_ll_change(self, val: str):
        self._barter_max_ll = int(val[2]) if len(val) >= 3 and val[2].isdigit() else 4
        self._run_search(self.search_entry.get())

    def _render_barters_view(self, query: str, token: int):
        if self._barters_bar is not None:
            self._barters_bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")

        items = filter_barters(
            trader=self._barter_trader,
            category=self._barter_category,
            only_essential=bool(self._barter_only_essential.get()),
            max_ll=self._barter_max_ll,
            query=query,
        )
        if hasattr(self, "_barter_count_lbl"):
            self._barter_count_lbl.configure(text=f"{len(items)} trueques")

        if not items:
            ctk.CTkLabel(
                self.results_scroll,
                text="No hay trueques para esos filtros (probá destildar 'Solo Trueques Esenciales').",
                font=ui_font(13, "bold"),
                text_color=C_TEXT_MUTED,
            ).grid(row=0, column=0, pady=40)
            return

        shown = items[:120]

        def render_batch(start: int = 0, batch_size: int = 16):
            if not self.winfo_exists() or token != self._render_token:
                return
            end = min(start + batch_size, len(shown))
            for idx in range(start, end):
                self._create_barter_row(idx, shown[idx])
            if end < len(shown):
                self.after(4, lambda: render_batch(end, batch_size))

        render_batch(0)

    def _create_barter_row(self, row_idx: int, b: Dict[str, Any]):
        card = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_row"] if row_idx % 2 == 0 else THEME["bg_row_alt"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["accent_gold"] if b.get("is_essential") else C_BORDER_SOFT,
        )
        card.grid(row=row_idx, column=0, padx=6, pady=3, sticky="ew")
        card.grid_columnconfigure(2, weight=1)

        icon_lbl = ctk.CTkLabel(card, text="", width=46, height=40)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=6)
        img = get_gear_ctk_icon(
            b.get("cache_key", ""),
            b.get("icon_url", ""),
            max_size=(42, 38),
            on_ready=lambda im: self.after(0, lambda: icon_lbl.winfo_exists() and icon_lbl.configure(image=im)),
        )
        if img is not None:
            icon_lbl.configure(image=img)

        t_badge = ctk.CTkFrame(card, fg_color="#161C28", corner_radius=6, width=130)
        t_badge.grid(row=0, column=1, rowspan=2, padx=(0, 10), pady=6, sticky="ns")
        t_badge.grid_propagate(False)
        ctk.CTkLabel(
            t_badge,
            text=f"{b['trader']} LL{b['ll']}",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        ).pack(anchor="center", pady=(8, 1))
        ctk.CTkLabel(
            t_badge,
            text="★ CLAVE" if b.get("is_essential") else b.get("category", ""),
            font=ui_font(10, "bold"),
            text_color=C_GREEN_LIGHT if b.get("is_essential") else C_TEXT_DIM,
        ).pack(anchor="center", pady=(0, 6))

        ctk.CTkLabel(
            card,
            text=b["reward"],
            font=ui_font(14, "bold"),
            text_color=C_WHITE,
            anchor="w",
        ).grid(row=0, column=2, padx=(0, 10), pady=(7, 1), sticky="ew")

        sub = f"Entrega: {b['inputs_text']}"
        if b.get("quest_unlock"):
            sub += f"   •   🔓 {b['quest_unlock']}"
        ctk.CTkLabel(
            card,
            text=sub,
            font=ui_font(12),
            text_color=C_TEXT_SOFT,
            anchor="w",
            wraplength=680,
            justify="left",
        ).grid(row=1, column=2, padx=(0, 10), pady=(0, 7), sticky="ew")

    def _render_cultist_circle_view(self, query: str):
        q = (query or "").strip().lower()

        # Tarjeta de Reglas & Umbrales Oficiales
        info_card = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color="#9333EA",
        )
        info_card.grid(row=0, column=0, padx=6, pady=(4, 10), sticky="ew")
        info_card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info_card,
            text="🌀 CULTIST CIRCLE — UMBRALES DE VALOR BASE Y MECÁNICA OFICIAL",
            font=ui_font(15, "bold"),
            text_color="#C084FC",
        ).grid(row=0, column=0, padx=14, pady=(10, 6), sticky="w")

        for idx, th in enumerate(CULTIST_CIRCLE_INFO["thresholds"], start=1):
            row_f = ctk.CTkFrame(info_card, fg_color=THEME["bg_row"], corner_radius=6)
            row_f.grid(row=idx, column=0, padx=12, pady=3, sticky="ew")
            row_f.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(
                row_f,
                text=f"{th['value']}  ({th['duration']})",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"],
                width=310,
                anchor="w",
            ).grid(row=0, column=0, padx=10, pady=6, sticky="w")
            ctk.CTkLabel(
                row_f,
                text=th["effect"],
                font=ui_font(12),
                text_color=C_TEXT,
                anchor="w",
                wraplength=540,
                justify="left",
            ).grid(row=0, column=1, padx=(4, 10), pady=6, sticky="ew")

        tips_txt = "\n".join(f"• {t}" for t in CULTIST_CIRCLE_INFO["tips"])
        ctk.CTkLabel(
            info_card,
            text=tips_txt,
            font=ui_font(12),
            text_color=C_TEXT_SOFT,
            anchor="w",
            wraplength=880,
            justify="left",
        ).grid(row=4, column=0, padx=14, pady=(6, 12), sticky="ew")

        all_sac = CULTIST_REPEATABLE_SACRIFICES + CULTIST_UNIQUE_SACRIFICES
        filtered = [
            s for s in all_sac
            if not q or q in s["input"].lower() or q in s["outcome"].lower()
        ]

        ctk.CTkLabel(
            self.results_scroll,
            text=f"🕯️ RECETAS FIJAS DE SACRIFICIO ({len(filtered)} resultados — Repetibles primero, luego Únicas)",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=1, column=0, padx=10, pady=(4, 6), sticky="w")

        for idx, s in enumerate(filtered, start=2):
            card = ctk.CTkFrame(
                self.results_scroll,
                fg_color=THEME["bg_row"] if idx % 2 == 0 else THEME["bg_row_alt"],
                corner_radius=6,
                border_width=1,
                border_color="#7E22CE" if s.get("repeatable") else C_BORDER_SOFT,
            )
            card.grid(row=idx, column=0, padx=6, pady=2, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            tag = "♻️ REPETIBLE" if s.get("repeatable") else "🔒 ÚNICO"
            ctk.CTkLabel(
                card,
                text=f"{tag}\n{s['duration']}",
                font=ui_font(11, "bold"),
                text_color="#C084FC" if s.get("repeatable") else THEME["accent_gold"],
                width=120,
            ).grid(row=0, column=0, padx=10, pady=6)

            ctk.CTkLabel(
                card,
                text=f"Sacrificar:  {s['input']}\nResultado:  {s['outcome']}",
                font=ui_font(12),
                text_color=C_WHITE,
                anchor="w",
                wraplength=700,
                justify="left",
            ).grid(row=0, column=1, padx=6, pady=6, sticky="ew")

    def _render_keep_or_sell_view(self, query: str):
        ds = get_datastore()
        fir_items = ds.search_fir_items("")
        hideout_mods = ds.get_hideout_modules(progression_mode="ALL")
        kappa_names = [it["name"] for it in KAPPA_COLLECTOR_ITEMS]

        res = check_item_keep_status(query, fir_items, hideout_mods, kappa_names)

        banner = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=2,
            border_color=THEME["accent_gold"],
        )
        banner.grid(row=0, column=0, padx=6, pady=(4, 10), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner,
            text="🚦 SEMÁFORO DE BOTÍN: ¿VENDER O GUARDAR?",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(10, 4), sticky="w")

        ctk.CTkLabel(
            banner,
            text=res["verdict"],
            font=ui_font(16, "bold"),
            text_color=C_WHITE,
        ).grid(row=1, column=0, padx=14, pady=(2, 10), sticky="w")

        if res["level"] == "INFO":
            ctk.CTkLabel(
                self.results_scroll,
                text="Escribí arriba el nombre de cualquier objeto que encontraste (ej: LEDX, Bolts, Flash drive, GPU, Salewa, Hose, Military battery)\npara ver al instante si te lo pide alguna Quest FiR, estación del Hideout, Collector (Kappa) o Trueque de Trader.",
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
                justify="left",
            ).grid(row=1, column=0, padx=16, pady=18, sticky="w")
            return

        sections = [
            ("📋 REQUERIDO PARA QUESTS FiR", res["quests"], lambda x: f"• {x['qty']}x {x['item']}  —  Misión: {x['quest']} ({x['trader']})"),
            ("🏆 COLECCIÓN KAPPA (COLLECTOR)", res["kappa"], lambda x: f"• Ítem Streamer FiR requerido para Kappa: {x}"),
            ("🏭 REQUERIDO PARA HIDEOUT", res["hideout"], lambda x: f"• {x['station']}: {x['requirement']}" + ("  [Ya construida]" if x["completed"] else "  [PENDIENTE]")),
            ("🔄 USADO EN TRUEQUES DE TRADERS", res["barters"], lambda x: f"• {x['trader']} → {x['reward']}  (Pide: {x['inputs_text']})"),
        ]
        row_pos = 1
        for title, lst, fmt in sections:
            box = ctk.CTkFrame(
                self.results_scroll,
                fg_color=THEME["bg_card"],
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER_SOFT,
            )
            box.grid(row=row_pos, column=0, padx=6, pady=4, sticky="ew")
            box.grid_columnconfigure(0, weight=1)
            row_pos += 1

            ctk.CTkLabel(
                box,
                text=f"{title} ({len(lst)})",
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).grid(row=0, column=0, padx=12, pady=(8, 4), sticky="w")

            body_txt = "\n".join(fmt(it) for it in lst) if lst else "Sin coincidencias en esta categoría."
            ctk.CTkLabel(
                box,
                text=body_txt,
                font=ui_font(12),
                text_color=C_WHITE if lst else C_TEXT_DIM,
                anchor="w",
                wraplength=860,
                justify="left",
            ).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
