"""
TarkovScope - Sub-vista Táctica de Blindaje, Placas Balísticas, Cascos & Auriculares
Mixin integrado en TabBallistics para consultar protección, compatibilidad de auriculares
y simular penetración multicapa en vivo usando simulate_plate_and_aramid().
"""
from typing import Any, Dict, List, Optional, Tuple
import tkinter as tk
import customtkinter as ctk

from core.armor_data import (
    GEAR_CATEGORIES,
    filter_protection_items,
)
from core.ballistics import calculate_armor_effectiveness, simulate_plate_and_aramid
from core.config import THEME
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_PANEL_ALT,
    C_BG_PANEL_ALT2,
    C_BORDER,
    C_EMERALD,
    C_GREEN_LIGHT,
    C_RED,
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


CLASS_BADGE_COLORS = {
    6: ("#7C3AED", "#FFFFFF"),
    5: ("#DC2626", "#FFFFFF"),
    4: ("#D97706", "#FFFFFF"),
    3: ("#0284C7", "#FFFFFF"),
    2: ("#0F766E", "#FFFFFF"),
    1: ("#334155", "#E2E8F0"),
    0: ("#1E293B", "#94A3B8"),
}

BENCHMARK_AMMO = [
    ("5.45x39mm PP gs", 50, 34, 30, 650),
    ("5.45x39mm BP gs", 46, 45, 41, 650),
    ("5.45x39mm BS gs", 40, 51, 57, 650),
    ("5.56x45mm M855A1", 49, 44, 52, 800),
    ("5.56x45mm M995", 42, 53, 58, 800),
    ("7.62x39mm PP gzh", 55, 41, 52, 600),
    ("7.62x39mm BP gzh", 58, 47, 63, 600),
    ("7.62x51mm M80", 80, 41, 66, 700),
    ("7.62x51mm M61", 70, 64, 83, 700),
    ("9x19mm AP 6.3", 52, 30, 48, 800),
    ("9x19mm PBP gzh", 52, 39, 53, 800),
    (".300 Blackout CBJ", 58, 43, 57, 800),
    ("12/70 Flechette (x8)", 25, 31, 26, 200),
]


ARMOR_PAGE_SIZE = 30


class ArmorMixin:
    """Mixin de Blindaje, Placas, Cascos y Auriculares para TabBallistics."""

    def _init_armor_state(self):
        self.is_armor_mode: bool = False
        self.armor_frame: Optional[ctk.CTkFrame] = None
        self._armor_cat: str = "Todos"
        self._armor_min_cls: int = 0
        self._armor_compat_only = ctk.BooleanVar(value=False)
        self._armor_selected_id: Optional[str] = None
        self._armor_render_token: int = 0
        self._armor_search_job: Optional[str] = None
        self._armor_page: int = 0
        self._armor_filtered_items: List[Dict[str, Any]] = []
        self._armor_cat_btns: Dict[str, ctk.CTkButton] = {}
        self._armor_cls_btns: Dict[int, ctk.CTkButton] = {}
        self._armor_row_refs: Dict[str, Tuple[Any, ...]] = {}

    def _build_armor_area(self):
        if self.armor_frame is not None:
            return
        self.armor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.armor_frame.grid_columnconfigure(0, weight=1)
        self.armor_frame.grid_rowconfigure(1, weight=1)

        # Barra de filtros de Blindaje
        fbar = ctk.CTkFrame(
            self.armor_frame,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        fbar.grid(row=0, column=0, padx=0, pady=(0, 8), sticky="ew")
        fbar.grid_columnconfigure(0, weight=1)

        # Fila 1: Categorías + Buscador
        r1 = ctk.CTkFrame(fbar, fg_color="transparent")
        r1.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="ew")
        r1.grid_columnconfigure(6, weight=1)

        for idx, cat in enumerate(GEAR_CATEGORIES):
            short_lbl = cat.replace("Placas Balísticas", "Placas").replace("Chalecos Blindados", "Chalecos").replace("Rigs Blindados", "Rigs Blind.").replace("Cascos Blindados", "Cascos")
            btn = ctk.CTkButton(
                r1,
                text=short_lbl,
                height=30,
                width=74 if cat == "Todos" else 94,
                corner_radius=6,
                font=ui_font(12, "bold"),
                fg_color=THEME["accent_gold"] if cat == self._armor_cat else THEME["bg_dark"],
                text_color="#0F1115" if cat == self._armor_cat else C_TEXT_MUTED,
                hover_color=THEME["border"],
                command=lambda c=cat: self._set_armor_cat(c),
            )
            btn.grid(row=0, column=idx, padx=2, sticky="w")
            self._armor_cat_btns[cat] = btn

        self.armor_search_entry = ctk.CTkEntry(
            r1,
            placeholder_text="Buscar placa, chaleco, casco o ComTac (GAC, Slick, ULACH)...",
            height=30,
            fg_color=C_BG_PANEL,
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12),
        )
        self.armor_search_entry.grid(row=0, column=6, padx=(8, 0), sticky="ew")
        self.armor_search_entry.bind("<KeyRelease>", self._on_armor_search_debounced)

        # Fila 2: Clases mínimas + Compatibilidad Auriculares + Contador
        r2 = ctk.CTkFrame(fbar, fg_color="transparent")
        r2.grid(row=1, column=0, padx=10, pady=(2, 8), sticky="ew")
        r2.grid_columnconfigure(6, weight=1)

        ctk.CTkLabel(
            r2,
            text="Clase mínima:",
            font=ui_font(11, "bold"),
            text_color=C_TEXT_DIM,
        ).grid(row=0, column=0, padx=(2, 6), sticky="w")

        for col_i, (cls_val, cls_lbl) in enumerate([(0, "Todas"), (3, "Cl. 3+"), (4, "Cl. 4+"), (5, "Cl. 5+"), (6, "Cl. 6")], start=1):
            btn = ctk.CTkButton(
                r2,
                text=cls_lbl,
                height=26,
                width=64,
                corner_radius=5,
                font=ui_font(11, "bold"),
                fg_color=THEME["accent_orange"] if cls_val == self._armor_min_cls else C_BG_PANEL,
                text_color=C_WHITE if cls_val == self._armor_min_cls else C_TEXT_MUTED,
                hover_color=THEME["border"],
                command=lambda v=cls_val: self._set_armor_min_cls(v),
            )
            btn.grid(row=0, column=col_i, padx=2, sticky="w")
            self._armor_cls_btns[cls_val] = btn

        self.armor_compat_chk = ctk.CTkCheckBox(
            r2,
            text="Solo cascos compatibles c/ Auriculares",
            variable=self._armor_compat_only,
            font=ui_font(11, "bold"),
            text_color=C_TEXT_SOFT,
            checkbox_width=18,
            checkbox_height=18,
            command=self._schedule_armor_render,
        )
        self.armor_compat_chk.grid(row=0, column=6, padx=14, sticky="w")

        self.armor_count_lbl = ctk.CTkLabel(
            r2,
            text="",
            font=ui_font(11, "bold"),
            text_color=THEME["accent_gold"],
        )
        self.armor_count_lbl.grid(row=0, column=7, padx=4, sticky="e")

        # Cuerpo dividido: Lista Izquierda + Dossier Táctico Derecha
        split = ctk.CTkFrame(self.armor_frame, fg_color="transparent")
        split.grid(row=1, column=0, sticky="nsew")
        split.grid_columnconfigure(0, weight=0)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)

        left_col = ctk.CTkFrame(split, fg_color="transparent")
        left_col.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        left_col.grid_rowconfigure(0, weight=1)
        left_col.grid_columnconfigure(0, weight=1)

        self.armor_list_scroll = ctk.CTkScrollableFrame(
            left_col,
            width=405,
            fg_color=THEME["bg_deep"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.armor_list_scroll.grid(row=0, column=0, sticky="nsew")
        self.armor_list_scroll.grid_columnconfigure(0, weight=1)

        armor_pager = ctk.CTkFrame(
            left_col,
            fg_color=THEME["bg_card"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"],
            height=36,
        )
        armor_pager.grid(row=1, column=0, pady=(6, 0), sticky="ew")
        armor_pager.grid_columnconfigure(1, weight=1)

        self.armor_prev_btn = ctk.CTkButton(
            armor_pager,
            text="◀ Ant.",
            width=72,
            height=26,
            corner_radius=6,
            fg_color=C_SLATE_800,
            hover_color=THEME["border"],
            font=ui_font(11, "bold"),
            command=self._armor_prev_page,
        )
        self.armor_prev_btn.grid(row=0, column=0, padx=6, pady=5)

        self.armor_page_lbl = ctk.CTkLabel(
            armor_pager,
            text="Pág. 1 / 1",
            font=ui_font(11, "bold"),
            text_color=C_TEXT_MUTED,
        )
        self.armor_page_lbl.grid(row=0, column=1, padx=4, pady=5)

        self.armor_next_btn = ctk.CTkButton(
            armor_pager,
            text="Sig. ▶",
            width=72,
            height=26,
            corner_radius=6,
            fg_color=C_SLATE_800,
            hover_color=THEME["border"],
            font=ui_font(11, "bold"),
            command=self._armor_next_page,
        )
        self.armor_next_btn.grid(row=0, column=2, padx=6, pady=5)

        self.armor_detail_scroll = ctk.CTkScrollableFrame(
            split,
            fg_color=THEME["bg_deep"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        self.armor_detail_scroll.grid(row=0, column=1, sticky="nsew")
        self.armor_detail_scroll.grid_columnconfigure(0, weight=1)

        self._schedule_armor_render()

    def _toggle_armor_mode(self):
        if self.is_armor_mode:
            self._exit_armor_mode()
            self._render_current_page()
            return

        if self.is_duel_mode:
            if getattr(self, "duel_frame", None) is not None:
                self.duel_frame.grid_remove()
            self.is_duel_mode = False
            self.btn_duel.configure(text="⚔️ Comparador Versus", fg_color=C_SLATE_800, text_color=C_TEXT)

        self.legend_frame.grid_remove()
        self.scroll_frame.grid_remove()
        self.pager.grid_remove()

        self._build_armor_area()
        self.is_armor_mode = True
        self.armor_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
        self.btn_armor.configure(
            text="📊 Volver a Munición",
            fg_color=THEME["accent_gold"],
            text_color="#0F1115",
        )

    def _exit_armor_mode(self):
        self.is_armor_mode = False
        if self.armor_frame is not None:
            self.armor_frame.grid_remove()
        self.legend_frame.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.pager.grid(row=3, column=0, pady=(6, 0), sticky="ew")
        self.btn_armor.configure(
            text="🛡️ Blindaje & Cascos",
            fg_color=C_SLATE_800,
            text_color=C_TEXT,
        )

    def _open_armor_from_search(self, item_name: str):
        if not self.is_armor_mode:
            self._toggle_armor_mode()
        self._armor_cat = "Todos"
        self._armor_min_cls = 0
        self._armor_compat_only.set(False)
        for c, b in self._armor_cat_btns.items():
            b.configure(
                fg_color=THEME["accent_gold"] if c == "Todos" else THEME["bg_dark"],
                text_color="#0F1115" if c == "Todos" else C_TEXT_MUTED,
            )
        for v, b in self._armor_cls_btns.items():
            b.configure(
                fg_color=THEME["accent_orange"] if v == 0 else C_BG_PANEL,
                text_color=C_WHITE if v == 0 else C_TEXT_MUTED,
            )
        if hasattr(self, "armor_search_entry"):
            self.armor_search_entry.delete(0, "end")
            self.armor_search_entry.insert(0, item_name)
        self._schedule_armor_render()

    def _set_armor_cat(self, cat: str):
        self._armor_cat = cat
        for c, b in self._armor_cat_btns.items():
            active = c == cat
            b.configure(
                fg_color=THEME["accent_gold"] if active else THEME["bg_dark"],
                text_color="#0F1115" if active else C_TEXT_MUTED,
            )
        self._schedule_armor_render()

    def _set_armor_min_cls(self, cls_val: int):
        self._armor_min_cls = cls_val
        for v, b in self._armor_cls_btns.items():
            active = v == cls_val
            b.configure(
                fg_color=THEME["accent_orange"] if active else C_BG_PANEL,
                text_color=C_WHITE if active else C_TEXT_MUTED,
            )
        self._schedule_armor_render()

    def _on_armor_search_debounced(self, _=None):
        if self._armor_search_job is not None:
            self.after_cancel(self._armor_search_job)
        self._armor_search_job = self.after(140, self._schedule_armor_render)

    def _armor_prev_page(self):
        if self._armor_page > 0:
            self._armor_page -= 1
            self._render_armor_page()

    def _armor_next_page(self):
        total_pages = max(1, (len(self._armor_filtered_items) + ARMOR_PAGE_SIZE - 1) // ARMOR_PAGE_SIZE)
        if self._armor_page + 1 < total_pages:
            self._armor_page += 1
            self._render_armor_page()

    def _schedule_armor_render(self):
        self._armor_search_job = None
        if not self.winfo_exists() or self.armor_frame is None:
            return
        query = self.armor_search_entry.get() if hasattr(self, "armor_search_entry") else ""
        items = filter_protection_items(
            category=self._armor_cat,
            min_class=self._armor_min_cls,
            query=query,
            headset_only_compat=bool(self._armor_compat_only.get()),
        )
        self._armor_filtered_items = items
        self._armor_page = 0
        self.armor_count_lbl.configure(text=f"{len(items)} ítems")

        if not items:
            self._armor_render_token += 1
            self._armor_row_refs.clear()
            for child in self.armor_list_scroll.winfo_children():
                child.destroy()
            self.armor_page_lbl.configure(text="Pág. 1 / 1")
            self.armor_prev_btn.configure(state="disabled")
            self.armor_next_btn.configure(state="disabled")
            ctk.CTkLabel(
                self.armor_list_scroll,
                text="Sin resultados para ese filtro.",
                font=ui_font(13, "bold"),
                text_color=C_TEXT_DIM,
            ).grid(row=0, column=0, pady=30)
            self._show_armor_detail(None)
            return

        if not any(it["id"] == self._armor_selected_id for it in items):
            self._armor_selected_id = items[0]["id"]
            self._show_armor_detail(items[0])
        else:
            sel = next(it for it in items if it["id"] == self._armor_selected_id)
            self._show_armor_detail(sel)

        self._render_armor_page()

    def _render_armor_page(self):
        if not self.winfo_exists() or self.armor_frame is None:
            return
        items = self._armor_filtered_items
        total = len(items)
        total_pages = max(1, (total + ARMOR_PAGE_SIZE - 1) // ARMOR_PAGE_SIZE)
        if self._armor_page >= total_pages:
            self._armor_page = max(0, total_pages - 1)

        start_idx = self._armor_page * ARMOR_PAGE_SIZE
        end_idx = min(start_idx + ARMOR_PAGE_SIZE, total)
        page_slice = items[start_idx:end_idx]

        self.armor_page_lbl.configure(text=f"Pág. {self._armor_page + 1} / {total_pages} ({start_idx + 1}-{end_idx})")
        self.armor_prev_btn.configure(state="normal" if self._armor_page > 0 else "disabled")
        self.armor_next_btn.configure(state="normal" if (self._armor_page + 1) < total_pages else "disabled")

        self._armor_render_token += 1
        token = self._armor_render_token
        self._armor_row_refs.clear()

        for child in self.armor_list_scroll.winfo_children():
            child.destroy()

        try:
            self.armor_list_scroll._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass

        def draw_batch(start: int = 0, batch_size: int = 15):
            if token != self._armor_render_token or not self.winfo_exists():
                return
            end = min(start + batch_size, len(page_slice))
            for idx in range(start, end):
                self._create_armor_card(idx, page_slice[idx])
            if end < len(page_slice):
                self.after(4, lambda: draw_batch(end, batch_size))

        draw_batch(0)

    def _style_armor_row(self, row_id: Optional[str], selected: bool):
        if not row_id:
            return
        refs = self._armor_row_refs.get(row_id)
        if not refs:
            return
        card, icon_lbl, name_lbl, sub_lbl = refs
        if not card.winfo_exists():
            return
        bg = THEME["bg_card_hover"] if selected else THEME["bg_card"]
        card.configure(
            bg=bg,
            highlightbackground=THEME["accent_gold"] if selected else THEME["border_soft"],
            highlightthickness=2 if selected else 1,
        )
        icon_lbl.configure(fg_color=bg)
        name_lbl.configure(bg=bg)
        sub_lbl.configure(bg=bg)

    def _create_armor_card(self, row_idx: int, item: Dict[str, Any]):
        is_sel = item["id"] == self._armor_selected_id
        row_bg = THEME["bg_card_hover"] if is_sel else THEME["bg_card"]

        card = tk.Frame(
            self.armor_list_scroll,
            bg=row_bg,
            highlightbackground=THEME["accent_gold"] if is_sel else THEME["border_soft"],
            highlightthickness=2 if is_sel else 1,
            bd=0,
            cursor="hand2",
        )
        card.grid(row=row_idx, column=0, padx=6, pady=3, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # Icono 42x38 (único CTkLabel plano por soporte HiDPI CTkImage)
        icon_lbl = ctk.CTkLabel(card, text="", width=48, height=40, fg_color=row_bg)
        icon_lbl.grid(row=0, column=0, rowspan=2, padx=(8, 8), pady=6)

        def _apply_img(img: ctk.CTkImage):
            if icon_lbl.winfo_exists():
                icon_lbl.configure(image=img)

        def _on_icon_ready(im: ctk.CTkImage):
            if self.winfo_exists():
                try:
                    self.after(0, lambda: _apply_img(im))
                except Exception:
                    pass

        ctk_img = get_gear_ctk_icon(
            item.get("cache_key", ""),
            item.get("icon_url", ""),
            max_size=(46, 38),
            on_ready=_on_icon_ready,
        )
        if ctk_img is not None:
            icon_lbl.configure(image=ctk_img)

        name_lbl = tk.Label(
            card,
            text=item["name"],
            font=ui_font(11, "bold"),
            bg=row_bg,
            fg=C_WHITE,
            anchor="w",
            wraplength=235,
            justify="left",
            bd=0,
        )
        name_lbl.grid(row=0, column=1, padx=(0, 6), pady=(6, 1), sticky="ew")

        cat = item.get("category", "")
        if cat == "Auriculares":
            sub_txt = f"{item.get('mount_type', '')}  •  Alcance: {item.get('hearing_distance_m', 0)} m"
            badge_txt = f"{item.get('hearing_distance_m', 0)}m"
            b_bg, b_fg = ("#0F766E", "#FFFFFF")
        elif cat == "Casco Blindado":
            compat = item.get("headset_compat", "")
            c_ico = "🚫 Bloquea Audio" if compat == "Bloquea Auriculares" else ("✅ High-Cut" if "High-Cut" in compat else "✅ Auric.")
            sub_txt = f"{c_ico}  •  Rebote: {item.get('ricochet', '')}  •  {item.get('weight_kg', 0)} kg"
            cls = int(item.get("armor_class", 0) or 0)
            badge_txt = f"Cl.{cls}"
            b_bg, b_fg = CLASS_BADGE_COLORS.get(cls, ("#334155", "#FFFFFF"))
        else:
            cls = int(item.get("armor_class", 0) or 0)
            mat = item.get("material", "")
            sub_txt = f"{cat}  •  {mat}  •  {item.get('weight_kg', 0)} kg"
            badge_txt = f"Cl.{cls}" if cls > 0 else "Mod."
            b_bg, b_fg = CLASS_BADGE_COLORS.get(cls, ("#334155", "#FFFFFF"))

        sub_lbl = tk.Label(
            card,
            text=sub_txt,
            font=ui_font(10),
            bg=row_bg,
            fg=C_TEXT_DIM,
            anchor="w",
            bd=0,
        )
        sub_lbl.grid(row=1, column=1, padx=(0, 6), pady=(0, 6), sticky="ew")

        badge = tk.Label(
            card,
            text=badge_txt,
            width=6,
            bg=b_bg,
            fg=b_fg,
            font=ui_font(10, "bold"),
            padx=6,
            pady=4,
            bd=0,
        )
        badge.grid(row=0, column=2, rowspan=2, padx=(4, 8))

        self._armor_row_refs[item["id"]] = (card, icon_lbl, name_lbl, sub_lbl)

        def _on_click(_e=None, target=item):
            prev_id = self._armor_selected_id
            new_id = target["id"]
            if prev_id != new_id:
                self._armor_selected_id = new_id
                self._style_armor_row(prev_id, False)
                self._style_armor_row(new_id, True)
            self._show_armor_detail(target)

        for w in (card, icon_lbl, name_lbl, sub_lbl, badge):
            w.bind("<Button-1>", _on_click)

    def _show_armor_detail(self, item: Optional[Dict[str, Any]]):
        for w in self.armor_detail_scroll.winfo_children():
            w.destroy()

        if not item:
            return

        cat = item.get("category", "")
        cls = int(item.get("armor_class", 0) or 0)

        # Header
        hdr = ctk.CTkFrame(
            self.armor_detail_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        hdr.grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        big_icon = ctk.CTkLabel(hdr, text="", width=92, height=84)
        big_icon.grid(row=0, column=0, rowspan=2, padx=12, pady=10)
        def _on_big_icon_ready(im: ctk.CTkImage):
            if self.winfo_exists():
                try:
                    self.after(0, lambda: big_icon.winfo_exists() and big_icon.configure(image=im))
                except Exception:
                    pass

        img = get_gear_ctk_icon(
            item.get("cache_key", ""),
            item.get("icon_url", ""),
            max_size=(88, 80),
            on_ready=_on_big_icon_ready,
        )
        if img is not None:
            big_icon.configure(image=img)

        ctk.CTkLabel(
            hdr,
            text=item["name"],
            font=ui_font(17, "bold"),
            text_color=C_WHITE,
            anchor="w",
            wraplength=480,
            justify="left",
        ).grid(row=0, column=1, padx=(4, 12), pady=(12, 2), sticky="ew")

        badge_str = f"  {cat.upper()}  "
        if cls > 0:
            badge_str += f" •  CLASE {cls}  "
        elif cat == "Auriculares":
            badge_str += f" •  ALCANCE {item.get('hearing_distance_m', 0)} m  "
        b_bg, b_fg = CLASS_BADGE_COLORS.get(cls, ("#0F766E", "#FFFFFF")) if cls > 0 else ("#0F766E", "#FFFFFF")
        ctk.CTkLabel(
            hdr,
            text=badge_str,
            font=ui_font(11, "bold"),
            fg_color=b_bg,
            text_color=b_fg,
            corner_radius=6,
            height=24,
        ).grid(row=1, column=1, padx=(4, 12), pady=(0, 12), sticky="w")

        # Ficha de especificaciones
        specs_box = ctk.CTkFrame(
            self.armor_detail_scroll,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        specs_box.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
        specs_box.grid_columnconfigure(1, weight=1)

        if cat == "Auriculares":
            specs = [
                ("Tipo de Montaje", item.get("mount_type", "")),
                ("Distancia de Audición (Sprint)", f"{item.get('hearing_distance_m', 0)} metros (Sin auriculares: 53m)"),
                ("Compatibilidad", item.get("compat_note", "")),
                ("Perfil Acústico", item.get("audio_profile", "")),
            ]
        elif cat == "Casco Blindado":
            specs = [
                ("Clase de Blindaje", item.get("class_detail", f"Clase {cls}")),
                ("Zonas Protegidas", item.get("areas", "")),
                ("Compatibilidad Auriculares", item.get("headset_compat", "")),
                ("Probabilidad de Rebote", item.get("ricochet", "")),
                ("Reducción de Sonido", item.get("sound_reduction", "")),
                ("Durabilidad", str(item.get("durability", 0))),
                ("Peso", f"{item.get('weight_kg', 0)} kg"),
                ("Penalizaciones", f"Mov: {item.get('move_penalty', 0)}%  •  Giro: {item.get('turn_penalty', 0)}%  •  Ergo: {item.get('ergo_penalty', 0)}%"),
            ]
        elif cat == "Placa Balística":
            specs = [
                ("Clase Balística", f"Clase {cls}"),
                ("Ranuras Compatibles", item.get("areas", "")),
                ("Material", item.get("material", "")),
                ("Durabilidad / Efectiva", f"{item.get('durability', 0)} pts  (Efectiva: {item.get('effective_durability', 0)} pts)"),
                ("Peso", f"{item.get('weight_kg', 0)} kg"),
                ("Penalizaciones", f"Mov: {item.get('move_penalty', 0)}%  •  Giro: {item.get('turn_penalty', 0)}%  •  Ergo: {item.get('ergo_penalty', 0)}%"),
            ]
        else:
            specs = [
                ("Protección Efectiva", f"Clase Máx. {cls}  (Aramid interno: Cl.{item.get('soft_class', 0)} | Placas: Cl.{item.get('plate_class', 0)})"),
                ("Placas por Defecto", item.get("default_plates", "")),
                ("Protección de Placas", item.get("plates_protection", "")),
                ("Zonas de Aramid", item.get("areas", "")),
                ("Material Base", item.get("material", "")),
                ("Durabilidad Base", str(item.get("durability", 0))),
                ("Peso Base", f"{item.get('weight_kg', 0)} kg"),
                ("Penalizaciones", f"Mov: {item.get('move_penalty', 0)}%  •  Giro: {item.get('turn_penalty', 0)}%  •  Ergo: {item.get('ergo_penalty', 0)}%"),
            ]
            if item.get("storage_slots"):
                specs.append(("Capacidad de Almacenamiento", f"{item['storage_slots']} slots (Eficiencia {item.get('storage_efficiency', 1.0)}x)"))

        for r_i, (k_lbl, v_txt) in enumerate(specs):
            ctk.CTkLabel(
                specs_box,
                text=f"{k_lbl}:",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"],
                anchor="nw",
                width=190,
            ).grid(row=r_i, column=0, padx=(12, 8), pady=5, sticky="nw")

            v_color = C_WHITE
            if k_lbl == "Compatibilidad Auriculares":
                v_color = C_RED if "Bloquea" in v_txt else C_GREEN_LIGHT

            ctk.CTkLabel(
                specs_box,
                text=v_txt,
                font=ui_font(12),
                text_color=v_color,
                anchor="w",
                wraplength=420,
                justify="left",
            ).grid(row=r_i, column=1, padx=(0, 12), pady=5, sticky="ew")

        # Barra visual de audición si es Auricular
        if cat == "Auriculares":
            aud_box = ctk.CTkFrame(
                self.armor_detail_scroll,
                fg_color=THEME["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=THEME["border"],
            )
            aud_box.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
            aud_box.grid_columnconfigure(0, weight=1)
            dist = int(item.get("hearing_distance_m", 53))
            gain = dist - 53
            ctk.CTkLabel(
                aud_box,
                text=f"🔊 VENTAJA AUDITIVA SOBRE JUGADOR SIN AURICULARES (+{gain} METROS DE DETECCIÓN DE SPRINT)",
                font=ui_font(12, "bold"),
                text_color=C_GREEN_LIGHT,
            ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")
            pb = ctk.CTkProgressBar(aud_box, height=16, progress_color=C_EMERALD, fg_color=C_BG_PANEL)
            pb.grid(row=1, column=0, padx=12, pady=(0, 12), sticky="ew")
            pb.set(min(1.0, max(0.05, (dist - 45) / 25.0)))
            return

        # Simulador Balístico en Vivo contra este Blindaje
        if cls > 0:
            sim_box = ctk.CTkFrame(
                self.armor_detail_scroll,
                fg_color=THEME["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color=THEME["border"],
            )
            sim_box.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
            sim_box.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                sim_box,
                text=f"⚔️ SIMULADOR BALÍSTICO EN VIVO CONTRA CLASE {cls}",
                font=ui_font(13, "bold"),
                text_color=THEME["accent_gold"],
            ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="w")

            plate_cls = int(item.get("plate_class", cls) or cls)
            soft_cls = int(item.get("soft_class", 0) or 0)
            eff_dur = float(item.get("effective_durability") or item.get("durability") or 55.0)
            if eff_dur <= 0:
                eff_dur = 55.0
            target_hp = 35.0 if cat == "Casco Blindado" else 85.0

            sim_table = tk.Frame(sim_box, bg=THEME["bg_card"], bd=0)
            sim_table.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")
            sim_table.grid_columnconfigure(0, weight=1)

            for b_idx, (a_name, dmg, pen, admg, rpm) in enumerate(BENCHMARK_AMMO):
                sim = simulate_plate_and_aramid(
                    damage=dmg,
                    penetration_power=pen,
                    armor_damage=admg,
                    plate_class=plate_cls,
                    plate_effective_durability=eff_dur,
                    aramid_class=soft_cls,
                    target_hp=target_hp,
                    rpm=rpm,
                )
                eff = calculate_armor_effectiveness(pen, plate_cls)
                rbg = THEME["bg_row"] if b_idx % 2 == 0 else THEME["bg_row_alt"]

                tk.Label(
                    sim_table,
                    text=f"{a_name}  (Pen {pen} • Daño {dmg})",
                    font=ui_font(11, "bold"),
                    bg=rbg,
                    fg=C_TEXT,
                    anchor="w",
                    padx=10,
                    pady=4,
                    bd=0,
                ).grid(row=b_idx, column=0, pady=1, sticky="ew")

                stk = sim["stk"]
                stk_txt = f"{stk} tiros" if stk < 30 else "30+ tiros"
                pct = sim["first_shot_pen_pct"]
                tk.Label(
                    sim_table,
                    text=f"1er tiro: {pct}%  •  {stk_txt}  ({eff['label']})",
                    font=ui_font(11, "bold"),
                    bg=rbg,
                    fg=eff["color"],
                    anchor="e",
                    padx=10,
                    pady=4,
                    bd=0,
                ).grid(row=b_idx, column=1, pady=1, sticky="ew")
