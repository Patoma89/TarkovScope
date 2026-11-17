"""
TarkovScope - Centro de Mando (Quick Dashboard Moderno)
Vista operativa de inicio estilo Bento Grid con:
  1) 4 tarjetas KPI con barras de progreso en vivo (Quests, Kappa, Hideout, Logros/Prestigio).
  2) Próximas misiones desbloqueadas para tildar en 1 clic.
  3) Ítems pendientes de Collector (Kappa) con miniatura oficial PNG y botón +1 Alijo.
  4) Reloj dual de Tarkov en vivo con detector de ventana nocturna/Cultists + accesos rápidos 1-clic.
"""
from typing import Any, Callable, Dict, List, Optional
import customtkinter as ctk

from core.config import THEME
from core.datastore import get_datastore
from core.i18n import t_ui
from core.pmc_prestige_achievements_data import ACHIEVEMENTS_CATALOG
from core.tarkov_time import get_tarkov_raid_times
from core.user_data import get_prestige_level, get_unlocked_achievement_ids
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from ui.image_utils import get_gear_ctk_icon
from ui.theme import (
    C_AMBER,
    C_BG_DARKEST,
    C_BG_DEEP,
    C_BG_PANEL,
    C_BG_ROW,
    C_BG_ROW_ALT,
    C_BLUE,
    C_BORDER,
    C_BORDER_ALT,
    C_BORDER_SOFT,
    C_EMERALD,
    C_GREEN,
    C_GREEN_LIGHT,
    C_RED,
    C_SLATE_700,
    C_TEXT,
    C_TEXT_DIM,
    C_TEXT_MUTED,
    C_TEXT_SOFT,
    C_WHITE,
    bind_card_hover,
    ui_font,
)


class TabCommandCenter(ctk.CTkFrame):
    """Dashboard operativo principal ('Centro de Mando') con métricas y acciones rápidas 0-lag."""

    def __init__(
        self,
        master,
        on_navigate: Optional[Callable[[str, str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._on_navigate = on_navigate
        self._clock_job: Optional[str] = None
        self._kpi_widgets: Dict[str, Dict[str, Any]] = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_hero_banner()
        self._build_kpi_row()
        self._build_bento_columns()
        self.reload_data()
        self._schedule_clock_tick()

    def _navigate(self, tab_key: str, sub_view: str = "") -> None:
        if callable(self._on_navigate):
            self._on_navigate(tab_key, sub_view)
            return
        top = self.winfo_toplevel()
        if hasattr(top, "switch_tab"):
            top.switch_tab(tab_key)

    def _notify_hud_refresh(self) -> None:
        top = self.winfo_toplevel()
        if hasattr(top, "refresh_hud_kpis"):
            top.refresh_hud_kpis()

    # ------------------------------------------------------------------
    # Fila 0: Banner Operativo
    # ------------------------------------------------------------------

    def _build_hero_banner(self) -> None:
        hero = ctk.CTkFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=12,
            border_width=1,
            border_color=C_BORDER_SOFT,
        )
        hero.grid(row=0, column=0, padx=0, pady=(0, 10), sticky="ew")
        hero.grid_columnconfigure(0, weight=1)

        left = ctk.CTkFrame(hero, fg_color="transparent")
        left.grid(row=0, column=0, padx=16, pady=12, sticky="ew")

        ctk.CTkLabel(
            left,
            text=t_ui("🏠 CENTRO DE MANDO TÁCTICO", "🏠 TACTICAL COMMAND CENTER"),
            font=ui_font(19, "bold", display=True),
            text_color=THEME["accent_gold"],
            anchor="w",
        ).pack(anchor="w")

        ctk.CTkLabel(
            left,
            text=t_ui(
                "Estado operativo de tu wipe, próximos objetivos listos para completar, ítems Collector pendientes y horario de incursión.",
                "Live wipe overview, ready-to-complete quests, missing Collector items and in-raid Tarkov clock.",
            ),
            font=ui_font(12),
            text_color=C_TEXT_MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        actions = ctk.CTkFrame(hero, fg_color="transparent")
        actions.grid(row=0, column=1, padx=14, pady=12, sticky="e")

        btn_search = ctk.CTkButton(
            actions,
            text=t_ui("🔍 Spotlight (Ctrl+K)", "🔍 Spotlight (Ctrl+K)"),
            height=34,
            width=158,
            corner_radius=8,
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=THEME["accent_gold"],
            text_color=C_TEXT,
            font=ui_font(12, "bold"),
            command=lambda: getattr(self.winfo_toplevel(), "open_global_search", lambda: None)(),
        )
        btn_search.pack(side="left", padx=(0, 8))

        btn_route = ctk.CTkButton(
            actions,
            text=t_ui("🧭 Planear Raid Óptima", "🧭 Plan Optimal Raid"),
            height=34,
            width=168,
            corner_radius=8,
            fg_color=THEME["active_tab_bg"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=C_BLUE,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            command=lambda: self._navigate("progression_planner"),
        )
        btn_route.pack(side="left")

    # ------------------------------------------------------------------
    # Fila 1: 4 Tarjetas KPI con Barras de Progreso
    # ------------------------------------------------------------------

    def _build_kpi_row(self) -> None:
        kpi_grid = ctk.CTkFrame(self, fg_color="transparent")
        kpi_grid.grid(row=1, column=0, padx=0, pady=(0, 10), sticky="ew")
        kpi_grid.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cc_kpi")

        specs = [
            ("quests", t_ui("📜 QUESTS", "📜 QUESTS"), THEME["accent_gold"], "quests", "", t_ui("Ir a Quests ➔", "Open Quests ➔")),
            ("kappa", t_ui("🏆 KAPPA COLLECTOR", "🏆 KAPPA COLLECTOR"), C_EMERALD, "flea", "KAPPA", t_ui("Ver Collector ➔", "Open Collector ➔")),
            ("hideout", t_ui("📦 REFUGIO (HIDEOUT)", "📦 HIDEOUT"), C_BLUE, "flea", "HIDEOUT", t_ui("Abrir Hideout ➔", "Open Hideout ➔")),
            ("pmc", t_ui("⭐ LOGROS & PRESTIGIO", "⭐ ACHIEVEMENTS & PRESTIGE"), THEME["accent_orange"], "pmc_systems", "prestige", t_ui("Sistemas PMC ➔", "PMC Systems ➔")),
        ]

        for col_idx, (key, title, accent, tab_target, sub_target, btn_lbl) in enumerate(specs):
            card = ctk.CTkFrame(
                kpi_grid,
                fg_color=C_BG_PANEL,
                corner_radius=10,
                border_width=1,
                border_color=C_BORDER_SOFT,
            )
            padx = (0, 6) if col_idx == 0 else ((6, 0) if col_idx == 3 else (4, 4))
            card.grid(row=0, column=col_idx, padx=padx, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            bind_card_hover(
                card,
                normal_border=C_BORDER_SOFT,
                hover_border=accent,
                normal_fg=C_BG_PANEL,
                hover_fg=THEME["bg_card_hover"],
            )

            top_row = ctk.CTkFrame(card, fg_color="transparent")
            top_row.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
            top_row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top_row,
                text=title,
                font=ui_font(11, "bold"),
                text_color=C_TEXT_DIM,
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            pct_badge = ctk.CTkLabel(
                top_row,
                text="0%",
                font=ui_font(11, "bold", display=True),
                text_color=accent,
                anchor="e",
            )
            pct_badge.grid(row=0, column=1, sticky="e")

            val_lbl = ctk.CTkLabel(
                card,
                text="0 / 0",
                font=ui_font(20, "bold", display=True),
                text_color=C_TEXT,
                anchor="w",
            )
            val_lbl.grid(row=1, column=0, padx=12, pady=(0, 6), sticky="ew")

            bar = ctk.CTkProgressBar(
                card,
                height=7,
                corner_radius=4,
                fg_color=C_BG_DARKEST,
                progress_color=accent,
            )
            bar.set(0.0)
            bar.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="ew")

            foot_row = ctk.CTkFrame(card, fg_color="transparent")
            foot_row.grid(row=3, column=0, padx=12, pady=(0, 10), sticky="ew")
            foot_row.grid_columnconfigure(0, weight=1)

            sub_lbl = ctk.CTkLabel(
                foot_row,
                text="",
                font=ui_font(11),
                text_color=C_TEXT_MUTED,
                anchor="w",
            )
            sub_lbl.grid(row=0, column=0, sticky="w")

            nav_btn = ctk.CTkButton(
                foot_row,
                text=btn_lbl,
                height=24,
                width=112,
                corner_radius=6,
                fg_color=THEME["btn_surface"],
                hover_color=THEME["btn_hover"],
                border_width=1,
                border_color=C_BORDER,
                text_color=accent,
                font=ui_font(11, "bold"),
                command=lambda tk=tab_target, sv=sub_target: self._navigate(tk, sv),
            )
            nav_btn.grid(row=0, column=1, sticky="e")

            self._kpi_widgets[key] = {
                "value": val_lbl,
                "pct": pct_badge,
                "bar": bar,
                "sub": sub_lbl,
            }

    # ------------------------------------------------------------------
    # Fila 2: Bento Grid 3 Columnas
    # ------------------------------------------------------------------

    def _build_bento_columns(self) -> None:
        bento = ctk.CTkFrame(self, fg_color="transparent")
        bento.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")
        bento.grid_columnconfigure((0, 1, 2), weight=1, uniform="cc_bento")
        bento.grid_rowconfigure(0, weight=1)

        # Columna 0: Próximas Misiones Desbloqueadas
        col_quests = ctk.CTkFrame(
            bento,
            fg_color=C_BG_DEEP,
            corner_radius=12,
            border_width=1,
            border_color=C_BORDER_SOFT,
        )
        col_quests.grid(row=0, column=0, padx=(0, 6), sticky="nsew")
        col_quests.grid_columnconfigure(0, weight=1)
        col_quests.grid_rowconfigure(1, weight=1)

        q_hdr = ctk.CTkFrame(col_quests, fg_color="transparent")
        q_hdr.grid(row=0, column=0, padx=14, pady=(12, 8), sticky="ew")
        q_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            q_hdr,
            text=t_ui("🎯 PRÓXIMAS MISIONES DISPONIBLES", "🎯 NEXT READY QUESTS"),
            font=ui_font(14, "bold", display=True),
            text_color=THEME["accent_gold"],
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            q_hdr,
            text=t_ui("Ver todas ➔", "View all ➔"),
            width=84,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color=C_BG_ROW,
            text_color=C_BLUE,
            font=ui_font(11, "bold"),
            command=lambda: self._navigate("quests"),
        ).grid(row=0, column=1, sticky="e")

        self.quests_list_frame = ctk.CTkScrollableFrame(
            col_quests,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=C_BORDER_SOFT,
            scrollbar_button_hover_color=THEME["accent_gold"],
        )
        self.quests_list_frame.grid(row=1, column=0, padx=8, pady=(0, 10), sticky="nsew")
        self.quests_list_frame.grid_columnconfigure(0, weight=1)

        # Columna 1: Ítems Collector (Kappa) Pendientes
        col_kappa = ctk.CTkFrame(
            bento,
            fg_color=C_BG_DEEP,
            corner_radius=12,
            border_width=1,
            border_color=C_BORDER_SOFT,
        )
        col_kappa.grid(row=0, column=1, padx=4, sticky="nsew")
        col_kappa.grid_columnconfigure(0, weight=1)
        col_kappa.grid_rowconfigure(1, weight=1)

        k_hdr = ctk.CTkFrame(col_kappa, fg_color="transparent")
        k_hdr.grid(row=0, column=0, padx=14, pady=(12, 8), sticky="ew")
        k_hdr.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            k_hdr,
            text=t_ui("🏆 ÍTEMS KAPPA PENDIENTES", "🏆 MISSING KAPPA ITEMS"),
            font=ui_font(14, "bold", display=True),
            text_color=C_EMERALD,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            k_hdr,
            text=t_ui("Ver 44 ítems ➔", "View all 44 ➔"),
            width=96,
            height=24,
            corner_radius=6,
            fg_color="transparent",
            hover_color=C_BG_ROW,
            text_color=C_BLUE,
            font=ui_font(11, "bold"),
            command=lambda: self._navigate("flea", "KAPPA"),
        ).grid(row=0, column=1, sticky="e")

        self.kappa_list_frame = ctk.CTkScrollableFrame(
            col_kappa,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=C_BORDER_SOFT,
            scrollbar_button_hover_color=C_EMERALD,
        )
        self.kappa_list_frame.grid(row=1, column=0, padx=8, pady=(0, 10), sticky="nsew")
        self.kappa_list_frame.grid_columnconfigure(0, weight=1)

        # Columna 2: Reloj In-Raid + Accesos Rápidos 1-Clic
        col_ops = ctk.CTkFrame(
            bento,
            fg_color=C_BG_DEEP,
            corner_radius=12,
            border_width=1,
            border_color=C_BORDER_SOFT,
        )
        col_ops.grid(row=0, column=2, padx=(6, 0), sticky="nsew")
        col_ops.grid_columnconfigure(0, weight=1)
        col_ops.grid_rowconfigure(2, weight=1)

        # Sub-tarjeta de Reloj de Tarkov
        clock_card = ctk.CTkFrame(
            col_ops,
            fg_color=C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=C_BORDER,
        )
        clock_card.grid(row=0, column=0, padx=12, pady=(12, 10), sticky="ew")
        clock_card.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            clock_card,
            text=t_ui("🕒 HORARIO OFICIAL DE INCURSIÓN (7x)", "🕒 OFFICIAL TARKOV RAID CLOCK (7x)"),
            font=ui_font(11, "bold"),
            text_color=C_TEXT_DIM,
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(10, 4), sticky="ew")

        self.lbl_clock_left = ctk.CTkLabel(
            clock_card,
            text="--:--:--",
            font=ui_font(20, "bold", mono=True),
            text_color=THEME["accent_gold"],
        )
        self.lbl_clock_left.grid(row=1, column=0, padx=(12, 4), pady=2, sticky="w")

        self.lbl_clock_right = ctk.CTkLabel(
            clock_card,
            text="--:--:--",
            font=ui_font(20, "bold", mono=True),
            text_color=C_BLUE,
        )
        self.lbl_clock_right.grid(row=1, column=1, padx=(4, 12), pady=2, sticky="e")

        self.lbl_cultists_status = ctk.CTkLabel(
            clock_card,
            text="",
            font=ui_font(11, "bold"),
            fg_color=C_BG_ROW,
            corner_radius=6,
            height=26,
            text_color=C_TEXT_MUTED,
        )
        self.lbl_cultists_status.grid(row=2, column=0, columnspan=2, padx=12, pady=(6, 10), sticky="ew")

        ctk.CTkLabel(
            col_ops,
            text=t_ui("⚡ ACCESOS RÁPIDOS DE INCURSIÓN", "⚡ 1-CLICK TACTICAL SHORTCUTS"),
            font=ui_font(13, "bold", display=True),
            text_color=C_TEXT_SOFT,
            anchor="w",
        ).grid(row=1, column=0, padx=14, pady=(2, 6), sticky="ew")

        shortcuts_wrap = ctk.CTkFrame(col_ops, fg_color="transparent")
        shortcuts_wrap.grid(row=2, column=0, padx=10, pady=(0, 12), sticky="nsew")
        shortcuts_wrap.grid_columnconfigure((0, 1), weight=1, uniform="cc_sc")

        shortcuts = [
            ("🧭", t_ui("Mapas Tácticos", "Tactical Maps"), t_ui("Extracts, spawns & pines", "Extracts, spawns & pins"), "maps", ""),
            ("🎯", t_ui("Balística & Duelo", "Ballistics & Duel"), t_ui("203 balas & placas", "203 rounds & plates"), "ballistics", ""),
            ("🔫", t_ui("Armería & Averías", "Modding & Jams"), t_ui("Workbench 3D & Gunsmith", "Workbench & Gunsmith"), "weapons", ""),
            ("💉", t_ui("Medicina & Comida", "Meds & Provisions"), t_ui("Stims, curas & 45 ítems", "Stims, meds & 45 foods"), "medical", ""),
            ("🧭", t_ui("Ruta Multi-Quest", "Multi-Quest Route"), t_ui("Optimizar próxima raid", "Optimize next raid"), "progression_planner", ""),
            ("💀", t_ui("Bosses & Facciones", "Bosses & AI"), t_ui("Black Div, Rogues & spawns", "Black Div, Rogues & spawns"), "bosses", ""),
        ]

        for idx, (icon_txt, title_txt, desc_txt, t_key, s_key) in enumerate(shortcuts):
            r, c = divmod(idx, 2)
            tile = ctk.CTkFrame(
                shortcuts_wrap,
                fg_color=C_BG_PANEL,
                corner_radius=9,
                border_width=1,
                border_color=C_BORDER_SOFT,
                cursor="hand2",
            )
            tile.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            tile.grid_columnconfigure(0, weight=1)
            shortcuts_wrap.grid_rowconfigure(r, weight=1)
            bind_card_hover(
                tile,
                normal_border=C_BORDER_SOFT,
                hover_border=THEME["accent_gold"],
                normal_fg=C_BG_PANEL,
                hover_fg=THEME["bg_card_hover"],
            )

            lbl1 = ctk.CTkLabel(
                tile,
                text=f"{icon_txt} {title_txt}",
                font=ui_font(12, "bold"),
                text_color=C_TEXT,
                anchor="w",
            )
            lbl1.grid(row=0, column=0, padx=10, pady=(10, 1), sticky="ew")

            lbl2 = ctk.CTkLabel(
                tile,
                text=desc_txt,
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                anchor="w",
            )
            lbl2.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

            for w in (tile, lbl1, lbl2):
                w.bind("<Button-1>", lambda _e, tk=t_key, sv=s_key: self._navigate(tk, sv))

    # ------------------------------------------------------------------
    # Carga de Datos & Renderizado Zero-Lag
    # ------------------------------------------------------------------

    def on_tab_activated(self) -> None:
        self.reload_data()
        self._update_clock_labels()

    def reload_data(self) -> None:
        if not self.winfo_exists():
            return
        ds = get_datastore()
        ds.ensure_loaded()

        # 1. Métricas KPI
        all_quests = ds.get_quests(progression_mode="ALL")
        q_total = len(all_quests)
        q_done = sum(1 for q in all_quests if q.get("is_completed"))
        q_pct = (q_done / q_total) if q_total else 0.0
        q_unlocked_pending = [
            q for q in ds.get_quests(hide_completed=True, progression_mode="CORRELATIVE")
            if not q.get("is_completed")
        ]
        self._set_kpi(
            "quests",
            f"{q_done} / {q_total}",
            f"{int(round(q_pct * 100))}%",
            q_pct,
            t_ui(f"{len(q_unlocked_pending)} desbloqueadas ahora", f"{len(q_unlocked_pending)} unlocked now"),
        )

        k_total = len(KAPPA_COLLECTOR_ITEMS)
        k_missing = [it for it in KAPPA_COLLECTOR_ITEMS if ds.get_stash_count(f"kappa:{it['name']}") < 1]
        k_done = k_total - len(k_missing)
        k_pct = (k_done / k_total) if k_total else 0.0
        self._set_kpi(
            "kappa",
            f"{k_done} / {k_total}",
            f"{int(round(k_pct * 100))}%",
            k_pct,
            t_ui(f"Faltan {len(k_missing)} ítems FiR", f"{len(k_missing)} FiR items left"),
        )

        all_hideout = ds.get_hideout_modules(progression_mode="ALL")
        h_total = len(all_hideout)
        h_done = sum(1 for m in all_hideout if m.get("is_completed"))
        h_pct = (h_done / h_total) if h_total else 0.0
        h_ready = sum(
            1 for m in ds.get_hideout_modules(progression_mode="CORRELATIVE", hide_completed=True)
            if not m.get("is_completed")
        )
        self._set_kpi(
            "hideout",
            f"{h_done} / {h_total}",
            f"{int(round(h_pct * 100))}%",
            h_pct,
            t_ui(f"{h_ready} mejoras listas", f"{h_ready} upgrades ready"),
        )

        a_total = len(ACHIEVEMENTS_CATALOG)
        a_done = len(get_unlocked_achievement_ids())
        a_pct = (a_done / a_total) if a_total else 0.0
        prestige_lvl = get_prestige_level()
        self._set_kpi(
            "pmc",
            f"{a_done} / {a_total}",
            f"P{prestige_lvl}",
            a_pct,
            t_ui(f"Prestigio Nv. {prestige_lvl} / 6", f"Prestige Lv. {prestige_lvl} / 6"),
        )

        # 2. Próximas Misiones (máx 6)
        q_unlocked_pending.sort(
            key=lambda q: (int(q.get("level_req") or 1), 0 if q.get("is_kappa") else 1, str(q.get("title", "")))
        )
        self._render_pending_quests(q_unlocked_pending[:6])

        # 3. Ítems Kappa Pendientes (máx 6)
        self._render_missing_kappa(k_missing[:6])
        self._update_clock_labels()

    def _set_kpi(self, key: str, val_text: str, pct_text: str, ratio: float, sub_text: str) -> None:
        w = self._kpi_widgets.get(key)
        if not w:
            return
        w["value"].configure(text=val_text)
        w["pct"].configure(text=pct_text)
        w["bar"].set(max(0.0, min(1.0, float(ratio))))
        w["sub"].configure(text=sub_text)

    def _clear_children(self, frame: ctk.CTkFrame) -> None:
        for child in frame.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

    def _render_pending_quests(self, quests: List[Dict[str, Any]]) -> None:
        self._clear_children(self.quests_list_frame)
        if not quests:
            ctk.CTkLabel(
                self.quests_list_frame,
                text=t_ui("¡Todas las misiones disponibles están completadas!", "All available quests completed!"),
                font=ui_font(12, "bold"),
                text_color=C_GREEN_LIGHT,
            ).grid(row=0, column=0, pady=24, padx=10)
            return

        for idx, q in enumerate(quests):
            row = ctk.CTkFrame(
                self.quests_list_frame,
                fg_color=C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER_SOFT,
            )
            row.grid(row=idx, column=0, padx=2, pady=3, sticky="ew")
            row.grid_columnconfigure(0, weight=1)
            bind_card_hover(row, normal_border=C_BORDER_SOFT, hover_border=THEME["accent_gold"])

            kappa_tag = " [KAPPA]" if q.get("is_kappa") else ""
            title_lbl = ctk.CTkLabel(
                row,
                text=f"{q.get('title', 'Quest')}{kappa_tag}",
                font=ui_font(12, "bold"),
                text_color=C_TEXT,
                anchor="w",
            )
            title_lbl.grid(row=0, column=0, padx=(10, 6), pady=(7, 0), sticky="ew")

            meta = f"{q.get('trader_name', 'Trader')}  •  Nv.{q.get('level_req', 1)}  •  {q.get('primary_map', 'Any')}"
            ctk.CTkLabel(
                row,
                text=meta,
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                anchor="w",
            ).grid(row=1, column=0, padx=(10, 6), pady=(0, 7), sticky="ew")

            qid = q["id"]
            ctk.CTkButton(
                row,
                text="✓",
                width=32,
                height=30,
                corner_radius=6,
                fg_color=THEME["btn_surface"],
                hover_color=C_EMERALD,
                border_width=1,
                border_color=C_BORDER,
                text_color=C_GREEN_LIGHT,
                font=ui_font(13, "bold"),
                command=lambda q_id=qid: self._complete_quest_quick(q_id),
            ).grid(row=0, column=1, rowspan=2, padx=(4, 8), pady=6)

    def _complete_quest_quick(self, quest_id: int) -> None:
        get_datastore().toggle_quest(quest_id)
        self.reload_data()
        self._notify_hud_refresh()

    def _safe_set_icon(self, lbl: ctk.CTkLabel, img: ctk.CTkImage) -> None:
        if not self.winfo_exists():
            return
        try:
            self.after(0, lambda: lbl.winfo_exists() and lbl.configure(image=img))
        except Exception:
            pass

    def _render_missing_kappa(self, items: List[Dict[str, str]]) -> None:
        self._clear_children(self.kappa_list_frame)
        if not items:
            ctk.CTkLabel(
                self.kappa_list_frame,
                text=t_ui("🏆 ¡Todos los ítems de Collector en tu alijo!", "🏆 All 44 Collector items secured!"),
                font=ui_font(12, "bold"),
                text_color=C_GREEN_LIGHT,
            ).grid(row=0, column=0, pady=24, padx=10)
            return

        for idx, it in enumerate(items):
            row = ctk.CTkFrame(
                self.kappa_list_frame,
                fg_color=C_BG_PANEL,
                corner_radius=8,
                border_width=1,
                border_color=C_BORDER_SOFT,
            )
            row.grid(row=idx, column=0, padx=2, pady=3, sticky="ew")
            row.grid_columnconfigure(1, weight=1)
            bind_card_hover(row, normal_border=C_BORDER_SOFT, hover_border=C_EMERALD)

            icon_lbl = ctk.CTkLabel(row, text="", width=38, height=38, fg_color=C_BG_DARKEST, corner_radius=6)
            icon_lbl.grid(row=0, column=0, rowspan=2, padx=(8, 8), pady=6)
            ctk_img = get_gear_ctk_icon(
                it.get("icon_key", ""),
                it.get("icon_url", ""),
                max_size=(34, 34),
                on_ready=lambda im, lbl=icon_lbl: self._safe_set_icon(lbl, im),
            )
            if ctk_img is not None:
                icon_lbl.configure(image=ctk_img)

            ctk.CTkLabel(
                row,
                text=it["name"],
                font=ui_font(12, "bold"),
                text_color=C_TEXT,
                anchor="w",
            ).grid(row=0, column=1, padx=(0, 6), pady=(7, 0), sticky="ew")

            spot = it.get("boss_or_spot", "")
            if len(spot) > 42:
                spot = spot[:40] + "…"
            ctk.CTkLabel(
                row,
                text=spot,
                font=ui_font(10),
                text_color=C_TEXT_DIM,
                anchor="w",
            ).grid(row=1, column=1, padx=(0, 6), pady=(0, 7), sticky="ew")

            item_name = it["name"]
            ctk.CTkButton(
                row,
                text=t_ui("+1 Alijo", "+1 Stash"),
                width=68,
                height=28,
                corner_radius=6,
                fg_color=THEME["btn_surface"],
                hover_color=C_EMERALD,
                border_width=1,
                border_color=C_BORDER,
                text_color=C_GREEN_LIGHT,
                font=ui_font(11, "bold"),
                command=lambda nm=item_name: self._add_kappa_item_quick(nm),
            ).grid(row=0, column=2, rowspan=2, padx=(4, 8), pady=6)

    def _add_kappa_item_quick(self, item_name: str) -> None:
        get_datastore().set_stash_count(f"kappa:{item_name}", 1)
        self.reload_data()
        self._notify_hud_refresh()

    # ------------------------------------------------------------------
    # Reloj de Tarkov en Vivo
    # ------------------------------------------------------------------

    def _update_clock_labels(self) -> None:
        if not self.winfo_exists():
            return
        t = get_tarkov_raid_times()
        l_icon = "🌙" if t["left_is_night"] else "🔆"
        r_icon = "🌙" if t["right_is_night"] else "🔆"
        self.lbl_clock_left.configure(text=f"{l_icon} {t['left_time']}")
        self.lbl_clock_right.configure(text=f"{r_icon} {t['right_time']}")

        if t["cultists_window_active"]:
            night_slots = []
            if t["left_is_night"]:
                night_slots.append(f"IZQ ({t['left_short']})")
            if t["right_is_night"]:
                night_slots.append(f"DER ({t['right_short']})")
            slots_str = " / ".join(night_slots)
            self.lbl_cultists_status.configure(
                text=t_ui(
                    f"🌙 CULTISTS ACTIVOS EN: {slots_str} (22:00-07:00)",
                    f"🌙 CULTISTS WINDOW ACTIVE: {slots_str} (22:00-07:00)",
                ),
                text_color=C_AMBER,
            )
        else:
            self.lbl_cultists_status.configure(
                text=t_ui("🔆 Horario Diurno — Cultists inactivos", "🔆 Daylight Raid — Cultists inactive"),
                text_color=C_TEXT_MUTED,
            )

    def _schedule_clock_tick(self) -> None:
        if not self.winfo_exists():
            return
        if self.winfo_ismapped():
            self._update_clock_labels()
        self._clock_job = self.after(1000, self._schedule_clock_tick)
