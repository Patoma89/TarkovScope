"""
TarkovScope - Pestaña dedicada: Llaves, Keycards & Marked Rooms (Keys & Intel)
Catálogo táctico por mapa y categoría con checklist personal de llavero y dossier detallado.
"""
import tkinter as tk
import customtkinter as ctk
from typing import Dict, Any, List, Optional, Set, Tuple

from core.config import THEME
from core.keys_data import (
    KEYS_CATALOG,
    get_keys_maps,
    get_keys_categories,
    filter_keys,
    get_key_stats,
    get_key_icon_path,
    fetch_key_icons_async,
)
from core.user_data import get_owned_key_ids, toggle_owned_key
from ui.image_utils import get_resized_ctk_image, get_resized_tk_image
from ui.theme import (
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_PANEL_ALT,
    C_BG_PANEL_ALT2,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED_DARK,
    C_SLATE_700,
    C_SLATE_800,
    C_TEXT,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    ui_font,
)


CATEGORY_COLORS = {
    "Quest Key": "#D97706",
    "Marked Room": "#9333EA",
    "Keycard": "#0284C7",
    "Extracto / Utilidad": "#0F766E",
    "Llaves": "#334155",
}


class TabKeys(ctk.CTkFrame):
    """Pestaña de Llaves, Keycards & Marked Rooms con checklist de llavero y dossier."""

    def __init__(self, master, datastore=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.datastore = datastore
        self.owned_keys: Set[str] = get_owned_key_ids()
        self.active_map: str = "Todos"
        self.active_category: str = "Todas"
        self.only_missing_quest: bool = False
        self.selected_key_id: Optional[str] = KEYS_CATALOG[0]["id"] if KEYS_CATALOG else None
        self._search_after_id: Optional[str] = None
        self._render_token: int = 0
        self._cat_buttons: Dict[str, ctk.CTkButton] = {}
        self._key_thumb_cache: Dict[Tuple[str, int], ctk.CTkImage] = {}
        self._key_tk_cache: Dict[Tuple[str, int], Any] = {}
        self._row_widgets: Dict[str, Dict[str, Any]] = {}
        self._render_limit: int = 30

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_filters_bar()
        self._build_main_split()

        self._refresh_stats()
        self._schedule_render_keys()
        if self.selected_key_id:
            self._show_key_detail(self.selected_key_id)

        def _on_icons_done():
            if self.winfo_exists():
                try:
                    self.after(0, self._on_icons_downloaded)
                except Exception:
                    pass

        fetch_key_icons_async(on_done=_on_icons_done)

    def _on_icons_downloaded(self):
        if not self.winfo_exists():
            return
        self._key_thumb_cache.clear()
        self._key_tk_cache.clear()
        self._schedule_render_keys()
        if self.selected_key_id:
            self._show_key_detail(self.selected_key_id)

    def _get_key_tk_image(self, key_id: str, size: int = 42):
        cache_key = (key_id, size)
        if cache_key in self._key_tk_cache:
            return self._key_tk_cache[cache_key]
        path = get_key_icon_path(key_id)
        if not path:
            return None
        tk_img = get_resized_tk_image(f"key:{key_id}", path, (size, size))
        if tk_img is not None:
            self._key_tk_cache[cache_key] = tk_img
        return tk_img

    def _get_key_ctk_image(self, key_id: str, size: int = 44) -> Optional[ctk.CTkImage]:
        cache_key = (key_id, size)
        if cache_key in self._key_thumb_cache:
            return self._key_thumb_cache[cache_key]
        path = get_key_icon_path(key_id)
        if not path:
            return None
        ctk_img = get_resized_ctk_image(f"key:{key_id}", path, (size, size))
        if ctk_img is not None:
            self._key_thumb_cache[cache_key] = ctk_img
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
            text="🔑 LLAVES, KEYCARDS & MARKED ROOMS (KEYS & INTEL)",
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text="Controla qué llaves guardar para misiones, qué puertas abren, loot destacado y dónde encontrarlas.",
            font=ui_font(12),
            text_color=C_TEXT_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        kpi_box = ctk.CTkFrame(hdr, fg_color="transparent")
        kpi_box.grid(row=0, column=1, sticky="e", padx=14, pady=10)

        self.lbl_kpi_owned = ctk.CTkLabel(
            kpi_box,
            text="",
            font=ui_font(12, "bold"),
            fg_color=C_BG_DEEP,
            text_color=C_EMERALD,
            corner_radius=6,
            padx=10,
            pady=6,
        )
        self.lbl_kpi_owned.pack(side="left", padx=4)

        self.lbl_kpi_missing_q = ctk.CTkLabel(
            kpi_box,
            text="",
            font=ui_font(12, "bold"),
            fg_color=C_BG_DEEP,
            text_color=THEME["accent_gold"],
            corner_radius=6,
            padx=10,
            pady=6,
        )
        self.lbl_kpi_missing_q.pack(side="left", padx=4)

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

        # Fila 0: Pills de categoría
        cat_row = ctk.CTkFrame(bar, fg_color="transparent")
        cat_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))

        for cat in get_keys_categories():
            btn = ctk.CTkButton(
                cat_row,
                text=cat,
                height=30,
                corner_radius=15,
                font=ui_font(11, "bold"),
                command=lambda c=cat: self._select_category(c),
            )
            btn.pack(side="left", padx=3)
            self._cat_buttons[cat] = btn

        self._update_category_pills()

        # Fila 1: Mapa + Buscador + Switch Quest Faltantes
        ctrl_row = ctk.CTkFrame(bar, fg_color="transparent")
        ctrl_row.grid(row=1, column=0, sticky="ew", padx=10, pady=(4, 8))
        ctrl_row.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(
            ctrl_row,
            text="Mapa:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=(2, 6))

        self.opt_map = ctk.CTkOptionMenu(
            ctrl_row,
            values=get_keys_maps(),
            width=180,
            height=32,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            fg_color=C_BG_DEEP,
            button_color=C_SLATE_800,
            button_hover_color=THEME["accent_gold"],
            command=self._on_map_changed,
        )
        self.opt_map.set("Todos")
        self.opt_map.grid(row=0, column=1, padx=(0, 10))

        self.entry_search = ctk.CTkEntry(
            ctrl_row,
            height=32,
            placeholder_text="🔍 Buscar llave, habitación, misión o loot (ej: Dorm 314, LEDX, Black, Checking)...",
            font=ui_font(12),
            fg_color=C_BG_DEEP,
            border_color=C_BORDER,
            text_color=C_WHITE,
        )
        self.entry_search.grid(row=0, column=2, sticky="ew", padx=(0, 10))
        self.entry_search.bind("<KeyRelease>", self._on_search_key)

        self.chk_missing_quest = ctk.CTkCheckBox(
            ctrl_row,
            text="Solo Quest Keys que me faltan",
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT,
            fg_color=THEME["accent_gold"],
            hover_color=THEME["accent_gold"],
            command=self._on_missing_toggle,
        )
        self.chk_missing_quest.grid(row=0, column=3, padx=(0, 4))

    def _build_main_split(self):
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.grid(row=2, column=0, sticky="nsew", padx=2, pady=0)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=2)
        split.grid_rowconfigure(0, weight=1)

        # Panel Izquierdo: Listado de llaves
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

        self.lbl_list_count = ctk.CTkLabel(
            left_wrap,
            text="",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w",
        )
        self.lbl_list_count.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 4))

        self.scroll_keys = ctk.CTkScrollableFrame(
            left_wrap,
            fg_color="transparent",
        )
        self.scroll_keys.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self.scroll_keys.grid_columnconfigure(0, weight=1)

        # Panel Derecho: Dossier Táctico de la llave seleccionada
        self.detail_panel = ctk.CTkScrollableFrame(
            split,
            fg_color=C_BG_PANEL,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER,
        )
        self.detail_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        self.detail_panel.grid_columnconfigure(0, weight=1)

    def _update_category_pills(self):
        for cat, btn in self._cat_buttons.items():
            is_active = cat == self.active_category
            btn.configure(
                fg_color=THEME["accent_gold"] if is_active else C_BG_DEEP,
                hover_color=THEME["accent_gold"] if is_active else C_SLATE_700,
                text_color=C_BG_DARKEST if is_active else C_TEXT_SOFT,
                border_width=1,
                border_color=THEME["accent_gold"] if is_active else C_BORDER,
            )

    def _select_category(self, category: str):
        self.active_category = category
        self._update_category_pills()
        self._schedule_render_keys()

    def _on_map_changed(self, map_name: str):
        self.active_map = map_name
        self._schedule_render_keys()

    def _on_missing_toggle(self):
        self.only_missing_quest = bool(self.chk_missing_quest.get())
        self._schedule_render_keys()

    def _on_search_key(self, _event=None):
        if self._search_after_id is not None:
            self.after_cancel(self._search_after_id)
        self._search_after_id = self.after(110, self._schedule_render_keys)

    def _refresh_stats(self):
        st = get_key_stats(self.owned_keys)
        self.lbl_kpi_owned.configure(text=f"✓ En tu llavero: {st['owned']} / {st['total']}")
        self.lbl_kpi_missing_q.configure(text=f"📌 Quest Keys faltantes: {st['quest_missing']}")

    def _schedule_render_keys(self, reset_limit: bool = True):
        self._render_token += 1
        token = self._render_token
        if reset_limit:
            self._render_limit = 30

        self._row_widgets.clear()
        for w in self.scroll_keys.winfo_children():
            w.destroy()

        query = self.entry_search.get() if hasattr(self, "entry_search") else ""
        items = filter_keys(
            map_filter=self.active_map,
            category_filter=self.active_category,
            query=query,
            owned_ids=self.owned_keys,
            only_missing_quest=self.only_missing_quest,
        )
        self.lbl_list_count.configure(text=f"🔑 Mostrando {len(items)} llaves")

        if not items:
            ctk.CTkLabel(
                self.scroll_keys,
                text="No se encontraron llaves con los filtros seleccionados.",
                font=ui_font(12),
                text_color=C_TEXT_MUTED,
            ).pack(pady=40)
            return

        if not any(i["id"] == self.selected_key_id for i in items):
            self.selected_key_id = items[0]["id"]
            self._show_key_detail(self.selected_key_id)

        visible_items = items[: self._render_limit]
        remaining = len(items) - len(visible_items)
        self._render_batch(visible_items, 0, token, remaining)

    def _render_batch(self, items: List[Dict[str, Any]], start_idx: int, token: int, remaining: int = 0):
        if not self.winfo_exists() or token != self._render_token:
            return
        batch_size = 12
        end_idx = min(start_idx + batch_size, len(items))
        for item in items[start_idx:end_idx]:
            self._create_key_row(item)
        if end_idx < len(items):
            self.after(8, lambda: self._render_batch(items, end_idx, token, remaining))
        elif remaining > 0:
            btn_more = ctk.CTkButton(
                self.scroll_keys,
                text=f"⬇ Cargar más llaves ({remaining} restantes)",
                height=34,
                fg_color=C_BG_PANEL,
                hover_color=THEME["accent_gold"],
                border_width=1,
                border_color=C_BORDER,
                text_color=C_WHITE,
                font=ui_font(12, "bold"),
                command=self._load_more_keys,
            )
            btn_more.pack(fill="x", padx=4, pady=8)

    def _load_more_keys(self):
        self._render_limit += 60
        self._schedule_render_keys(reset_limit=False)

    def _create_key_row(self, item: Dict[str, Any]):
        kid = item["id"]
        is_owned = kid in self.owned_keys
        is_selected = kid == self.selected_key_id
        cat = item["category"]
        cat_color = CATEGORY_COLORS.get(cat, C_SLATE_700)
        row_bg = C_BG_PANEL if is_selected else C_BG_DEEP

        card = tk.Frame(
            self.scroll_keys,
            bg=row_bg,
            highlightbackground=THEME["accent_gold"] if is_selected else C_BORDER,
            highlightthickness=2 if is_selected else 1,
            bd=0,
            cursor="hand2",
        )
        card.pack(fill="x", padx=4, pady=3)
        card.grid_columnconfigure(1, weight=1)

        img_box = tk.Frame(
            card,
            width=50,
            height=50,
            bg="#080C14",
            highlightbackground=THEME["accent_gold"] if is_selected else C_BORDER,
            highlightthickness=1,
            bd=0,
        )
        img_box.grid(row=0, column=0, rowspan=2, padx=(8, 10), pady=6)
        img_box.grid_propagate(False)

        key_img = self._get_key_tk_image(kid, size=42)
        if key_img is not None:
            lbl_img = tk.Label(img_box, text="", image=key_img, bg="#080C14", bd=0)
        else:
            fallback_icon = "💳" if cat == "Keycard" else "🔑"
            lbl_img = tk.Label(
                img_box,
                text=fallback_icon,
                font=ui_font(18),
                bg="#080C14",
                fg=THEME["accent_gold"] if cat != "Keycard" else "#38BDF8",
                bd=0,
            )
        lbl_img.pack(expand=True, fill="both")

        lbl_name = tk.Label(
            card,
            text=item["name"],
            font=ui_font(12, "bold"),
            bg=row_bg,
            fg=THEME["accent_gold"] if is_selected else C_WHITE,
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
        cat_lbl.pack(side="left", padx=(0, 5))

        map_lbl = tk.Label(
            meta,
            text=f"📍 {item['map']}",
            font=ui_font(10, "bold"),
            bg=row_bg,
            fg="#38BDF8",
            bd=0,
        )
        map_lbl.pack(side="left", padx=4)

        uses_lbl = tk.Label(
            meta,
            text=f"• Usos: {item['uses']}",
            font=ui_font(10),
            bg=row_bg,
            fg=C_TEXT_MUTED,
            bd=0,
        )
        uses_lbl.pack(side="left", padx=4)

        meta_children = [cat_lbl, map_lbl, uses_lbl]
        if item.get("quests"):
            q_lbl = tk.Label(
                meta,
                text=f"• 📌 {len(item['quests'])}Q",
                font=ui_font(10, "bold"),
                bg=row_bg,
                fg=C_GREEN_LIGHT,
                bd=0,
            )
            q_lbl.pack(side="left", padx=4)
            meta_children.append(q_lbl)

        btn_own = tk.Label(
            card,
            text="✓" if is_owned else "",
            width=2,
            font=ui_font(12, "bold"),
            bg="#15803D" if is_owned else C_BG_DARKEST,
            fg=C_WHITE,
            highlightbackground=C_EMERALD if is_owned else C_SLATE_700,
            highlightthickness=2,
            bd=0,
            cursor="hand2",
        )
        btn_own.grid(row=0, column=2, rowspan=2, padx=(6, 12), pady=6, ipadx=2, ipady=1)
        btn_own.bind("<Button-1>", lambda _e, key_id=kid: self._on_toggle_owned(key_id))

        for widget in (card, img_box, lbl_img, lbl_name, meta, *meta_children):
            widget.bind("<Button-1>", lambda _e, key_id=kid: self._on_select_key(key_id))

        self._row_widgets[kid] = {
            "card": card,
            "img_box": img_box,
            "lbl_name": lbl_name,
            "meta": meta,
            "meta_bg_labels": [map_lbl, uses_lbl] + ([meta_children[-1]] if item.get("quests") else []),
            "btn_own": btn_own,
        }

    def _apply_row_selection_style(self, key_id: Optional[str], selected: bool):
        rw = self._row_widgets.get(key_id or "")
        if not rw:
            return
        if not rw["card"].winfo_exists():
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
        for ml in rw.get("meta_bg_labels", []):
            if ml.winfo_exists():
                ml.configure(bg=row_bg)

    def _on_select_key(self, key_id: str):
        if self.selected_key_id == key_id:
            return
        prev_id = self.selected_key_id
        self.selected_key_id = key_id
        self._apply_row_selection_style(prev_id, False)
        self._apply_row_selection_style(key_id, True)
        self._show_key_detail(key_id)

    def _on_toggle_owned(self, key_id: str):
        new_state = toggle_owned_key(key_id)
        if new_state:
            self.owned_keys.add(key_id)
        else:
            self.owned_keys.discard(key_id)
        self._refresh_stats()

        if self.only_missing_quest:
            self._schedule_render_keys()
        else:
            rw = self._row_widgets.get(key_id)
            if rw and rw["btn_own"].winfo_exists():
                rw["btn_own"].configure(
                    text="✓" if new_state else "",
                    bg="#15803D" if new_state else C_BG_DARKEST,
                    highlightbackground=C_EMERALD if new_state else C_SLATE_700,
                )

        if self.selected_key_id == key_id:
            self._show_key_detail(key_id)

    def _show_key_detail(self, key_id: str):
        for w in self.detail_panel.winfo_children():
            w.destroy()

        item = next((k for k in KEYS_CATALOG if k["id"] == key_id), None)
        if not item:
            return

        is_owned = key_id in self.owned_keys
        cat_color = CATEGORY_COLORS.get(item["category"], C_SLATE_700)

        # Cabecera con icono + título
        hdr_detail = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        hdr_detail.pack(fill="x", padx=14, pady=(14, 6))
        hdr_detail.grid_columnconfigure(1, weight=1)

        detail_img_box = ctk.CTkFrame(
            hdr_detail,
            width=60,
            height=60,
            fg_color="#080C14",
            corner_radius=8,
            border_width=1,
            border_color=THEME["accent_gold"],
        )
        detail_img_box.grid(row=0, column=0, padx=(0, 12))
        detail_img_box.grid_propagate(False)

        d_img = self._get_key_ctk_image(key_id, size=52)
        if d_img is not None:
            ctk.CTkLabel(detail_img_box, text="", image=d_img).pack(expand=True)
        else:
            ctk.CTkLabel(
                detail_img_box,
                text="💳" if item["category"] == "Keycard" else "🔑",
                font=ui_font(24),
                text_color=THEME["accent_gold"],
            ).pack(expand=True)

        ctk.CTkLabel(
            hdr_detail,
            text=item["name"],
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
            wraplength=290,
            justify="left",
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        badges = ctk.CTkFrame(self.detail_panel, fg_color="transparent")
        badges.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkLabel(
            badges,
            text=f" {item['category']} ",
            font=ui_font(11, "bold"),
            fg_color=cat_color,
            text_color=C_WHITE,
            corner_radius=4,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkLabel(
            badges,
            text=f"📍 {item['map']}  •  Usos: {item['uses']}",
            font=ui_font(12, "bold"),
            text_color="#38BDF8",
        ).pack(side="left")

        # Botón grande de estado
        ctk.CTkButton(
            self.detail_panel,
            text="✓ EN TU LLAVERO (Clic para quitar)" if is_owned else "○ NO LA TIENES (Clic para marcar)",
            height=36,
            fg_color="#15803D" if is_owned else C_SLATE_800,
            hover_color="#16A34A" if is_owned else THEME["accent_gold"],
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=lambda: self._on_toggle_owned(key_id),
        ).pack(fill="x", padx=14, pady=(0, 12))

        sections = [
            ("⚖️ VEREDICTO / RECOMENDACIÓN", item.get("verdict", ""), THEME["accent_gold"]),
            ("🚪 QUÉ ABRE EXACTAMENTE", item.get("opens", ""), C_WHITE),
            ("📌 MISIONES QUE LA PIDEN", ", ".join(item.get("quests", [])) or "Ninguna misión obligatoria", C_GREEN_LIGHT if item.get("quests") else C_TEXT_MUTED),
            ("💎 LOOT DESTACADO", item.get("loot", ""), C_TEXT_SOFT),
            ("🔎 DÓNDE ENCONTRARLA / SPAWNS", item.get("spawns", ""), C_TEXT_SOFT),
            ("💰 VALOR ESTIMADO", item.get("approx_value", ""), C_EMERALD),
        ]

        for title, body, txt_color in sections:
            box = ctk.CTkFrame(
                self.detail_panel,
                fg_color=C_BG_DEEP,
                corner_radius=6,
                border_width=1,
                border_color=C_BORDER,
            )
            box.pack(fill="x", padx=14, pady=4)

            ctk.CTkLabel(
                box,
                text=title,
                font=ui_font(11, "bold"),
                text_color=THEME["accent_gold"],
                anchor="w",
            ).pack(fill="x", padx=10, pady=(7, 2))

            ctk.CTkLabel(
                box,
                text=body,
                font=ui_font(12),
                text_color=txt_color,
                wraplength=350,
                justify="left",
                anchor="w",
            ).pack(fill="x", padx=10, pady=(0, 8))
