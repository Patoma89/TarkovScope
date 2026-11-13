"""
TarkovScope - Modal de Buscador Global Rápido (Spotlight / Command Palette: Ctrl + K)
Búsqueda instantánea indexada en memoria RAM sobre:
- Misiones y Traders (459 quests)
- Jefes y Zonas de Spawn (Bosses)
- Mapas tácticos y Extracciones
- Balística, Calibres y Proyectiles
- Ítems Found in Raid (FiR) y Contenedor Kappa
- Estaciones y Módulos del Hideout
"""
import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any
from core.config import THEME
from ui.theme import ui_font
from core.datastore import get_datastore
from ui.theme import C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL_ALT, C_RED_DARK, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE


class GlobalSearchModal(ctk.CTkToplevel):
    def __init__(self, parent, on_navigate: Optional[Callable[[str, str], None]] = None):
        super().__init__(parent)
        self.on_navigate = on_navigate
        self._debounce_job: Optional[str] = None
        self._results: List[Dict[str, Any]] = []

        self.title("Buscador Global Táctico — TTC Spotlight (Ctrl + K)")
        self.geometry("780x560")
        self.minsize(680, 480)
        self.configure(fg_color="#0A0C10")

        # Configurar modalidad y foco
        self.transient(parent)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_search_input()
        self._build_results_view()
        self._build_footer()

        # Atajos de teclado
        self.bind("<Escape>", lambda e: self.destroy())
        self.after(50, self._focus_input)

    def _focus_input(self):
        if self.winfo_exists():
            self.search_entry.focus_set()

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="#0D1017", height=50, corner_radius=0, border_width=1, border_color="#202634")
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text="🔍  BUSCADOR GLOBAL SPOTLIGHT",
            font=ui_font(15, "bold"),
            text_color=THEME["accent_gold"]
        ).grid(row=0, column=0, padx=18, pady=12, sticky="w")

        close_btn = ctk.CTkButton(
            hdr,
            text="✕ Cerrar (Esc)",
            width=105,
            height=30,
            fg_color="#1E2430",
            hover_color=C_RED_DARK,
            text_color=C_TEXT_MUTED,
            font=ui_font(12, "bold"),
            command=self.destroy
        )
        close_btn.grid(row=0, column=1, padx=14, pady=10, sticky="e")

    def _build_search_input(self):
        search_box = ctk.CTkFrame(self, fg_color="transparent")
        search_box.grid(row=1, column=0, padx=18, pady=(14, 8), sticky="ew")
        search_box.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_box,
            placeholder_text="Buscar quests, bosses, mapas, munición, blindaje, llaves, stims, barters o skills...",
            font=ui_font(15),
            height=46,
            fg_color=C_BG_PANEL_ALT,
            border_width=2,
            border_color=THEME["accent_gold"],
            text_color=C_WHITE,
            corner_radius=8
        )
        self.search_entry.grid(row=0, column=0, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_key_release)
        self.search_entry.bind("<Return>", self._on_enter_pressed)

    def _build_results_view(self):
        self.results_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=C_BG_DEEP,
            corner_radius=8,
            border_width=1,
            border_color="#232936"
        )
        self.results_scroll.grid(row=2, column=0, padx=18, pady=6, sticky="nsew")
        self.results_scroll.grid_columnconfigure(0, weight=1)

        self._render_empty_state("Escribe al menos 2 letras para buscar instantáneamente en todo TarkovScope...")

    def _build_footer(self):
        ft = ctk.CTkFrame(self, fg_color="transparent", height=32)
        ft.grid(row=3, column=0, padx=18, pady=(4, 10), sticky="ew")
        ft.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ft,
            text="Tip: Puedes presionar Ctrl + K desde cualquier ventana de la app para abrir este buscador.",
            font=ui_font(11),
            text_color="#64748B"
        ).grid(row=0, column=0, sticky="w")

        self.count_lbl = ctk.CTkLabel(
            ft,
            text="",
            font=ui_font(12, "bold"),
            text_color=C_TEXT_DIM
        )
        self.count_lbl.grid(row=0, column=1, sticky="e")

    def _on_key_release(self, event=None):
        if event and event.keysym in ("Up", "Down", "Escape", "Return"):
            return
        if self._debounce_job is not None:
            self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(140, self._perform_search)

    def _on_enter_pressed(self, event=None):
        if self._results:
            first = self._results[0]
            self._select_item(first)

    def _perform_search(self):
        self._debounce_job = None
        if not self.winfo_exists():
            return
        query = self.search_entry.get().strip()
        if len(query) < 2:
            self._render_empty_state("Escribe al menos 2 letras para buscar...")
            self.count_lbl.configure(text="")
            self._results = []
            return

        ds = get_datastore()
        self._results = ds.global_search(query)
        self._render_results()

    def _render_empty_state(self, message: str):
        for w in self.results_scroll.winfo_children():
            w.destroy()
        ctk.CTkLabel(
            self.results_scroll,
            text=message,
            font=ui_font(13),
            text_color=C_TEXT_DIM
        ).grid(row=0, column=0, pady=50)

    def _render_results(self):
        for w in self.results_scroll.winfo_children():
            w.destroy()

        if not self._results:
            self._render_empty_state("No se encontraron resultados coincidentes.")
            self.count_lbl.configure(text="0 resultados")
            return

        self.count_lbl.configure(text=f"{len(self._results)} coincidencias")

        for idx, item in enumerate(self._results):
            card = ctk.CTkFrame(
                self.results_scroll,
                fg_color="#121622" if idx % 2 == 0 else "#151B2A",
                corner_radius=6,
                border_width=1,
                border_color="#242B3B"
            )
            card.grid(row=idx, column=0, padx=4, pady=3, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Badge de Categoría
            badge_col = item.get("badge_color", THEME["accent_gold"])
            ctk.CTkLabel(
                card,
                text=f" {item.get('category', '').upper()} ",
                font=ui_font(10, "bold"),
                fg_color=badge_col,
                text_color=C_BG_DARKEST,
                corner_radius=3,
                width=115,
                height=24
            ).grid(row=0, column=0, padx=(10, 8), pady=8, sticky="w")

            # Información principal (Título + Subtítulo)
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=6, pady=6, sticky="w")

            ctk.CTkLabel(
                info_frame,
                text=item.get("title", ""),
                font=ui_font(13, "bold"),
                text_color=C_TEXT,
                anchor="w"
            ).pack(fill="x", anchor="w")

            ctk.CTkLabel(
                info_frame,
                text=item.get("subtitle", ""),
                font=ui_font(11),
                text_color=C_TEXT_DIM,
                anchor="w"
            ).pack(fill="x", anchor="w")

            # Botón de Navegación directa
            nav_btn = ctk.CTkButton(
                card,
                text="Ir ➔",
                width=65,
                height=28,
                fg_color="#1E2738",
                hover_color=THEME["accent_gold"],
                text_color=C_WHITE,
                font=ui_font(12, "bold"),
                command=lambda it=item: self._select_item(it)
            )
            nav_btn.grid(row=0, column=2, padx=12, pady=8, sticky="e")

    def _select_item(self, item: Dict[str, Any]):
        tab = item.get("tab")
        target = item.get("target")
        self.destroy()
        if self.on_navigate and tab:
            self.on_navigate(tab, target)
