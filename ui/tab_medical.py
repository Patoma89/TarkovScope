"""
TarkovScope - Pestaña Ultra PRO: Medicina, Botiquines & Estimulantes (Medical & Stims)
Catálogo completo con iconos oficiales, filtro por síntoma/lesión y dossier táctico.
"""
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, List, Optional, Tuple

from core.config import THEME
from core.medical_data import (
    MEDICAL_CATALOG,
    get_medical_categories,
    get_symptom_filters,
    filter_medical_items,
    get_medical_icon_path,
)
from ui.image_utils import get_resized_ctk_image, get_resized_tk_image
from ui.theme import (
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_PANEL_ALT,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_SLATE_700,
    C_WHITE,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    ui_font,
)


MED_CATEGORY_COLORS = {
    "Botiquines": "#DC2626",
    "Curación de Lesiones": "#D97706",
    "Analgésicos": "#0284C7",
    "Estimulantes (Stims)": "#9333EA",
}


class TabMedical(ctk.CTkFrame):
    """Pestaña ultra fluida de Medicina, Curación de Lesiones y Estimulantes."""

    def __init__(self, master, datastore=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.datastore = datastore
        self.active_category: str = "Todas"
        self.active_symptom: str = "all"
        self.selected_item_id: Optional[str] = MEDICAL_CATALOG[0]["id"] if MEDICAL_CATALOG else None
        self._search_after_id: Optional[str] = None
        self._render_token: int = 0
        self._cat_buttons: Dict[str, ctk.CTkButton] = {}
        self._sym_buttons: Dict[str, ctk.CTkButton] = {}
        self._thumb_cache: Dict[Tuple[str, int, int], ctk.CTkImage] = {}
        self._tk_thumb_cache: Dict[Tuple[str, int, int], Any] = {}
        self._row_widgets: Dict[str, Dict[str, Any]] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters_bar()
        self._build_main_split()

        self._schedule_render_items()
        if self.selected_item_id:
            self._show_detail(self.selected_item_id)

    def _get_tk_icon(self, item_id: str, max_w: int = 58, max_h: int = 44):
        key = (item_id, max_w, max_h)
        if key in self._tk_thumb_cache:
            return self._tk_thumb_cache[key]
        path = get_medical_icon_path(item_id)
        if not path:
            return None
        tk_img = get_resized_tk_image(f"med:{item_id}", path, (max_w, max_h))
        if tk_img is not None:
            self._tk_thumb_cache[key] = tk_img
        return tk_img

    def _get_ctk_icon(self, item_id: str, max_w: int = 58, max_h: int = 44) -> Optional[ctk.CTkImage]:
        key = (item_id, max_w, max_h)
        if key in self._thumb_cache:
            return self._thumb_cache[key]
        path = get_medical_icon_path(item_id)
        if not path:
            return None
        ctk_img = get_resized_ctk_image(f"med:{item_id}", path, (max_w, max_h))
        if ctk_img is not None:
            self._thumb_cache[key] = ctk_img
        return ctk_img

    def _build_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        hdr.grid(row=0, column=0, sticky="ew", padx=2, pady=(0, 8))
        hdr.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hdr, fg_color="transparent")
        left.grid(row=0, column=0, sticky="w", padx=14, pady=10)

        ctk.CTkLabel(
            left,
            text="💊 MEDICINA, BOTIQUINES & ESTIMULANTES (MEDICAL & STIMS)",
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Filtra por tipo o síntoma (hemorragia, fractura, extremidad negra, dolor, stamina) y consulta efectos exactos.",
            font=ui_font(12),
            text_color=C_TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        stims_cnt = sum(1 for m in MEDICAL_CATALOG if m["category"] == "Estimulantes (Stims)")
        kpi_box = ctk.CTkFrame(hdr, fg_color="transparent")
        kpi_box.grid(row=0, column=1, sticky="e", padx=14, pady=10)

        ctk.CTkLabel(
            kpi_box,
            text=f"🩺 {len(MEDICAL_CATALOG)} Ítems Médicos",
            font=ui_font(12, "bold"),
            fg_color=C_BG_DEEP,
            text_color=C_EMERALD,
            corner_radius=6,
            padx=10,
            pady=6,
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            kpi_box,
            text=f"💉 {stims_cnt} Inyectores / Stims",
            font=ui_font(12, "bold"),
            fg_color=C_BG_DEEP,
            text_color=THEME["accent_gold"],
            corner_radius=6,
            padx=10,
            pady=6,
        ).pack(side="left", padx=4)

    def _build_filters_bar(self):
        bar = ctk.CTkFrame(
            self,
            fg_color=C_BG_PANEL_ALT,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        bar.grid(row=1, column=0, sticky="ew", padx=2, pady=(0, 8))
        bar.grid_columnconfigure(0, weight=1)

        # Fila 0: Categorías (izq) y fila 1: Buscador + Síntomas
        top_row = ctk.CTkFrame(bar, fg_color="transparent")
        top_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
        top_row.grid_columnconfigure(1, weight=1)

        cat_box = ctk.CTkFrame(top_row, fg_color="transparent")
        cat_box.grid(row=0, column=0, sticky="w")

        for cat in get_medical_categories():
            btn = ctk.CTkButton(
                cat_box,
                text=cat,
                height=28,
                width=0,
                corner_radius=14,
                font=ui_font(11, "bold"),
                command=lambda c=cat: self._select_category(c),
            )
            btn.pack(side="left", padx=2)
            self._cat_buttons[cat] = btn

        self.entry_search = ctk.CTkEntry(
            top_row,
            height=28,
            placeholder_text="🔍 Buscar medkit, stim o efecto (Salewa, SJ6, Propital, MULE)...",
            font=ui_font(11),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
            text_color=C_WHITE,
        )
        self.entry_search.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.entry_search.bind("<KeyRelease>", self._on_search_key)

        # Fila 1: Chips de Síntoma / Necesidad
        sym_row = ctk.CTkFrame(bar, fg_color="transparent")
        sym_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 8))

        for sym_key, sym_label in get_symptom_filters():
            btn = ctk.CTkButton(
                sym_row,
                text=sym_label,
                height=26,
                width=0,
                corner_radius=6,
                font=ui_font(10, "bold"),
                command=lambda sk=sym_key: self._select_symptom(sk),
            )
            btn.pack(side="left", padx=2)
            self._sym_buttons[sym_key] = btn

        self._update_filter_styles()

    def _update_filter_styles(self):
        for cat, btn in self._cat_buttons.items():
            active = cat == self.active_category
            btn.configure(
                fg_color=THEME["accent_gold"] if active else C_BG_DEEP,
                hover_color=THEME["accent_gold"] if active else C_SLATE_700,
                text_color=C_BG_DARKEST if active else C_TEXT_SOFT,
                border_width=1,
                border_color=THEME["accent_gold"] if active else C_BORDER,
            )

        for sym, btn in self._sym_buttons.items():
            active = sym == self.active_symptom
            btn.configure(
                fg_color="#0284C7" if active else C_BG_DEEP,
                hover_color="#0369A1" if active else C_SLATE_700,
                text_color=C_WHITE if active else C_TEXT_MUTED,
                border_width=1,
                border_color="#38BDF8" if active else C_BORDER,
            )

    def _select_category(self, category: str):
        self.active_category = category
        self._update_filter_styles()
        self._schedule_render_items()

    def _select_symptom(self, symptom: str):
        self.active_symptom = symptom
        self._update_filter_styles()
        self._schedule_render_items()

    def _on_search_key(self, _event=None):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(100, self._schedule_render_items)

    def _build_main_split(self):
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.grid(row=2, column=0, sticky="nsew", padx=2, pady=0)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)

        left_wrap = ctk.CTkFrame(
            split,
            fg_color=C_BG_DARKEST,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        left_wrap.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left_wrap.grid_columnconfigure(0, weight=1)
        left_wrap.grid_rowconfigure(1, weight=1)

        self.lbl_count = ctk.CTkLabel(
            left_wrap,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w",
        )
        self.lbl_count.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        self.scroll_items = ctk.CTkScrollableFrame(left_wrap, fg_color="transparent")
        self.scroll_items.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.scroll_items.grid_columnconfigure(0, weight=1)

        self.detail_panel = ctk.CTkScrollableFrame(
            split,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.detail_panel.grid_columnconfigure(0, weight=1)

    def _schedule_render_items(self):
        self._render_token += 1
        token = self._render_token

        self._row_widgets.clear()
        for w in self.scroll_items.winfo_children():
            w.destroy()

        query = self.entry_search.get() if hasattr(self, "entry_search") else ""
        items = filter_medical_items(
            category=self.active_category,
            symptom=self.active_symptom,
            query=query,
        )
        self.lbl_count.configure(text=f"💊 Mostrando {len(items)} ítems médicos")

        if not items:
            ctk.CTkLabel(
                self.scroll_items,
                text="No se encontraron ítems médicos con esos filtros.",
                font=ui_font(12),
                text_color=C_TEXT_MUTED,
            ).pack(pady=40)
            return

        if not any(i["id"] == self.selected_item_id for i in items):
            self.selected_item_id = items[0]["id"]
            self._show_detail(self.selected_item_id)

        self._render_batch(items, 0, token)

    def _render_batch(self, items: List[Dict[str, Any]], start_idx: int, token: int):
        if not self.winfo_exists() or token != self._render_token:
            return
        batch_size = 12
        end_idx = min(start_idx + batch_size, len(items))
        for item in items[start_idx:end_idx]:
            self._create_row(item)
        if end_idx < len(items):
            self.after(8, lambda: self._render_batch(items, end_idx, token))

    def _create_row(self, item: Dict[str, Any]):
        iid = item["id"]
        is_sel = iid == self.selected_item_id
        cat = item["category"]
        cat_color = MED_CATEGORY_COLORS.get(cat, C_SLATE_700)
        row_bg = C_BG_PANEL if is_sel else C_BG_DEEP

        card = tk.Frame(
            self.scroll_items,
            bg=row_bg,
            highlightbackground=THEME["accent_gold"] if is_sel else C_BORDER,
            highlightthickness=2 if is_sel else 1,
            bd=0,
            cursor="hand2",
        )
        card.pack(fill="x", padx=4, pady=3)
        card.grid_columnconfigure(1, weight=1)

        img_box = tk.Frame(
            card,
            width=66,
            height=50,
            bg="#080C14",
            highlightbackground=THEME["accent_gold"] if is_sel else C_BORDER,
            highlightthickness=1,
            bd=0,
        )
        img_box.grid(row=0, column=0, rowspan=2, padx=(8, 10), pady=6)
        img_box.grid_propagate(False)

        icon = self._get_tk_icon(iid, max_w=58, max_h=44)
        if icon is not None:
            lbl_img = tk.Label(img_box, text="", image=icon, bg="#080C14", bd=0)
        else:
            lbl_img = tk.Label(img_box, text="💊", font=ui_font(18), bg="#080C14", fg=THEME["accent_gold"], bd=0)
        lbl_img.pack(expand=True, fill="both")

        lbl_name = tk.Label(
            card,
            text=item["name"],
            font=ui_font(12, "bold"),
            bg=row_bg,
            fg=THEME["accent_gold"] if is_sel else C_WHITE,
            anchor="w",
            bd=0,
        )
        lbl_name.grid(row=0, column=1, sticky="ew", padx=2, pady=(6, 1))

        meta = tk.Frame(card, bg=row_bg, bd=0)
        meta.grid(row=1, column=1, sticky="w", padx=2, pady=(0, 6))

        cat_lbl = tk.Label(
            meta,
            text=f" {cat} ",
            font=ui_font(9, "bold"),
            bg=cat_color,
            fg=C_WHITE,
            padx=4,
            pady=1,
            bd=0,
        )
        cat_lbl.pack(side="left", padx=(0, 6))

        stats_lbl = tk.Label(
            meta,
            text=f"⏱ {item['use_time']}  •  📦 {item['uses']}",
            font=ui_font(10),
            bg=row_bg,
            fg=C_TEXT_MUTED,
            bd=0,
        )
        stats_lbl.pack(side="left")

        for widget in (card, img_box, lbl_img, lbl_name, meta, cat_lbl, stats_lbl):
            widget.bind("<Button-1>", lambda _e, item_id=iid: self._on_select_item(item_id))

        self._row_widgets[iid] = {
            "card": card,
            "img_box": img_box,
            "lbl_name": lbl_name,
            "meta": meta,
            "stats_lbl": stats_lbl,
        }

    def _apply_row_style(self, item_id: Optional[str], selected: bool):
        rw = self._row_widgets.get(item_id or "")
        if not rw or not rw["card"].winfo_exists():
            return
        row_bg = C_BG_PANEL if selected else C_BG_DEEP
        rw["card"].configure(
            bg=row_bg,
            highlightbackground=THEME["accent_gold"] if selected else C_BORDER,
            highlightthickness=2 if selected else 1,
        )
        rw["img_box"].configure(
            highlightbackground=THEME["accent_gold"] if selected else C_BORDER,
        )
        rw["lbl_name"].configure(
            bg=row_bg,
            fg=THEME["accent_gold"] if selected else C_WHITE,
        )
        rw["meta"].configure(bg=row_bg)
        rw["stats_lbl"].configure(bg=row_bg)

    def _on_select_item(self, item_id: str):
        if self.selected_item_id == item_id:
            return
        prev = self.selected_item_id
        self.selected_item_id = item_id
        self._apply_row_style(prev, False)
        self._apply_row_style(item_id, True)
        self._show_detail(item_id)

    def _show_detail(self, item_id: str):
        for w in self.detail_panel.winfo_children():
            w.destroy()

        item = next((m for m in MEDICAL_CATALOG if m["id"] == item_id), None)
        if not item:
            return

        cat_color = MED_CATEGORY_COLORS.get(item["category"], C_SLATE_700)

        hdr = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(14, 8))
        hdr.grid_columnconfigure(1, weight=1)

        img_box = ctk.CTkFrame(
            hdr,
            width=76,
            height=64,
            fg_color="#080C14",
            corner_radius=8,
            border_width=1,
            border_color=THEME["accent_gold"],
        )
        img_box.grid(row=0, column=0, padx=(0, 12))
        img_box.grid_propagate(False)

        icon = self._get_ctk_icon(item_id, max_w=68, max_h=56)
        if icon is not None:
            ctk.CTkLabel(img_box, text="", image=icon).pack(expand=True)
        else:
            ctk.CTkLabel(img_box, text="💊", font=ui_font(26), text_color=THEME["accent_gold"]).pack(expand=True)

        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            title_col,
            text=item["name"],
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
            wraplength=290,
            justify="left",
            anchor="w",
        ).pack(anchor="w")

        badges = ctk.CTkFrame(title_col, fg_color="transparent")
        badges.pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            badges,
            text=f" {item['category']} ",
            font=ui_font(11, "bold"),
            fg_color=cat_color,
            text_color=C_WHITE,
            corner_radius=4,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            badges,
            text=f"⏱ {item['use_time']}  •  📦 {item['uses']}",
            font=ui_font(12, "bold"),
            text_color="#38BDF8",
        ).pack(side="left")

        sections = [
            ("🩺 CURA / EFECTO PRINCIPAL", item.get("cures_label", ""), C_WHITE),
            ("✅ EFECTOS POSITIVOS", item.get("positive_effects", ""), C_GREEN_LIGHT),
            ("⚠️ EFECTOS NEGATIVOS / PENALIZACIONES", item.get("negative_effects", ""), "#FCA5A5"),
            ("🎯 USO TÁCTICO RECOMENDADO EN RAID", item.get("tactical_tip", ""), THEME["accent_gold"]),
        ]

        for title, body, txt_color in sections:
            box = ctk.CTkFrame(
                self.detail_panel,
                fg_color=C_BG_DEEP,
                corner_radius=6,
                border_width=1,
                border_color=C_BORDER,
            )
            box.pack(fill="x", padx=14, pady=5)

            ctk.CTkLabel(
                box,
                text=title,
                font=ui_font(11, "bold"),
                text_color=THEME["accent_gold"],
                anchor="w",
            ).pack(fill="x", padx=10, pady=(8, 2))

            ctk.CTkLabel(
                box,
                text=body,
                font=ui_font(12),
                text_color=txt_color,
                wraplength=350,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=10, pady=(0, 8))
