"""
TarkovScope - Vista de Módulos del Hideout, Crafteos y Contenedor KAPPA (Mixin de TabFleaAndItems).
Extraído de tab_flea.py para respetar el principio de responsabilidad única (SOLID).
"""
import tkinter as tk
import customtkinter as ctk
from typing import List, Dict, Any, Optional
from core.config import THEME
from core.datastore import get_datastore
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA
from ui.theme import (
    ui_font,
    C_WHITE, C_TEXT, C_TEXT_SOFT, C_TEXT_MUTED, C_TEXT_DIM,
    C_BLUE, C_BORDER, C_BORDER_SOFT, C_BG_DARKEST, C_BG_DEEP,
    C_GREEN_LIGHT, C_GREEN, C_EMERALD, C_RED, C_AMBER, C_SLATE_700
)


class FleaHideoutMixin:
    """Mixin que contiene la lógica de renderizado de módulos del Refugio (Hideout), recetas de crafteo y objetos de Kappa."""

    def _render_hideout_modules(self, modules: List[Dict[str, Any]], token: int):
        if not modules:
            ctk.CTkLabel(
                self.results_scroll,
                text="No hay zonas del Hideout visibles con estos filtros.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=0, column=0, pady=40)
            return

        # Cabecera de tabla de Hideout
        hdr = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_panel_alt"],
            corner_radius=4,
            border_width=1,
            border_color=C_BORDER
        )
        hdr.grid(row=0, column=0, padx=2, pady=(0, 2), sticky="ew")
        hdr.grid_columnconfigure(0, minsize=54, weight=0)
        hdr.grid_columnconfigure(1, minsize=265, weight=0)
        hdr.grid_columnconfigure(2, minsize=430, weight=3)
        hdr.grid_columnconfigure(3, minsize=310, weight=2)

        for col_i, title in [
            (0, "✓"),
            (1, "Zona & Nivel Correlativo"),
            (2, "Requisitos de Construcción (Ítems & Módulos)"),
            (3, "Funciones & Bonificaciones"),
        ]:
            ctk.CTkLabel(
                hdr,
                text=title,
                font=ui_font(13, "bold"),
                text_color=C_WHITE
            ).grid(row=0, column=col_i, padx=8, pady=7, sticky="w" if col_i > 0 else "")

        def render_batch(idx: int):
            if not self.winfo_exists() or token != self._render_token:
                return
            limit = min(idx + 8, len(modules))
            for i in range(idx, limit):
                self._create_hideout_row(i + 1, modules[i])
            if limit < len(modules):
                self.after(4, lambda: render_batch(limit))

        render_batch(0)

    def _create_hideout_row(self, grid_row: int, mod: Dict[str, Any]):
        is_done = bool(mod.get("is_completed"))
        row_bg = THEME["bg_row_done"] if is_done else (C_BG_DARKEST if grid_row % 2 == 0 else THEME["bg_panel_alt"])
        border_col = C_GREEN if is_done else C_BORDER_SOFT

        row_frame = ctk.CTkFrame(
            self.results_scroll,
            fg_color=row_bg,
            corner_radius=0,
            border_width=1,
            border_color=border_col
        )
        row_frame.grid(row=grid_row, column=0, padx=2, pady=0, sticky="ew")
        row_frame.grid_columnconfigure(0, minsize=54, weight=0)
        row_frame.grid_columnconfigure(1, minsize=265, weight=0)
        row_frame.grid_columnconfigure(2, minsize=430, weight=3)
        row_frame.grid_columnconfigure(3, minsize=310, weight=2)

        # Col 0: Checkbox Construido
        chk_var = ctk.BooleanVar(value=is_done)
        chk = ctk.CTkCheckBox(
            row_frame,
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
            command=lambda m=mod: self._on_toggle_hideout(m)
        )
        chk.grid(row=0, column=0, padx=(16, 6), pady=10)

        # Col 1: Nombre de Estación + Nivel + Qué Desbloquea
        st_cell = ctk.CTkFrame(row_frame, fg_color="transparent")
        st_cell.grid(row=0, column=1, padx=8, pady=10, sticky="nsew")

        ctk.CTkLabel(
            st_cell,
            text=f"{mod['station']} — Nivel {mod['level']} / {mod['max_level']}",
            font=ui_font(14, "bold"),
            text_color=C_GREEN_LIGHT if is_done else THEME["accent_gold"],
            anchor="w",
            justify="left"
        ).pack(fill="x", anchor="w")

        ctk.CTkLabel(
            st_cell,
            text=f"⏱ Tiempo: {mod.get('construction_time', 'Instant')}",
            font=ui_font(11, "bold"),
            text_color=C_TEXT_MUTED,
            anchor="w"
        ).pack(fill="x", anchor="w", pady=(2, 2))

        prereqs = mod.get("prereq_modules", [])
        if prereqs:
            req_txt = ", ".join(f"{p['station']} Nv.{p['level']}" for p in prereqs)
            ctk.CTkLabel(
                st_cell,
                text=f"🔗 Requiere: {req_txt}",
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                anchor="w",
                justify="left",
                wraplength=245
            ).pack(fill="x", anchor="w")
        else:
            ctk.CTkLabel(
                st_cell,
                text="🟢 Estación Inicial (Disponible de base)",
                font=ui_font(11, "bold"),
                text_color=C_GREEN_LIGHT,
                anchor="w"
            ).pack(fill="x", anchor="w")

        unlocks = mod.get("unlocks_modules", [])
        if unlocks:
            u_txt = ", ".join(unlocks[:3]) + (f" (+{len(unlocks)-3})" if len(unlocks) > 3 else "")
            ctk.CTkLabel(
                st_cell,
                text=f"↳ Desbloquea: {u_txt}",
                font=ui_font(11, "bold"),
                text_color="#60A5FA",
                anchor="w",
                justify="left",
                wraplength=245
            ).pack(fill="x", anchor="w", pady=(2, 0))

        # Col 2: Requisitos de Construcción
        req_lines = mod.get("requirements_lines") or ["• Sin requisitos adicionales"]
        ctk.CTkLabel(
            row_frame,
            text="\n".join(req_lines[:10]),
            font=ui_font(13),
            text_color=C_TEXT,
            anchor="w",
            justify="left",
            wraplength=420
        ).grid(row=0, column=2, padx=10, pady=10, sticky="nw")

        # Col 3: Funciones y Bonificaciones
        fn_lines = mod.get("function_lines") or ["• Mejora estructural del Hideout"]
        ctk.CTkLabel(
            row_frame,
            text="\n".join(fn_lines[:8]),
            font=ui_font(13),
            text_color=C_TEXT_SOFT,
            anchor="w",
            justify="left",
            wraplength=300
        ).grid(row=0, column=3, padx=10, pady=10, sticky="nw")

    def _on_toggle_hideout(self, mod: Dict[str, Any]):
        new_state = get_datastore().toggle_hideout_module(mod["key"])
        unlocks = mod.get("unlocks_modules", [])
        label = f"{mod['station']} Nv. {mod['level']}"
        if new_state and unlocks:
            self.hideout_notice_lbl.configure(
                text=f"✓ Construiste '{label}' → Desbloqueó: {', '.join(unlocks[:3])}",
                text_color=THEME["accent_green"]
            )
        elif new_state:
            self.hideout_notice_lbl.configure(
                text=f"✓ Construiste '{label}'",
                text_color=THEME["accent_green"]
            )
        else:
            self.hideout_notice_lbl.configure(
                text=f"↩ Desmarcaste '{label}'",
                text_color=THEME["accent_gold"]
            )
        self._run_search(self.search_entry.get())

    def _render_kappa_items(self, query: str, token: int = 0):
        ds = get_datastore()
        q = query.strip().lower()
        all_kappa = KAPPA_COLLECTOR_ITEMS
        tot_k = len(all_kappa)
        done_k = sum(1 for it in all_kappa if ds.get_stash_count(f"kappa:{it['name']}") >= 1)

        prog_hdr = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_panel_alt"],
            corner_radius=6,
            border_width=1,
            border_color=THEME["accent_gold"]
        )
        prog_hdr.grid(row=0, column=0, padx=8, pady=(4, 8), sticky="ew")
        prog_hdr.grid_columnconfigure(0, weight=1)

        pct_k = int((done_k / tot_k) * 100) if tot_k > 0 else 0
        prog_lbl = ctk.CTkLabel(
            prog_hdr,
            text=f"🏆 PROGRESO MISIÓN 'COLLECTOR' (SECURE CONTAINER KAPPA):  {done_k} / {tot_k} Objetos Streamer FiR en tu Alijo ({pct_k}%)",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"]
        )
        prog_lbl.grid(row=0, column=0, padx=14, pady=8, sticky="w")

        items = [
            it for it in all_kappa
            if not q or q in it["name"].lower() or q in it["boss_or_spot"].lower()
        ]
        if self.filter_only_missing.get():
            items = [it for it in items if ds.get_stash_count(f"kappa:{it['name']}") < 1]

        if not items:
            ctk.CTkLabel(
                self.results_scroll,
                text="No se encontraron ítems de Collector (Kappa) con ese filtro.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=1, column=0, pady=40)
            return

        def _refresh_prog_header():
            d_cnt = sum(1 for k_it in all_kappa if ds.get_stash_count(f"kappa:{k_it['name']}") >= 1)
            p_val = int((d_cnt / tot_k) * 100) if tot_k > 0 else 0
            if prog_lbl.winfo_exists():
                prog_lbl.configure(
                    text=f"🏆 PROGRESO MISIÓN 'COLLECTOR' (SECURE CONTAINER KAPPA):  {d_cnt} / {tot_k} Objetos Streamer FiR en tu Alijo ({p_val}%)"
                )

        def draw_batch(start: int = 0, batch_size: int = 16):
            if not self.winfo_exists() or (token and token != self._render_token):
                return
            end = min(start + batch_size, len(items))
            for i in range(start, end):
                it = items[i]
                k_key = f"kappa:{it['name']}"
                has_item = ds.get_stash_count(k_key) >= 1
                row_bg = "#0D1612" if has_item else C_BG_DEEP

                card = tk.Frame(
                    self.results_scroll,
                    bg=row_bg,
                    highlightbackground=C_EMERALD if has_item else C_BORDER_SOFT,
                    highlightthickness=1,
                    bd=0,
                )
                card.grid(row=i + 1, column=0, padx=8, pady=3, sticky="ew")
                card.grid_columnconfigure(1, weight=1)

                n_lbl = tk.Label(
                    card,
                    text=it["name"],
                    font=ui_font(13, "bold"),
                    bg=row_bg,
                    fg=C_GREEN_LIGHT if has_item else THEME["accent_gold"],
                    anchor="w",
                    bd=0,
                )
                n_lbl.grid(row=0, column=0, padx=14, pady=8, sticky="w")

                s_lbl = tk.Label(
                    card,
                    text=f"Dónde conseguirlo: {it['boss_or_spot']}",
                    font=ui_font(12),
                    bg=row_bg,
                    fg=C_TEXT,
                    anchor="w",
                    bd=0,
                )
                s_lbl.grid(row=0, column=1, padx=10, pady=8, sticky="w")

                btn_toggle = ctk.CTkButton(
                    card,
                    text="✓ En Alijo (1/1 FiR)" if has_item else "Marcar FiR (0/1)",
                    width=150,
                    height=28,
                    corner_radius=5,
                    fg_color=C_EMERALD if has_item else "#1E2534",
                    hover_color="#059669" if has_item else C_SLATE_700,
                    text_color=C_BG_DARKEST if has_item else C_TEXT,
                    font=ui_font(12, "bold"),
                )

                def make_kappa_toggler(item_key=k_key, c_card=card, c_nlbl=n_lbl, c_slbl=s_lbl, c_btn=btn_toggle):
                    def _toggle():
                        cur = ds.get_stash_count(item_key)
                        new_done = cur < 1
                        ds.set_stash_count(item_key, 1 if new_done else 0)
                        _refresh_prog_header()
                        if self.filter_only_missing.get() and new_done:
                            if c_card.winfo_exists():
                                c_card.destroy()
                            return
                        new_bg = "#0D1612" if new_done else C_BG_DEEP
                        c_card.configure(bg=new_bg, highlightbackground=C_EMERALD if new_done else C_BORDER_SOFT)
                        c_nlbl.configure(bg=new_bg, fg=C_GREEN_LIGHT if new_done else THEME["accent_gold"])
                        c_slbl.configure(bg=new_bg)
                        c_btn.configure(
                            text="✓ En Alijo (1/1 FiR)" if new_done else "Marcar FiR (0/1)",
                            fg_color=C_EMERALD if new_done else "#1E2534",
                            hover_color="#059669" if new_done else C_SLATE_700,
                            text_color=C_BG_DARKEST if new_done else C_TEXT,
                        )
                    return _toggle

                btn_toggle.configure(command=make_kappa_toggler())
                btn_toggle.grid(row=0, column=2, padx=14, pady=7, sticky="e")

            if end < len(items):
                self.after(4, lambda: draw_batch(end, batch_size))

        draw_batch(0)

    def _render_hideout_crafts(self, query: str, token: int = 0):
        q = query.strip().lower()
        crafts = [
            c for c in HIDEOUT_CRAFTS_DATA
            if not q
            or q in c["station"].lower()
            or q in c["output"].lower()
            or q in c["inputs"].lower()
            or q in c["usage"].lower()
            or q in c["category"].lower()
        ]

        banner = ctk.CTkFrame(
            self.results_scroll,
            fg_color=THEME["bg_panel_alt"],
            corner_radius=6,
            border_width=1,
            border_color=THEME["accent_gold"]
        )
        banner.grid(row=0, column=0, padx=8, pady=(4, 8), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner,
            text="⚗️ RECETAS DE CRAFTEO CLAVE (FOUND IN RAID PARA QUESTS, MUNICIÓN META & CÍRCULO CULTISTA)",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"]
        ).grid(row=0, column=0, padx=14, pady=(8, 2), sticky="w")

        ctk.CTkLabel(
            banner,
            text="Todo ítem fabricado en el Hideout o recibido del Círculo Cultista cuenta con estado 'Found in Raid' [✓] válido para entregar en misiones.",
            font=ui_font(12),
            text_color=C_TEXT_MUTED
        ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

        if not crafts:
            ctk.CTkLabel(
                self.results_scroll,
                text="No se encontraron recetas de crafteo para esa búsqueda.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_MUTED
            ).grid(row=1, column=0, pady=40)
            return

        cat_colors = {
            "QUEST FiR": (C_EMERALD, C_BG_DARKEST),
            "MUNICIÓN META": (C_RED, C_WHITE),
            "RENTABLE / META": ("#3B82F6", C_WHITE),
            "CÍRCULO CULTISTA": ("#A855F7", C_WHITE),
            "MATERIAL / QUEST": (C_AMBER, C_BG_DARKEST),
        }

        def draw_craft_batch(start: int = 0, batch_size: int = 14):
            if not self.winfo_exists() or (token and token != self._render_token):
                return
            end = min(start + batch_size, len(crafts))
            for i in range(start, end):
                idx = i + 1
                c = crafts[i]
                row_bg = C_BG_DEEP if idx % 2 == 1 else "#11151E"
                card = tk.Frame(
                    self.results_scroll,
                    bg=row_bg,
                    highlightbackground=C_BORDER_SOFT,
                    highlightthickness=1,
                    bd=0,
                )
                card.grid(row=idx, column=0, padx=8, pady=4, sticky="ew")
                card.grid_columnconfigure(1, weight=1)

                left_box = tk.Frame(card, bg="#161C28", width=210, bd=0)
                left_box.grid(row=0, column=0, padx=10, pady=8, sticky="nsew")
                left_box.grid_propagate(False)

                tk.Label(
                    left_box,
                    text=f"🏭 {c['station']} Nv.{c['level']}",
                    font=ui_font(12, "bold"),
                    bg="#161C28",
                    fg=THEME["accent_gold"],
                    anchor="w",
                    bd=0,
                ).pack(anchor="w", padx=10, pady=(8, 2))

                tk.Label(
                    left_box,
                    text=f"⏱ Duración: {c['time']}",
                    font=ui_font(11, "bold"),
                    bg="#161C28",
                    fg=C_BLUE,
                    anchor="w",
                    bd=0,
                ).pack(anchor="w", padx=10, pady=(0, 6))

                mid_box = tk.Frame(card, bg=row_bg, bd=0)
                mid_box.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

                tk.Label(
                    mid_box,
                    text=f"➜ Produce: {c['output']}",
                    font=ui_font(13, "bold"),
                    bg=row_bg,
                    fg=C_GREEN_LIGHT,
                    anchor="w",
                    bd=0,
                ).pack(anchor="w")

                tk.Label(
                    mid_box,
                    text=f"🧩 Materiales requeridos: {c['inputs']}",
                    font=ui_font(11, "bold"),
                    bg=row_bg,
                    fg=C_TEXT,
                    anchor="w",
                    justify="left",
                    wraplength=640,
                    bd=0,
                ).pack(anchor="w", pady=(3, 2))

                tk.Label(
                    mid_box,
                    text=f"💡 Utilidad Táctica / Quest: {c['usage']}",
                    font=ui_font(11),
                    bg=row_bg,
                    fg=C_TEXT_DIM,
                    anchor="w",
                    justify="left",
                    wraplength=640,
                    bd=0,
                ).pack(anchor="w")

                bg_c, fg_c = cat_colors.get(c["category"], (C_SLATE_700, C_WHITE))
                tk.Label(
                    card,
                    text=f" {c['category']} ",
                    font=ui_font(10, "bold"),
                    bg=bg_c,
                    fg=fg_c,
                    padx=6,
                    pady=4,
                    bd=0,
                ).grid(row=0, column=2, padx=12, pady=10, sticky="ne")

            if end < len(crafts):
                self.after(4, lambda: draw_craft_batch(end, batch_size))

        draw_craft_batch(0)
