"""TarkovScope - Guia wiki de Story Quests (mixin de TabStoryQuests).
Extraido de tab_story_quests.py (responsabilidad unica).
"""
import customtkinter as ctk
from typing import Any, Dict, List
from core.config import THEME
from ui.theme import C_BG_PANEL_ALT2, C_BLUE, C_GREEN, C_GREEN_LIGHT, C_RED, C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE, ui_font
from ui.image_utils import get_story_gallery_ctk_image, get_story_gallery_full_pil


TICKET_BRANCH_FILTERS = [
    ("ALL", "Todas las Rutas"),
    ("[SAVIOR]", "🌟 Ruta Savior"),
    ("[DEBTOR]", "💀 Ruta Debtor"),
    ("[SURVIVOR]", "🛡️ Ruta Survivor"),
    ("[FALLEN]", "🔥 Ruta Fallen"),
    ("[TERMINAL]", "🚢 Guía Terminal"),
]

STEPS_PER_PAGE = 8


class StoryGuideMixin:
    """Guia wiki paso a paso de TabStoryQuests (pasos, items relacionados, galeria, zoom)."""


    # =========================================================================
    # COMPONENTE 3: GUÍA PASO A PASO COMPLETA CON TABLAS Y GALERÍA DE IMÁGENES
    # =========================================================================
    def _render_wiki_guide_section(self, parent, chapter: Dict[str, Any], row_idx: int, token: int):
        guide_outer = ctk.CTkFrame(parent, fg_color="transparent")
        guide_outer.grid(row=row_idx, column=0, padx=8, pady=(0, 12), sticky="ew")
        guide_outer.grid_columnconfigure(0, weight=1)

        # Si es el Capítulo 9 (The Ticket), mostrar barra selectora de los 4 Finales + Terminal
        if chapter.get("slug") == "the_ticket":
            branch_bar = ctk.CTkFrame(
                guide_outer,
                fg_color="#111622",
                corner_radius=8,
                border_width=1,
                border_color=THEME["accent_gold"]
            )
            branch_bar.grid(row=0, column=0, padx=0, pady=(0, 8), sticky="ew")

            ctk.CTkLabel(
                branch_bar,
                text="🎭 FILTRAR FINAL DE 'THE TICKET':",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"]
            ).pack(side="left", padx=12, pady=8)

            for b_key, b_lbl in TICKET_BRANCH_FILTERS:
                is_b = (b_key == self.ticket_branch)
                ctk.CTkButton(
                    branch_bar,
                    text=b_lbl,
                    height=28,
                    corner_radius=5,
                    fg_color=THEME["active_tab_bg"] if is_b else THEME["btn_surface"],
                    hover_color=THEME["btn_hover"],
                    border_width=1,
                    border_color=THEME["accent_gold"] if is_b else THEME["border"],
                    text_color=C_WHITE if is_b else C_TEXT_MUTED,
                    font=ui_font(11, "bold"),
                    command=lambda bk=b_key: self._select_ticket_branch(bk)
                ).pack(side="left", padx=4, pady=6)

        # Filtrar pasos de guía según búsqueda y rama
        raw_steps = chapter.get("guide_steps", [])
        q = (self.search_entry.get() or "").strip().lower()
        filtered_steps = []

        for idx_s, st in enumerate(raw_steps, start=1):
            t_en = st.get("title", "")
            t_es = st.get("title_es", "")
            w_en = st.get("walkthrough_en", "")
            w_es = st.get("walkthrough_es", "")

            if chapter.get("slug") == "the_ticket" and self.ticket_branch != "ALL":
                if not t_en.startswith(self.ticket_branch):
                    continue

            if q:
                in_title = q in t_en.lower() or q in t_es.lower()
                in_walk = q in w_en.lower() or q in w_es.lower()
                in_items = any(q in it.get("item", "").lower() or q in it.get("notes", "").lower() for it in st.get("related_items", []))
                in_caps = any(q in g.get("caption", "").lower() or q in g.get("caption_es", "").lower() for g in st.get("gallery", []))
                if not (in_title or in_walk or in_items or in_caps):
                    continue

            st_copy = dict(st)
            st_copy["_step_num"] = idx_s
            filtered_steps.append(st_copy)

        total_steps = len(filtered_steps)
        if total_steps == 0:
            ctk.CTkLabel(
                guide_outer,
                text="No se encontraron pasos en la guía que coincidan con tu búsqueda.",
                font=ui_font(14, "bold"),
                text_color=C_TEXT_DIM
            ).grid(row=1, column=0, pady=30)
            return

        # Paginación de pasos para mantener 60 FPS instantáneos incluso en capítulos gigantes (Boreas 71 pasos, The Ticket 262 pasos)
        total_pages = max(1, (total_steps + STEPS_PER_PAGE - 1) // STEPS_PER_PAGE)
        if self.guide_page >= total_pages:
            self.guide_page = 0

        start_i = self.guide_page * STEPS_PER_PAGE
        end_i = min(start_i + STEPS_PER_PAGE, total_steps)
        page_steps = filtered_steps[start_i:end_i]

        # Barra de paginación superior
        if total_pages > 1:
            self._build_guide_pagination_bar(guide_outer, row_idx=1, total_steps=total_steps, start_i=start_i, end_i=end_i, total_pages=total_pages)

        steps_container = ctk.CTkFrame(guide_outer, fg_color="transparent")
        steps_container.grid(row=2, column=0, sticky="ew")
        steps_container.grid_columnconfigure(0, weight=1)

        # Barra de paginación inferior
        if total_pages > 1:
            self._build_guide_pagination_bar(guide_outer, row_idx=3, total_steps=total_steps, start_i=start_i, end_i=end_i, total_pages=total_pages)

        # Renderizado por lotes (Batch Rendering) de los pasos de la página actual
        def render_step_batch(idx: int = 0):
            if not self.winfo_exists() or token != self._render_token:
                return
            limit = min(idx + 3, len(page_steps))
            for i in range(idx, limit):
                self._create_guide_step_card(steps_container, i, page_steps[i])
            if limit < len(page_steps):
                self.after(6, lambda: render_step_batch(limit))

        render_step_batch(0)

    def _build_guide_pagination_bar(self, parent, row_idx: int, total_steps: int, start_i: int, end_i: int, total_pages: int):
        pbar = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=6,
            border_width=1,
            border_color="#2A3346"
        )
        pbar.grid(row=row_idx, column=0, padx=0, pady=6, sticky="ew")

        ctk.CTkLabel(
            pbar,
            text=f"📖 Mostrando Pasos {start_i + 1} – {end_i} de {total_steps}  (Página {self.guide_page + 1} de {total_pages})",
            font=ui_font(12, "bold"),
            text_color=C_TEXT_SOFT
        ).pack(side="left", padx=12, pady=6)

        nav_box = ctk.CTkFrame(pbar, fg_color="transparent")
        nav_box.pack(side="right", padx=8, pady=4)

        btn_prev = ctk.CTkButton(
            nav_box,
            text="⬅ Anterior",
            width=105,
            height=28,
            corner_radius=5,
            fg_color=C_SLATE_800 if self.guide_page > 0 else "#11151E",
            state="normal" if self.guide_page > 0 else "disabled",
            font=ui_font(11, "bold"),
            command=lambda: self._change_guide_page(self.guide_page - 1)
        )
        btn_prev.pack(side="left", padx=(0, 6))

        # Botones rápidos de página ordenados de izquierda a derecha (1, 2, 3, 4...)
        for p in range(total_pages):
            if total_pages > 10 and p not in (0, total_pages - 1, self.guide_page, self.guide_page - 1, self.guide_page + 1):
                continue
            is_cur = (p == self.guide_page)
            ctk.CTkButton(
                nav_box,
                text=str(p + 1),
                width=32,
                height=26,
                corner_radius=4,
                fg_color=THEME["accent_gold"] if is_cur else "#1A2130",
                text_color="#000000" if is_cur else C_TEXT_MUTED,
                font=ui_font(11, "bold"),
                command=lambda pg=p: self._change_guide_page(pg)
            ).pack(side="left", padx=2)

        btn_next = ctk.CTkButton(
            nav_box,
            text="Siguiente Página ➔",
            width=140,
            height=28,
            corner_radius=5,
            fg_color=C_SLATE_800 if self.guide_page + 1 < total_pages else "#11151E",
            state="normal" if self.guide_page + 1 < total_pages else "disabled",
            font=ui_font(11, "bold"),
            command=lambda: self._change_guide_page(self.guide_page + 1)
        )
        btn_next.pack(side="left", padx=(6, 0))

    def _change_guide_page(self, new_page: int):
        self.guide_page = max(0, new_page)
        self.reload_data()

    # =========================================================================
    # TARJETA INDIVIDUAL DE PASO DE LA GUÍA WIKI
    # =========================================================================
    def _create_guide_step_card(self, parent, row_idx: int, step: Dict[str, Any]):
        level = step.get("level", 3)
        step_num = step.get("_step_num", row_idx + 1)
        is_substep = (level >= 4)

        card = ctk.CTkFrame(
            parent,
            fg_color="#0E131D" if not is_substep else "#111724",
            corner_radius=8,
            border_width=1,
            border_color="#2E384D" if not is_substep else "#242D3F"
        )
        card.grid(row=row_idx, column=0, padx=(20 if is_substep else 0, 0), pady=6, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # 1. Barra de Título del Paso
        hdr_bar = ctk.CTkFrame(
            card,
            fg_color="#171F2E" if not is_substep else "#1A2334",
            corner_radius=6
        )
        hdr_bar.grid(row=0, column=0, padx=8, pady=(8, 6), sticky="ew")
        hdr_bar.grid_columnconfigure(1, weight=1)

        badge_txt = f" PASO {step_num} " if not is_substep else f" SUB-PASO {step_num} "
        badge_bg = THEME["accent_gold"] if not is_substep else C_BLUE
        badge_fg = "#000000" if not is_substep else "#000000"

        ctk.CTkLabel(
            hdr_bar,
            text=badge_txt,
            font=ui_font(11, "bold"),
            fg_color=badge_bg,
            text_color=badge_fg,
            corner_radius=4
        ).grid(row=0, column=0, padx=(8, 10), pady=6)

        title_txt = step.get("title_es" if self.lang_mode == "ES" else "title", "") or step.get("title", "")
        ctk.CTkLabel(
            hdr_bar,
            text=title_txt,
            font=ui_font(15 if not is_substep else 14, "bold"),
            text_color=C_WHITE,
            anchor="w",
            justify="left"
        ).grid(row=0, column=1, padx=4, pady=6, sticky="ew")

        cur_row = 1

        # 2. Banners de Condición (Ej: "This objective only happens if you kept the Armored case...")
        for cond in step.get("conditions", []):
            col_name = cond.get("color", "gold")
            if "red" in col_name:
                c_bg, c_border, c_fg = "#2A1215", C_RED, "#FCA5A5"
            elif "green" in col_name:
                c_bg, c_border, c_fg = "#0F291E", C_GREEN, "#86EFAC"
            else:
                c_bg, c_border, c_fg = "#261F10", "#EAB308", "#FDE047"

            cond_box = ctk.CTkFrame(card, fg_color=c_bg, corner_radius=6, border_width=1, border_color=c_border)
            cond_box.grid(row=cur_row, column=0, padx=12, pady=(2, 6), sticky="ew")
            c_txt = cond.get("text_es" if self.lang_mode == "ES" else "text", "") or cond.get("text", "")
            ctk.CTkLabel(
                cond_box,
                text=f"⚠️ CONDICIÓN DE RUTA: {c_txt}",
                font=ui_font(12, "bold"),
                text_color=c_fg,
                wraplength=920,
                justify="left",
                anchor="w"
            ).pack(padx=10, pady=6, fill="x")
            cur_row += 1

        # 3. Tabla Estructurada de "Related Quest Items" (Igual a la Wiki)
        rel_items = step.get("related_items", [])
        if rel_items:
            self._render_related_items_table(card, rel_items, row_idx=cur_row)
            cur_row += 1

        # 4. Explicación Paso a Paso Completa (Walkthrough Text)
        walk_txt = step.get("walkthrough_es" if self.lang_mode == "ES" else "walkthrough_en", "") or step.get("walkthrough_en", "")
        if walk_txt:
            txt_frame = ctk.CTkFrame(card, fg_color="#0A0E15", corner_radius=6, border_width=1, border_color="#1E2636")
            txt_frame.grid(row=cur_row, column=0, padx=12, pady=(2, 8), sticky="ew")

            ctk.CTkLabel(
                txt_frame,
                text=walk_txt,
                font=ui_font(13),
                text_color=C_TEXT_SOFT,
                wraplength=940,
                justify="left",
                anchor="w"
            ).pack(padx=12, pady=10, fill="x")
            cur_row += 1

        # 5. Galería Visual de Mapas y Capturas In-Game (en cuadrícula de 3 columnas con Zoom al hacer clic)
        gallery = step.get("gallery", [])
        if gallery:
            self._render_step_gallery(card, gallery, row_idx=cur_row, step_title=title_txt)
            cur_row += 1

    def _render_related_items_table(self, parent, items: List[Dict[str, Any]], row_idx: int):
        tbl = ctk.CTkFrame(
            parent,
            fg_color="#121824",
            corner_radius=6,
            border_width=1,
            border_color=C_SLATE_700
        )
        tbl.grid(row=row_idx, column=0, padx=12, pady=(2, 8), sticky="ew")
        tbl.grid_columnconfigure(0, weight=3)
        tbl.grid_columnconfigure(1, weight=1)
        tbl.grid_columnconfigure(2, weight=1)
        tbl.grid_columnconfigure(3, weight=1)
        tbl.grid_columnconfigure(4, weight=4)

        # Cabecera de la tabla
        hdr = ctk.CTkFrame(tbl, fg_color=C_SLATE_800, corner_radius=4)
        hdr.grid(row=0, column=0, columnspan=5, padx=2, pady=2, sticky="ew")
        hdr.grid_columnconfigure(0, weight=3)
        hdr.grid_columnconfigure(1, weight=1)
        hdr.grid_columnconfigure(2, weight=1)
        hdr.grid_columnconfigure(3, weight=1)
        hdr.grid_columnconfigure(4, weight=4)

        headers = [
            (0, "🎒 Ítem de Misión / Llave Requerida"),
            (1, "Cant."),
            (2, "Requisito"),
            (3, "En Raid (FIR)"),
            (4, "Notas e Instrucciones de Uso"),
        ]
        for col_i, h_text in headers:
            ctk.CTkLabel(
                hdr,
                text=h_text,
                font=ui_font(11, "bold"),
                text_color="#FDE047" if col_i == 0 else C_TEXT_MUTED,
                anchor="w"
            ).grid(row=0, column=col_i, padx=8, pady=4, sticky="w")

        for r_idx, it in enumerate(items, start=1):
            if it.get("is_or"):
                or_lbl = ctk.CTkLabel(
                    tbl,
                    text="— O BIEN (ALTERNATIVA COMPATIBLE) —",
                    font=ui_font(10, "bold"),
                    text_color=C_BLUE
                )
                or_lbl.grid(row=r_idx, column=0, columnspan=5, pady=2)
                continue

            raw_fir = it.get("fir", "N/A")
            if self.lang_mode == "ES":
                if "yes" in raw_fir.lower():
                    fir_val = "Sí (En Raid)"
                elif "no" in raw_fir.lower():
                    fir_val = "No"
                else:
                    fir_val = raw_fir
            else:
                fir_val = raw_fir

            fir_col = C_RED if "yes" in raw_fir.lower() else (C_GREEN_LIGHT if "no" in raw_fir.lower() else C_TEXT_DIM)
            notes_val = it.get("notes_es" if self.lang_mode == "ES" else "notes", "") or it.get("notes", "")
            req_val = it.get("requirement_es" if self.lang_mode == "ES" else "requirement", "") or it.get("requirement", "Requerido")

            ctk.CTkLabel(
                tbl,
                text=it.get("item", ""),
                font=ui_font(12, "bold"),
                text_color=C_WHITE,
                wraplength=280,
                justify="left",
                anchor="w"
            ).grid(row=r_idx, column=0, padx=8, pady=4, sticky="w")

            ctk.CTkLabel(
                tbl,
                text=str(it.get("amount", "1")),
                font=ui_font(12, "bold"),
                text_color=C_BLUE,
                anchor="w"
            ).grid(row=r_idx, column=1, padx=8, pady=4, sticky="w")

            ctk.CTkLabel(
                tbl,
                text=req_val,
                font=ui_font(11),
                text_color=C_TEXT_SOFT,
                anchor="w"
            ).grid(row=r_idx, column=2, padx=8, pady=4, sticky="w")

            ctk.CTkLabel(
                tbl,
                text=fir_val,
                font=ui_font(11, "bold"),
                text_color=fir_col,
                anchor="w"
            ).grid(row=r_idx, column=3, padx=8, pady=4, sticky="w")

            ctk.CTkLabel(
                tbl,
                text=notes_val or "—",
                font=ui_font(11),
                text_color=C_TEXT_MUTED,
                wraplength=360,
                justify="left",
                anchor="w"
            ).grid(row=r_idx, column=4, padx=8, pady=4, sticky="w")

    def _render_step_gallery(self, parent, gallery: List[Dict[str, Any]], row_idx: int, step_title: str):
        gal_frame = ctk.CTkFrame(
            parent,
            fg_color="#090C12",
            corner_radius=6,
            border_width=1,
            border_color="#222B3B"
        )
        gal_frame.grid(row=row_idx, column=0, padx=12, pady=(2, 10), sticky="ew")

        hdr = ctk.CTkFrame(gal_frame, fg_color="transparent")
        hdr.pack(fill="x", padx=10, pady=(6, 2))

        ctk.CTkLabel(
            hdr,
            text=f"🗺️ MAPAS Y CAPTURAS DE UBICACIÓN ({len(gallery)}) — Haz clic en cualquier imagen para ampliar en Alta Resolución (Zoom HD)",
            font=ui_font(11, "bold"),
            text_color=C_BLUE
        ).pack(side="left")

        grid_box = ctk.CTkFrame(gal_frame, fg_color="transparent")
        grid_box.pack(fill="x", padx=6, pady=(2, 8))

        cols = 3
        for c in range(cols):
            grid_box.grid_columnconfigure(c, weight=1)

        for idx, g_item in enumerate(gallery):
            r = idx // cols
            c = idx % cols
            fn = g_item.get("file", "")
            cap = g_item.get("caption_es" if self.lang_mode == "ES" else "caption", "") or g_item.get("caption", "")

            item_card = ctk.CTkFrame(
                grid_box,
                fg_color=C_BG_PANEL_ALT2,
                corner_radius=6,
                border_width=1,
                border_color="#2B3548",
                cursor="hand2"
            )
            item_card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

            ctk_img = get_story_gallery_ctk_image(fn, max_size=(310, 175))
            if ctk_img:
                img_lbl = ctk.CTkLabel(item_card, text="", image=ctk_img)
                img_lbl.pack(padx=4, pady=(4, 2))
            else:
                img_lbl = ctk.CTkLabel(
                    item_card,
                    text=f"[Imagen: {g_item.get('raw_name', fn)}]",
                    font=ui_font(11),
                    text_color="#64748B",
                    height=100
                )
                img_lbl.pack(padx=4, pady=4)

            cap_lbl = ctk.CTkLabel(
                item_card,
                text=cap,
                font=ui_font(11, "bold"),
                text_color=C_TEXT_SOFT,
                wraplength=295,
                justify="center"
            )
            cap_lbl.pack(padx=6, pady=(0, 6))

            for w in (item_card, img_lbl, cap_lbl):
                w.bind("<Button-1>", lambda e, f=fn, cp=cap, st=step_title: self._open_image_zoom_modal(f, cp, st))

    def _open_image_zoom_modal(self, gallery_file: str, caption: str, step_title: str):
        pil_img = get_story_gallery_full_pil(gallery_file, max_size=(1240, 720))
        if not pil_img:
            return

        top = ctk.CTkToplevel(self)
        top.title(f"TTC — Visor Táctico HD: {step_title}")
        top.geometry("1280x820")
        top.configure(fg_color="#090B10")
        top.transient(self.winfo_toplevel())
        top.grab_set()

        hdr = ctk.CTkFrame(top, fg_color=C_BG_PANEL_ALT2, corner_radius=0, height=54)
        hdr.pack(fill="x", side="top")

        ctk.CTkLabel(
            hdr,
            text=f"🔍 {step_title}  —  {caption}",
            font=ui_font(14, "bold"),
            text_color=C_TEXT
        ).pack(side="left", padx=16, pady=12)

        ctk.CTkButton(
            hdr,
            text="✕ Cerrar (ESC)",
            width=120,
            height=32,
            fg_color="#7F1D1D",
            hover_color="#991B1B",
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=top.destroy
        ).pack(side="right", padx=16, pady=10)

        top.bind("<Escape>", lambda e: top.destroy())

        img_container = ctk.CTkFrame(top, fg_color="#090B10")
        img_container.pack(fill="both", expand=True, padx=12, pady=12)

        ctk_full = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
        lbl = ctk.CTkLabel(img_container, text="", image=ctk_full)
        lbl.pack(expand=True)
