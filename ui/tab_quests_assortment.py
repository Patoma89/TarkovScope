"""TarkovScope - Vista de Inventario & Barters (mixin de TabQuests).
Extraido de tab_quests.py para respetar el principio de responsabilidad unica.
"""
import webbrowser
import customtkinter as ctk
from typing import Any, Dict, List
from core.config import THEME
from core.trader_assortment_data import get_trader_assortment, get_trader_requirements
from ui.theme import C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL, C_BG_PANEL_ALT, C_BLUE, C_BORDER, C_BORDER_SOFT, C_GREEN_LIGHT, C_RED_DARK, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE, ui_font
from ui.image_utils import get_trader_ctk_image, get_trader_stock_ctk_image, get_weapon_or_part_ctk_image


ASSORTMENT_TRADERS = [
    "Prapor",
    "Therapist",
    "Skier",
    "Peacekeeper",
    "Mechanic",
    "Ragman",
    "Jaeger",
    "Ref",
    "Fence",
]

CATEGORY_COLOR_MAP = {
    "ARMA": ("#0284C7", "#E0F2FE"),
    "MUNICIÓN": ("#D97706", "#FEF3C7"),
    "BARTER": ("#CA8A04", "#FEF08A"),
    "ARMADURA": ("#7C3AED", "#EDE9FE"),
    "CASCO": ("#6D28D9", "#EDE9FE"),
    "CHALECO": ("#0D9488", "#CCFBF1"),
    "MOCHILA": ("#059669", "#D1FAE5"),
    "MÉDICO": ("#16A34A", "#DCFCE7"),
    "PROVISIÓN": ("#E11D48", "#FFE4E6"),
    "ACCESORIO": ("#475569", "#F1F5F9"),
    "ÓPTICA": ("#9333EA", "#F3E8FF"),
    "TÉRMICO": (C_RED_DARK, "#FEE2E2"),
    "VISIÓN NOCTURNA": ("#2563EB", "#DBEAFE"),
    "CONTENEDOR": ("#4338CA", "#E0E7FF"),
    "GRANADA": ("#EA580C", "#FFEDD5"),
    "AURICULARES": ("#0891B2", "#CFFAFE"),
    "EQUIPO": (C_SLATE_700, C_TEXT),
    "LLAVE": ("#B45309", "#FEF3C7"),
    "SERVICIO": ("#0284C7", "#E0F2FE"),
    "PASIVO": ("#059669", "#D1FAE5"),
    "TIENDA VIP": ("#D97706", "#FEF3C7"),
    "CUERPO A CUERPO": (C_RED_DARK, "#FEE2E2"),
}


class AssortmentViewMixin:
    """Vista de Inventario & Barters (LL1-LL4) de TabQuests. Requiere el estado inicializado en TabQuests.__init__."""


    # =========================================================================
    # VISTA 2: INVENTARIO & BARTERS (LL1 A LL4)
    # =========================================================================
    def _setup_assortment_view(self):
        self._build_assort_traders_bar()
        self._build_assort_ll_and_req_bar()
        self._build_assort_filters_bar()
        self._build_assort_items_area()
        # En modo GRID ocultamos la barra de filtros de texto para maximizar el área visual
        if getattr(self, "assort_view_mode", "GRID") == "GRID":
            self.assort_filter_bar.grid_remove()

    def _build_assort_traders_bar(self):
        box = ctk.CTkFrame(
            self.assortment_view,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        box.grid(row=0, column=0, padx=0, pady=(0, 6), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        traders_row = ctk.CTkFrame(box, fg_color="transparent")
        traders_row.grid(row=0, column=0, padx=10, pady=6, sticky="ew")

        for idx, t_name in enumerate(ASSORTMENT_TRADERS):
            traders_row.grid_columnconfigure(idx, weight=1)
            is_sel = (t_name == self.selected_assort_trader)

            card = ctk.CTkFrame(
                traders_row,
                fg_color=C_BG_PANEL_ALT,
                corner_radius=4,
                border_width=2,
                border_color=THEME["accent_gold"] if is_sel else C_BORDER_SOFT,
                cursor="hand2"
            )
            card.grid(row=0, column=idx, padx=3, pady=2, sticky="nsew")
            self.assort_trader_cards[t_name] = card

            img_lbl = ctk.CTkLabel(card, text="")
            img_lbl.pack(padx=2, pady=(3, 1))

            def make_cb(label_widget):
                def _cb(new_img):
                    if self.winfo_exists() and label_widget.winfo_exists():
                        try:
                            self.after(0, lambda: label_widget.winfo_exists() and label_widget.configure(image=new_img))
                        except Exception:
                            pass
                return _cb

            ctk_img = get_trader_ctk_image(t_name, size=(60, 60), widget_callback=make_cb(img_lbl))
            img_lbl.configure(image=ctk_img)

            name_lbl = ctk.CTkLabel(
                card,
                text=t_name,
                font=ui_font(11, "bold"),
                text_color=C_WHITE if is_sel else C_TEXT_DIM
            )
            name_lbl.pack(padx=2, pady=(0, 3))
            self.assort_trader_name_lbls[t_name] = name_lbl

            for w in (card, img_lbl, name_lbl):
                w.bind("<Button-1>", lambda e, tr=t_name: self._select_assort_trader(tr))

    def _select_assort_trader(self, trader_name: str):
        self.selected_assort_trader = trader_name
        for t_key, card in self.assort_trader_cards.items():
            is_sel = (t_key == trader_name)
            card.configure(border_color=THEME["accent_gold"] if is_sel else C_BORDER_SOFT)
            if t_key in self.assort_trader_name_lbls:
                self.assort_trader_name_lbls[t_key].configure(
                    text_color=C_WHITE if is_sel else C_TEXT_DIM
                )
        self._apply_assortment_filters()

    def _build_assort_ll_and_req_bar(self):
        ll_row = ctk.CTkFrame(
            self.assortment_view,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT,
            height=46
        )
        ll_row.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
        ll_row.grid_columnconfigure(2, weight=1)

        # 1. Título "Items for sale" como en la wiki
        title_box = ctk.CTkFrame(ll_row, fg_color="transparent")
        title_box.grid(row=0, column=0, padx=(12, 14), pady=6, sticky="w")

        ctk.CTkLabel(
            title_box,
            text="Items for sale  🔗",
            font=ui_font(15, "bold"),
            text_color=C_TEXT
        ).pack(side="left")

        # 2. Pestañas exactas [LL1] [LL2] [LL3] [LL4] idénticas a la wiki / captura
        tabs_box = ctk.CTkFrame(ll_row, fg_color="transparent")
        tabs_box.grid(row=0, column=1, padx=4, pady=6, sticky="w")

        ll_specs = [
            (1, "LL1"),
            (2, "LL2"),
            (3, "LL3"),
            (4, "LL4"),
        ]

        for idx, (ll_val, ll_label) in enumerate(ll_specs):
            is_act = (ll_val == self.selected_ll)
            btn = ctk.CTkButton(
                tabs_box,
                text=ll_label,
                width=52,
                height=30,
                corner_radius=4,
                border_width=1,
                border_color=THEME["accent_gold"] if is_act else "#333C4D",
                fg_color="#252D3D" if is_act else "#141822",
                hover_color="#323C50",
                text_color=C_WHITE if is_act else C_TEXT_DIM,
                font=ui_font(12, "bold"),
                command=lambda lv=ll_val: self._select_loyalty_level(lv)
            )
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else 3, 3), pady=0)
            self.ll_buttons[ll_val] = btn

        # 3. Banner de Requisitos Oficiales del LL
        self.req_banner_lbl = ctk.CTkLabel(
            ll_row,
            text="",
            font=ui_font(12, "bold"),
            text_color=C_BLUE,
            anchor="e"
        )
        self.req_banner_lbl.grid(row=0, column=2, padx=14, pady=6, sticky="e")

        # 4. Botón de Alternar Modo: [ 🖼️ Cuadrícula Oficial (In-Game) ] vs [ 📋 Buscador ]
        self.btn_assort_mode = ctk.CTkButton(
            ll_row,
            text="📋 Cambiar a Lista Filtrable",
            width=190,
            height=30,
            corner_radius=5,
            border_width=1,
            border_color="#384357",
            fg_color="#18202D",
            hover_color="#243044",
            text_color=C_TEXT_SOFT,
            font=ui_font(11, "bold"),
            command=self._toggle_assort_mode
        )
        self.btn_assort_mode.grid(row=0, column=3, padx=(0, 10), pady=6, sticky="e")

    def _toggle_assort_mode(self):
        if self.assort_view_mode == "GRID":
            self.assort_view_mode = "LIST"
            self.btn_assort_mode.configure(
                text="🖼️ Cuadrícula Oficial (In-Game)",
                border_color=THEME["accent_gold"],
                fg_color="#1F2838"
            )
            self.assort_filter_bar.grid(row=2, column=0, padx=0, pady=(0, 6), sticky="ew")
        else:
            self.assort_view_mode = "GRID"
            self.btn_assort_mode.configure(
                text="📋 Cambiar a Lista Filtrable",
                border_color="#384357",
                fg_color="#18202D"
            )
            self.assort_filter_bar.grid_remove()
        self._apply_assortment_filters()

    def _select_loyalty_level(self, level: int):
        self.selected_ll = level
        for lv, btn in self.ll_buttons.items():
            is_act = (lv == level)
            btn.configure(
                fg_color="#252D3D" if is_act else "#141822",
                border_color=THEME["accent_gold"] if is_act else "#333C4D",
                text_color=C_WHITE if is_act else C_TEXT_DIM
            )
        self._apply_assortment_filters()

    def _build_assort_filters_bar(self):
        self.assort_filter_bar = ctk.CTkFrame(
            self.assortment_view,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER_SOFT,
            height=42
        )
        self.assort_filter_bar.grid(row=2, column=0, padx=0, pady=(0, 6), sticky="ew")
        self.assort_filter_bar.grid_columnconfigure(1, weight=1)

        # Categoría
        categories = [
            "TODAS LAS CATEGORÍAS",
            "ARMA",
            "MUNICIÓN",
            "BARTER",
            "ARMADURA",
            "MÉDICO",
            "CONTENEDOR",
            "ACCESORIO",
            "ÓPTICA",
            "CASCO",
            "CHALECO",
            "MOCHILA",
            "GRANADA",
        ]
        self.assort_cat_combo = ctk.CTkComboBox(
            self.assort_filter_bar,
            values=categories,
            width=200,
            height=30,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            state="readonly",
            command=self._on_assort_cat_change
        )
        self.assort_cat_combo.set("TODAS LAS CATEGORÍAS")
        self.assort_cat_combo.grid(row=0, column=0, padx=10, pady=6, sticky="w")

        # Buscador de Ítems / Trueques
        self.assort_search_entry = ctk.CTkEntry(
            self.assort_filter_bar,
            placeholder_text="Buscar arma, munición, barter o ítem en venta...",
            height=30,
            fg_color=C_BG_PANEL,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12)
        )
        self.assort_search_entry.grid(row=0, column=1, padx=(6, 10), pady=6, sticky="ew")
        self.assort_search_entry.bind("<KeyRelease>", self._on_assort_search_debounced)

    def _on_assort_cat_change(self, choice: str):
        self.assort_category_filter = choice
        self._apply_assortment_filters()

    def _on_assort_search_debounced(self, event=None):
        if self._assort_debounce_job is not None:
            self.after_cancel(self._assort_debounce_job)
        self._assort_debounce_job = self.after(160, self._apply_assortment_filters)

    def _build_assort_items_area(self):
        self.assort_scroll = ctk.CTkScrollableFrame(
            self.assortment_view,
            fg_color=C_BG_DARKEST,
            corner_radius=6,
            border_width=1,
            border_color=C_BORDER_SOFT
        )
        self.assort_scroll.grid(row=3, column=0, sticky="nsew")
        self.assort_scroll.grid_columnconfigure(0, weight=1)

    def _apply_assortment_filters(self):
        self._assort_debounce_job = None
        try:
            self.assort_scroll._parent_canvas.yview_moveto(0.0)
        except Exception:
            pass
        req = get_trader_requirements(self.selected_assort_trader, self.selected_ll)
        lvl_req = req.get("level", 1)
        rep_req = req.get("rep", 0.0)
        spd_req = req.get("spend", "0 ₽")
        title_req = req.get("title", f"LL{self.selected_ll}")

        self.req_banner_lbl.configure(
            text=f"🎖️ Req: Nivel {lvl_req}   |   🤝 Reputación: {rep_req:+.2f}   |   💰 Gasto: {spd_req}   ({title_req})"
        )

        if getattr(self, "assort_view_mode", "GRID") == "GRID":
            self._render_grid_view()
        else:
            raw_items = get_trader_assortment(self.selected_assort_trader, self.selected_ll)
            q = (self.assort_search_entry.get() or "").strip().lower()
            cat_f = self.assort_category_filter

            filtered = []
            for it in raw_items:
                cat = it.get("category", "").upper()
                if cat_f != "TODAS LAS CATEGORÍAS" and cat != cat_f:
                    continue
                if q:
                    match_name = q in it.get("name", "").lower()
                    match_desc = q in it.get("desc", "").lower()
                    match_cost = q in it.get("cost", "").lower()
                    if not (match_name or match_desc or match_cost):
                        continue
                filtered.append(it)

            self._render_assortment_items(filtered)

    def _render_grid_view(self):
        self._assort_render_token += 1
        token = self._assort_render_token

        for w in self.assort_scroll.winfo_children():
            w.destroy()

        trader = self.selected_assort_trader
        ll = self.selected_ll

        # Caso Especial: Fence (Stock Dinámico y Scav Karma)
        if trader == "Fence":
            self._render_fence_special_card()
            return

        stock_ctk_img = get_trader_stock_ctk_image(trader, ll, target_width=None)
        if not stock_ctk_img:
            # Fallback
            fb = ctk.CTkFrame(
                self.assort_scroll,
                fg_color="#0D111A",
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER_SOFT
            )
            fb.grid(row=0, column=0, padx=20, pady=40)
            ctk.CTkLabel(
                fb,
                text=f"No se encontró la imagen de stock para {trader} en LL{ll}.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_DIM
            ).pack(padx=20, pady=(16, 8))

            ctk.CTkButton(
                fb,
                text="📋 Ver Lista de Ítems",
                font=ui_font(12, "bold"),
                command=self._toggle_assort_mode
            ).pack(padx=20, pady=(0, 16))
            return

        # Marco con borde sutil para alojar la imagen de inventario
        grid_container = ctk.CTkFrame(
            self.assort_scroll,
            fg_color=C_BG_DARKEST,
            corner_radius=6,
            border_width=1,
            border_color="#1E232F"
        )
        grid_container.grid(row=0, column=0, padx=10, pady=8)

        img_lbl = ctk.CTkLabel(
            grid_container,
            text="",
            image=stock_ctk_img
        )
        img_lbl.pack(padx=4, pady=4)

    def _render_fence_special_card(self):
        card = ctk.CTkFrame(
            self.assort_scroll,
            fg_color=C_BG_DEEP,
            corner_radius=10,
            border_width=2,
            border_color="#EAB308"
        )
        card.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Header
        top_bar = ctk.CTkFrame(card, fg_color=THEME["btn_surface"], corner_radius=8)
        top_bar.grid(row=0, column=0, padx=14, pady=(14, 10), sticky="ew")
        top_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_bar,
            text="🤝 FENCE — MERCADO DINÁMICO & SISTEMA DE REPUTACIÓN SCAV",
            font=ui_font(15, "bold"),
            text_color="#FDE047"
        ).grid(row=0, column=0, padx=14, pady=10, sticky="w")

        info_txt = (
            "A diferencia de los demás comerciantes de Tarkov, el inventario de Fence no es fijo ni predeterminado:\n\n"
            "• 📦 Inventario Base (LL1): Compuesto por todas las armas, cargadores, piezas y equipamiento que los jugadores "
            "le venden directamente. Es una casa de empeño en tiempo real.\n\n"
            "• 👑 Corona de Fence (Reputación Scav +6.00):\n"
            "    - Desbloquea una pestaña secreta de ventas exclusiva con un 30% de descuento en todos los ítems.\n"
            "    - Acceso prioritario para comprar equipamiento no asegurado perdido por jugadores en raid.\n"
            "    - Los Scavs con IA te tratan como aliado de honor, te siguen, te protegen y te ofrecen regalos.\n"
            "    - Tiempo de enfriamiento entre incursiones de Scav reducido drásticamente a solo 5 minutos.\n"
            "    - Reducción masiva en el tiempo del Scav Case en tu Hideout."
        )

        ctk.CTkLabel(
            card,
            text=info_txt,
            font=ui_font(13),
            text_color=C_TEXT_SOFT,
            justify="left",
            wraplength=760
        ).grid(row=1, column=0, padx=20, pady=(6, 16), sticky="w")

        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.grid(row=2, column=0, padx=20, pady=(0, 16), sticky="w")

        ctk.CTkButton(
            btn_box,
            text="🌐 Abrir Fence en la Wiki Oficial",
            font=ui_font(12, "bold"),
            fg_color=C_SLATE_800,
            hover_color=C_SLATE_700,
            border_width=1,
            border_color="#475569",
            height=32,
            command=lambda: webbrowser.open("https://escapefromtarkov.fandom.com/wiki/Fence")
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_box,
            text="📋 Ver Lista de Ítems Frecuentes",
            font=ui_font(12, "bold"),
            fg_color=THEME["accent_gold"],
            hover_color="#B45309",
            text_color="#000000",
            height=32,
            command=self._toggle_assort_mode
        ).pack(side="left")

    def _render_assortment_items(self, items: List[Dict[str, Any]]):
        self._assort_render_token += 1
        token = self._assort_render_token

        for w in self.assort_scroll.winfo_children():
            w.destroy()

        if not items:
            ctk.CTkLabel(
                self.assort_scroll,
                text=f"No se encontraron ítems para {self.selected_assort_trader} en LL{self.selected_ll} con estos filtros.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_DIM
            ).grid(row=0, column=0, pady=50)
            return

        def render_batch(idx: int):
            if not self.winfo_exists() or token != self._assort_render_token:
                return
            limit = min(idx + 6, len(items))
            for i in range(idx, limit):
                self._create_assortment_card(i, items[i])
            if limit < len(items):
                self.after(4, lambda: render_batch(limit))

        render_batch(0)

    def _create_assortment_card(self, row_idx: int, item: Dict[str, Any]):
        is_barter = bool(item.get("is_barter"))
        cat = item.get("category", "ÍTEM").upper()
        bg_col = "#0D111A" if row_idx % 2 == 0 else "#111622"
        border_col = "#CA8A04" if is_barter else "#232A38"

        card = ctk.CTkFrame(
            self.assort_scroll,
            fg_color=bg_col,
            corner_radius=6,
            border_width=1,
            border_color=border_col
        )
        card.grid(row=row_idx, column=0, padx=6, pady=4, sticky="ew")
        card.grid_columnconfigure(1, weight=1)

        # 1. Miniatura / Icono de Arma o Ítem
        img_box = ctk.CTkFrame(card, fg_color="#141822", corner_radius=4, border_width=1, border_color="#262D3D", width=120, height=72)
        img_box.grid(row=0, column=0, padx=8, pady=8, sticky="nsw")
        img_box.pack_propagate(False)

        img_key = item.get("image_key", "gs_1")
        item_ctk_img = get_weapon_or_part_ctk_image(img_key, size=(110, 64), label_fallback=cat)
        lbl_img = ctk.CTkLabel(img_box, text="", image=item_ctk_img)
        lbl_img.pack(expand=True, fill="both")

        # 2. Detalles Centrales: Nombre, Badges, Descripción
        info_col = ctk.CTkFrame(card, fg_color="transparent")
        info_col.grid(row=0, column=1, padx=(6, 12), pady=8, sticky="nsew")
        info_col.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(info_col, fg_color="transparent")
        title_row.pack(fill="x", anchor="w")

        title_lbl = ctk.CTkLabel(
            title_row,
            text=item.get("name", "Ítem"),
            font=ui_font(14, "bold"),
            text_color=C_WHITE,
            anchor="w"
        )
        title_lbl.pack(side="left", anchor="w")

        # Badges (Categoría + Límite por reset)
        badges_row = ctk.CTkFrame(info_col, fg_color="transparent")
        badges_row.pack(fill="x", anchor="w", pady=(3, 2))

        cat_bg, cat_fg = CATEGORY_COLOR_MAP.get(cat, (C_SLATE_700, C_TEXT))
        ctk.CTkLabel(
            badges_row,
            text=f" {cat} ",
            font=ui_font(10, "bold"),
            fg_color=cat_bg,
            text_color=cat_fg,
            corner_radius=3
        ).pack(side="left", padx=(0, 6))

        if is_barter:
            ctk.CTkLabel(
                badges_row,
                text=" TRUEQUE / BARTER ",
                font=ui_font(10, "bold"),
                fg_color="#854D0E",
                text_color="#FEF08A",
                corner_radius=3
            ).pack(side="left", padx=(0, 6))

        limit_txt = item.get("limit", "Límite: Estándar")
        ctk.CTkLabel(
            badges_row,
            text=f"⏳ {limit_txt}",
            font=ui_font(11),
            text_color=C_TEXT_DIM
        ).pack(side="left", padx=(0, 6))

        # Descripción
        desc_txt = item.get("desc", "")
        if desc_txt:
            ctk.CTkLabel(
                info_col,
                text=desc_txt,
                font=ui_font(12),
                text_color=C_TEXT_MUTED,
                anchor="w",
                justify="left"
            ).pack(fill="x", anchor="w", pady=(2, 0))

        # 3. Columna Derecha: Tarjeta de Precio o Receta de Trueque
        cost_box = ctk.CTkFrame(
            card,
            fg_color="#18202F" if not is_barter else "#2A2111",
            corner_radius=6,
            border_width=1,
            border_color=C_BLUE if not is_barter else "#EAB308",
            width=210,
            height=66
        )
        cost_box.grid(row=0, column=2, padx=(0, 10), pady=8, sticky="ns")
        cost_box.pack_propagate(False)

        cost_val = item.get("cost", "—")
        if is_barter:
            ctk.CTkLabel(
                cost_box,
                text="RECETA DE TRUEQUE",
                font=ui_font(9, "bold"),
                text_color="#FEF08A"
            ).pack(anchor="center", pady=(5, 1))

            ctk.CTkLabel(
                cost_box,
                text=cost_val,
                font=ui_font(12, "bold"),
                text_color="#FDE047",
                wraplength=190,
                justify="center"
            ).pack(anchor="center", expand=True, padx=4)
        else:
            ctk.CTkLabel(
                cost_box,
                text="PRECIO DE COMPRA",
                font=ui_font(9, "bold"),
                text_color=C_TEXT_DIM
            ).pack(anchor="center", pady=(6, 1))

            price_col = C_GREEN_LIGHT if "₽" in cost_val else (C_BLUE if "$" in cost_val else C_TEXT)
            ctk.CTkLabel(
                cost_box,
                text=cost_val,
                font=ui_font(15, "bold"),
                text_color=price_col,
                justify="center"
            ).pack(anchor="center", expand=True, padx=4)
