"""
TarkovScope - Modal Táctico de Notas de Versión (Patch Notes)
Muestra el historial de novedades, mejoras y correcciones por versión.
"""
import customtkinter as ctk
from core.config import APP_VERSION, THEME
from core.i18n import get_active_lang, t_ui
from core.patch_notes_data import get_patch_notes
from ui.theme import C_BADGE_NEW, C_BLUE, C_BORDER, C_GREEN_LIGHT, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE, ui_font


_KIND_STYLE = {
    "NEW": ("#14532D", "#4ADE80"),
    "IMPROVED": ("#1E3A8A", "#60A5FA"),
    "FIX": ("#7C2D12", "#FDBA74"),
}


class PatchNotesModal(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title(t_ui("TTC — Notas de Versión (Patch Notes)", "TTC — Patch Notes"))
        self.geometry("760x580")
        self.minsize(640, 460)
        self.configure(fg_color=THEME["bg_deep"])
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_body()
        self._build_footer()

        self.bind("<Escape>", lambda _e: self.destroy())
        self.after(40, self._center_on_parent)

    def _center_on_parent(self):
        try:
            self.update_idletasks()
            mx = self.master.winfo_rootx() + (self.master.winfo_width() - self.winfo_width()) // 2
            my = self.master.winfo_rooty() + (self.master.winfo_height() - self.winfo_height()) // 2
            self.geometry(f"+{max(20, mx)}+{max(20, my)}")
        except Exception:
            pass

    def _build_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=THEME["bg_card"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        hdr.grid(row=0, column=0, padx=16, pady=(14, 10), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            hdr,
            text=t_ui("📋 NOTAS DE VERSIÓN — TARKOVSCOPE (TTC)", "📋 PATCH NOTES — TARKOVSCOPE (TTC)"),
            font=ui_font(16, "bold"),
            text_color=THEME["accent_gold"],
        ).grid(row=0, column=0, padx=14, pady=(10, 2), sticky="w")

        ctk.CTkLabel(
            hdr,
            text=t_ui(
                f"Versión instalada: v{APP_VERSION} • Historial de actualizaciones y novedades",
                f"Installed version: v{APP_VERSION} • Update history & changelog",
            ),
            font=ui_font(12),
            text_color=C_TEXT_DIM,
        ).grid(row=1, column=0, padx=14, pady=(0, 10), sticky="w")

    def _build_body(self):
        scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=THEME["bg_inset"],
            corner_radius=10,
            border_width=1,
            border_color=THEME["border"],
        )
        scroll.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        lang = get_active_lang()
        notes = get_patch_notes(lang)

        for idx, rel in enumerate(notes):
            card = ctk.CTkFrame(
                scroll,
                fg_color=THEME["bg_card"],
                corner_radius=8,
                border_width=1,
                border_color=THEME["border_soft"],
            )
            card.grid(row=idx, column=0, padx=8, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, padx=12, pady=(10, 6), sticky="ew")

            ver_lbl = ctk.CTkLabel(
                top,
                text=f"v{rel['version']}",
                font=ui_font(14, "bold"),
                text_color=THEME["accent_orange"],
            )
            ver_lbl.pack(side="left")

            if rel["version"] == APP_VERSION:
                ctk.CTkLabel(
                    top,
                    text=t_ui("ACTUAL", "CURRENT"),
                    font=ui_font(10, "bold"),
                    fg_color=C_BADGE_NEW,
                    text_color=C_WHITE,
                    corner_radius=4,
                    padx=6,
                    pady=1,
                ).pack(side="left", padx=(8, 0))
            elif rel["tag"]:
                ctk.CTkLabel(
                    top,
                    text=rel["tag"],
                    font=ui_font(10, "bold"),
                    fg_color=THEME["btn_surface"],
                    text_color=C_TEXT_MUTED,
                    corner_radius=4,
                    padx=6,
                    pady=1,
                ).pack(side="left", padx=(8, 0))

            ctk.CTkLabel(
                top,
                text=f"—  {rel['title']}",
                font=ui_font(13, "bold"),
                text_color=C_TEXT,
            ).pack(side="left", padx=(8, 0))

            for i_idx, item in enumerate(rel["items"], start=1):
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.grid(row=i_idx, column=0, padx=12, pady=(0, 6), sticky="ew")
                row.grid_columnconfigure(1, weight=1)

                kind = item["kind"]
                bg_c, fg_c = _KIND_STYLE.get(kind, (THEME["btn_surface"], C_TEXT))
                badge_txt = kind
                if lang == "es":
                    badge_txt = {"NEW": "NUEVO", "IMPROVED": "MEJORA", "FIX": "FIX"}.get(kind, kind)

                ctk.CTkLabel(
                    row,
                    text=badge_txt,
                    width=66,
                    font=ui_font(10, "bold"),
                    fg_color=bg_c,
                    text_color=fg_c,
                    corner_radius=4,
                    pady=2,
                ).grid(row=0, column=0, padx=(0, 10), pady=2, sticky="nw")

                ctk.CTkLabel(
                    row,
                    text=item["text"],
                    font=ui_font(12),
                    text_color=C_TEXT_MUTED,
                    justify="left",
                    anchor="w",
                    wraplength=600,
                ).grid(row=0, column=1, sticky="ew")

            # Pequeño respiro inferior en la tarjeta
            ctk.CTkFrame(card, height=4, fg_color="transparent").grid(row=len(rel["items"]) + 1, column=0)

    def _build_footer(self):
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, padx=16, pady=(0, 14), sticky="ew")
        ctk.CTkButton(
            foot,
            text=t_ui("Cerrar", "Close"),
            width=110,
            height=32,
            corner_radius=6,
            fg_color=THEME["btn_surface"],
            hover_color=THEME["btn_hover"],
            border_width=1,
            border_color=C_BORDER,
            font=ui_font(12, "bold"),
            command=self.destroy,
        ).pack(side="right")
