"""
TarkovScope - Pestaña de Bosses (Jefes de Incursión) Zero-Lag
Diseño táctico con avatares (incluyendo Glukhar, Cultistas, Wedge, Goons, Partisan, Zryachiy),
probabilidades exactas sincronizadas con https://eftboss.com/pve (selector PvE / PvP en tiempo real),
reutilización de widgets en caliente (<8 ms al cambiar de Boss), plano 2D con zonas de spawn
numeradas superpuestas y visor interactivo HD (Zoom/Pan).
"""
import threading
import customtkinter as ctk
from typing import Dict, Any, List
from core.config import THEME
from ui.theme import ui_font
from core.bosses_data import (
    get_all_bosses,
    get_boss_map_spawn_chance,
    sync_live_boss_spawns_from_eftboss,
)
from ui.image_utils import get_boss_ctk_image, get_boss_spawn_map_ctk_image, clear_image_ram_cache
from ui.map_viewer_modal import open_boss_map_viewer_modal
from ui.theme import C_WHITE


class TabBosses(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.bosses = get_all_bosses()
        self.game_mode: str = "pve"  # Por defecto Modo PvE (https://eftboss.com/pve)
        self.selected_boss: Dict[str, Any] = self.bosses[0]
        self.selected_map: str = self.selected_boss["maps"][0]
        self.boss_buttons: Dict[str, ctk.CTkButton] = {}
        self.map_selector_buttons: Dict[str, ctk.CTkButton] = {}

        self.grid_columnconfigure(0, weight=0)  # Sidebar lista de bosses
        self.grid_columnconfigure(1, weight=1)  # Panel principal de detalle
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_detail_skeleton()
        self._select_boss(self.bosses[0])

        # Sincronización silenciosa en segundo plano con eftboss.com/pve al iniciar
        self.after(1200, self._trigger_live_sync_background)

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(
            self,
            width=305,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        sidebar.grid(row=0, column=0, padx=(0, 12), pady=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(3, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            sidebar,
            text="💀 JEFES & CULTISTAS",
            font=ui_font(size=17, weight="bold"),
            text_color=THEME["accent_orange"]
        )
        title_lbl.grid(row=0, column=0, padx=16, pady=(14, 6), sticky="w")

        # Selector de Modo PvE / PvP sincronizado con eftboss.com
        mode_row = ctk.CTkFrame(sidebar, fg_color=THEME["bg_dark"], corner_radius=8)
        mode_row.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="ew")
        mode_row.grid_columnconfigure((0, 1), weight=1)

        self.btn_mode_pve = ctk.CTkButton(
            mode_row,
            text="🎯 Modo PvE",
            height=30,
            corner_radius=6,
            font=ui_font(size=12, weight="bold"),
            fg_color=THEME["accent_orange"],
            text_color=C_WHITE,
            hover_color="#D97706",
            command=lambda: self._set_game_mode("pve")
        )
        self.btn_mode_pve.grid(row=0, column=0, padx=(4, 2), pady=4, sticky="ew")

        self.btn_mode_pvp = ctk.CTkButton(
            mode_row,
            text="⚔️ Modo PvP",
            height=30,
            corner_radius=6,
            font=ui_font(size=12, weight="bold"),
            fg_color="transparent",
            text_color=THEME["text_muted"],
            hover_color=THEME["bg_card_hover"],
            command=lambda: self._set_game_mode("pvp")
        )
        self.btn_mode_pvp.grid(row=0, column=1, padx=(2, 4), pady=4, sticky="ew")

        self.sync_btn = ctk.CTkButton(
            sidebar,
            text="🔄 Spawns en Vivo: eftboss.com/pve",
            height=26,
            corner_radius=6,
            font=ui_font(size=11, weight="bold"),
            fg_color=THEME["bg_dark"],
            text_color=THEME["accent_green"],
            hover_color=THEME["bg_card_hover"],
            border_width=1,
            border_color=THEME["border"],
            command=self._trigger_live_sync_background
        )
        self.sync_btn.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

        scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        scroll.grid(row=3, column=0, padx=6, pady=(0, 10), sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        for idx, boss in enumerate(self.bosses):
            b_id = boss["id"]
            avatar_img = get_boss_ctk_image(b_id, size=(42, 42))

            btn = ctk.CTkButton(
                scroll,
                text=self._format_sidebar_boss_text(boss),
                image=avatar_img,
                compound="left",
                anchor="w",
                height=52,
                corner_radius=8,
                font=ui_font(size=13, weight="bold"),
                fg_color="transparent",
                text_color=THEME["text_main"],
                hover_color=THEME["bg_card_hover"],
                command=lambda b=boss: self._select_boss(b)
            )
            btn.grid(row=idx, column=0, padx=4, pady=3, sticky="ew")
            self.boss_buttons[b_id] = btn

    def _format_sidebar_boss_text(self, boss: Dict[str, Any]) -> str:
        short_name = boss["name"].split(" (")[0]
        rate = boss.get("pve_chance" if self.game_mode == "pve" else "pvp_chance") or ""
        if rate:
            return f"  {short_name}  •  {rate}"
        return f"  {short_name}"

    def _set_game_mode(self, mode: str):
        if mode == self.game_mode:
            return
        self.game_mode = mode
        is_pve = (mode == "pve")
        self.btn_mode_pve.configure(
            fg_color=THEME["accent_orange"] if is_pve else "transparent",
            text_color=C_WHITE if is_pve else THEME["text_muted"]
        )
        self.btn_mode_pvp.configure(
            fg_color=THEME["accent_blue"] if not is_pve else "transparent",
            text_color=C_WHITE if not is_pve else THEME["text_muted"]
        )
        for b in self.bosses:
            btn = self.boss_buttons.get(b["id"])
            if btn:
                btn.configure(text=self._format_sidebar_boss_text(b))
        self._render_boss_details()

    def _trigger_live_sync_background(self):
        if not self.winfo_exists():
            return
        self.sync_btn.configure(text="⏳ Sincronizando con eftboss.com...", text_color=THEME["accent_yellow"])

        def worker():
            ok, _msg = sync_live_boss_spawns_from_eftboss()

            def on_done():
                if not self.winfo_exists():
                    return
                if ok:
                    self.sync_btn.configure(
                        text=f"🟢 Sincronizado en Vivo (eftboss.com/{self.game_mode})",
                        text_color=THEME["accent_green"]
                    )
                    for b in self.bosses:
                        btn = self.boss_buttons.get(b["id"])
                        if btn:
                            btn.configure(text=self._format_sidebar_boss_text(b))
                    self._render_boss_details()
                else:
                    self.sync_btn.configure(
                        text="🟢 Datos Oficiales eftboss.com/pve Activos",
                        text_color=THEME["accent_green"]
                    )

            try:
                self.after(0, on_done)
            except RuntimeError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _build_detail_skeleton(self):
        """Construye la estructura fija del panel de detalle una sola vez para cambios en <8 ms."""
        self.detail_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        self.detail_scroll.grid(row=0, column=1, sticky="nsew")
        self.detail_scroll.grid_columnconfigure(0, weight=1)
        self.detail_scroll.grid_columnconfigure(1, weight=1)

        # 1. Header con Retrato Grande y Estadísticas Vitales (Reutilizado in-place)
        header = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"]
        )
        header.grid(row=0, column=0, columnspan=2, padx=16, pady=(16, 12), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        self.portrait_lbl = ctk.CTkLabel(header, text="")
        self.portrait_lbl.grid(row=0, column=0, rowspan=2, padx=18, pady=16)

        info_box = ctk.CTkFrame(header, fg_color="transparent")
        info_box.grid(row=0, column=1, padx=(4, 16), pady=(16, 4), sticky="nw")

        self.boss_title_lbl = ctk.CTkLabel(
            info_box,
            text="",
            font=ui_font(size=23, weight="bold"),
            text_color=THEME["accent_orange"]
        )
        self.boss_title_lbl.pack(anchor="w")

        self.boss_meta_lbl = ctk.CTkLabel(
            info_box,
            text="",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["text_muted"],
            justify="left"
        )
        self.boss_meta_lbl.pack(anchor="w", pady=(6, 0))

        hp_badge = ctk.CTkFrame(
            header,
            fg_color=THEME["bg_card"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["accent_red"]
        )
        hp_badge.grid(row=0, column=2, rowspan=2, padx=18, pady=16, sticky="e")

        ctk.CTkLabel(
            hp_badge,
            text="❤️ SALUD TOTAL",
            font=ui_font(size=12, weight="bold"),
            text_color=THEME["text_muted"]
        ).pack(padx=18, pady=(10, 0))

        self.total_hp_lbl = ctk.CTkLabel(
            hp_badge,
            text="",
            font=ui_font(size=25, weight="bold"),
            text_color=THEME["accent_red"]
        )
        self.total_hp_lbl.pack(padx=18, pady=(2, 10))

        # 2. Desglose de Salud por Zona Corporal
        hp_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        hp_frame.grid(row=1, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(
            hp_frame,
            text="🛡️ DESGLOSE DE SALUD POR ZONA CORPORAL",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["accent_yellow"]
        ).pack(anchor="w", padx=16, pady=(12, 6))

        self.parts_row = ctk.CTkFrame(hp_frame, fg_color="transparent")
        self.parts_row.pack(fill="x", padx=12, pady=(0, 12))

        # 3. Sección de Mapa de Spawns
        spawns_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        spawns_frame.grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 12), sticky="ew")
        spawns_frame.grid_columnconfigure(0, weight=1)

        top_spawn_bar = ctk.CTkFrame(spawns_frame, fg_color="transparent")
        top_spawn_bar.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="ew")
        top_spawn_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top_spawn_bar,
            text="🗺️ RADAR DE APARICIÓN (SPAWNS EN EL MAPA — EFTBOSS.COM)",
            font=ui_font(size=16, weight="bold"),
            text_color=THEME["accent_orange"]
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            top_spawn_bar,
            text="🔍 Abrir Mapa de Spawns en HD (Zoom / Pan)",
            height=34,
            fg_color=THEME["accent_blue"],
            hover_color="#2563EB",
            font=ui_font(size=13, weight="bold"),
            command=lambda: open_boss_map_viewer_modal(self, self.selected_boss, self.selected_map)
        ).grid(row=0, column=1, sticky="e")

        self.map_tabs_bar = ctk.CTkFrame(spawns_frame, fg_color="transparent")
        self.map_tabs_bar.grid(row=1, column=0, padx=16, pady=(0, 8), sticky="w")

        self.spawn_map_container = ctk.CTkFrame(
            spawns_frame,
            fg_color=THEME["bg_card"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        self.spawn_map_container.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="ew")
        self.spawn_map_container.grid_columnconfigure(0, weight=1)

        self.spawn_legend_box = ctk.CTkFrame(self.spawn_map_container, fg_color="transparent")
        self.spawn_legend_box.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")

        self.map_img_lbl = ctk.CTkLabel(self.spawn_map_container, text="", cursor="hand2")
        self.map_img_lbl.grid(row=1, column=0, padx=12, pady=(4, 12))
        self.map_img_lbl.bind("<Button-1>", lambda e: open_boss_map_viewer_modal(self, self.selected_boss, self.selected_map))

        # 4. Guardias y Armamento (Izquierda) + Botín Notable (Derecha)
        gear_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        gear_frame.grid(row=3, column=0, padx=(16, 8), pady=(0, 12), sticky="nsew")

        ctk.CTkLabel(
            gear_frame,
            text="🔫 ARMAMENTO & ESCOLTA TÁCTICA",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_orange"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.followers_lbl = ctk.CTkLabel(
            gear_frame,
            text="",
            font=ui_font(size=13),
            text_color=THEME["text_main"],
            justify="left",
            wraplength=420
        )
        self.followers_lbl.pack(anchor="w", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            gear_frame,
            text="Armas Principales del Jefe:",
            font=ui_font(size=13, weight="bold"),
            text_color=THEME["accent_yellow"]
        ).pack(anchor="w", padx=16, pady=(4, 4))

        self.weapons_lbl = ctk.CTkLabel(
            gear_frame,
            text="",
            font=ui_font(size=13),
            text_color=THEME["text_main"],
            justify="left",
            wraplength=420
        )
        self.weapons_lbl.pack(anchor="w", padx=16, pady=(0, 12))

        loot_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        loot_frame.grid(row=3, column=1, padx=(8, 16), pady=(0, 12), sticky="nsew")

        ctk.CTkLabel(
            loot_frame,
            text="💎 BOTÍN EXCLUSIVO (NOTABLE LOOT)",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_green"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.loot_lbl = ctk.CTkLabel(
            loot_frame,
            text="",
            font=ui_font(size=14, weight="bold"),
            text_color=THEME["text_main"],
            justify="left",
            wraplength=420
        )
        self.loot_lbl.pack(anchor="w", padx=16, pady=(0, 12))

        # 5. Estrategia y Tácticas
        tactics_frame = ctk.CTkFrame(
            self.detail_scroll,
            fg_color=THEME["bg_dark"],
            corner_radius=8,
            border_width=1,
            border_color=THEME["border"]
        )
        tactics_frame.grid(row=4, column=0, columnspan=2, padx=16, pady=(0, 16), sticky="ew")

        ctk.CTkLabel(
            tactics_frame,
            text="🧠 ESTRATEGIA Y TÁCTICAS PARA DERROTARLO",
            font=ui_font(size=15, weight="bold"),
            text_color=THEME["accent_blue"]
        ).pack(anchor="w", padx=16, pady=(12, 8))

        self.tactics_lbl = ctk.CTkLabel(
            tactics_frame,
            text="",
            font=ui_font(size=14),
            text_color=THEME["text_main"],
            justify="left",
            wraplength=880
        )
        self.tactics_lbl.pack(anchor="w", padx=16, pady=(0, 14))

    def _select_boss(self, boss: Dict[str, Any]):
        self.selected_boss = boss
        self.selected_map = boss["maps"][0] if boss.get("maps") else "Customs"

        for b_id, btn in self.boss_buttons.items():
            if b_id == boss["id"]:
                btn.configure(fg_color=THEME["accent_orange"], text_color=C_WHITE)
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_main"])

        self._render_boss_details()

    def _update_header_meta(self):
        b = self.selected_boss
        m_name = self.selected_map
        pve_rate = get_boss_map_spawn_chance(b, m_name, "pve")
        pvp_rate = get_boss_map_spawn_chance(b, m_name, "pvp")
        active_rate = pve_rate if self.game_mode == "pve" else pvp_rate
        mode_tag = "PvE" if self.game_mode == "pve" else "PvP"
        other_tag = f"PvP: {pvp_rate}" if self.game_mode == "pve" else f"PvE: {pve_rate}"
        self.boss_meta_lbl.configure(
            text=(
                f"📍 Mapa Activo: {m_name}   |   "
                f"🎯 Probabilidad de Spawn ({mode_tag}): {active_rate}   "
                f"[{other_tag}]"
            )
        )

    def _render_boss_details(self):
        b = self.selected_boss

        # Actualizar Header in-place (0 ms)
        img = get_boss_ctk_image(b["id"], size=(108, 108))
        self.portrait_lbl.configure(image=img)
        self.boss_title_lbl.configure(text=f"{b['name']}  [{b['russian_name']}]")
        self._update_header_meta()
        self.total_hp_lbl.configure(text=f"{b['total_hp']} HP")

        # Actualizar tarjetas de salud corporal
        for w in self.parts_row.winfo_children():
            w.destroy()
        for idx, (part_name, hp_val) in enumerate(b["hp_breakdown"].items()):
            self.parts_row.grid_columnconfigure(idx, weight=1)
            p_card = ctk.CTkFrame(
                self.parts_row,
                fg_color=THEME["bg_card"],
                corner_radius=6,
                border_width=1,
                border_color=THEME["border"]
            )
            p_card.grid(row=0, column=idx, padx=5, pady=4, sticky="ew")
            ctk.CTkLabel(
                p_card,
                text=part_name.upper(),
                font=ui_font(size=12, weight="bold"),
                text_color=THEME["text_muted"]
            ).pack(pady=(6, 0))
            ctk.CTkLabel(
                p_card,
                text=f"{hp_val} HP",
                font=ui_font(size=17, weight="bold"),
                text_color=THEME["accent_green"]
            ).pack(pady=(2, 6))

        # Actualizar botones de mapas del Boss con su % de spawn del modo activo
        for w in self.map_tabs_bar.winfo_children():
            w.destroy()
        self.map_selector_buttons.clear()

        mode_label = "PvE" if self.game_mode == "pve" else "PvP"
        for m_name in b.get("maps", []):
            is_active = (m_name == self.selected_map)
            m_chance = get_boss_map_spawn_chance(b, m_name, self.game_mode)
            m_btn = ctk.CTkButton(
                self.map_tabs_bar,
                text=f"📍 {m_name}  •  {m_chance} ({mode_label})",
                height=34,
                corner_radius=6,
                font=ui_font(size=13, weight="bold"),
                fg_color=THEME["accent_orange"] if is_active else THEME["bg_card"],
                text_color=C_WHITE if is_active else THEME["text_main"],
                hover_color=THEME["bg_card_hover"],
                border_width=1,
                border_color=THEME["accent_orange"] if is_active else THEME["border"],
                command=lambda mn=m_name: self._switch_boss_map(mn)
            )
            m_btn.pack(side="left", padx=(0, 8))
            self.map_selector_buttons[m_name] = m_btn

        self._render_active_boss_map()

        # Actualizar Textos de Escolta, Armas, Botín y Tácticas in-place
        fol = b["followers"]
        self.followers_lbl.configure(
            text=f"👥 Guardias ({fol['count']}): {fol['name']}\n• Equipo: {fol['gear']}\n• IA: {fol['behavior']}"
        )
        self.weapons_lbl.configure(text="\n".join(f"  • {w}" for w in b["weapons"]))
        self.loot_lbl.configure(text="\n\n".join(f"  ★ {item}" for item in b["notable_loot"]))
        self.tactics_lbl.configure(
            text="\n\n".join(f"{idx}. {tip}" for idx, tip in enumerate(b["tactics"], 1))
        )

    def _switch_boss_map(self, map_name: str):
        self.selected_map = map_name
        for mn, btn in self.map_selector_buttons.items():
            is_act = (mn == map_name)
            btn.configure(
                fg_color=THEME["accent_orange"] if is_act else THEME["bg_card"],
                text_color=C_WHITE if is_act else THEME["text_main"],
                border_color=THEME["accent_orange"] if is_act else THEME["border"]
            )
        self._update_header_meta()
        self._render_active_boss_map()

    def _render_active_boss_map(self):
        for w in self.spawn_legend_box.winfo_children():
            w.destroy()

        b = self.selected_boss
        m_name = self.selected_map
        zones: List[Dict[str, Any]] = b.get("map_spawns", {}).get(m_name, [])

        for idx, z in enumerate(zones, start=1):
            row_f = ctk.CTkFrame(self.spawn_legend_box, fg_color=THEME["bg_dark"], corner_radius=6)
            row_f.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row_f,
                text=f" #{idx} ",
                font=ui_font(size=13, weight="bold"),
                fg_color=THEME["accent_orange"],
                text_color=C_WHITE,
                corner_radius=4
            ).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(
                row_f,
                text=f"{z['zone']}:",
                font=ui_font(size=14, weight="bold"),
                text_color=THEME["accent_yellow"]
            ).pack(side="left", padx=(2, 6), pady=6)
            ctk.CTkLabel(
                row_f,
                text=z["details"],
                font=ui_font(size=13),
                text_color=THEME["text_main"]
            ).pack(side="left", padx=2, pady=6)

        def update_img(new_ctk):
            if self.map_img_lbl.winfo_exists():
                self.after(0, lambda: self.map_img_lbl.configure(image=new_ctk))

        ctk_map = get_boss_spawn_map_ctk_image(b, m_name, target_size=(740, 450), widget_callback=update_img)
        self.map_img_lbl.configure(image=ctk_map)
