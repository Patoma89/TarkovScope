"""
TarkovScope - Pestaña de Hideout (Progresión Correlativa por Niveles) & Ítems Found in Raid (FiR)
Incluye:
1) Hideout con Progresión Correlativa real (68 niveles en 26 módulos de la Wiki):
   - Al inicio solo aparecen las estaciones Nivel 1 sin requisitos previos.
   - Al marcar una estación como construida [✓], se desbloquean automáticamente las zonas y niveles
     siguientes que dependen de ella (ej: Hall of Fame Nv. 3 jamás aparece sin antes desbloquear
     Defective Wall, Illumination 2/3, Workbench 2/3, Hall of Fame 1 y Hall of Fame 2).
2) Buscador de Ítems requeridos para Quests (Found in Raid).
3) Rastreador de objetos Streamer para la misión Collector (Contenedor Kappa).
"""
import tkinter as tk
import customtkinter as ctk
from typing import Optional, List, Dict, Any
from core.config import THEME
from core.datastore import get_datastore
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA
from ui.theme import ui_font
from ui.theme import C_AMBER, C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL, C_BG_ROW, C_BG_ROW_ALT, C_BLUE, C_BORDER, C_BORDER_ALT, C_BORDER_SOFT, C_EMERALD, C_GREEN, C_GREEN_LIGHT, C_RED, C_RED_DARK, C_SLATE_700, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE
from ui.tab_flea_hideout import FleaHideoutMixin
from ui.tab_flea_barters import FleaBartersMixin


class TabFleaAndItems(FleaBartersMixin, FleaHideoutMixin, ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.view_mode = "HIDEOUT"  # "HIDEOUT", "FIR", "KAPPA", "CRAFTS", "BARTERS", "CULTIST", "KEEP_SELL"
        self.hideout_progression = "CORRELATIVE"  # "CORRELATIVE" o "ALL"
        self.filter_only_missing = ctk.BooleanVar(value=False)
        self._debounce_job: Optional[str] = None
        self._render_token: int = 0
        self._fir_limit: int = 35
        self._barters_limit: int = 40
        self._init_barters_state()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_top_bar()
        self._build_hideout_controls_bar()
        self._build_barters_controls_bar()
        self._build_results_area()
        self._run_search("")

    def _build_top_bar(self):
        box = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        box.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        header_row = ctk.CTkFrame(box, fg_color="transparent")
        header_row.grid(row=0, column=0, padx=14, pady=(10, 6), sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_row,
            text="HIDEOUT, TRUEQUES (BARTERS), CULTIST CIRCLE & ÍTEMS FiR",
            font=ui_font(16, "bold"),
            text_color=C_TEXT
        ).grid(row=0, column=0, sticky="w")

        mode_bar = ctk.CTkFrame(box, fg_color="transparent")
        mode_bar.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="ew")

        self.btn_mode_hideout = ctk.CTkButton(
            mode_bar,
            text="Hideout & Estaciones",
            width=142,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=THEME["accent_gold"],
            fg_color=C_BG_ROW_ALT,
            hover_color=C_BORDER_ALT,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("HIDEOUT")
        )
        self.btn_mode_hideout.pack(side="left", padx=(0, 3))

        self.btn_mode_fir = ctk.CTkButton(
            mode_bar,
            text="Ítems FiR",
            width=88,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("FIR")
        )
        self.btn_mode_fir.pack(side="left", padx=3)

        self.btn_mode_kappa = ctk.CTkButton(
            mode_bar,
            text="Collector (Kappa)",
            width=126,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("KAPPA")
        )
        self.btn_mode_kappa.pack(side="left", padx=3)

        self.btn_mode_crafts = ctk.CTkButton(
            mode_bar,
            text="⚗️ Crafteos",
            width=96,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("CRAFTS")
        )
        self.btn_mode_crafts.pack(side="left", padx=3)

        self.btn_mode_barters = ctk.CTkButton(
            mode_bar,
            text="🔄 Trueques (Barters)",
            width=146,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("BARTERS")
        )
        self.btn_mode_barters.pack(side="left", padx=3)

        self.btn_mode_cultist = ctk.CTkButton(
            mode_bar,
            text="🌀 Cultist Circle",
            width=122,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("CULTIST")
        )
        self.btn_mode_cultist.pack(side="left", padx=3)

        self.btn_mode_keep_sell = ctk.CTkButton(
            mode_bar,
            text="🚦 ¿Vender o Guardar?",
            width=150,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color=C_BORDER_ALT,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._switch_mode("KEEP_SELL")
        )
        self.btn_mode_keep_sell.pack(side="left", padx=3)

        search_row = ctk.CTkFrame(box, fg_color="transparent")
        search_row.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="ew")
        search_row.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Buscar zona del Hideout, ítem FiR o material (ej: Workbench, Hall of Fame, LEDX, Salewa, GPU)...",
            height=34,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(13)
        )
        self.search_entry.grid(row=0, column=0, padx=(0, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_key_debounced)

        self.chk_only_missing = ctk.CTkCheckBox(
            search_row,
            text="Solo pendientes / incompletos",
            variable=self.filter_only_missing,
            font=ui_font(12, "bold"),
            text_color=C_TEXT_MUTED,
            fg_color=THEME["accent_green"],
            command=lambda: self._run_search(self.search_entry.get())
        )
        self.chk_only_missing.grid(row=0, column=1, padx=(6, 10))

        ctk.CTkButton(
            search_row,
            text="Limpiar",
            width=95,
            height=34,
            corner_radius=5,
            fg_color="#161B24",
            hover_color=C_RED_DARK,
            border_width=1,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=self._on_clear_action
        ).grid(row=0, column=2)

    def _build_hideout_controls_bar(self):
        self.hideout_bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.hideout_bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        self.hideout_bar.grid_columnconfigure(2, weight=1)

        self.btn_prog_corr = ctk.CTkButton(
            self.hideout_bar,
            text="Progresión Correlativa",
            height=30,
            width=165,
            corner_radius=5,
            border_width=1,
            border_color=THEME["accent_gold"],
            fg_color=C_BG_ROW_ALT,
            hover_color="#2A3244",
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=lambda: self._set_hideout_progression("CORRELATIVE")
        )
        self.btn_prog_corr.grid(row=0, column=0, padx=(12, 6), pady=(7, 3), sticky="w")

        self.btn_prog_all = ctk.CTkButton(
            self.hideout_bar,
            text="Todas las Zonas (68 Niveles)",
            height=30,
            width=185,
            corner_radius=5,
            border_width=1,
            border_color=C_BORDER,
            fg_color=C_BG_PANEL,
            hover_color="#2A3244",
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=lambda: self._set_hideout_progression("ALL")
        )
        self.btn_prog_all.grid(row=0, column=1, padx=4, pady=(7, 3), sticky="w")

        self.hide_built_var = ctk.BooleanVar(value=False)
        self.hide_built_chk = ctk.CTkCheckBox(
            self.hideout_bar,
            text="Ocultar construidas",
            variable=self.hide_built_var,
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_green"],
            command=lambda: self._run_search(self.search_entry.get())
        )
        self.hide_built_chk.grid(row=0, column=3, padx=8, pady=(7, 3), sticky="e")

        self.btn_reset_hideout = ctk.CTkButton(
            self.hideout_bar,
            text="Desmarcar Zonas",
            height=28,
            width=130,
            corner_radius=5,
            border_width=1,
            border_color=C_RED,
            fg_color="#1F1215",
            hover_color=C_RED_DARK,
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=self._on_clear_action
        )
        self.btn_reset_hideout.grid(row=0, column=4, padx=6, pady=(7, 3), sticky="e")

        self.hideout_stats_lbl = ctk.CTkLabel(
            self.hideout_bar,
            text="Construidas: 0 / 68 (0%)",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_green"]
        )
        self.hideout_stats_lbl.grid(row=0, column=5, padx=(6, 14), pady=(7, 3), sticky="e")

        self.hideout_notice_lbl = ctk.CTkLabel(
            self.hideout_bar,
            text="Marcá cada nivel construido para desbloquear correlativamente las siguientes zonas del Hideout",
            font=ui_font(11, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w",
        )
        self.hideout_notice_lbl.grid(row=1, column=0, columnspan=6, padx=14, pady=(0, 6), sticky="ew")

    def _build_results_area(self):
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG_DARKEST,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.results_scroll.grid(row=2, column=0, sticky="nsew")
        self.results_scroll.grid_columnconfigure(0, weight=1)

    def _set_hideout_progression(self, mode: str):
        self.hideout_progression = mode
        is_corr = (mode == "CORRELATIVE")
        self.btn_prog_corr.configure(
            fg_color=C_BG_ROW_ALT if is_corr else C_BG_PANEL,
            border_color=THEME["accent_gold"] if is_corr else C_BORDER,
            text_color=C_WHITE if is_corr else C_TEXT_MUTED
        )
        self.btn_prog_all.configure(
            fg_color=C_BG_ROW_ALT if not is_corr else C_BG_PANEL,
            border_color=THEME["accent_gold"] if not is_corr else C_BORDER,
            text_color=C_WHITE if not is_corr else C_TEXT_MUTED
        )
        self._run_search(self.search_entry.get())

    def _switch_mode(self, mode: str):
        self.view_mode = mode
        self._fir_limit = 35
        self._barters_limit = 40
        for m_key, btn in [
            ("HIDEOUT", self.btn_mode_hideout),
            ("FIR", self.btn_mode_fir),
            ("KAPPA", self.btn_mode_kappa),
            ("CRAFTS", self.btn_mode_crafts),
            ("BARTERS", self.btn_mode_barters),
            ("CULTIST", self.btn_mode_cultist),
            ("KEEP_SELL", self.btn_mode_keep_sell),
        ]:
            is_act = (m_key == mode)
            btn.configure(
                fg_color=C_BG_ROW_ALT if is_act else C_BG_PANEL,
                border_color=THEME["accent_gold"] if is_act else C_BORDER,
                text_color=C_WHITE if is_act else C_TEXT_MUTED
            )
        if mode == "HIDEOUT":
            if self._barters_bar is not None:
                self._barters_bar.grid_remove()
            self.hideout_bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        elif mode == "BARTERS":
            self.hideout_bar.grid_remove()
            if self._barters_bar is not None:
                self._barters_bar.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        else:
            self.hideout_bar.grid_remove()
            if self._barters_bar is not None:
                self._barters_bar.grid_remove()
        self._run_search(self.search_entry.get())

    def _quick_search(self, term: str):
        if term.startswith("BARTER:"):
            clean_term = term[len("BARTER:"):]
            self.search_entry.delete(0, "end")
            self.search_entry.insert(0, clean_term)
            if self.view_mode != "BARTERS":
                self._switch_mode("BARTERS")
            else:
                self._run_search(clean_term)
            return
        if term.startswith("CULTIST:"):
            self.search_entry.delete(0, "end")
            self._switch_mode("CULTIST")
            return
        self.search_entry.delete(0, "end")
        if term:
            self.search_entry.insert(0, term)
        self._run_search(term)

    def _on_clear_action(self):
        """Limpia el buscador y, si está en la vista Hideout, desmarca todas las zonas construidas."""
        self.search_entry.delete(0, "end")
        if self.view_mode == "HIDEOUT":
            get_datastore().reset_hideout_progress()
            self.hideout_notice_lbl.configure(
                text="✓ Se desmarcaron todas las zonas del Hideout (progreso reiniciado)",
                text_color=THEME["accent_gold"]
            )
        self._run_search("")

    def _on_key_debounced(self, event=None):
        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(180, lambda: self._run_search(self.search_entry.get()))

    def _run_search(self, query: str):
        self._debounce_job = None
        self._render_token += 1
        token = self._render_token

        for w in self.results_scroll.winfo_children():
            w.destroy()

        ds = get_datastore()

        if self.view_mode == "HIDEOUT":
            all_mods = ds.get_hideout_modules(progression_mode="ALL")
            tot_m = len(all_mods)
            done_m = sum(1 for m in all_mods if m.get("is_completed") == 1)
            pct_m = int((done_m / tot_m) * 100) if tot_m > 0 else 0
            self.hideout_stats_lbl.configure(text=f"Construidas: {done_m} / {tot_m} ({pct_m}%)")

            visible_mods = ds.get_hideout_modules(
                query=query,
                progression_mode=self.hideout_progression,
                hide_completed=self.hide_built_var.get()
            )
            self._render_hideout_modules(visible_mods, token)
            return

        if self.view_mode == "KAPPA":
            self._render_kappa_items(query, token)
            return

        if self.view_mode == "CRAFTS":
            self._render_hideout_crafts(query, token)
            return

        if self.view_mode == "BARTERS":
            self._render_barters_view(query, token)
            return

        if self.view_mode == "CULTIST":
            self._render_cultist_circle_view(query, token)
            return

        if self.view_mode == "KEEP_SELL":
            self._render_keep_or_sell_view(query)
            return

        all_results = ds.search_fir_items(query)
        only_missing = bool(self.filter_only_missing.get())
        filtered: List[tuple] = []
        for r in all_results:
            item_name = r["item_name"]
            req_count = int(r.get("count_required", 1))
            collected = ds.get_stash_count(item_name)
            is_done = (collected >= req_count)
            if only_missing and is_done:
                continue
            filtered.append((r, item_name, req_count, collected, is_done))

        if not filtered:
            ctk.CTkLabel(
                self.results_scroll,
                text="No se encontraron requerimientos de misión para ese ítem.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=0, column=0, pady=40)
            return

        shown = filtered[: self._fir_limit]
        remaining = len(filtered) - len(shown)

        def render_batch(idx: int):
            if not self.winfo_exists() or token != self._render_token:
                return
            limit = min(idx + 14, len(shown))
            for i in range(idx, limit):
                r, item_name, req_count, collected, is_done = shown[i]
                row_bg = "#0D1612" if is_done else C_BG_DEEP

                card = tk.Frame(
                    self.results_scroll,
                    bg=row_bg,
                    highlightbackground=C_EMERALD if is_done else C_BORDER_SOFT,
                    highlightthickness=1,
                    bd=0,
                )
                card.grid(row=i, column=0, padx=8, pady=3, sticky="ew")
                card.grid_columnconfigure(1, weight=1)

                name_lbl = tk.Label(
                    card,
                    text=r["item_name"],
                    font=ui_font(13, "bold"),
                    bg=row_bg,
                    fg=C_GREEN_LIGHT if is_done else THEME["accent_gold"],
                    anchor="w",
                    bd=0,
                )
                name_lbl.grid(row=0, column=0, padx=14, pady=8, sticky="w")

                q_lbl = tk.Label(
                    card,
                    text=f"Quest: {r['quest_title']}  •  Trader: {r['trader_name']}",
                    font=ui_font(12),
                    bg=row_bg,
                    fg=C_TEXT,
                    anchor="w",
                    bd=0,
                )
                q_lbl.grid(row=0, column=1, padx=10, pady=8, sticky="w")

                tracker_frame = tk.Frame(card, bg=row_bg, bd=0)
                tracker_frame.grid(row=0, column=2, padx=14, pady=5, sticky="e")

                lbl_stash = tk.Label(
                    tracker_frame,
                    text=f"✓ {collected}/{req_count}x" if is_done else f"Alijo: {collected}/{req_count}x",
                    font=ui_font(11, "bold"),
                    bg=C_EMERALD if is_done else "#1E2534",
                    fg=C_BG_DARKEST if is_done else C_TEXT_MUTED,
                    width=13,
                    pady=4,
                    bd=0,
                )

                def make_updater(name=item_name, req=req_count, lbl=lbl_stash, c_card=card,
                                 n_lbl=name_lbl, ql=q_lbl, tf=tracker_frame):
                    def update_counter(delta: int):
                        cur = ds.get_stash_count(name)
                        new_val = max(0, cur + delta)
                        ds.set_stash_count(name, new_val)
                        done = (new_val >= req)
                        new_bg = "#0D1612" if done else C_BG_DEEP
                        lbl.configure(
                            text=f"✓ {new_val}/{req}x" if done else f"Alijo: {new_val}/{req}x",
                            bg=C_EMERALD if done else "#1E2534",
                            fg=C_BG_DARKEST if done else C_TEXT_MUTED,
                        )
                        c_card.configure(bg=new_bg, highlightbackground=C_EMERALD if done else C_BORDER_SOFT)
                        n_lbl.configure(bg=new_bg, fg=C_GREEN_LIGHT if done else THEME["accent_gold"])
                        ql.configure(bg=new_bg)
                        tf.configure(bg=new_bg)
                    return update_counter

                fn_update = make_updater()

                ctk.CTkButton(
                    tracker_frame,
                    text="−",
                    width=28,
                    height=26,
                    fg_color=C_BG_ROW,
                    hover_color=C_RED_DARK,
                    font=ui_font(13, "bold"),
                    command=lambda fn=fn_update: fn(-1)
                ).pack(side="left", padx=2)

                lbl_stash.pack(side="left", padx=4)

                ctk.CTkButton(
                    tracker_frame,
                    text="+",
                    width=28,
                    height=26,
                    fg_color=C_BG_ROW,
                    hover_color="#16A34A",
                    font=ui_font(13, "bold"),
                    command=lambda fn=fn_update: fn(1)
                ).pack(side="left", padx=2)

            if limit < len(shown):
                self.after(4, lambda: render_batch(limit))
            elif remaining > 0:
                def _load_more_fir():
                    self._fir_limit += 40
                    self._run_search(self.search_entry.get())

                ctk.CTkButton(
                    self.results_scroll,
                    text=f"⬇ Cargar más ítems FiR ({remaining} restantes)",
                    height=34,
                    fg_color=C_BG_PANEL,
                    hover_color=THEME["accent_gold"],
                    border_width=1,
                    border_color=C_BORDER,
                    text_color=C_WHITE,
                    font=ui_font(12, "bold"),
                    command=_load_more_fir,
                ).grid(row=len(shown), column=0, padx=8, pady=8, sticky="ew")

        render_batch(0)


# Alias de compatibilidad
TabFlea = TabFleaAndItems
