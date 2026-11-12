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
from typing import Dict
import customtkinter as ctk

# Asegurar importaciones relativas
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from core.config import APP_NAME, THEME, BUNDLE_DIR, BASE_DIR
from core.database import init_db, is_db_populated
from core.datastore import get_datastore
from core.sync_service import SyncService
from ui.image_utils import clear_image_ram_cache
from ui.theme import THEME_SETTINGS, ui_font
from ui.tab_bosses import TabBosses
from ui.tab_weapons import TabWeapons
from ui.tab_ballistics import TabBallistics
from ui.tab_quests import TabQuests
from ui.tab_maps import TabMaps
from ui.tab_flea import TabFlea
from ui.tab_lore import TabLore
from ui.tab_story_quests import TabStoryQuests
from ui.global_search_modal import GlobalSearchModal
from ui.theme import C_AMBER, C_BG_DEEP, C_BG_ROW, C_BORDER, C_BORDER_ALT, C_GREEN, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE

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
        self._current_tab_key: str = "quests"
        self._tab_classes = {
            "bosses": TabBosses,
            "maps": TabMaps,
            "quests": TabQuests,
            "story_quests": TabStoryQuests,
            "weapons": TabWeapons,
            "ballistics": TabBallistics,
            "flea": TabFlea,
            "lore": TabLore,
        }

        self.switch_tab("quests")
        self._check_initial_sync()
        self.after(80, self._warmup_remaining_tabs)

    def _build_sidebar(self):
        """Barra de navegación lateral limpia, tipográfica y con alto contraste."""
        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            fg_color=C_BG_DEEP,
            border_width=1,
            border_color="#232936",
            corner_radius=0
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)
        self.sidebar.grid_rowconfigure(3, weight=1)

        # 1. Bloque de Marca / Título
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=18, pady=(22, 14), sticky="ew")
        logo_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            logo_frame,
            text="TTC",
            font=ui_font(24, "bold"),
            text_color=THEME["accent_gold"],
            anchor="w"
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            logo_frame,
            text="TACTICAL TARKOV COMPANION",
            font=ui_font(10, "bold"),
            text_color=C_TEXT_DIM,
            anchor="w"
        ).grid(row=1, column=0, pady=(2, 0), sticky="ew")

        # Botón de Búsqueda Global Rápida (Spotlight / Command Palette)
        self.search_btn = ctk.CTkButton(
            logo_frame,
            text="🔍 Buscar... (Ctrl+K)",
            font=ui_font(12, "bold"),
            fg_color="#141824",
            hover_color="#1F2637",
            border_width=1,
            border_color=THEME["accent_gold"],
            text_color=C_TEXT,
            height=34,
            corner_radius=6,
            anchor="w",
            command=self.open_global_search
        )
        self.search_btn.grid(row=2, column=0, pady=(10, 4), sticky="ew")

        # Botón de Modo Ventana Siempre Visible (Always on Top)
        self.btn_topmost = ctk.CTkButton(
            logo_frame,
            text="📌 Fijar Arriba: Desactivado",
            font=ui_font(11, "bold"),
            fg_color="transparent",
            hover_color=C_BG_ROW,
            border_width=1,
            border_color=C_BORDER,
            text_color=C_TEXT_DIM,
            height=28,
            corner_radius=6,
            anchor="w",
            command=self.toggle_always_on_top
        )
        self.btn_topmost.grid(row=3, column=0, pady=(2, 0), sticky="ew")

        # 2. Separador Superior
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color="#232936")
        sep.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="ew")

        # 3. Contenedor de Botones de Navegación (Sin números, alineación limpia)
        nav_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_container.grid(row=2, column=0, padx=14, pady=0, sticky="ew")
        nav_container.grid_columnconfigure(0, weight=1)

        self.nav_buttons: Dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("bosses", "Bosses & Spawns"),
            ("maps", "Mapas & Extracciones"),
            ("quests", "Quests & Traders"),
            ("story_quests", "Quests de la Historia"),
            ("weapons", "Armas & Gunsmith"),
            ("ballistics", "Balística & Munición"),
            ("flea", "Hideout & Ítems FiR"),
            ("lore", "Story & Lore"),
        ]

        for idx, (tab_key, label_text) in enumerate(nav_items):
            btn = ctk.CTkButton(
                nav_container,
                text=f"  {label_text}",
                font=ui_font(14, "bold"),
                fg_color="transparent",
                text_color=C_TEXT_MUTED,
                hover_color=C_BG_ROW,
                border_width=1,
                border_color=C_BG_DEEP,
                anchor="w",
                height=44,
                corner_radius=6,
                command=lambda k=tab_key: self.switch_tab(k)
            )
            btn.grid(row=idx, column=0, padx=0, pady=4, sticky="ew")
            self.nav_buttons[tab_key] = btn

        # 4. Pie de Barra Lateral
        footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer_frame.grid(row=4, column=0, padx=16, pady=18, sticky="ew")
        footer_frame.grid_columnconfigure(0, weight=1)

        sep_bot = ctk.CTkFrame(footer_frame, height=1, fg_color="#232936")
        sep_bot.grid(row=0, column=0, pady=(0, 12), sticky="ew")

        self.db_status_lbl = ctk.CTkLabel(
            footer_frame,
            text="● Caché RAM Zero-Lag activo",
            font=ui_font(12, "bold"),
            text_color=C_GREEN,
            anchor="w"
        )
        self.db_status_lbl.grid(row=1, column=0, pady=(0, 8), sticky="ew")

        # Botones de Respaldo de Progreso (Exportar / Importar Perfil)
        backup_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        backup_row.grid(row=2, column=0, pady=(0, 8), sticky="ew")
        backup_row.grid_columnconfigure(0, weight=1)
        backup_row.grid_columnconfigure(1, weight=1)

        self.btn_export = ctk.CTkButton(
            backup_row,
            text="📤 Exportar",
            font=ui_font(11, "bold"),
            fg_color="#141824",
            hover_color="#242E42",
            border_width=1,
            border_color="#2E3748",
            text_color=C_TEXT_MUTED,
            height=28,
            corner_radius=5,
            command=self.export_profile
        )
        self.btn_export.grid(row=0, column=0, padx=(0, 3), sticky="ew")

        self.btn_import = ctk.CTkButton(
            backup_row,
            text="📥 Importar",
            font=ui_font(11, "bold"),
            fg_color="#141824",
            hover_color="#242E42",
            border_width=1,
            border_color="#2E3748",
            text_color=C_TEXT_MUTED,
            height=28,
            corner_radius=5,
            command=self.import_profile
        )
        self.btn_import.grid(row=0, column=1, padx=(3, 0), sticky="ew")

        self.sync_btn = ctk.CTkButton(
            footer_frame,
            text="Sincronizar Datos",
            font=ui_font(13, "bold"),
            fg_color=C_BG_ROW,
            hover_color=C_BORDER_ALT,
            border_width=1,
            border_color="#384152",
            text_color=C_TEXT,
            height=36,
            corner_radius=6,
            command=self.start_sync_in_background
        )
        self.sync_btn.grid(row=3, column=0, sticky="ew")

    def _build_content_area(self):
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

    def _get_or_create_tab(self, tab_key: str) -> ctk.CTkFrame:
        if tab_key not in self.tabs:
            cls = self._tab_classes[tab_key]
            frame = cls(self.content_frame)
            frame.grid(row=0, column=0, sticky="nsew")
            self.tabs[tab_key] = frame
        return self.tabs[tab_key]

    def switch_tab(self, selected_key: str):
        """Muestra la pestaña seleccionada de forma instantánea (<1 ms si ya está en RAM)."""
        if not self.winfo_exists():
            return

        self._current_tab_key = selected_key
        target_frame = self._get_or_create_tab(selected_key)
        target_frame.tkraise()
        if hasattr(target_frame, "_refresh_scrollregion"):
            self.after(20, target_frame._refresh_scrollregion)

        for k, btn in self.nav_buttons.items():
            if k == selected_key:
                btn.configure(
                    fg_color="#1E2536",
                    border_color=THEME["accent_gold"],
                    text_color=C_WHITE
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_color=C_BG_DEEP,
                    text_color=C_TEXT_MUTED
                )

    def _warmup_remaining_tabs(self):
        """Pre-construye las pestañas ligeras en idle para que al hacer clic cambien en 0 ms."""
        tabs_to_warm = ["bosses", "maps", "weapons", "ballistics", "flea"]

        def _warm_step(idx: int = 0):
            if not self.winfo_exists() or idx >= len(tabs_to_warm):
                return
            key = tabs_to_warm[idx]
            if key not in self.tabs:
                try:
                    self._get_or_create_tab(key)
                except Exception as e:
                    logger.warning("Fallo pre-calentando pestaña %s: %s", key, e)
            # Asegurar que la pestaña activa se mantenga arriba
            if self._current_tab_key in self.tabs:
                self.tabs[self._current_tab_key].tkraise()
            self.after(90, lambda: _warm_step(idx + 1))

        self.after(150, lambda: _warm_step(0))

    def _check_initial_sync(self):
        if not is_db_populated():
            self.start_sync_in_background()

    def start_sync_in_background(self):
        self.sync_btn.configure(state="disabled", text="Sincronizando...")
        self.db_status_lbl.configure(text="● Descargando datos...", text_color=C_AMBER)

        def worker():
            service = SyncService()

            def progress(pct, msg):
                def update_ui():
                    if not self.winfo_exists():
                        return
                    self.db_status_lbl.configure(text=f"● {msg}")
                self.after(0, update_ui)

            success = service.sync_all(progress_callback=progress)

            def on_finish():
                if not self.winfo_exists():
                    return
                self.sync_btn.configure(state="normal", text="Sincronizar Datos")
                if success:
                    clear_image_ram_cache()
                    self.db_status_lbl.configure(text="● Caché RAM Zero-Lag activo", text_color=C_GREEN)
                    for tab_key in ("ballistics", "quests", "maps"):
                        if tab_key in self.tabs and hasattr(self.tabs[tab_key], "reload_data"):
                            self.tabs[tab_key].reload_data()
                else:
                    self.db_status_lbl.configure(text="● Error al sincronizar", text_color=C_RED)

            self.after(0, on_finish)

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
            if hasattr(tab_frame, "search_entry"):
                tab_frame.search_entry.delete(0, "end")
                tab_frame.search_entry.insert(0, target)
                tab_frame._reset_and_filter()
        elif tab_key == "flea":
            if hasattr(tab_frame, "_quick_search"):
                tab_frame._quick_search(target)

    # --- Modo Ventana Siempre Visible (Always on Top) ---

    def toggle_always_on_top(self):
        self._always_on_top = not self._always_on_top
        self.attributes("-topmost", self._always_on_top)
        if self._always_on_top:
            self.btn_topmost.configure(
                text="📌 Fijar Arriba: ACTIVO",
                fg_color="#1E3A8A",
                border_color="#3B82F6",
                text_color=C_WHITE
            )
        else:
            self.btn_topmost.configure(
                text="📌 Fijar Arriba: Desactivado",
                fg_color="transparent",
                border_color=C_BORDER,
                text_color=C_TEXT_DIM
            )

    # --- Respaldo de Perfil (Exportar / Importar) ---

    def export_profile(self):
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Guardar Respaldo de Progreso TarkovScope",
            defaultextension=".json",
            filetypes=[("Perfil TarkovScope (*.json)", "*.json")],
            initialfile="perfil_tarkovscope.json"
        )
        if not file_path:
            return
        try:
            data = get_datastore().export_profile()
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.db_status_lbl.configure(text="✓ Perfil exportado correctamente", text_color=C_GREEN)
        except Exception as e:
            logger.error("Error al exportar perfil: %s", e)
            self.db_status_lbl.configure(text="✕ Error al exportar perfil", text_color=C_RED)

    def import_profile(self):
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Cargar Respaldo de Progreso TarkovScope",
            filetypes=[("Perfil TarkovScope (*.json)", "*.json")]
        )
        if not file_path or not os.path.exists(file_path):
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ok = get_datastore().import_profile(data)
            if ok:
                self.db_status_lbl.configure(text="✓ Perfil restaurado correctamente", text_color=C_GREEN)
                for tab_key in ("quests", "flea", "maps"):
                    if tab_key in self.tabs and hasattr(self.tabs[tab_key], "reload_data"):
                        self.tabs[tab_key].reload_data()
            else:
                self.db_status_lbl.configure(text="✕ Formato de perfil inválido", text_color=C_RED)
        except Exception as e:
            logger.error("Error al importar perfil: %s", e)
            self.db_status_lbl.configure(text="✕ Error al importar perfil", text_color=C_RED)


def main():
    app = TarkovScopeApp()
    app.mainloop()


if __name__ == "__main__":
    main()
