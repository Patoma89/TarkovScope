"""
TarkovScope - Modal CustomTkinter para Verificación y Descarga de Actualizaciones
"""
import os
import subprocess
import sys
import threading
import webbrowser
from typing import Any, Dict
import customtkinter as ctk

from core.config import APP_VERSION, BASE_DIR, THEME
from core.updater import download_installer, run_git_fast_forward_pull
from ui.theme import C_AMBER, C_BG_DEEP, C_BG_PANEL, C_BORDER, C_GREEN, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE, ui_font


class UpdateDialog(ctk.CTkToplevel):
    """Ventana modal integrada para mostrar el estado de actualización de la app."""

    def __init__(self, master, release_info: Dict[str, Any]):
        super().__init__(master)
        self.release_info = release_info
        self.title("Actualización de TTC")
        self.geometry("500x340")
        self.resizable(False, False)
        self.configure(fg_color=C_BG_DEEP)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_ui()

    def _build_ui(self):
        info = self.release_info
        ok = bool(info.get("ok"))
        has_update = bool(info.get("has_update"))
        is_frozen = getattr(sys, "frozen", False)

        # Cabecera
        hdr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, corner_radius=8, border_width=1, border_color=C_BORDER)
        hdr.grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

        if not ok:
            title_txt = "✕ No se pudo verificar actualizaciones"
            title_col = C_RED
        elif has_update:
            title_txt = f"🚀 Nueva versión disponible: {info.get('latest_version')}"
            title_col = THEME["accent_gold"]
        else:
            title_txt = f"✓ TTC está actualizado (v{APP_VERSION})"
            title_col = C_GREEN

        ctk.CTkLabel(hdr, text=title_txt, font=ui_font(15, "bold"), text_color=title_col).pack(
            anchor="w", padx=14, pady=(10, 2)
        )
        ctk.CTkLabel(
            hdr,
            text=f"Versión instalada: v{APP_VERSION}   •   Última en GitHub: {info.get('latest_version', APP_VERSION)}",
            font=ui_font(12),
            text_color=C_TEXT_DIM,
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # Cuerpo con notas o error
        body = ctk.CTkTextbox(
            self,
            fg_color=C_BG_PANEL,
            border_width=1,
            border_color=C_BORDER,
            text_color=C_TEXT,
            font=ui_font(12),
            wrap="word",
        )
        body.grid(row=1, column=0, padx=16, pady=(0, 10), sticky="nsew")
        if not ok:
            body.insert("1.0", f"Error de conexión:\n{info.get('error', 'Desconocido')}")
        elif has_update:
            notes = info.get("notes") or "Nueva versión disponible en GitHub Releases."
            body.insert("1.0", notes)
        else:
            body.insert("1.0", "Ya cuentas con la versión más reciente de TTC (Tactical Tarkov Companion).")
        body.configure(state="disabled")

        self.status_lbl = ctk.CTkLabel(self, text="", font=ui_font(11, "bold"), text_color=C_AMBER)
        self.status_lbl.grid(row=2, column=0, padx=16, pady=(0, 6), sticky="w")

        # Botonera inferior
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, padx=16, pady=(0, 16), sticky="ew")

        if ok and has_update:
            installer_url = info.get("installer_url")
            if is_frozen and installer_url:
                self.action_btn = ctk.CTkButton(
                    btn_row,
                    text="⬇ Descargar e Instalar",
                    font=ui_font(12, "bold"),
                    fg_color=C_GREEN,
                    hover_color="#15803D",
                    text_color=C_WHITE,
                    height=34,
                    command=self._start_installer_download,
                )
                self.action_btn.pack(side="left", padx=(0, 8))
            elif not is_frozen and os.path.isdir(os.path.join(BASE_DIR, ".git")):
                self.action_btn = ctk.CTkButton(
                    btn_row,
                    text="⚡ Actualizar vía Git",
                    font=ui_font(12, "bold"),
                    fg_color=C_GREEN,
                    hover_color="#15803D",
                    text_color=C_WHITE,
                    height=34,
                    command=self._start_git_pull,
                )
                self.action_btn.pack(side="left", padx=(0, 8))

        release_url = info.get("release_url")
        if release_url:
            ctk.CTkButton(
                btn_row,
                text="🌐 Abrir GitHub",
                font=ui_font(12, "bold"),
                fg_color="#1E2536",
                hover_color="#2A344B",
                border_width=1,
                border_color=C_BORDER,
                text_color=C_TEXT,
                height=34,
                command=lambda: webbrowser.open(release_url),
            ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row,
            text="Cerrar",
            font=ui_font(12, "bold"),
            fg_color="transparent",
            hover_color="#1F2637",
            border_width=1,
            border_color=C_BORDER,
            text_color=C_TEXT_MUTED,
            height=34,
            width=90,
            command=self.destroy,
        ).pack(side="right")

    def _start_installer_download(self):
        url = self.release_info.get("installer_url")
        name = self.release_info.get("installer_name") or "TTC_Setup.exe"
        if not url:
            return
        self.action_btn.configure(state="disabled", text="Descargando...")
        self.status_lbl.configure(text="Descargando instalador...", text_color=C_AMBER)

        def worker():
            try:
                def on_prog(pct: int):
                    def _upd():
                        if self.winfo_exists():
                            self.status_lbl.configure(text=f"Descargando instalador... {pct}%")
                    try:
                        self.after(0, _upd)
                    except RuntimeError:
                        pass

                exe_path = download_installer(url, filename=name, progress_cb=on_prog)

                def on_ok():
                    if not self.winfo_exists():
                        return
                    self.status_lbl.configure(text="✓ Instalador listo. Iniciando...", text_color=C_GREEN)
                    subprocess.Popen([exe_path], close_fds=True)
                    self.master.destroy()

                self.after(0, on_ok)
            except Exception as exc:
                def on_err():
                    if self.winfo_exists():
                        self.action_btn.configure(state="normal", text="⬇ Descargar e Instalar")
                        self.status_lbl.configure(text=f"✕ Error: {exc}", text_color=C_RED)
                try:
                    self.after(0, on_err)
                except RuntimeError:
                    pass

        threading.Thread(target=worker, daemon=True).start()

    def _start_git_pull(self):
        self.action_btn.configure(state="disabled", text="Actualizando...")
        self.status_lbl.configure(text="Ejecutando git pull --ff-only...", text_color=C_AMBER)

        def worker():
            ok, msg = run_git_fast_forward_pull(BASE_DIR)

            def on_done():
                if not self.winfo_exists():
                    return
                if ok:
                    self.action_btn.configure(text="✓ Actualizado")
                    self.status_lbl.configure(
                        text="✓ Actualizado. Reinicia la app para aplicar cambios.",
                        text_color=C_GREEN,
                    )
                else:
                    self.action_btn.configure(state="normal", text="⚡ Actualizar vía Git")
                    self.status_lbl.configure(text=f"✕ {msg[:80]}", text_color=C_RED)

            try:
                self.after(0, on_done)
            except RuntimeError:
                pass

        threading.Thread(target=worker, daemon=True).start()
