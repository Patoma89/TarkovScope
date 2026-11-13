"""
TarkovScope - Pestaña Táctica: Contenedores, Mochilas & Rigs Tácticos
Permite explorar Pouches seguros (Kappa/Gamma/Theta), Cajas de alijo (Junkbox/THICC/SICC/Docs),
Mochilas y Rigs tácticos (con filtro de slots 2x2 / 1x3, eficiencia y diagrama de grilla real).
"""
from typing import Any, Dict, List, Optional
import customtkinter as ctk

from core.config import THEME
from core.containers_data import (
    CONTAINER_CATEGORIES,
    SICC_VS_DOCS_COMPARISON,
    filter_storage_items,
    get_all_storage_items,
)
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_PANEL,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_SLATE_700,
    C_TEXT,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


CAT_BADGE_COLORS = {
    "Contenedor Seguro": ("#D97706", "#FFFFFF"),
    "Caja / Contenedor": ("#4F46E5", "#FFFFFF"),
    "Mochila": ("#0F766E", "#FFFFFF"),
    "Rig Táctico": ("#0284C7", "#FFFFFF"),
}


class TabContainers(ctk.CTkFrame):
    """Pestaña de Contenedores, Mochilas & Rigs Tácticos con diagramas de grilla y SICC vs Docs."""

    def __init__(self, master, datastore=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.datastore = datastore
        self.active_cat: str = "Todos"
        self.only_secure = ctk.BooleanVar(value=False)
        self.only_2x2 = ctk.BooleanVar(value=False)
        self.only_1x3 = ctk.BooleanVar(value=False)
        all_items = get_all_storage_items()
        self.selected_id: Optional[str] = all_items[0]["id"] if all_items else None
        self._render_token: int = 0
        self._search_job: Optional[str] = None
        self._cat_btns: Dict[str, ctk.CTkButton] = {}
        self._row_refs: Dict[str, ctk.CTkFrame] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters()
        self._build_split_body()
        self._schedule_render()

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
            text="🎒 RIGS, MOCHILAS & CONTENEDORES DE ALIJO",
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            hdr,
            text="Pouches seguros (Kappa / Gamma / Theta), cajas de almacenamiento, eficiencia real, layouts de grilla y comparativa SICC vs Docs.",
            font=ui_font(12),
            text_color=C_TEXT_DIM,
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

        ctk.CTkButton(
            hdr,
            text="⚖️ Ver SICC vs Docs Case",
            width=185,
            height=34,
            corner_radius=8,
            fg_color="#4F46E5",
            hover_color="#4338CA",
            font=ui_font(12, "bold"),
            command=self._show_sicc_vs_docs,
        ).grid(row=0, column=1, rowspan=2, padx=14, pady=10, sticky="e")

    def _build_filters(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        bar.grid(row=1, column=0, padx=0, pady=(0, 8), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        r1 = ctk.CTkFrame(bar, fg_color="transparent")
        r1.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="ew")
        r1.grid_columnconfigure(5, weight=1)

        for idx, cat in enumerate(CONTAINER_CATEGORIES):
            lbl = cat.replace("Contenedor Seguro", "Pouches").replace("Caja / Contenedor", "Cajas / Cases").replace("Mochila", "Mochilas").replace("Rig Táctico", "Rigs")
            btn = ctk.CTkButton(
                r1,
                text=lbl,
                height=30,
                width=92 if cat == "Todos" else 112,
                corner_radius=6,
                font=ui_font(12, "bold"),
                fg_color=THEME["accent_gold"] if cat == self.active_cat else THEME["bg_dark"],
                text_color="#0F1115" if cat == self.active_cat else C_TEXT_MUTED,
                hover_color=THEME["border"],
                command=lambda c=cat: self._set_cat(c),
            )
            btn.grid(row=0, column=idx, padx=3, sticky="w")
            self._cat_btns[cat] = btn

        self.search_entry = ctk.CTkEntry(
            r1,
            placeholder_text="Buscar SICC, Docs, Junkbox, Raid, BlackRock, THICC, Kappa...",
            height=32,
            fg_color=C_BG_PANEL,
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12),
        )
        self.search_entry.grid(row=0, column=5, padx=(10, 0), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_debounced)

        r2 = ctk.CTkFrame(bar, fg_color="transparent")
        r2.grid(row=1, column=0, padx=10, pady=(2, 8), sticky="ew")
        r2.grid_columnconfigure(3, weight=1)

        ctk.CTkCheckBox(
            r2,
            text="Entra en Pouch Seguro",
            variable=self.only_secure,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            checkbox_width=18,
            checkbox_height=18,
            command=self._schedule_render,
        ).grid(row=0, column=0, padx=(4, 14), sticky="w")

        ctk.CTkCheckBox(
            r2,
            text="Rigs con slot 2x2 (Casco/Chaleco)",
            variable=self.only_2x2,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            checkbox_width=18,
            checkbox_height=18,
            command=self._schedule_render,
        ).grid(row=0, column=1, padx=(0, 14), sticky="w")

        ctk.CTkCheckBox(
            r2,
            text="Rigs con slot 1x3 (Mags largos)",
            variable=self.only_1x3,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            checkbox_width=18,
            checkbox_height=18,
            command=self._schedule_render,
        ).grid(row=0, column=2, padx=(0, 14), sticky="w")

        self.count_lbl = ctk.CTkLabel(
            r2,
            text="",
            font=ui_font(11, "bold"),
            text_color=THEME["accent_gold"],
        )
        self.count_lbl.grid(row=0, column=3, padx=6, sticky="e")

    def _build_split_body(self):
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.grid(row=2, column=0, sticky="nsew")
        split.grid_columnconfigure(0, weight=0)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)

        self.list_scroll = ctk.CTkScrollableFrame(
            split,
            width=430,
            fg_color=THEME["bg_deep"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.list_scroll.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        self.list_scroll.grid_columnconfigure(0, weight=1)

        self.detail_scroll = ctk.CTkScrollableFrame(
            split,
            fg_color=THEME["bg_deep"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.detail_scroll.grid(row=0, column=1, sticky="nsew")
        self.detail_scroll.grid_columnconfigure(0, weight=1)

    def open_from_search(self, target_name: str):
        self.active_cat = "Todos"
        self.only_secure.set(False)
        self.only_2x2.set(False)
        self.only_1x3.set(False)
        for c, b in self._cat_btns.items():
            b.configure(
                fg_color=THEME["accent_gold"] if c == "Todos" else THEME["bg_dark"],
                text_color="#0F1115" if c == "Todos" else C_TEXT_MUTED,
            )
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, target_name)
        self._schedule_render()

    def _set_cat(self, cat: str):
        self.active_cat = cat
        for c, b in self._cat_btns.items():
            active = c == cat
            b.configure(
                fg_color=THEME["accent_gold"] if active else THEME["bg_dark"],
                text_color="#0F1115" if active else C_TEXT_MUTED,
            )
        self._schedule_render()

    def _on_search_debounced(self, _=None):
        if self._search_job is not None:
            self.after_cancel(self._search_job)
        self._search_job = self.after(140, self._schedule_render)

    def _schedule_render(self):
        self._search_job = None
        if not self.winfo_exists():
            return
        items = filter_storage_items(
            category=self.active_cat,
            query=self.search_entry.get(),
            only_in_secure=bool(self.only_secure.get()),
            only_2x2_rigs=bool(self.only_2x2.get()),
            only_1x3_rigs=bool(self.only_1x3.get()),
        )
        self.count_lbl.configure(text=f"{len(items)} ítems")
        self._render_token += 1
        token = self._render_token
        self._row_refs.clear()

        for child in self.list_scroll.winfo_children():
            child.destroy()

        if not items:
            ctk.CTkLabel(
                self.list_scroll,
                text="No se encontraron contenedores/mochilas/rigs con ese filtro.",
                font=ui_font(12, "bold"),
                text_color=C_TEXT_DIM,
            ).grid(row=0, column=0, pady=30)
            self._show_detail(None)
            return

        if not any(it["id"] == self.selected_id for it in items):
            self.selected_id = items[0]["id"]
            self._show_detail(items[0])
        else:
            sel = next(it for it in items if it["id"] == self.selected_id)
            self._show_detail(sel)

        def draw_batch(start: int = 0, batch_size: int = 16):
            if token != self._render_token or not self.winfo_exists():
                return
            end = min(start + batch_size, len(items))
            for idx in range(start, end):
                self._create_item_card(idx, items[idx])
            if end < len(items):
                self.after(4, lambda: draw_batch(end, batch_size))

        draw_batch(0)

    def _create_item_card(self, row_idx: int, item: Dict[str, Any]):
        is_sel = item["id"] == self.selected_id
        card = ctk.CTkFrame(
            self.list_scroll,
            fg_color=THEME["bg_card_hover"] if is_sel else THEME["bg_card"],
            corner_radius=8,
            border_width=2 if is_sel else 1,
            border_color=THEME["accent_gold"] if is_sel else THEME["border_soft"],
        )
        card.grid(row=row_idx, column=0, padx=6, pady=3, sticky="ew")
        card.grid_columnconfigure(1, weight=1)
        self._row_refs[item["id"]] = card

        icon_lbl = ctk.CTkLabel(card, text="", width=48, height=40)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(8, 8), pady=6)
        img = get_gear_ctk_icon(
            item.get("cache_key", ""),
            item.get("icon_url", ""),
            max_size=(46, 38),
            on_ready=lambda im: self.after(0, lambda: icon_lbl.winfo_exists() and icon_lbl.configure(image=im)),
        )
        if img is not None:
            icon_lbl.configure(image=img)

        name_lbl = ctk.CTkLabel(
            card,
            text=item["name"],
            font=ui_font(12, "bold"),
            text_color=C_WHITE,
            anchor="w",
            wraplength=255,
            justify="left",
        )
        name_lbl.grid(row=0, column=1, padx=(0, 6), pady=(6, 1), sticky="ew")

        eff = item.get("efficiency", 1.0)
        ext = item.get("external_grid", "")
        sub_txt = f"{item.get('category', '')}  •  Ext: {ext}  •  Efic: {eff}x"
        if item.get("has_2x2"):
            sub_txt += "  •  [2x2]"
        sub_lbl = ctk.CTkLabel(
            card,
            text=sub_txt,
            font=ui_font(11),
            text_color=C_TEXT_DIM,
            anchor="w",
        )
        sub_lbl.grid(row=1, column=1, padx=(0, 6), pady=(0, 6), sticky="ew")

        b_bg, b_fg = CAT_BADGE_COLORS.get(item.get("category", ""), ("#334155", "#FFFFFF"))
        badge = ctk.CTkLabel(
            card,
            text=f"{item.get('slots', 0)}s",
            width=46,
            height=24,
            corner_radius=6,
            fg_color=b_bg,
            text_color=b_fg,
            font=ui_font(11, "bold"),
        )
        badge.grid(row=0, column=2, rowspan=2, padx=(4, 8))

        def _on_click(_e=None, target=item):
            self.selected_id = target["id"]
            for kid, frame in self._row_refs.items():
                if frame.winfo_exists():
                    sel = kid == target["id"]
                    frame.configure(
                        fg_color=THEME["bg_card_hover"] if sel else THEME["bg_card"],
                        border_width=2 if sel else 1,
                        border_color=THEME["accent_gold"] if sel else THEME["border_soft"],
                    )
            self._show_detail(target)

        for w in (card, icon_lbl, name_lbl, sub_lbl, badge):
            w.bind("<Button-1>", _on_click)

    def _show_detail(self, item: Optional[Dict[str, Any]]):
        for w in self.detail_scroll.winfo_children():
            w.destroy()
        if not item:
            return

        hdr = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        hdr.grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        big_icon = ctk.CTkLabel(hdr, text="", width=92, height=84)
        big_icon.grid(row=0, column=0, rowspan=2, padx=12, pady=10)
        img = get_gear_ctk_icon(
            item.get("cache_key", ""),
            item.get("icon_url", ""),
            max_size=(88, 80),
            on_ready=lambda im: self.after(0, lambda: big_icon.winfo_exists() and big_icon.configure(image=im)),
        )
        if img is not None:
            big_icon.configure(image=img)

        ctk.CTkLabel(
            hdr,
            text=item["name"],
            font=ui_font(17, "bold"),
            text_color=C_WHITE,
            anchor="w",
            wraplength=470,
            justify="left",
        ).grid(row=0, column=1, padx=(4, 12), pady=(12, 2), sticky="ew")

        cat = item.get("category", "")
        b_bg, b_fg = CAT_BADGE_COLORS.get(cat, ("#334155", "#FFFFFF"))
        ctk.CTkLabel(
            hdr,
            text=f"  {cat.upper()}  •  {item.get('slots', 0)} SLOTS INTERNOS  ",
            font=ui_font(11, "bold"),
            fg_color=b_bg,
            text_color=b_fg,
            corner_radius=6,
            height=24,
        ).grid(row=1, column=1, padx=(4, 12), pady=(0, 12), sticky="w")

        specs_box = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        specs_box.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
        specs_box.grid_columnconfigure(1, weight=1)

        rows = [
            ("Capacidad Interna", f"{item.get('slots', 0)} slots"),
            ("Tamaño Externo", str(item.get("external_grid", "Variable"))),
            ("Eficiencia de Espacio", f"{item.get('efficiency', 1.0)}x  (espacio ganado vs ocupado)"),
            ("Distribución / Layout", str(item.get("layout", ""))),
            ("Peso", f"{item.get('weight_kg', 0)} kg"),
            ("Entra en Contenedor Seguro", str(item.get("in_secure", "No"))),
            ("Qué Guarda / Notas", str(item.get("holds", ""))),
        ]
        if item.get("trader"):
            rows.append(("Comerciante", str(item["trader"])))
        if cat == "Mochila":
            rows.append((
                "Penalizaciones",
                f"Mov: {item.get('move_penalty', 0)}%  •  Giro: {item.get('turn_penalty', 0)}%  •  Ergo: {item.get('ergo_penalty', 0)}%  •  {item.get('slots_per_kg', 0)} slots/kg",
            ))

        for r_i, (k_lbl, v_txt) in enumerate(rows):
            ctk.CTkLabel(
                specs_box,
                text=f"{k_lbl}:",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"],
                anchor="nw",
                width=200,
            ).grid(row=r_i, column=0, padx=(12, 8), pady=5, sticky="nw")
            ctk.CTkLabel(
                specs_box,
                text=v_txt,
                font=ui_font(12),
                text_color=C_GREEN_LIGHT if (k_lbl == "Entra en Contenedor Seguro" and v_txt == "Sí") else C_WHITE,
                anchor="w",
                wraplength=420,
                justify="left",
            ).grid(row=r_i, column=1, padx=(0, 12), pady=5, sticky="ew")

        # Diagrama real de grilla si es Rig / Contenedor con layout_cache_key
        lay_key = item.get("layout_cache_key") or ""
        if lay_key:
            lay_box = ctk.CTkFrame(
                self.detail_scroll,
                fg_color=THEME["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=THEME["border"],
            )
            lay_box.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="ew")
            lay_box.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                lay_box,
                text="📐 DISTRIBUCIÓN VISUAL DE BOLSILLOS",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"],
            ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

            lay_lbl = ctk.CTkLabel(lay_box, text="")
            lay_lbl.grid(row=1, column=0, padx=12, pady=(0, 12))
            lay_img = get_gear_ctk_icon(
                lay_key,
                item.get("layout_url", ""),
                max_size=(420, 260),
                on_ready=lambda im: self.after(0, lambda: lay_lbl.winfo_exists() and lay_lbl.configure(image=im)),
            )
            if lay_img is not None:
                lay_lbl.configure(image=lay_img)

        # Si selecciona SICC o Documents case, mostrar tabla comparativa abajo
        low = item["name"].lower()
        if "s i c c" in low or "sicc" in low or "documents case" in low:
            self._render_sicc_docs_card(row=3)

    def _show_sicc_vs_docs(self):
        for w in self.detail_scroll.winfo_children():
            w.destroy()
        self._render_sicc_docs_card(row=0)

    def _render_sicc_docs_card(self, row: int = 0):
        box = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color="#4F46E5",
        )
        box.grid(row=row, column=0, padx=10, pady=10, sticky="ew")
        box.grid_columnconfigure(1, weight=1)
        box.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            box,
            text="⚖️ COMPARATIVA DIRECTA: SICC POUCH vs DOCUMENTS CASE",
            font=ui_font(14, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, columnspan=3, padx=12, pady=(12, 8), sticky="w")

        for c_i, h_txt in enumerate(["Característica", "SICC (5x5 • 25 slots)", "Documents Case (4x4 • 16 slots)"]):
            ctk.CTkLabel(
                box,
                text=h_txt,
                font=ui_font(12, "bold"),
                text_color=C_AMBER if c_i > 0 else C_TEXT_SOFT,
                anchor="w",
            ).grid(row=1, column=c_i, padx=10, pady=(0, 6), sticky="w")

        for idx, row_d in enumerate(SICC_VS_DOCS_COMPARISON, start=2):
            bg = THEME["bg_row"] if idx % 2 == 0 else THEME["bg_row_alt"]
            for c_i, field in enumerate(["aspect", "sicc", "docs"]):
                lbl = ctk.CTkLabel(
                    box,
                    text=row_d[field],
                    font=ui_font(11, "bold" if c_i == 0 else "normal"),
                    text_color=THEME["accent_gold"] if c_i == 0 else C_WHITE,
                    fg_color=bg,
                    corner_radius=4,
                    anchor="w",
                    wraplength=200,
                    justify="left",
                    padx=8,
                    pady=6,
                )
                lbl.grid(row=idx, column=c_i, padx=4, pady=3, sticky="nsew")
