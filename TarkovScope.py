"""
====================================================================
TARKOV SCOPE v2.0 - Ultimate Escape from Tarkov Companion & Encyclopedia
Arquitectura Limpia Pro, In-Memory DataStore Zero-Lag, SQLite WAL & UI CustomTkinter
====================================================================
"""
import os
import sys
import json
import threading
import logging
from typing import Dict, Optional
import customtkinter as ctk

# Asegurar importaciones relativas
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.config import APP_NAME, APP_VERSION, THEME, THEME_SKIN_META, BUNDLE_DIR, BASE_DIR
from core.database import init_db, is_db_populated
from core.datastore import get_datastore
from core.i18n import SUPPORTED_LANGS, get_active_lang, set_active_lang, tr
from core.pmc_prestige_achievements_data import ACHIEVEMENTS_CATALOG
from core.sync_service import SyncService
from core.tarkov_time import get_tarkov_raid_times
from core.updater import check_github_release
from core.user_data import (
    get_prestige_level,
    get_unlocked_achievement_ids,
    get_user_preference,
    set_user_preference,
)
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from ui.image_utils import clear_image_ram_cache, prewarm_ui_thumbnails
import ui.theme as theme_mod
from ui.theme import THEME_SETTINGS, ui_font, apply_ui_skin, get_active_skin_id, bind_card_hover
from ui.patch_notes_modal import PatchNotesModal
from ui.update_modal import UpdateDialog
from ui.tab_bosses import TabBosses
from ui.tab_command_center import TabCommandCenter
from ui.tab_weapons import TabWeapons
from ui.tab_ballistics import TabBallistics
from ui.tab_containers import TabContainers
from ui.tab_quests import TabQuests
from ui.tab_quest_tracker import TabQuestTracker
from ui.tab_progression_planner import TabProgressionPlanner
from ui.tab_maps import TabMaps
from ui.tab_flea import TabFlea
from ui.tab_lore import TabLore
from ui.tab_story_quests import TabStoryQuests
from ui.tab_keys import TabKeys
from ui.tab_medical import TabMedical
from ui.tab_pmc_systems import TabPMCSystems
from ui.global_search_modal import GlobalSearchModal
from ui.theme import C_AMBER, C_BADGE_NEW, C_BG_DEEP, C_BG_ROW, C_BORDER, C_BORDER_ALT, C_GREEN, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE

# Pestañas con badge "NEW" auto-descartable al visitarlas por primera vez en esa versión.
NEW_TAB_VERSIONS: Dict[str, str] = {
    "command_center": "1.5.0",
    "pmc_systems": "1.5.0",
    "medical": "1.5.0",
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TarkovScope.Main")


class TarkovScopeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTC (Tactical Tarkov Companion)")
        self.geometry("1420x880")
        self.minsize(1160, 740)
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=THEME["bg_dark"])

        # Registrar AppUserModelID en Windows para ícono individual en barra de tareas
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TTC.TacticalTarkovCompanion")
        except Exception:
            pass

        # Configurar icono nativo de ventana y barra de tareas
        icon_path = os.path.join(BUNDLE_DIR, "ttc.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(BASE_DIR, "ttc.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # Inicializar DB SQLite y precargar el DataStore en memoria RAM (<15 ms)
        init_db()
        if is_db_populated():
            get_datastore().ensure_loaded()

        self._always_on_top: bool = False
        self._sidebar_collapsed: bool = (get_user_preference("sidebar_collapsed", "0") == "1")
        self._clock_after_id: Optional[str] = None
        self._last_hud_kpi_state: Optional[tuple] = None
        self._nav_pills: Dict[str, ctk.CTkFrame] = {}
        self._nav_meta: Dict[str, tuple] = {}

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_area()

        # Atajos globales de búsqueda
        self.bind("<Control-k>", lambda e: self.open_global_search())
        self.bind("<Control-K>", lambda e: self.open_global_search())
        self.bind("<Control-f>", lambda e: self.open_global_search())
        self.bind("<Control-F>", lambda e: self.open_global_search())

        # Lazy Tab Loading & Pipeline de Pre-calentamiento en Idle
        self.tabs: Dict[str, ctk.CTkFrame] = {}
        self._current_tab_key: str = "command_center"
        self._active_nav_key: str = ""
        self._tab_classes = {
            "command_center": TabCommandCenter,
            "bosses": TabBosses,
            "maps": TabMaps,
            "quests": TabQuests,
            "quest_tracker": TabQuestTracker,
            "progression_planner": TabProgressionPlanner,
            "story_quests": TabStoryQuests,
            "weapons": TabWeapons,
            "ballistics": TabBallistics,
            "containers": TabContainers,
            "flea": TabFlea,
            "keys": TabKeys,
            "medical": TabMedical,
            "pmc_systems": TabPMCSystems,
            "lore": TabLore,
        }

        self.switch_tab("command_center")
        self._tick_tarkov_clock()
        self._check_initial_sync()
        self.after(150, self._prewarm_background_caches)

    def _get_nav_groups(self):
        return [
            (
                tr("nav.cat.overview"),
                [("command_center", "🏠", tr("nav.command_center"))],
            ),
            (
                tr("nav.cat.incursion"),
                [
                    ("maps", "🧭", tr("nav.maps")),
                    ("bosses", "💀", tr("nav.bosses")),
                    ("keys", "🔑", tr("nav.keys")),
                ],
            ),
            (
                tr("nav.cat.progression"),
                [
                    ("quests", "📜", tr("nav.quests")),
                    ("quest_tracker", "🎯", tr("nav.quest_tracker")),
                    ("progression_planner", "📈", tr("nav.progression_planner")),
                    ("story_quests", "📕", tr("nav.story_quests")),
                ],
            ),
            (
                tr("nav.cat.combat"),
                [
                    ("weapons", "🔫", tr("nav.weapons")),
                    ("ballistics", "💥", tr("nav.ballistics")),
                ],
            ),
            (
                tr("nav.cat.economy"),
                [
                    ("flea", "📦", tr("nav.flea")),
                    ("containers", "🎒", tr("nav.containers")),
                    ("medical", "💉", tr("nav.medical")),
                    ("pmc_systems", "⭐", tr("nav.pmc_systems")),
                    ("lore", "📖", tr("nav.lore")),
                ],
            ),
        ]

    def _build_sidebar(self):
        """Barra de navegación lateral agrupada, balanceada y con Active Pill luminoso."""
        collapsed = bool(getattr(self, "_sidebar_collapsed", False))
        sb_width = 68 if collapsed else 248

        self.sidebar = ctk.CTkFrame(
            self,
            width=sb_width,
            fg_color=theme_mod.C_BG_DEEP,
            border_width=1,
            border_color=theme_mod.C_BORDER_SOFT,
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(2, weight=1)

        # 1. Bloque de Marca / Título + Toggle Colapsar
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=8 if collapsed else 14, pady=(8, 4), sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)

        brand_row = ctk.CTkFrame(logo_frame, fg_color="transparent")
        brand_row.grid(row=0, column=0, sticky="ew")
        brand_row.grid_columnconfigure(0, weight=1)

        if not collapsed:
            ctk.CTkLabel(
                brand_row,
                text="TTC",
                font=ui_font(20, "bold", display=True),
                text_color=THEME["accent_gold"],
                anchor="w"
            ).grid(row=0, column=0, sticky="w")

        self.btn_collapse_sidebar = ctk.CTkButton(
            brand_row,
            text="»" if collapsed else "«",
            width=28 if not collapsed else 48,
            height=24,
            corner_radius=6,
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=theme_mod.C_BORDER,
            text_color=THEME["accent_gold"],
            font=ui_font(12, "bold"),
            command=self.toggle_sidebar_collapsed,
        )
        self.btn_collapse_sidebar.grid(row=0, column=1 if not collapsed else 0, sticky="e" if not collapsed else "ew")

        if not collapsed:
            ctk.CTkLabel(
                logo_frame,
                text="TACTICAL TARKOV COMPANION",
                font=ui_font(10, "bold"),
                text_color=C_TEXT_DIM,
                anchor="w"
            ).grid(row=1, column=0, pady=(0, 0), sticky="ew")

        # Botón de Modo Ventana Siempre Visible (Always on Top)
        topmost_txt = "📌" if collapsed else (tr("sidebar.topmost_on") if self._always_on_top else tr("sidebar.topmost_off"))
        self.btn_topmost = ctk.CTkButton(
            logo_frame,
            text=topmost_txt,
            font=ui_font(12 if collapsed else 11, "bold"),
            fg_color=THEME["active_tab_bg"] if self._always_on_top else "transparent",
            hover_color=C_BG_ROW,
            border_width=1,
            border_color=THEME["accent_blue"] if self._always_on_top else C_BORDER,
            text_color=C_WHITE if self._always_on_top else C_TEXT_DIM,
            height=24,
            corner_radius=7,
            anchor="center",
            command=self.toggle_always_on_top
        )
        self.btn_topmost.grid(row=2, column=0, pady=(5, 4), sticky="ew")

        self._skin_label_to_id = {v["label"]: k for k, v in THEME_SKIN_META.items()}
        self._lang_label_to_id = {v: k for k, v in SUPPORTED_LANGS.items()}

        if not collapsed:
            # Grid unificado para alinear Skin e Idioma al píxel
            settings_grid = ctk.CTkFrame(logo_frame, fg_color="transparent")
            settings_grid.grid(row=3, column=0, pady=(0, 0), sticky="ew")
            settings_grid.grid_columnconfigure(0, minsize=72, weight=0)
            settings_grid.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                settings_grid,
                text=tr("sidebar.skin"),
                font=ui_font(11, "bold"),
                text_color=theme_mod.C_TEXT_DIM,
                anchor="w"
            ).grid(row=0, column=0, padx=(0, 6), pady=(0, 4), sticky="w")

            active_skin_id = get_active_skin_id()
            active_skin_label = THEME_SKIN_META.get(active_skin_id, {}).get("label", "EFT Hideout")
            self.skin_menu = ctk.CTkOptionMenu(
                settings_grid,
                values=list(self._skin_label_to_id.keys()),
                height=24,
                font=ui_font(11, "bold"),
                fg_color=theme_mod.C_BG_PANEL,
                button_color=theme_mod.C_BORDER,
                button_hover_color=theme_mod.C_BG_ROW_ALT,
                dropdown_fg_color=theme_mod.C_BG_PANEL,
                dropdown_hover_color=theme_mod.C_BG_ROW_ALT,
                text_color=THEME["accent_gold"],
                command=self._on_skin_changed
            )
            self.skin_menu.set(active_skin_label)
            self.skin_menu.grid(row=0, column=1, pady=(0, 4), sticky="ew")

            ctk.CTkLabel(
                settings_grid,
                text=tr("sidebar.lang"),
                font=ui_font(11, "bold"),
                text_color=theme_mod.C_TEXT_DIM,
                anchor="w"
            ).grid(row=1, column=0, padx=(0, 6), sticky="w")

            active_lang_label = SUPPORTED_LANGS.get(get_active_lang(), "Español")
            self.lang_menu = ctk.CTkOptionMenu(
                settings_grid,
                values=list(self._lang_label_to_id.keys()),
                height=24,
                font=ui_font(11, "bold"),
                fg_color=theme_mod.C_BG_PANEL,
                button_color=theme_mod.C_BORDER,
                button_hover_color=theme_mod.C_BG_ROW_ALT,
                dropdown_fg_color=theme_mod.C_BG_PANEL,
                dropdown_hover_color=theme_mod.C_BG_ROW_ALT,
                text_color=THEME["accent_gold"],
                command=self._on_lang_changed
            )
            self.lang_menu.set(active_lang_label)
            self.lang_menu.grid(row=1, column=1, sticky="ew")

        # 2. Separador Superior
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=THEME["border_soft"])
        sep.grid(row=1, column=0, padx=10 if collapsed else 14, pady=(0, 2), sticky="ew")

        # 3. Contenedor de Botones de Navegación Agrupados (Espaciado compacto balanceado)
        nav_container = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color=theme_mod.C_BORDER_SOFT,
            scrollbar_button_hover_color=THEME["accent_gold"],
        )
        nav_container.grid(row=2, column=0, padx=4 if collapsed else 8, pady=0, sticky="nsew")
        nav_container.grid_columnconfigure(0, weight=1)

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        self._nav_pills: Dict[str, ctk.CTkFrame] = {}
        self._nav_meta: Dict[str, tuple] = {}
        self._new_badges: Dict[str, ctk.CTkLabel] = {}
        seen_new_tabs = self._load_seen_new_tabs()

        row_idx = 0
        nav_groups = self._get_nav_groups()
        for grp_i, (cat_title, items) in enumerate(nav_groups):
            if collapsed:
                if grp_i > 0:
                    ctk.CTkFrame(nav_container, height=1, fg_color=THEME["border_soft"]).grid(
                        row=row_idx, column=0, padx=8, pady=3, sticky="ew"
                    )
                    row_idx += 1
            else:
                ctk.CTkLabel(
                    nav_container,
                    text=cat_title,
                    font=ui_font(9, "bold"),
                    text_color=C_TEXT_DIM,
                    anchor="w",
                ).grid(row=row_idx, column=0, padx=(8, 4), pady=(4 if grp_i > 0 else 1, 0), sticky="ew")
                row_idx += 1

            for tab_key, icon_txt, label_text in items:
                self._nav_meta[tab_key] = (cat_title, icon_txt, label_text)
                btn = ctk.CTkButton(
                    nav_container,
                    text=icon_txt if collapsed else f"   {icon_txt}  {label_text}",
                    font=ui_font(16 if collapsed else 12, "normal" if collapsed else "bold"),
                    fg_color="transparent",
                    text_color=C_TEXT_MUTED,
                    hover_color=C_BG_ROW,
                    border_width=1,
                    border_color=C_BG_DEEP,
                    anchor="center" if collapsed else "w",
                    height=30 if collapsed else 24,
                    corner_radius=6,
                    command=lambda k=tab_key: self.switch_tab(k)
                )
                btn.grid(row=row_idx, column=0, padx=2, pady=(0, 1), sticky="ew")
                self.nav_buttons[tab_key] = btn

                pill = ctk.CTkFrame(
                    btn,
                    width=4,
                    height=15,
                    corner_radius=2,
                    fg_color=THEME["accent_gold"],
                )
                self._nav_pills[tab_key] = pill

                target_ver = NEW_TAB_VERSIONS.get(tab_key)
                if not collapsed and target_ver and seen_new_tabs.get(tab_key) != target_ver:
                    badge = ctk.CTkLabel(
                        btn,
                        text="NEW",
                        font=ui_font(10, "bold"),
                        fg_color=C_BADGE_NEW,
                        text_color=C_WHITE,
                        corner_radius=4,
                        width=34,
                        height=16,
                        cursor="hand2",
                    )
                    badge.place(relx=1.0, rely=0.5, x=-8, anchor="e")
                    badge.bind("<Button-1>", lambda _e, k=tab_key: self.switch_tab(k))
                    self._new_badges[tab_key] = badge

                row_idx += 1

        # 4. Pie de Barra Lateral Compacto
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=3, column=0, padx=8 if collapsed else 14, pady=(2, 8), sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)

        sep_bot = ctk.CTkFrame(footer_frame, height=1, fg_color=THEME["border_soft"])
        sep_bot.grid(row=0, column=0, pady=(0, 4), sticky="ew")

        self.db_status_lbl = ctk.CTkLabel(
            footer_frame,
            text="●" if collapsed else tr("sidebar.db_ready"),
            font=ui_font(11, "bold"),
            text_color=C_GREEN,
            anchor="center" if collapsed else "w"
        )
        self.db_status_lbl.grid(row=1, column=0, pady=(0, 4), sticky="ew")

        if not collapsed:
            backup_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
            backup_row.grid(row=2, column=0, pady=(0, 4), sticky="ew")
            backup_row.grid_columnconfigure(0, weight=1)
            backup_row.grid_columnconfigure(1, weight=1)

            self.btn_export = ctk.CTkButton(
                backup_row,
                text=tr("sidebar.export"),
                font=ui_font(11, "bold"),
                fg_color=THEME["btn_surface"],
                hover_color=THEME["btn_hover"],
                border_width=1,
                border_color=THEME["border_alt"],
                text_color=C_TEXT_MUTED,
                height=24,
                corner_radius=6,
                command=self.export_profile
            )
            self.btn_export.grid(row=0, column=0, padx=(0, 3), sticky="ew")

            self.btn_import = ctk.CTkButton(
                backup_row,
                text=tr("sidebar.import"),
                font=ui_font(11, "bold"),
                fg_color=THEME["btn_surface"],
                hover_color=THEME["btn_hover"],
                border_width=1,
                border_color=THEME["border_alt"],
                text_color=C_TEXT_MUTED,
                height=24,
                corner_radius=6,
                command=self.import_profile
            )
            self.btn_import.grid(row=0, column=1, padx=(3, 0), sticky="ew")

        self.sync_btn = ctk.CTkButton(
            footer_frame,
            text="⟳" if collapsed else tr("sidebar.sync"),
            font=ui_font(15 if collapsed else 12, "bold"),
            fg_color=C_BG_ROW,
            hover_color=C_BORDER_ALT,
            border_width=1,
            border_color=THEME["border_alt"],
            text_color=C_TEXT,
            height=28,
            corner_radius=7,
            command=self.start_sync_in_background
        )
        self.sync_btn.grid(row=3, column=0, pady=(0, 4), sticky="ew")

        self.patch_notes_btn = ctk.CTkButton(
            footer_frame,
            text="📋" if collapsed else tr("sidebar.patch_notes"),
            font=ui_font(13 if collapsed else 11, "bold"),
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=THEME["border_alt"],
            text_color=THEME["accent_gold"],
            height=24,
            corner_radius=6,
            command=self.open_patch_notes
        )
        self.patch_notes_btn.grid(row=4, column=0, pady=(0, 4), sticky="ew")

        self.update_btn = ctk.CTkButton(
            footer_frame,
            text="🔄" if collapsed else tr("sidebar.update", ver=APP_VERSION),
            font=ui_font(13 if collapsed else 11, "bold"),
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=THEME["border_alt"],
            text_color=C_TEXT_MUTED,
            height=24,
            corner_radius=6,
            command=self.check_for_app_updates
        )
        self.update_btn.grid(row=5, column=0, sticky="ew")

    def _apply_nav_button_state(self, tab_key: str, active: bool) -> None:
        btn = self.nav_buttons.get(tab_key)
        pill = self._nav_pills.get(tab_key)
        if btn is not None and btn.winfo_exists():
            if active:
                btn.configure(
                    fg_color=THEME["active_tab_bg"],
                    border_color=THEME["accent_gold"],
                    text_color=C_WHITE,
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_color=theme_mod.C_BG_DEEP,
                    text_color=C_TEXT_MUTED,
                )
        if pill is not None and pill.winfo_exists():
            if active:
                pill.configure(fg_color=THEME["accent_gold"])
                pill.place(x=3, rely=0.5, anchor="w")
            else:
                pill.place_forget()

    def _rebuild_sidebar_only(self) -> None:
        current_key = self._current_tab_key or "command_center"
        try:
            self.sidebar.destroy()
        except Exception:
            pass
        self._build_sidebar()
        self._apply_nav_button_state(current_key, True)

    def toggle_sidebar_collapsed(self) -> None:
        self._sidebar_collapsed = not self._sidebar_collapsed
        set_user_preference("sidebar_collapsed", "1" if self._sidebar_collapsed else "0")
        self._rebuild_sidebar_only()

    def _build_content_area(self):
        self.workspace_wrap = ctk.CTkFrame(self, fg_color="transparent")
        self.workspace_wrap.grid(row=0, column=1, sticky="nsew", padx=14, pady=(10, 14))
        self.workspace_wrap.grid_columnconfigure(0, weight=1)
        self.workspace_wrap.grid_rowconfigure(0, weight=0)
        self.workspace_wrap.grid_rowconfigure(1, weight=1)

        # Top HUD Bar Global
        self.top_hud_bar = ctk.CTkFrame(
            self.workspace_wrap,
            height=44,
            fg_color=theme_mod.C_BG_PANEL,
            corner_radius=10,
            border_width=1,
            border_color=theme_mod.C_BORDER_SOFT,
        )
        self.top_hud_bar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.top_hud_bar.grid_propagate(False)
        self.top_hud_bar.grid_columnconfigure(0, weight=1)

        self.hud_breadcrumb_lbl = ctk.CTkLabel(
            self.top_hud_bar,
            text="",
            font=ui_font(13, "bold", display=True),
            text_color=theme_mod.C_TEXT_SOFT,
            anchor="w",
        )
        self.hud_breadcrumb_lbl.grid(row=0, column=0, padx=(14, 8), pady=8, sticky="ew")

        kpi_strip = ctk.CTkFrame(self.top_hud_bar, fg_color="transparent")
        kpi_strip.grid(row=0, column=1, padx=4, pady=6)

        pill_kw = dict(
            height=26,
            corner_radius=7,
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=theme_mod.C_BORDER_SOFT,
            font=ui_font(11, "bold"),
        )
        self.hud_kpi_quests = ctk.CTkButton(
            kpi_strip, text="📜 0/0", width=98, text_color=THEME["accent_gold"],
            command=lambda: self.navigate_to_section("quests"), **pill_kw
        )
        self.hud_kpi_quests.pack(side="left", padx=2)

        self.hud_kpi_kappa = ctk.CTkButton(
            kpi_strip, text="🏆 0/44", width=86, text_color=theme_mod.C_EMERALD,
            command=lambda: self.navigate_to_section("flea", "KAPPA"), **pill_kw
        )
        self.hud_kpi_kappa.pack(side="left", padx=2)

        self.hud_kpi_ach = ctk.CTkButton(
            kpi_strip, text="⭐ 0/32", width=82, text_color=theme_mod.C_BLUE,
            command=lambda: self.navigate_to_section("pmc_systems", "achievements"), **pill_kw
        )
        self.hud_kpi_ach.pack(side="left", padx=2)

        self.hud_kpi_prestige = ctk.CTkButton(
            kpi_strip, text="👑 P0", width=56, text_color=THEME["accent_orange"],
            command=lambda: self.navigate_to_section("pmc_systems", "prestige"), **pill_kw
        )
        self.hud_kpi_prestige.pack(side="left", padx=2)

        right_strip = ctk.CTkFrame(self.top_hud_bar, fg_color="transparent")
        right_strip.grid(row=0, column=2, padx=(6, 10), pady=6, sticky="e")

        self.hud_clock_btn = ctk.CTkButton(
            right_strip,
            text="🔆 --:--  |  🌙 --:--",
            width=154,
            height=28,
            corner_radius=7,
            fg_color=theme_mod.C_BG_DEEP,
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=theme_mod.C_BORDER,
            text_color=theme_mod.C_TEXT,
            font=ui_font(11, "bold", mono=True),
            command=lambda: self.navigate_to_section("command_center"),
        )
        self.hud_clock_btn.pack(side="left", padx=(0, 6))

        self.hud_search_btn = ctk.CTkButton(
            right_strip,
            text="🔍 Ctrl+K",
            width=82,
            height=28,
            corner_radius=7,
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=THEME["accent_gold"],
            text_color=THEME["accent_gold"],
            font=ui_font(11, "bold"),
            command=self.open_global_search,
        )
        self.hud_search_btn.pack(side="left")

        self.content_frame = ctk.CTkFrame(self.workspace_wrap, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.refresh_hud_kpis()
        self._update_hud_clock()

    def refresh_hud_kpis(self) -> None:
        if not self.winfo_exists() or not hasattr(self, "hud_kpi_quests"):
            return
        try:
            ds = get_datastore()
            q_done, q_total = ds.get_quest_completion_counts()
            q_pct = int(round((q_done / q_total) * 100)) if q_total else 0

            k_total = len(KAPPA_COLLECTOR_ITEMS)
            k_done = sum(1 for it in KAPPA_COLLECTOR_ITEMS if ds.get_stash_count(f"kappa:{it['name']}") >= 1)

            a_total = len(ACHIEVEMENTS_CATALOG)
            a_done = len(get_unlocked_achievement_ids())
            prestige_lvl = get_prestige_level()

            state = (q_done, q_total, k_done, k_total, a_done, a_total, prestige_lvl, get_active_lang())
            if state == self._last_hud_kpi_state:
                return
            self._last_hud_kpi_state = state

            self.hud_kpi_quests.configure(text=f"📜 {tr('hud.quests')} {q_done}/{q_total} ({q_pct}%)")
            self.hud_kpi_kappa.configure(text=f"🏆 {tr('hud.kappa')} {k_done}/{k_total}")
            self.hud_kpi_ach.configure(text=f"⭐ {a_done}/{a_total}")
            self.hud_kpi_prestige.configure(text=f"👑 P{prestige_lvl}")
        except Exception:
            pass

    def _update_hud_clock(self) -> None:
        if not self.winfo_exists() or not hasattr(self, "hud_clock_btn"):
            return
        try:
            t = get_tarkov_raid_times()
            l_ico = "🌙" if t["left_is_night"] else "🔆"
            r_ico = "🌙" if t["right_is_night"] else "🔆"
            self.hud_clock_btn.configure(
                text=f"{l_ico} {t['left_short']}  |  {r_ico} {t['right_short']}",
                text_color=theme_mod.C_AMBER if t["cultists_window_active"] else theme_mod.C_TEXT,
            )
        except Exception:
            pass

    def _tick_tarkov_clock(self) -> None:
        if not self.winfo_exists():
            return
        self._update_hud_clock()
        self._clock_after_id = self.after(1000, self._tick_tarkov_clock)

    def _update_hud_breadcrumb(self, tab_key: str) -> None:
        if not hasattr(self, "hud_breadcrumb_lbl") or not self.hud_breadcrumb_lbl.winfo_exists():
            return
        cat_title, icon_txt, label_text = self._nav_meta.get(tab_key, ("TTC", "", tab_key.title()))
        self.hud_breadcrumb_lbl.configure(text=f"{cat_title}  ›   {icon_txt} {label_text}")

    def navigate_to_section(self, tab_key: str, sub_view: str = "") -> None:
        self.switch_tab(tab_key)
        if not sub_view:
            return
        tab_frame = self.tabs.get(tab_key)
        if not tab_frame:
            return
        if tab_key == "flea" and hasattr(tab_frame, "_switch_mode"):
            tab_frame._switch_mode(sub_view)
        elif tab_key == "pmc_systems" and hasattr(tab_frame, "_switch_view"):
            tab_frame._switch_view(sub_view)

    def _rebuild_workspace(self):
        current_key = self._current_tab_key or "command_center"
        if self._clock_after_id:
            try:
                self.after_cancel(self._clock_after_id)
            except Exception:
                pass
            self._clock_after_id = None

        for frame in list(self.tabs.values()):
            try:
                frame.destroy()
            except Exception:
                pass
        self.tabs.clear()
        self._active_nav_key = ""
        self._last_hud_kpi_state = None

        try:
            self.sidebar.destroy()
        except Exception:
            pass
        try:
            self.workspace_wrap.destroy()
        except Exception:
            pass

        self._build_sidebar()
        self._build_content_area()
        self.switch_tab(current_key)
        self._tick_tarkov_clock()

    def _on_skin_changed(self, selected_label: str):
        skin_id = self._skin_label_to_id.get(selected_label, "tarkov_classic")
        if skin_id == get_active_skin_id():
            return
        set_user_preference("ui_skin", skin_id)
        apply_ui_skin(skin_id)
        self.configure(fg_color=THEME["bg_dark"])
        self._rebuild_workspace()

    def _on_lang_changed(self, selected_label: str):
        lang_id = self._lang_label_to_id.get(selected_label, "es")
        if lang_id == get_active_lang():
            return
        set_active_lang(lang_id)
        self._rebuild_workspace()

    def _get_or_create_tab(self, tab_key: str, background: bool = False) -> ctk.CTkFrame:
        if tab_key not in self.tabs:
            cls = self._tab_classes[tab_key]
            if tab_key == "command_center":
                frame = cls(self.content_frame, on_navigate=self.navigate_to_section)
            else:
                frame = cls(self.content_frame)
            if not background:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                # Gridear y ocultar de inmediato para que no participe en redimensionados (maximizar/restaurar)
                frame.grid(row=0, column=0, sticky="nsew")
                frame.grid_remove()
            self.tabs[tab_key] = frame
        return self.tabs[tab_key]

    def _load_seen_new_tabs(self) -> Dict[str, str]:
        raw = get_user_preference("seen_new_tabs", "{}")
        try:
            data = json.loads(raw) if raw else {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _dismiss_new_badge(self, tab_key: str) -> None:
        badge = self._new_badges.pop(tab_key, None)
        if badge is not None:
            try:
                badge.destroy()
            except Exception:
                pass
        target_ver = NEW_TAB_VERSIONS.get(tab_key)
        if target_ver:
            seen = self._load_seen_new_tabs()
            if seen.get(tab_key) != target_ver:
                seen[tab_key] = target_ver
                set_user_preference("seen_new_tabs", json.dumps(seen, ensure_ascii=False))

    def open_patch_notes(self):
        PatchNotesModal(self)

    def switch_tab(self, selected_key: str):
        """Muestra la pestaña seleccionada manteniendo solo 1 pestaña mapeada (maximizar/resize 4x más rápido)."""
        if not self.winfo_exists():
            return
        if selected_key not in self._tab_classes:
            selected_key = "command_center"
        self._dismiss_new_badge(selected_key)
        if selected_key == self._active_nav_key and selected_key in self.tabs:
            return

        prev_key = self._active_nav_key
        if prev_key and prev_key != selected_key and prev_key in self.tabs:
            self.tabs[prev_key].grid_remove()

        self._current_tab_key = selected_key
        self._active_nav_key = selected_key

        was_cached = selected_key in self.tabs
        target_frame = self._get_or_create_tab(selected_key)
        target_frame.grid(row=0, column=0, sticky="nsew")
        target_frame.tkraise()
        if was_cached and hasattr(target_frame, "on_tab_activated"):
            target_frame.on_tab_activated()
        if hasattr(target_frame, "_refresh_scrollregion"):
            self.after(20, target_frame._refresh_scrollregion)

        # Actualizar solo los 2 botones que cambian de estado + Active Pill
        if prev_key and prev_key != selected_key:
            self._apply_nav_button_state(prev_key, False)
        self._apply_nav_button_state(selected_key, True)
        self._update_hud_breadcrumb(selected_key)
        self.refresh_hud_kpis()

    def _check_initial_sync(self):
        if not is_db_populated():
            self.start_sync_in_background()

    def _prewarm_background_caches(self):
        """Pre-carga en segundo plano datasets pesados y miniaturas en RAM para apertura en 0 ms."""
        def worker():
            try:
                from core.quest_route_data import load_route_dataset
                load_route_dataset()
            except Exception:
                pass
            try:
                get_datastore().get_wiki_story_chapters()
            except Exception:
                pass
            try:
                prewarm_ui_thumbnails()
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def start_sync_in_background(self):
        collapsed = bool(getattr(self, "_sidebar_collapsed", False))
        self.sync_btn.configure(state="disabled", text="⏳" if collapsed else tr("sidebar.syncing", "Sincronizando..."))
        self.db_status_lbl.configure(
            text="●" if collapsed else tr("sidebar.db_syncing", "● Descargando datos..."),
            text_color=C_AMBER,
        )

        def worker():
            service = SyncService()

            def progress(pct, msg):
                def update_ui():
                    if not self.winfo_exists():
                        return
                    if not getattr(self, "_sidebar_collapsed", False):
                        self.db_status_lbl.configure(text=f"● {msg}")
                self.after(0, update_ui)

            success = service.sync_all(progress_callback=progress)

            def on_finish():
                if not self.winfo_exists():
                    return
                is_col = bool(getattr(self, "_sidebar_collapsed", False))
                self.sync_btn.configure(state="normal", text="⟳" if is_col else tr("sidebar.sync", "Sincronizar Datos"))
                if success:
                    clear_image_ram_cache()
                    self.db_status_lbl.configure(
                        text="●" if is_col else tr("sidebar.db_ready", "● Caché RAM Zero-Lag activo"),
                        text_color=C_GREEN,
                    )
                    for tab_key in ("command_center", "ballistics", "quests", "maps", "quest_tracker", "progression_planner"):
                        tab_obj = self.tabs.get(tab_key)
                        if tab_obj and hasattr(tab_obj, "reload_data"):
                            try:
                                tab_obj.reload_data(force=True)
                            except TypeError:
                                tab_obj.reload_data()
                    self.refresh_hud_kpis()
                else:
                    self.db_status_lbl.configure(
                        text="●" if is_col else "● Error al sincronizar",
                        text_color=C_RED,
                    )

            self.after(0, on_finish)

        threading.Thread(target=worker, daemon=True).start()

    # --- Verificación de Actualizaciones en GitHub ---

    def check_for_app_updates(self):
        collapsed = bool(getattr(self, "_sidebar_collapsed", False))
        self.update_btn.configure(state="disabled", text="⏳" if collapsed else "⏳ Buscando actualización...")

        def worker():
            info = check_github_release()

            def on_done():
                if not self.winfo_exists():
                    return
                is_col = bool(getattr(self, "_sidebar_collapsed", False))
                self.update_btn.configure(
                    state="normal",
                    text="🔄" if is_col else tr("sidebar.update", ver=APP_VERSION),
                )
                UpdateDialog(self, info)

            try:
                self.after(0, on_done)
            except RuntimeError:
                pass

        threading.Thread(target=worker, daemon=True).start()

    # --- Buscador Global Rápido (Ctrl + K) ---

    def open_global_search(self):
        GlobalSearchModal(self, on_navigate=self._handle_global_search_nav)

    def _handle_global_search_nav(self, tab_key: str, target: str):
        self.switch_tab(tab_key)
        tab_frame = self.tabs.get(tab_key)
        if not tab_frame:
            return

        if tab_key == "quests":
            if hasattr(tab_frame, "search_entry"):
                tab_frame.search_entry.delete(0, "end")
                tab_frame.search_entry.insert(0, target)
                tab_frame._reset_and_apply_filters()
        elif tab_key == "maps":
            if hasattr(tab_frame, "_select_map"):
                tab_frame._select_map(target)
        elif tab_key == "bosses":
            if hasattr(tab_frame, "_select_boss"):
                tab_frame._select_boss(target)
        elif tab_key == "ballistics":
            if target.startswith("ARMOR:") and hasattr(tab_frame, "_open_armor_from_search"):
                tab_frame._open_armor_from_search(target.split(":", 1)[1])
            else:
                if hasattr(tab_frame, "_exit_armor_mode"):
                    tab_frame._exit_armor_mode()
                if hasattr(tab_frame, "search_entry"):
                    tab_frame.search_entry.delete(0, "end")
                    tab_frame.search_entry.insert(0, target)
                    tab_frame._reset_and_filter()
        elif tab_key == "containers":
            if hasattr(tab_frame, "open_from_search"):
                tab_frame.open_from_search(target)
        elif tab_key == "flea":
            if hasattr(tab_frame, "_quick_search"):
                tab_frame._quick_search(target)
        elif tab_key == "keys":
            if hasattr(tab_frame, "entry_search"):
                tab_frame.entry_search.delete(0, "end")
                tab_frame.entry_search.insert(0, target)
                if hasattr(tab_frame, "_schedule_render_keys"):
                    tab_frame._schedule_render_keys()
        elif tab_key == "medical":
            if hasattr(tab_frame, "open_from_search"):
                tab_frame.open_from_search(target)
            elif hasattr(tab_frame, "entry_search"):
                tab_frame.entry_search.delete(0, "end")
                tab_frame.entry_search.insert(0, target)
                if hasattr(tab_frame, "_schedule_render_items"):
                    tab_frame._schedule_render_items()
        elif tab_key == "weapons":
            if target.startswith("MALFUNCTION:") and hasattr(tab_frame, "_switch_mode"):
                tab_frame._switch_mode("MALFUNCTIONS")
        elif tab_key == "pmc_systems":
            if hasattr(tab_frame, "open_from_search"):
                tab_frame.open_from_search(target)

    # --- Modo Ventana Siempre Visible (Always on Top) ---

    def toggle_always_on_top(self):
        self._always_on_top = not self._always_on_top
        self.attributes("-topmost", self._always_on_top)
        collapsed = bool(getattr(self, "_sidebar_collapsed", False))
        if self._always_on_top:
            self.btn_topmost.configure(
                text="📌" if collapsed else tr("sidebar.topmost_on", "📌 Fijar Arriba: ACTIVO"),
                fg_color=THEME["active_tab_bg"],
                border_color=THEME["accent_blue"],
                text_color=C_WHITE
            )
        else:
            self.btn_topmost.configure(
                text="📌" if collapsed else tr("sidebar.topmost_off", "📌 Fijar Arriba: Desactivado"),
                fg_color="transparent",
                border_color=C_BORDER,
                text_color=C_TEXT_DIM
            )

    # --- Respaldo de Perfil (Exportar / Importar) ---

    def export_profile(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar Respaldo de Progreso TTC",
            defaultextension=".json",
            filetypes=[("Perfil TTC (*.json)", "*.json")],
            initialfile="perfil_ttc.json"
        )
        if not file_path:
            return
        try:
            data = get_datastore().export_profile()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            if not getattr(self, "_sidebar_collapsed", False):
                self.db_status_lbl.configure(text="✓ Perfil exportado correctamente", text_color=C_GREEN)
        except Exception as e:
            logger.error("Error al exportar perfil: %s", e)
            if not getattr(self, "_sidebar_collapsed", False):
                self.db_status_lbl.configure(text="✕ Error al exportar perfil", text_color=C_RED)

    def import_profile(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Cargar Respaldo de Progreso TTC",
            filetypes=[("Perfil TTC (*.json)", "*.json")]
        )
        if not file_path or not os.path.exists(file_path):
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ok = get_datastore().import_profile(data)
            if ok:
                if not getattr(self, "_sidebar_collapsed", False):
                    self.db_status_lbl.configure(text="✓ Perfil restaurado correctamente", text_color=C_GREEN)
                for tab_key in ("command_center", "quests", "flea", "maps", "quest_tracker", "progression_planner"):
                    if tab_key in self.tabs and hasattr(self.tabs[tab_key], "reload_data"):
                        self.tabs[tab_key].reload_data()
                self.refresh_hud_kpis()
            else:
                if not getattr(self, "_sidebar_collapsed", False):
                    self.db_status_lbl.configure(text="✕ Formato de perfil inválido", text_color=C_RED)
        except Exception as e:
            logger.error("Error al importar perfil: %s", e)
            if not getattr(self, "_sidebar_collapsed", False):
                self.db_status_lbl.configure(text="✕ Error al importar perfil", text_color=C_RED)


_APP_MUTEX_HANDLE = None


def _acquire_app_mutex() -> None:
    """Crea el mutex nombrado de Windows para que el instalador Inno Setup detecte instancias activas."""
    global _APP_MUTEX_HANDLE
    if sys.platform.startswith("win"):
        try:
            import ctypes
            _APP_MUTEX_HANDLE = ctypes.windll.kernel32.CreateMutexW(
                None, False, "TTC_TacticalTarkovCompanion_Mutex"
            )
        except Exception:
            pass


def main():
    _acquire_app_mutex()
    app = TarkovScopeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
