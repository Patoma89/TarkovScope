"""TarkovScope - Modo Duelo de Balistica (mixin de TabBallistics).
Extraido de tab_ballistics.py (responsabilidad unica).
"""
import customtkinter as ctk
from typing import Any, Dict, List, Optional
from core.config import THEME
from ui.theme import C_AMBER, C_BG_DARKEST, C_BG_INSET, C_BG_PANEL_ALT, C_BLUE, C_GREEN, C_GREEN_LIGHT, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE, ui_font
from core.datastore import get_datastore
from core.ballistics import calculate_armor_effectiveness, calculate_leg_meta_shots, simulate_boss_targets, simulate_shots_to_kill
from ui.ballistics_common import format_caliber_dropdown, format_caliber_short, CLASS_SCORE_COLORS


class DuelMixin:
    """Modo Duelo de proyectiles (A vs B) de TabBallistics. Requiere el estado inicializado en TabBallistics.__init__."""


    # --- Comparador Versus (Side-by-Side Duel Pro - Calibre y Munición) ---

    def _build_duel_area(self):
        if getattr(self, "duel_frame", None) is not None:
            return
        self.duel_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.duel_frame.grid_columnconfigure(0, weight=1)
        self.duel_frame.grid_rowconfigure(1, weight=1)

        # Panel de control superior táctico
        top_duel = ctk.CTkFrame(self.duel_frame, fg_color=THEME["bg_card"], corner_radius=10, border_width=1, border_color=THEME["border"])
        top_duel.grid(row=0, column=0, padx=0, pady=(0, 8), sticky="ew")
        top_duel.grid_columnconfigure(0, weight=1)
        top_duel.grid_columnconfigure(1, weight=0)
        top_duel.grid_columnconfigure(2, weight=1)

        # Barra Superior: Búsqueda Rápida Universal
        quick_bar = ctk.CTkFrame(top_duel, fg_color=C_BG_PANEL_ALT, corner_radius=8, border_width=1, border_color="#242B3B")
        quick_bar.grid(row=0, column=0, columnspan=3, padx=12, pady=(10, 8), sticky="ew")
        quick_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            quick_bar,
            text="⚡ BÚSQUEDA RÁPIDA:",
            font=ui_font(12, "bold"),
            text_color=THEME["accent_gold"]
        ).grid(row=0, column=0, padx=(12, 6), pady=8, sticky="w")

        self.duel_search_entry = ctk.CTkEntry(
            quick_bar,
            placeholder_text="Escribe para filtrar cualquier proyectil (ej: M855A1, BP, RIP, Igolnik, M61, AP-20)...",
            height=32,
            fg_color="#0F131C",
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12)
        )
        self.duel_search_entry.grid(row=0, column=1, padx=6, pady=8, sticky="ew")
        self.duel_search_entry.bind("<KeyRelease>", self._on_duel_quick_search)

        self.duel_search_results = ctk.CTkComboBox(
            quick_bar,
            values=["Escribe para buscar..."],
            width=250,
            height=32,
            fg_color="#0F131C",
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12),
            dropdown_font=ui_font(12),
            state="readonly"
        )
        self.duel_search_results.grid(row=0, column=2, padx=6, pady=8)

        btn_load_a = ctk.CTkButton(
            quick_bar,
            text="➔ Cargar en A",
            width=100,
            height=32,
            fg_color=C_SLATE_800,
            hover_color=THEME["accent_gold"],
            text_color=THEME["accent_gold"],
            font=ui_font(11, "bold"),
            command=lambda: self._apply_quick_search_to_target("A")
        )
        btn_load_a.grid(row=0, column=3, padx=4, pady=8)

        btn_load_b = ctk.CTkButton(
            quick_bar,
            text="➔ Cargar en B",
            width=100,
            height=32,
            fg_color=C_SLATE_800,
            hover_color=C_BLUE,
            text_color=C_BLUE,
            font=ui_font(11, "bold"),
            command=lambda: self._apply_quick_search_to_target("B")
        )
        btn_load_b.grid(row=0, column=4, padx=(4, 12), pady=8)

        # Fila 1: Selectores Jerárquicos Dobles (Calibre -> Munición)
        # Panel Izquierdo: PROYECTIL A (Dorado)
        frame_a = ctk.CTkFrame(top_duel, fg_color="#121622", corner_radius=8, border_width=1, border_color=THEME["accent_gold"])
        frame_a.grid(row=1, column=0, padx=(12, 6), pady=(0, 10), sticky="ew")
        frame_a.grid_columnconfigure(1, weight=1)

        lbl_hdr_a = ctk.CTkLabel(
            frame_a,
            text=" PROYECTIL A ",
            font=ui_font(11, "bold"),
            fg_color=THEME["accent_gold"],
            text_color=C_BG_DARKEST,
            corner_radius=3,
            height=20
        )
        lbl_hdr_a.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        ctk.CTkLabel(frame_a, text="1. Calibre:", font=ui_font(12, "bold"), text_color=C_TEXT_DIM).grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.combo_duel_cal_a = ctk.CTkComboBox(
            frame_a,
            values=["Cargando calibres..."],
            height=32,
            fg_color="#0D111A",
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            command=self._on_duel_cal_a_changed,
            state="readonly"
        )
        self.combo_duel_cal_a.grid(row=1, column=1, padx=(4, 10), pady=4, sticky="ew")

        ctk.CTkLabel(frame_a, text="2. Munición:", font=ui_font(12, "bold"), text_color=THEME["accent_gold"]).grid(row=2, column=0, padx=10, pady=(4, 8), sticky="w")
        self.combo_duel_ammo_a = ctk.CTkComboBox(
            frame_a,
            values=["Cargando..."],
            height=32,
            fg_color="#0D111A",
            border_color=THEME["accent_gold"],
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            command=self._on_duel_ammo_a_changed,
            state="readonly"
        )
        self.combo_duel_ammo_a.grid(row=2, column=1, padx=(4, 10), pady=(4, 8), sticky="ew")

        # Centro: VS + Botón de Intercambio (Swap)
        mid_frame = ctk.CTkFrame(top_duel, fg_color="transparent")
        mid_frame.grid(row=1, column=1, padx=4, pady=(0, 10))

        ctk.CTkLabel(mid_frame, text="⚡ VS ⚡", font=ui_font(15, "bold"), text_color=THEME["accent_orange"]).pack(pady=(8, 4))
        btn_swap = ctk.CTkButton(
            mid_frame,
            text="⇄ Intercambiar",
            width=100,
            height=30,
            fg_color=C_SLATE_800,
            hover_color=THEME["accent_orange"],
            text_color=C_TEXT,
            font=ui_font(11, "bold"),
            command=self._swap_duel_projectiles
        )
        btn_swap.pack(pady=4)

        # Panel Derecho: PROYECTIL B (Cian)
        frame_b = ctk.CTkFrame(top_duel, fg_color="#121622", corner_radius=8, border_width=1, border_color=C_BLUE)
        frame_b.grid(row=1, column=2, padx=(6, 12), pady=(0, 10), sticky="ew")
        frame_b.grid_columnconfigure(1, weight=1)

        lbl_hdr_b = ctk.CTkLabel(
            frame_b,
            text=" PROYECTIL B ",
            font=ui_font(11, "bold"),
            fg_color=C_BLUE,
            text_color=C_BG_DARKEST,
            corner_radius=3,
            height=20
        )
        lbl_hdr_b.grid(row=0, column=0, padx=10, pady=(8, 4), sticky="w")

        ctk.CTkLabel(frame_b, text="1. Calibre:", font=ui_font(12, "bold"), text_color=C_TEXT_DIM).grid(row=1, column=0, padx=10, pady=4, sticky="w")
        self.combo_duel_cal_b = ctk.CTkComboBox(
            frame_b,
            values=["Cargando calibres..."],
            height=32,
            fg_color="#0D111A",
            border_color="#2E3646",
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            command=self._on_duel_cal_b_changed,
            state="readonly"
        )
        self.combo_duel_cal_b.grid(row=1, column=1, padx=(4, 10), pady=4, sticky="ew")

        ctk.CTkLabel(frame_b, text="2. Munición:", font=ui_font(12, "bold"), text_color=C_BLUE).grid(row=2, column=0, padx=10, pady=(4, 8), sticky="w")
        self.combo_duel_ammo_b = ctk.CTkComboBox(
            frame_b,
            values=["Cargando..."],
            height=32,
            fg_color="#0D111A",
            border_color=C_BLUE,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            dropdown_font=ui_font(12),
            command=self._on_duel_ammo_b_changed,
            state="readonly"
        )
        self.combo_duel_ammo_b.grid(row=2, column=1, padx=(4, 10), pady=(4, 8), sticky="ew")

        # Alias de compatibilidad
        self.combo_duel_a = self.combo_duel_ammo_a
        self.combo_duel_b = self.combo_duel_ammo_b

        # Área de resultados scrollable
        self.duel_scroll = ctk.CTkScrollableFrame(self.duel_frame, fg_color=THEME["bg_card"], corner_radius=10, border_width=1, border_color=THEME["border"])
        self.duel_scroll.grid(row=1, column=0, sticky="nsew")
        self.duel_scroll.grid_columnconfigure(0, weight=1)
        self.duel_scroll.grid_columnconfigure(1, weight=1)

    def _toggle_duel_mode(self):
        if getattr(self, "is_armor_mode", False):
            self._exit_armor_mode()
        self.is_duel_mode = not self.is_duel_mode
        if self.is_duel_mode:
            self._build_duel_area()
            self.legend_frame.grid_remove()
            self.scroll_frame.grid_remove()
            self.pager.grid_remove()
            self.duel_frame.grid(row=1, column=0, rowspan=3, sticky="nsew")
            self.btn_duel.configure(text="📊 Volver a Tabla", fg_color=THEME["accent_green"], text_color="#0F1115")
            self._init_duel_dropdowns()
            self._render_duel_content()
        else:
            if self.duel_frame is not None:
                self.duel_frame.grid_remove()
            self.legend_frame.grid(row=1, column=0, padx=0, pady=(0, 6), sticky="ew")
            self.scroll_frame.grid(row=2, column=0, sticky="nsew")
            self.pager.grid(row=3, column=0, pady=(6, 0), sticky="ew")
            self.btn_duel.configure(text="⚔️ Comparador Versus", fg_color=C_SLATE_800, text_color=C_TEXT)

    def _init_duel_dropdowns(self):
        if getattr(self, "duel_frame", None) is None:
            return
        try:
            ds = get_datastore()
            all_ammo = ds.get_ammo(caliber="TODOS", sort_by="penetration_power", descending=True)
            self._all_ammo_map = {a.get("id") or a.get("name", ""): a for a in all_ammo if a.get("name")}
            self._ammo_by_name = {a.get("name", ""): a for a in all_ammo if a.get("name")}

            self._duel_cal_to_ammo: Dict[str, List[Dict[str, Any]]] = {}
            self._duel_cal_to_labels: Dict[str, List[str]] = {}
            self._duel_label_to_ammo: Dict[str, Dict[str, Any]] = {}
            self._all_search_labels: List[str] = []

            for a in all_ammo:
                pen = float(a.get("penetration_power", 0))
                dmg = int(a.get("damage", 0))
                if dmg <= 0 and pen <= 0:
                    continue  # Omitir bengalas y flashbangs no letales del comparador de combate

                raw_cal = a.get("caliber", "")
                cal_disp = format_caliber_dropdown(raw_cal)
                if cal_disp not in self._duel_cal_to_ammo:
                    self._duel_cal_to_ammo[cal_disp] = []
                    self._duel_cal_to_labels[cal_disp] = []
                self._duel_cal_to_ammo[cal_disp].append(a)

                name = a.get("name", "")
                label = f"{name} • Pen {pen:.0f} | Dmg {dmg}"
                self._duel_label_to_ammo[label] = a
                self._duel_cal_to_labels[cal_disp].append(label)

                # También registrar por nombre exacto para lookup rápido
                self._duel_label_to_ammo[name] = a

                search_tag = f"[{format_caliber_short(raw_cal)}] {name} • Pen {pen:.0f}"
                self._duel_label_to_ammo[search_tag] = a
                self._all_search_labels.append(search_tag)

            available_calibers = sorted(list(self._duel_cal_to_ammo.keys()))
            if not available_calibers:
                return

            self.combo_duel_cal_a.configure(values=available_calibers)
            self.combo_duel_cal_b.configure(values=available_calibers)

            cal_a_default = next((c for c in available_calibers if "5.56x45" in c), available_calibers[0])
            cal_b_default = next((c for c in available_calibers if "7.62x39" in c and "5.45" not in c), (available_calibers[1] if len(available_calibers) > 1 else available_calibers[0]))

            curr_cal_a = self.combo_duel_cal_a.get()
            if curr_cal_a not in self._duel_cal_to_ammo:
                self.combo_duel_cal_a.set(cal_a_default)
                curr_cal_a = cal_a_default

            curr_cal_b = self.combo_duel_cal_b.get()
            if curr_cal_b not in self._duel_cal_to_ammo:
                self.combo_duel_cal_b.set(cal_b_default)
                curr_cal_b = cal_b_default

            self._populate_ammo_dropdown_a(curr_cal_a)
            self._populate_ammo_dropdown_b(curr_cal_b)

            if hasattr(self, "duel_search_results") and self._all_search_labels:
                self.duel_search_results.configure(values=self._all_search_labels[:25])
                self.duel_search_results.set(self._all_search_labels[0])
        except Exception as e:
            pass

    def _populate_ammo_dropdown_a(self, caliber_name: str, prefer_bullet_name: Optional[str] = None):
        labels = getattr(self, "_duel_cal_to_labels", {}).get(caliber_name, [])
        if not labels:
            self.combo_duel_ammo_a.configure(values=["Sin municiones"])
            self.combo_duel_ammo_a.set("Sin municiones")
            return

        self.combo_duel_ammo_a.configure(values=labels)
        target_label = labels[0]
        if prefer_bullet_name:
            match = next((lbl for lbl in labels if prefer_bullet_name.lower() in lbl.lower()), None)
            if match:
                target_label = match
        else:
            pref = next((lbl for lbl in labels if "M855A1" in lbl or "M995" in lbl), labels[0])
            target_label = pref

        self.combo_duel_ammo_a.set(target_label)

    def _populate_ammo_dropdown_b(self, caliber_name: str, prefer_bullet_name: Optional[str] = None):
        labels = getattr(self, "_duel_cal_to_labels", {}).get(caliber_name, [])
        if not labels:
            self.combo_duel_ammo_b.configure(values=["Sin municiones"])
            self.combo_duel_ammo_b.set("Sin municiones")
            return

        self.combo_duel_ammo_b.configure(values=labels)
        target_label = labels[0]
        if prefer_bullet_name:
            match = next((lbl for lbl in labels if prefer_bullet_name.lower() in lbl.lower()), None)
            if match:
                target_label = match
        else:
            pref = next((lbl for lbl in labels if "BP" in lbl or "BT" in lbl or "MAI" in lbl), labels[0])
            target_label = pref

        self.combo_duel_ammo_b.set(target_label)

    def _on_duel_cal_a_changed(self, chosen_cal: str):
        self._populate_ammo_dropdown_a(chosen_cal)
        self._render_duel_content()

    def _on_duel_cal_b_changed(self, chosen_cal: str):
        self._populate_ammo_dropdown_b(chosen_cal)
        self._render_duel_content()

    def _on_duel_ammo_a_changed(self, _=None):
        self._render_duel_content()

    def _on_duel_ammo_b_changed(self, _=None):
        self._render_duel_content()

    def _on_duel_selection_changed(self, _=None):
        self._render_duel_content()

    def _swap_duel_projectiles(self):
        cal_a = self.combo_duel_cal_a.get()
        cal_b = self.combo_duel_cal_b.get()
        ammo_lbl_a = self.combo_duel_ammo_a.get()
        ammo_lbl_b = self.combo_duel_ammo_b.get()

        self.combo_duel_cal_a.set(cal_b)
        self.combo_duel_cal_b.set(cal_a)

        labels_a = getattr(self, "_duel_cal_to_labels", {}).get(cal_b, [])
        labels_b = getattr(self, "_duel_cal_to_labels", {}).get(cal_a, [])

        self.combo_duel_ammo_a.configure(values=labels_a)
        self.combo_duel_ammo_b.configure(values=labels_b)

        self.combo_duel_ammo_a.set(ammo_lbl_b if ammo_lbl_b in labels_a else (labels_a[0] if labels_a else ""))
        self.combo_duel_ammo_b.set(ammo_lbl_a if ammo_lbl_a in labels_b else (labels_b[0] if labels_b else ""))

        self._render_duel_content()

    def _on_duel_quick_search(self, event=None):
        job = getattr(self, "_duel_search_job", None)
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass
        self._duel_search_job = self.after(120, self._flush_duel_quick_search)

    def _flush_duel_quick_search(self):
        self._duel_search_job = None
        if not self.winfo_exists():
            return
        query = self.duel_search_entry.get().strip().lower()
        if not hasattr(self, "_all_search_labels"):
            return
        if not query:
            matches = self._all_search_labels[:25]
        else:
            matches = [lbl for lbl in self._all_search_labels if query in lbl.lower()][:30]

        if matches:
            self.duel_search_results.configure(values=matches)
            self.duel_search_results.set(matches[0])
        else:
            self.duel_search_results.configure(values=["Sin coincidencias"])
            self.duel_search_results.set("Sin coincidencias")

    def _apply_quick_search_to_target(self, target: str):
        selected = self.duel_search_results.get()
        if not selected or selected in ("Sin coincidencias", "Escribe para buscar..."):
            return
        ammo = getattr(self, "_duel_label_to_ammo", {}).get(selected)
        if not ammo:
            return

        cal_disp = format_caliber_dropdown(ammo.get("caliber", ""))
        pen = float(ammo.get("penetration_power", 0))
        dmg = int(ammo.get("damage", 0))
        ammo_label = f"{ammo.get('name', '')} • Pen {pen:.0f} | Dmg {dmg}"

        if target == "A":
            self.combo_duel_cal_a.set(cal_disp)
            self._populate_ammo_dropdown_a(cal_disp, prefer_bullet_name=ammo.get("name"))
            if ammo_label in self._duel_cal_to_labels.get(cal_disp, []):
                self.combo_duel_ammo_a.set(ammo_label)
        else:
            self.combo_duel_cal_b.set(cal_disp)
            self._populate_ammo_dropdown_b(cal_disp, prefer_bullet_name=ammo.get("name"))
            if ammo_label in self._duel_cal_to_labels.get(cal_disp, []):
                self.combo_duel_ammo_b.set(ammo_label)

        self._render_duel_content()

    def _render_duel_content(self):
        for w in self.duel_scroll.winfo_children():
            w.destroy()

        if not hasattr(self, "_duel_label_to_ammo") or not self._duel_label_to_ammo:
            self._init_duel_dropdowns()

        label_to_ammo = getattr(self, "_duel_label_to_ammo", {})
        ammo_by_name = getattr(self, "_ammo_by_name", {})
        all_map = getattr(self, "_all_ammo_map", {})

        lbl_a = self.combo_duel_ammo_a.get()
        lbl_b = self.combo_duel_ammo_b.get()

        ammo_a = label_to_ammo.get(lbl_a) or ammo_by_name.get(lbl_a) or all_map.get(lbl_a)
        ammo_b = label_to_ammo.get(lbl_b) or ammo_by_name.get(lbl_b) or all_map.get(lbl_b)

        if (not ammo_a or not ammo_b) and all_map:
            names = sorted(list(all_map.keys()))
            if not ammo_a and names:
                ammo_a = all_map[names[0]]
            if not ammo_b and len(names) > 1:
                ammo_b = all_map[names[1]]
            elif not ammo_b and names:
                ammo_b = all_map[names[0]]

        if not ammo_a or not ammo_b:
            ctk.CTkLabel(
                self.duel_scroll,
                text="Selecciona un calibre y proyectil para comparar.",
                font=ui_font(14, "bold"),
                text_color=THEME["text_muted"]
            ).grid(row=0, column=0, columnspan=2, pady=30)
            return

        self._build_bullet_stat_card(self.duel_scroll, ammo_a, ammo_b, is_a=True).grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self._build_bullet_stat_card(self.duel_scroll, ammo_b, ammo_a, is_a=False).grid(row=0, column=1, padx=8, pady=8, sticky="nsew")

        def _fmt_shots(n: int) -> str:
            return "1 tiro" if n == 1 else f"{n} tiros"

        duel_box = ctk.CTkFrame(self.duel_scroll, fg_color="#10141D", corner_radius=8, border_width=1, border_color="#2B3548")
        duel_box.grid(row=1, column=0, columnspan=2, padx=8, pady=12, sticky="ew")
        duel_box.grid_columnconfigure(0, weight=1)

        duel_table = ctk.CTkFrame(duel_box, fg_color="#232B3D", corner_radius=6)
        duel_table.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        duel_table.grid_columnconfigure(0, minsize=215, weight=0)
        duel_table.grid_columnconfigure(1, minsize=185, weight=0)
        duel_table.grid_columnconfigure(2, minsize=185, weight=0)
        duel_table.grid_columnconfigure(3, minsize=320, weight=1)

        hdr_specs = [
            (0, "NIVEL DE BLINDAJE", C_TEXT_DIM, "w", "center"),
            (1, "EFECTIVIDAD A", THEME["accent_gold"], "center", "center"),
            (2, "EFECTIVIDAD B", C_BLUE, "center", "center"),
            (3, "VEREDICTO TÁCTICO DE COMBATE", C_TEXT, "w", "w"),
        ]
        for col_i, h_txt, h_col, h_anchor, _ in hdr_specs:
            h_cell = ctk.CTkFrame(duel_table, fg_color="#181F2C", corner_radius=0, height=34)
            h_cell.grid(row=0, column=col_i, padx=(0, 1 if col_i < 3 else 0), pady=(0, 1), sticky="nsew")
            h_cell.grid_propagate(False)
            h_cell.grid_columnconfigure(0, weight=1)
            h_cell.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(
                h_cell,
                text=h_txt,
                font=ui_font(11, "bold"),
                text_color=h_col,
                anchor=h_anchor
            ).grid(row=0, column=0, padx=12, pady=4, sticky="ew" if h_anchor == "w" else "")

        armor_class_names = {
            1: "Clase 1 (Tela / Zhuk-3)",
            2: "Clase 2 (PACA / 3M)",
            3: "Clase 3 (Kirasa / UNTAR)",
            4: "Clase 4 (Trooper / CPC / M2)",
            5: "Clase 5 (Korund / Gzhel / Gen4)",
            6: "Clase 6 (Zabralo / Slick / T7)"
        }

        pen_a = float(ammo_a.get("penetration_power", 0))
        pen_b = float(ammo_b.get("penetration_power", 0))
        dmg_a, dmg_b = int(ammo_a.get("damage", 0)), int(ammo_b.get("damage", 0))
        admg_a, admg_b = int(ammo_a.get("armor_damage", 0)), int(ammo_b.get("armor_damage", 0))

        for ac in range(1, 7):
            eff_a = calculate_armor_effectiveness(pen_a, ac)
            eff_b = calculate_armor_effectiveness(pen_b, ac)
            sim_a = simulate_shots_to_kill(dmg_a, pen_a, admg_a, ac)
            sim_b = simulate_shots_to_kill(dmg_b, pen_b, admg_b, ac)
            sc_a, sc_b = eff_a["score"], eff_b["score"]
            stk_a, stk_b = sim_a["stk"], sim_b["stk"]

            bg_a, fg_a = CLASS_SCORE_COLORS.get(sc_a, (eff_a["color"], C_BG_INSET))
            bg_b, fg_b = CLASS_SCORE_COLORS.get(sc_b, (eff_b["color"], C_BG_INSET))

            if stk_a < stk_b:
                comment = f"🟢 Ventaja A: Abate en {_fmt_shots(stk_a)} ({sim_a['ttk_ms']} ms) vs {_fmt_shots(stk_b)} ({sim_b['ttk_ms']} ms) de B."
                txt_c = C_GREEN_LIGHT
            elif stk_b < stk_a:
                comment = f"🔵 Ventaja B: Abate en {_fmt_shots(stk_b)} ({sim_b['ttk_ms']} ms) vs {_fmt_shots(stk_a)} ({sim_a['ttk_ms']} ms) de A."
                txt_c = C_BLUE
            elif sc_a > sc_b:
                comment = f"🟢 Ventaja A en 1er impacto ({sim_a['first_shot_pen_pct']}% pen vs {sim_b['first_shot_pen_pct']}%). Ambos abaten en ~{_fmt_shots(stk_a)}."
                txt_c = C_GREEN_LIGHT
            elif sc_b > sc_a:
                comment = f"🔵 Ventaja B en 1er impacto ({sim_b['first_shot_pen_pct']}% pen vs {sim_a['first_shot_pen_pct']}%). Ambos abaten en ~{_fmt_shots(stk_b)}."
                txt_c = C_BLUE
            else:
                comment = f"⚖️ Empate táctico: Ambos abaten al tórax en ~{_fmt_shots(stk_a)} ({sim_a['ttk_ms']} ms a 700 RPM)."
                txt_c = C_TEXT_SOFT

            row_bg = "#121622" if ac % 2 == 0 else "#151B2A"
            pad_bot = 1 if ac < 6 else 0

            c0 = ctk.CTkFrame(duel_table, fg_color=row_bg, corner_radius=0, height=40)
            c0.grid(row=ac, column=0, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            c0.grid_propagate(False)
            c0.grid_columnconfigure(0, weight=1)
            c0.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(c0, text=armor_class_names[ac], font=ui_font(12, "bold"), text_color=C_TEXT, anchor="w").grid(row=0, column=0, padx=12, sticky="ew")

            c1 = ctk.CTkFrame(duel_table, fg_color=row_bg, corner_radius=0, height=40)
            c1.grid(row=ac, column=1, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            c1.grid_propagate(False)
            c1.grid_columnconfigure(0, weight=1)
            c1.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(
                c1,
                text=f"{sc_a}/6  •  {_fmt_shots(stk_a)} ({sim_a['ttk_ms']}ms)",
                font=ui_font(11, "bold"),
                fg_color=bg_a,
                text_color=fg_a,
                corner_radius=5,
                width=164,
                height=26
            ).grid(row=0, column=0)

            c2 = ctk.CTkFrame(duel_table, fg_color=row_bg, corner_radius=0, height=40)
            c2.grid(row=ac, column=2, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            c2.grid_propagate(False)
            c2.grid_columnconfigure(0, weight=1)
            c2.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(
                c2,
                text=f"{sc_b}/6  •  {_fmt_shots(stk_b)} ({sim_b['ttk_ms']}ms)",
                font=ui_font(11, "bold"),
                fg_color=bg_b,
                text_color=fg_b,
                corner_radius=5,
                width=164,
                height=26
            ).grid(row=0, column=0)

            c3 = ctk.CTkFrame(duel_table, fg_color=row_bg, corner_radius=0, height=40)
            c3.grid(row=ac, column=3, padx=0, pady=(0, pad_bot), sticky="nsew")
            c3.grid_propagate(False)
            c3.grid_columnconfigure(0, weight=1)
            c3.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(c3, text=comment, font=ui_font(12), text_color=txt_c, anchor="w").grid(row=0, column=0, padx=12, sticky="ew")

        # --- Simulador contra Bosses Icónicos ---
        boss_box = ctk.CTkFrame(self.duel_scroll, fg_color="#10141D", corner_radius=8, border_width=1, border_color="#2B3548")
        boss_box.grid(row=2, column=0, columnspan=2, padx=8, pady=(4, 10), sticky="ew")
        boss_box.grid_columnconfigure(0, weight=1)

        boss_table = ctk.CTkFrame(boss_box, fg_color="#232B3D", corner_radius=6)
        boss_table.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        boss_table.grid_columnconfigure(0, minsize=215, weight=0)
        boss_table.grid_columnconfigure(1, minsize=185, weight=0)
        boss_table.grid_columnconfigure(2, minsize=185, weight=0)
        boss_table.grid_columnconfigure(3, minsize=320, weight=1)

        boss_hdrs = [
            (0, "💀 SIMULADOR CONTRA BOSSES", C_AMBER, "w"),
            (1, "IMPACTO PROYECTIL A", THEME["accent_gold"], "center"),
            (2, "IMPACTO PROYECTIL B", C_BLUE, "center"),
            (3, "ANÁLISIS LETALIDAD BOSS", C_TEXT, "w"),
        ]
        for col_i, h_txt, h_col, h_anchor in boss_hdrs:
            h_cell = ctk.CTkFrame(boss_table, fg_color="#1A1625", corner_radius=0, height=34)
            h_cell.grid(row=0, column=col_i, padx=(0, 1 if col_i < 3 else 0), pady=(0, 1), sticky="nsew")
            h_cell.grid_propagate(False)
            h_cell.grid_columnconfigure(0, weight=1)
            h_cell.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(
                h_cell,
                text=h_txt,
                font=ui_font(11, "bold"),
                text_color=h_col,
                anchor=h_anchor
            ).grid(row=0, column=0, padx=12, pady=4, sticky="ew" if h_anchor == "w" else "")

        boss_sim_a = simulate_boss_targets(dmg_a, pen_a, admg_a)
        boss_sim_b = simulate_boss_targets(dmg_b, pen_b, admg_b)
        total_bosses = len(boss_sim_a)
        for idx, (ba, bb) in enumerate(zip(boss_sim_a, boss_sim_b), start=1):
            row_bg = "#121622" if idx % 2 == 0 else "#151B2A"
            pad_bot = 1 if idx < total_bosses else 0

            b0 = ctk.CTkFrame(boss_table, fg_color=row_bg, corner_radius=0, height=36)
            b0.grid(row=idx, column=0, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            b0.grid_propagate(False)
            b0.grid_columnconfigure(0, weight=1)
            b0.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(b0, text=ba["target"], font=ui_font(12, "bold"), text_color=C_TEXT, anchor="w").grid(row=0, column=0, padx=12, sticky="ew")

            b1 = ctk.CTkFrame(boss_table, fg_color=row_bg, corner_radius=0, height=36)
            b1.grid(row=idx, column=1, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            b1.grid_propagate(False)
            b1.grid_columnconfigure(0, weight=1)
            b1.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(b1, text=f"{_fmt_shots(ba['stk'])} ({ba['pen_pct']}% pen)", font=ui_font(12, "bold"), text_color=C_GREEN_LIGHT if ba["stk"] <= bb["stk"] else C_TEXT_MUTED).grid(row=0, column=0)

            b2 = ctk.CTkFrame(boss_table, fg_color=row_bg, corner_radius=0, height=36)
            b2.grid(row=idx, column=2, padx=(0, 1), pady=(0, pad_bot), sticky="nsew")
            b2.grid_propagate(False)
            b2.grid_columnconfigure(0, weight=1)
            b2.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(b2, text=f"{_fmt_shots(bb['stk'])} ({bb['pen_pct']}% pen)", font=ui_font(12, "bold"), text_color=C_BLUE if bb["stk"] <= ba["stk"] else C_TEXT_MUTED).grid(row=0, column=0)

            b3 = ctk.CTkFrame(boss_table, fg_color=row_bg, corner_radius=0, height=36)
            b3.grid(row=idx, column=3, padx=0, pady=(0, pad_bot), sticky="nsew")
            b3.grid_propagate(False)
            b3.grid_columnconfigure(0, weight=1)
            b3.grid_rowconfigure(0, weight=1)
            ctk.CTkLabel(b3, text=f"A: {ba['verdict']}  |  B: {bb['verdict']}", font=ui_font(11), text_color=C_TEXT_DIM, anchor="w").grid(row=0, column=0, padx=12, sticky="ew")

        pen_winner = ammo_a["name"] if pen_a >= pen_b else ammo_b["name"]
        dmg_winner = ammo_a["name"] if dmg_a >= dmg_b else ammo_b["name"]

        banner = ctk.CTkFrame(self.duel_scroll, fg_color=C_BG_PANEL_ALT, corner_radius=8, border_width=1, border_color=THEME["accent_gold"])
        banner.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(banner, text="🏆 VEREDICTO FINAL DE ELECCIÓN TÁCTICA", font=ui_font(14, "bold"), text_color=THEME["accent_gold"]).pack(anchor="w", padx=16, pady=(10, 4))
        verdict_txt = (
            f"• Perforación Anti-Armadura: {pen_winner} (Pen {max(pen_a, pen_b):.1f} vs {min(pen_a, pen_b):.1f})\n"
            f"• Daño Destructivo a Carne: {dmg_winner} (Daño {max(dmg_a, dmg_b)} HP vs {min(dmg_a, dmg_b)} HP)"
        )
        ctk.CTkLabel(banner, text=verdict_txt, font=ui_font(13), text_color=C_TEXT, justify="left").pack(anchor="w", padx=16, pady=(0, 12))

    def _build_bullet_stat_card(self, parent, ammo: Dict[str, Any], other: Dict[str, Any], is_a: bool) -> ctk.CTkFrame:
        card = ctk.CTkFrame(parent, fg_color=C_BG_PANEL_ALT, corner_radius=8, border_width=1, border_color=THEME["accent_gold"] if is_a else C_BLUE)
        card.grid_columnconfigure(1, weight=1)

        accent_c = THEME["accent_gold"] if is_a else C_BLUE
        tag_t = "PROYECTIL A" if is_a else "PROYECTIL B"

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=2, padx=14, pady=(12, 6), sticky="ew")

        ctk.CTkLabel(hdr, text=tag_t, font=ui_font(11, "bold"), fg_color=accent_c, text_color=C_BG_DARKEST, corner_radius=3, width=95, height=22).pack(side="left")
        ctk.CTkLabel(hdr, text=f"  {format_caliber_short(ammo.get('caliber', ''))}", font=ui_font(12, "bold"), text_color=C_TEXT_DIM).pack(side="left")

        ctk.CTkLabel(card, text=ammo.get("name", ""), font=ui_font(15, "bold"), text_color=C_WHITE).grid(row=1, column=0, columnspan=2, padx=14, pady=(0, 10), sticky="w")

        dmg, dmg_o = int(ammo.get("damage", 0)), int(other.get("damage", 0))
        pen, pen_o = float(ammo.get("penetration_power", 0)), float(other.get("penetration_power", 0))
        arm, arm_o = int(ammo.get("armor_damage", 0)), int(other.get("armor_damage", 0))
        spd, spd_o = int(ammo.get("initial_speed", 0)), int(other.get("initial_speed", 0))

        leg_shots = calculate_leg_meta_shots(dmg)
        leg_shots_o = calculate_leg_meta_shots(dmg_o)
        stk_c4 = simulate_shots_to_kill(dmg, pen, arm, 4)["stk"]
        stk_c4_o = simulate_shots_to_kill(dmg_o, pen_o, arm_o, 4)["stk"]
        stk_c5 = simulate_shots_to_kill(dmg, pen, arm, 5)["stk"]
        stk_c5_o = simulate_shots_to_kill(dmg_o, pen_o, arm_o, 5)["stk"]

        stats_data = [
            ("Daño a Carne:", f"{dmg} HP", dmg >= dmg_o),
            ("Poder de Penetración:", f"{pen:.1f}", pen >= pen_o),
            ("Daño a Blindaje:", f"{arm}%", arm >= arm_o),
            ("Velocidad Inicial:", f"{spd} m/s", spd >= spd_o),
            ("STK Tórax Clase 4 (85 HP):", f"{stk_c4} tiros", stk_c4 <= stk_c4_o),
            ("STK Tórax Clase 5 (85 HP):", f"{stk_c5} tiros", stk_c5 <= stk_c5_o),
            ("Leg Meta (Piernas 440 HP):", f"{leg_shots} tiros", leg_shots <= leg_shots_o),
        ]

        for s_idx, (lbl, val, is_better) in enumerate(stats_data, start=2):
            ctk.CTkLabel(card, text=lbl, font=ui_font(12), text_color=C_TEXT_DIM).grid(row=s_idx, column=0, padx=14, pady=3, sticky="w")
            badge_fg = C_GREEN if is_better else C_TEXT_MUTED
            win_tag = " ▲" if is_better else ""
            ctk.CTkLabel(card, text=f"{val}{win_tag}", font=ui_font(13, "bold"), text_color=badge_fg).grid(row=s_idx, column=1, padx=14, pady=3, sticky="e")

        ctk.CTkLabel(card, text="", height=4).grid(row=10, column=0)
        return card
