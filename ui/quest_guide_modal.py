"""
TarkovScope - Dossier Táctico Offline de Misiones (Wiki Dossier 100% Offline)
Permite consultar la guía paso a paso, plano topográfico con retícula de objetivo,
llaves necesarias con trueques, y cadena de progresión sin necesidad de salir al navegador web.
"""
import re
import webbrowser
import customtkinter as ctk
from typing import Any, Dict, List, Optional

from core.config import THEME
from core.datastore import get_datastore
from core.quest_guides_data import get_quest_tactical_guide, extract_required_keys_deep
from ui.theme import (
    C_AMBER, C_BG_DARKEST, C_BG_DEEP, C_BG_PANEL, C_BG_PANEL_ALT, C_BG_PANEL_ALT2,
    C_BLUE, C_BORDER, C_BORDER_ALT, C_EMERALD, C_GREEN_LIGHT, C_RED, C_RED_DARK,
    C_SLATE_700, C_SLATE_800, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_TEXT_SOFT, C_WHITE,
    ui_font
)
from ui.image_utils import get_trader_ctk_image, get_quest_objective_map_ctk_image
from ui.map_viewer_modal import open_map_viewer_modal


def extract_required_keys(q: Dict[str, Any]) -> List[str]:
    """Detecta nombres de llaves o keycards requeridas para la misión (helper retrocompatible)."""
    keys_found = []
    lines = q.get("objectives_lines", [])
    for line in lines:
        l_low = line.lower()
        if "key" in l_low or "llave" in l_low or "keycard" in l_low:
            m = re.search(
                r"((?:[A-Za-z0-9\.\'\-]+\s+){1,4}(?:key|keycard|marked\s+key|llave)(?:\s+[0-9a-zA-Z\-]+)?)",
                line,
                flags=re.IGNORECASE
            )
            if m:
                k_name = m.group(1).strip(" •-:,.")
                if len(k_name) > 3 and k_name.lower() not in [k.lower() for k in keys_found]:
                    keys_found.append(k_name)
    return keys_found[:3]


class QuestGuideModal(ctk.CTkToplevel):
    """
    Dossier Táctico Integral de Misión (100% Offline estilo Wiki Tarkov).
    Ofrece navegación multi-pestaña:
      - 🗺️ Guía Táctica & Mapa (Walkthrough paso a paso + Plano 2D con retícula lumínica de objetivo)
      - 🎯 Objetivos & Recompensas (Lista de tareas y desglose de EXP, dinero e ítems)
      - 🔑 Llaves & Equipamiento (Fichas de llaves con ubicación/trueques y recomendaciones tácticas)
      - 🔗 Cadena de Desbloqueo (Prerrequisitos, correlatividad y meta Kappa/Lightkeeper)
    """

    def __init__(self, parent, quest: Dict[str, Any], on_toggle_callback=None):
        super().__init__(parent)
        self.quest = quest
        self.on_toggle_callback = on_toggle_callback

        # Obtener ficha táctica unificada (curada o sintetizada con 100% cobertura)
        self.guide = get_quest_tactical_guide(quest)

        title = quest.get("title", "Misión")
        self.title(f"TarkovScope — Ficha Táctica: {title}")
        self.geometry("960x740")
        self.minsize(860, 620)
        self.configure(fg_color=C_BG_DARKEST)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._active_tab = "🗺️ Guía Táctica & Mapa"
        self._content_container = None
        self.map_img_label = None

        self._build_header()
        self._build_navigation_bar()
        self._build_content_area()
        self._build_footer()

    def _build_header(self):
        hdr = ctk.CTkFrame(
            self,
            fg_color=C_BG_PANEL,
            corner_radius=0,
            border_width=1,
            border_color=C_BORDER
        )
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        t_name = self.quest.get("trader_name", "Prapor")
        avatar_lbl = ctk.CTkLabel(hdr, text="")
        avatar_lbl.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=12)
        ctk_img = get_trader_ctk_image(t_name, size=(60, 60))
        if ctk_img:
            avatar_lbl.configure(image=ctk_img)

        title_row = ctk.CTkFrame(hdr, fg_color="transparent")
        title_row.grid(row=0, column=1, padx=4, pady=(12, 2), sticky="ew")

        ctk.CTkLabel(
            title_row,
            text=self.quest.get("title", ""),
            font=ui_font(20, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left", padx=(0, 10))

        if self.quest.get("is_kappa"):
            ctk.CTkLabel(
                title_row,
                text=" REQUERIDA KAPPA ",
                font=ui_font(11, "bold"),
                fg_color=C_AMBER,
                text_color=C_BG_DARKEST,
                corner_radius=4
            ).pack(side="left", padx=4)

        if self.quest.get("is_lightkeeper"):
            ctk.CTkLabel(
                title_row,
                text=" RUTA LIGHTKEEPER ",
                font=ui_font(11, "bold"),
                fg_color="#06B6D4",
                text_color=C_BG_DARKEST,
                corner_radius=4
            ).pack(side="left", padx=4)

        sub_row = ctk.CTkFrame(hdr, fg_color="transparent")
        sub_row.grid(row=1, column=1, padx=4, pady=(0, 12), sticky="ew")

        primary_map = self.quest.get("primary_map", "Cualquier Mapa")
        exp_val = self.quest.get("exp", 0)
        min_lvl = self.quest.get("min_player_level", 1)
        ctk.CTkLabel(
            sub_row,
            text=f"Trader: {t_name}   •   Mapa: {primary_map}   •   Nivel Mínimo PMC: {min_lvl}   •   EXP: +{exp_val:,}",
            font=ui_font(12, "bold"),
            text_color=C_TEXT_MUTED
        ).pack(side="left")

        is_done = bool(self.quest.get("completed", False))
        self.status_btn = ctk.CTkButton(
            hdr,
            text="✓ Misión Completada" if is_done else "Marcar Completada",
            width=170,
            height=36,
            corner_radius=6,
            fg_color="#16A34A" if is_done else C_SLATE_800,
            hover_color="#15803D" if is_done else THEME["accent_gold"],
            text_color=C_WHITE,
            font=ui_font(13, "bold"),
            command=self._toggle_status
        )
        self.status_btn.grid(row=0, column=2, rowspan=2, padx=16, pady=12)

    def _toggle_status(self):
        if self.on_toggle_callback:
            self.on_toggle_callback(self.quest)
            is_done = get_datastore().is_quest_completed(self.quest["id"])
            self.quest["completed"] = is_done
            self.status_btn.configure(
                text="✓ Misión Completada" if is_done else "Marcar Completada",
                fg_color="#16A34A" if is_done else C_SLATE_800
            )

    def _build_navigation_bar(self):
        nav_frame = ctk.CTkFrame(self, fg_color=C_BG_DARKEST, height=44, corner_radius=0)
        nav_frame.grid(row=1, column=0, sticky="ew", padx=14, pady=(8, 4))
        nav_frame.grid_columnconfigure(0, weight=1)

        tabs = [
            "🗺️ Guía Táctica & Mapa",
            "🎯 Objetivos & Recompensas",
            "🔑 Llaves & Equipamiento",
            "🔗 Cadena de Desbloqueo"
        ]

        self.seg_nav = ctk.CTkSegmentedButton(
            nav_frame,
            values=tabs,
            selected_color=THEME["accent_gold"],
            selected_hover_color="#B89658",
            unselected_color=C_BG_PANEL,
            unselected_hover_color=C_SLATE_800,
            text_color=C_WHITE,
            font=ui_font(12, "bold"),
            height=34,
            command=self._on_tab_change
        )
        self.seg_nav.set(self._active_tab)
        self.seg_nav.pack(fill="x", padx=2, pady=4)

    def _on_tab_change(self, selected_tab: str):
        self._active_tab = selected_tab
        self._render_active_tab_view()

    def _build_content_area(self):
        self._content_container = ctk.CTkFrame(self, fg_color="transparent")
        self._content_container.grid(row=2, column=0, sticky="nsew", padx=14, pady=(2, 6))
        self._content_container.grid_columnconfigure(0, weight=1)
        self._content_container.grid_rowconfigure(0, weight=1)

        self._render_active_tab_view()

    def _clear_content_container(self):
        for w in self._content_container.winfo_children():
            w.destroy()

    def _render_active_tab_view(self):
        self._clear_content_container()

        scroll = ctk.CTkScrollableFrame(
            self._content_container,
            fg_color=C_BG_DARKEST,
            corner_radius=6
        )
        scroll.grid(row=0, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        if self._active_tab == "🗺️ Guía Táctica & Mapa":
            self._render_tab_guide_and_map(scroll)
        elif self._active_tab == "🎯 Objetivos & Recompensas":
            self._render_tab_objectives_and_rewards(scroll)
        elif self._active_tab == "🔑 Llaves & Equipamiento":
            self._render_tab_keys_and_gear(scroll)
        elif self._active_tab == "🔗 Cadena de Desbloqueo":
            self._render_tab_progression_chain(scroll)

    # -------------------------------------------------------------
    # PESTAÑA 1: GUÍA TÁCTICA & MAPA
    # -------------------------------------------------------------
    def _render_tab_guide_and_map(self, parent):
        # 1. Alerta de Peligro Táctico (si aplica)
        danger_notes = self.guide.get("danger_notes", [])
        if danger_notes:
            danger_box = ctk.CTkFrame(
                parent,
                fg_color="#181113",
                corner_radius=8,
                border_width=1,
                border_color="#991B1B"
            )
            danger_box.pack(fill="x", padx=4, pady=(4, 10))
            ctk.CTkLabel(
                danger_box,
                text="⚠️ ADVERTENCIAS DE PELIGRO Y ZONAS CRÍTICAS",
                font=ui_font(13, "bold"),
                text_color="#F87171"
            ).pack(anchor="w", padx=14, pady=(8, 4))
            for dn in danger_notes:
                ctk.CTkLabel(
                    danger_box,
                    text=f"• {dn.lstrip('⚠️ ').strip()}",
                    font=ui_font(12),
                    text_color=C_TEXT,
                    justify="left",
                    wraplength=860
                ).pack(anchor="w", padx=16, pady=(1, 4))

        # 2. Tarjeta del Plano Táctico 2D con Retícula de Objetivo
        primary_map = self.guide.get("primary_map", "Cualquier Mapa")
        map_key = self.guide.get("map_key", "customs")
        obj_poi = self.guide.get("objective_poi", f"Zona de Misión en {primary_map}")

        map_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        map_card.pack(fill="x", padx=4, pady=(0, 12))
        map_card.grid_columnconfigure(0, weight=1)

        # Barra de título del mapa
        map_hdr = ctk.CTkFrame(map_card, fg_color="transparent")
        map_hdr.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(
            map_hdr,
            text=f"📍 PLANO TOPOGRÁFICO & LOCALIZACIÓN: {primary_map.upper()}",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(side="left")

        # Imagen del mapa táctico con retícula lumínica
        img_container = ctk.CTkFrame(map_card, fg_color="#07090E", corner_radius=6)
        img_container.pack(fill="x", padx=14, pady=4)

        self.map_img_label = ctk.CTkLabel(img_container, text="")
        self.map_img_label.pack(pady=8)

        # Cargar en hilo background sin bloquear la interfaz
        pin_coords = self.guide.get("map_pin", (0.50, 0.50))
        ctk_map = get_quest_objective_map_ctk_image(
            map_key=map_key,
            pin_coords=pin_coords,
            quest_title=self.quest.get("title", ""),
            objective_poi=obj_poi,
            target_size=(680, 360),
            widget_callback=lambda img: self.after(0, lambda: self._apply_map_image(img))
        )
        self.map_img_label.configure(image=ctk_map)

        # Barra de acciones del mapa
        map_action_bar = ctk.CTkFrame(map_card, fg_color="transparent")
        map_action_bar.pack(fill="x", padx=14, pady=(4, 10))

        ctk.CTkLabel(
            map_action_bar,
            text=f"🎯 Objetivo: {obj_poi}",
            font=ui_font(12, "bold"),
            text_color="#38BDF8"
        ).pack(side="left", padx=2)

        if primary_map and primary_map != "Cualquier Mapa":
            ctk.CTkButton(
                map_action_bar,
                text=f"🔍 Abrir en Visor Completo ({primary_map})",
                height=30,
                corner_radius=5,
                fg_color="#1E3A8A",
                hover_color="#2563EB",
                text_color=C_WHITE,
                font=ui_font(12, "bold"),
                command=lambda mp=primary_map: open_map_viewer_modal(self, mp)
            ).pack(side="right")

        # 3. Fases de Ejecución Paso a Paso (Walkthrough en Español)
        phases_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        phases_card.pack(fill="x", padx=4, pady=(0, 8))

        ctk.CTkLabel(
            phases_card,
            text="📋 FASES TÁCTICAS DE EJECUCIÓN (PASO A PASO EN ESPAÑOL)",
            font=ui_font(13, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w", padx=14, pady=(10, 8))

        phases = self.guide.get("phases", [])
        for idx, ph in enumerate(phases):
            p_box = ctk.CTkFrame(
                phases_card,
                fg_color=C_BG_PANEL,
                corner_radius=6,
                border_width=1,
                border_color="#1F293D"
            )
            p_box.pack(fill="x", padx=12, pady=(0, 8))

            p_hdr = ctk.CTkFrame(p_box, fg_color="transparent")
            p_hdr.pack(fill="x", padx=10, pady=(8, 4))

            ctk.CTkLabel(
                p_hdr,
                text=ph.get("phase", f"FASE {idx+1}"),
                font=ui_font(13, "bold"),
                text_color=C_WHITE
            ).pack(side="left")

            badge = ph.get("badge", "MISIÓN")
            badge_color = C_SLATE_700
            if "EQUIPO" in badge or "LLAVE" in badge:
                badge_color = "#0284C7"
            elif "INFILTRACIÓN" in badge or "RUTA" in badge:
                badge_color = "#D97706"
            elif "OBJETIVO" in badge or "PARTE" in badge:
                badge_color = "#2563EB"
            elif "EXTRACCIÓN" in badge:
                badge_color = "#16A34A"
            elif "COMBATE" in badge:
                badge_color = "#DC2626"

            ctk.CTkLabel(
                p_hdr,
                text=f" {badge} ",
                font=ui_font(10, "bold"),
                fg_color=badge_color,
                text_color=C_WHITE,
                corner_radius=4
            ).pack(side="left", padx=8)

            desc = ph.get("desc", "")
            ctk.CTkLabel(
                p_box,
                text=desc,
                font=ui_font(13),
                text_color=C_TEXT,
                justify="left",
                wraplength=850
            ).pack(anchor="w", padx=12, pady=(0, 10))

    def _apply_map_image(self, ctk_img: ctk.CTkImage):
        """Aplica la imagen del mapa renderizado de forma segura tras el cálculo en background."""
        if not self.winfo_exists():
            return
        if self.map_img_label and self.map_img_label.winfo_exists():
            self.map_img_label.configure(image=ctk_img)

    # -------------------------------------------------------------
    # PESTAÑA 2: OBJETIVOS & RECOMPENSAS
    # -------------------------------------------------------------
    def _render_tab_objectives_and_rewards(self, parent):
        # 1. Objetivos
        obj_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        obj_card.pack(fill="x", padx=4, pady=(4, 10))

        ctk.CTkLabel(
            obj_card,
            text="🎯 OBJETIVOS TÁCTICOS Y CONDICIONES DE MISIÓN",
            font=ui_font(13, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w", padx=14, pady=(10, 6))

        obj_lines = self.quest.get("objectives_lines") or ["• Completar los objetivos asignados por el Trader."]
        for obj in obj_lines:
            row = ctk.CTkFrame(obj_card, fg_color=C_BG_PANEL, corner_radius=6)
            row.pack(fill="x", padx=12, pady=(0, 6))

            ctk.CTkLabel(
                row,
                text="✔",
                font=ui_font(12, "bold"),
                text_color=THEME["accent_gold"]
            ).pack(side="left", padx=(10, 6), pady=6)

            ctk.CTkLabel(
                row,
                text=obj.lstrip("• ").strip(),
                font=ui_font(13),
                text_color=C_TEXT,
                justify="left",
                wraplength=820
            ).pack(side="left", padx=4, pady=6)

        # 2. Recompensas
        rew_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        rew_card.pack(fill="x", padx=4, pady=(0, 10))

        ctk.CTkLabel(
            rew_card,
            text="🎁 RECOMPENSAS Y DESBLOQUEOS AL ENTREGAR",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        rew_lines = self.quest.get("rewards_lines") or [f"• +{self.quest.get('exp', 0):,} EXP"]
        for rew in rew_lines:
            row = ctk.CTkFrame(rew_card, fg_color=C_BG_PANEL, corner_radius=6)
            row.pack(fill="x", padx=12, pady=(0, 6))

            icon = "⭐" if "exp" in rew.lower() else "📦"
            if "₽" in rew or "rub" in rew.lower() or "$" in rew or "eur" in rew.lower():
                icon = "💰"
            elif "rep" in rew.lower() or "+" in rew:
                icon = "📈"

            ctk.CTkLabel(
                row,
                text=icon,
                font=ui_font(12)
            ).pack(side="left", padx=(10, 6), pady=6)

            ctk.CTkLabel(
                row,
                text=rew.lstrip("• ").strip(),
                font=ui_font(13),
                text_color=C_TEXT_SOFT,
                justify="left",
                wraplength=820
            ).pack(side="left", padx=4, pady=6)

    # -------------------------------------------------------------
    # PESTAÑA 3: LLAVES & EQUIPAMIENTO
    # -------------------------------------------------------------
    def _render_tab_keys_and_gear(self, parent):
        keys = self.guide.get("keys", [])

        # Tarjeta de Llaves
        keys_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        keys_card.pack(fill="x", padx=4, pady=(4, 10))

        ctk.CTkLabel(
            keys_card,
            text="🔑 LLAVES Y TARJETAS DE ACCESO REQUERIDAS",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        if keys:
            for k in keys:
                k_box = ctk.CTkFrame(
                    keys_card,
                    fg_color=C_BG_PANEL,
                    corner_radius=6,
                    border_width=1,
                    border_color="#334155"
                )
                k_box.pack(fill="x", padx=12, pady=(0, 8))

                k_title_row = ctk.CTkFrame(k_box, fg_color="transparent")
                k_title_row.pack(fill="x", padx=10, pady=(8, 4))

                ctk.CTkLabel(
                    k_title_row,
                    text="🗝️",
                    font=ui_font(15)
                ).pack(side="left", padx=(0, 6))

                ctk.CTkLabel(
                    k_title_row,
                    text=k.get("name", "Llave Requerida"),
                    font=ui_font(14, "bold"),
                    text_color=THEME["accent_gold"]
                ).pack(side="left")

                loc = k.get("location", "")
                if loc:
                    ctk.CTkLabel(
                        k_box,
                        text=f"📍 Ubicación / Spawn: {loc}",
                        font=ui_font(12),
                        text_color=C_TEXT,
                        justify="left",
                        wraplength=840
                    ).pack(anchor="w", padx=14, pady=(2, 2))

                barter = k.get("barter", "")
                if barter:
                    ctk.CTkLabel(
                        k_box,
                        text=f"🔄 Trueques / Compra: {barter}",
                        font=ui_font(12),
                        text_color=C_GREEN_LIGHT,
                        justify="left",
                        wraplength=840
                    ).pack(anchor="w", padx=14, pady=(2, 8))
        else:
            no_key_box = ctk.CTkFrame(keys_card, fg_color=C_BG_PANEL, corner_radius=6)
            no_key_box.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkLabel(
                no_key_box,
                text="✓ No se requiere ninguna llave ni tarjeta de acceso para ingresar a las zonas de esta misión. El paso es de acceso libre.",
                font=ui_font(13),
                text_color=C_GREEN_LIGHT,
                justify="left",
                wraplength=840
            ).pack(anchor="w", padx=14, pady=10)

        # Tarjeta de Equipamiento Táctico Recomendado
        gear_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        gear_card.pack(fill="x", padx=4, pady=(0, 10))

        ctk.CTkLabel(
            gear_card,
            text="🎒 EQUIPAMIENTO RECOMENDADO Y LOGÍSTICA DE POUCH",
            font=ui_font(13, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w", padx=14, pady=(10, 6))

        obj_text = " ".join(self.quest.get("objectives_lines", [])).lower()
        tips = []

        if keys:
            tips.append("🔒 Contenedor Seguro (Pouch): Guarda las llaves en un Docs Case, Keytool o SICC Case en tu pouch para no perderlas al morir.")
        if "marker" in obj_text or "ms2000" in obj_text or "baliza" in obj_text:
            tips.append("📡 Balizas MS2000: Llévalas en tu contenedor seguro (Alpha/Beta/Gamma/Epsilon/Kappa). Puedes colocarlas directamente desde el pouch sin exponerlas.")
        if "wi-fi" in obj_text or "camera" in obj_text or "jammer" in obj_text:
            tips.append("📹 Dispositivos de Señal: Las cámaras Wi-Fi y jammers se consumen desde el pouch seguro al fijarlas.")
        if "fir" in obj_text or "found in raid" in obj_text or "en raid" in obj_text:
            tips.append("📦 Estado FiR: Para que los ítems cuenten como Found in Raid, debes extraer como 'Survived' (mínimo 7 minutos de raid o 200+ EXP).")
        if "night" in obj_text or "noche" in obj_text or "nocturno" in obj_text:
            tips.append("🌙 Visión Nocturna: Se recomienda visor NVG PNV-10T o AN/PVS-14 con montura Norotos en casco nivel 3+.")
        if not tips:
            tips.append("🛡️ Blindaje y Balística: Lleva chaleco clase 4 o superior (Thor / Korund) y munición con penetración 35+ para atravesar armadura Scav y PMC.")
            tips.append("🩹 Kit Médico Táctico: Lleva un kit Salewa o IFAK en teclas rápidas, una férula de aluminio (Splint) y analgésico inyectable (Morphine / Propital).")

        for tip in tips:
            t_row = ctk.CTkFrame(gear_card, fg_color=C_BG_PANEL, corner_radius=6)
            t_row.pack(fill="x", padx=12, pady=(0, 6))
            ctk.CTkLabel(
                t_row,
                text=tip,
                font=ui_font(13),
                text_color=C_TEXT,
                justify="left",
                wraplength=840
            ).pack(anchor="w", padx=12, pady=8)

    # -------------------------------------------------------------
    # PESTAÑA 4: CADENA DE DESBLOQUEO
    # -------------------------------------------------------------
    def _render_tab_progression_chain(self, parent):
        chain_card = ctk.CTkFrame(
            parent,
            fg_color=C_BG_PANEL_ALT2,
            corner_radius=8,
            border_width=1,
            border_color=C_BORDER
        )
        chain_card.pack(fill="x", padx=4, pady=(4, 10))

        ctk.CTkLabel(
            chain_card,
            text="🔗 ÁRBOL DE PROGRESIÓN Y CORRELATIVIDAD",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        # Prerrequisitos
        prereqs = self.quest.get("prereq_titles") or []
        pre_box = ctk.CTkFrame(chain_card, fg_color=C_BG_PANEL, corner_radius=6)
        pre_box.pack(fill="x", padx=12, pady=(0, 8))

        ctk.CTkLabel(
            pre_box,
            text="⬅️ MISIONES PREVIAS REQUERIDAS (PRERREQUISITOS):",
            font=ui_font(12, "bold"),
            text_color=C_AMBER
        ).pack(anchor="w", padx=12, pady=(8, 2))

        if prereqs:
            for p in prereqs:
                ctk.CTkLabel(
                    pre_box,
                    text=f"  • {p}",
                    font=ui_font(13),
                    text_color=C_TEXT,
                    justify="left"
                ).pack(anchor="w", padx=14, pady=1)
        else:
            ctk.CTkLabel(
                pre_box,
                text="  • Ninguna misión previa requerida. Disponible directamente por nivel o inicio de capítulo.",
                font=ui_font(13),
                text_color=C_GREEN_LIGHT,
                justify="left"
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(pre_box, height=4, fg_color="transparent").pack()

        # Misión Actual
        cur_box = ctk.CTkFrame(
            chain_card,
            fg_color="#182234",
            corner_radius=6,
            border_width=1,
            border_color=THEME["accent_gold"]
        )
        cur_box.pack(fill="x", padx=12, pady=(0, 8))
        ctk.CTkLabel(
            cur_box,
            text=f"📍 ENCARGO ACTUAL: {self.quest.get('title', '')} ({self.quest.get('trader_name', '')})",
            font=ui_font(13, "bold"),
            text_color=THEME["accent_gold"]
        ).pack(anchor="w", padx=14, pady=10)

        # Desbloqueos Posteriores
        unlocks = self.quest.get("unlocks_titles") or []
        unl_box = ctk.CTkFrame(chain_card, fg_color=C_BG_PANEL, corner_radius=6)
        unl_box.pack(fill="x", padx=12, pady=(0, 10))

        ctk.CTkLabel(
            unl_box,
            text="➡️ MISIONES QUE DESBLOQUEA AL COMPLETAR:",
            font=ui_font(12, "bold"),
            text_color=C_BLUE
        ).pack(anchor="w", padx=12, pady=(8, 2))

        if unlocks:
            for u in unlocks:
                ctk.CTkLabel(
                    unl_box,
                    text=f"  • {u}",
                    font=ui_font(13),
                    text_color=C_TEXT,
                    justify="left"
                ).pack(anchor="w", padx=14, pady=1)
        else:
            ctk.CTkLabel(
                unl_box,
                text="  • Fin de rama o sin desbloqueos directos registrados.",
                font=ui_font(13),
                text_color=C_TEXT_MUTED,
                justify="left"
            ).pack(anchor="w", padx=14, pady=2)
        ctk.CTkFrame(unl_box, height=4, fg_color="transparent").pack()

        # Metas Especiales (Kappa / Lightkeeper)
        if self.quest.get("is_kappa") or self.quest.get("is_lightkeeper"):
            meta_box = ctk.CTkFrame(
                chain_card,
                fg_color="#141E18",
                corner_radius=6,
                border_width=1,
                border_color="#15803D"
            )
            meta_box.pack(fill="x", padx=12, pady=(0, 10))
            ctk.CTkLabel(
                meta_box,
                text="🏆 RELEVANCIA EN EL ENDGAME (META DEL JUEGO):",
                font=ui_font(12, "bold"),
                text_color=C_GREEN_LIGHT
            ).pack(anchor="w", padx=12, pady=(8, 2))

            if self.quest.get("is_kappa"):
                ctk.CTkLabel(
                    meta_box,
                    text="  • Esencial para KAPPA: Esta misión es requisito obligatorio para que Fence te entregue la misión final 'Collector' que otorga el Contenedor Seguro Kappa (3x4).",
                    font=ui_font(12),
                    text_color=C_TEXT,
                    justify="left",
                    wraplength=840
                ).pack(anchor="w", padx=14, pady=2)

            if self.quest.get("is_lightkeeper"):
                ctk.CTkLabel(
                    meta_box,
                    text="  • Esencial para LIGHTKEEPER: Forma parte de la cadena de confianza para codificar el transmisor DSP y tener acceso sin hostilidad al Faro de Lighthouse.",
                    font=ui_font(12),
                    text_color=C_TEXT,
                    justify="left",
                    wraplength=840
                ).pack(anchor="w", padx=14, pady=2)
            ctk.CTkFrame(meta_box, height=4, fg_color="transparent").pack()

    def _build_footer(self):
        ftr = ctk.CTkFrame(self, fg_color=C_BG_PANEL, corner_radius=0, height=52)
        ftr.grid(row=3, column=0, sticky="ew")

        primary_map = self.quest.get("primary_map", "Cualquier Mapa")
        if primary_map and primary_map != "Cualquier Mapa":
            ctk.CTkButton(
                ftr,
                text=f"🗺️ Abrir Mapa Táctico Interactivo ({primary_map})",
                height=34,
                corner_radius=6,
                fg_color="#1E3A8A",
                hover_color="#2563EB",
                text_color=C_WHITE,
                font=ui_font(13, "bold"),
                command=lambda mp=primary_map: open_map_viewer_modal(self, mp)
            ).pack(side="left", padx=16, pady=9)

        if self.quest.get("wiki_url"):
            ctk.CTkButton(
                ftr,
                text="🌐 Ver en Wiki Oficial ↗",
                height=34,
                corner_radius=6,
                fg_color=C_SLATE_800,
                hover_color=C_SLATE_700,
                text_color=THEME["accent_gold"],
                font=ui_font(12, "bold"),
                command=lambda u=self.quest["wiki_url"]: webbrowser.open(u)
            ).pack(side="left", padx=6, pady=9)

        ctk.CTkButton(
            ftr,
            text="Cerrar Guía",
            width=120,
            height=34,
            corner_radius=6,
            fg_color=C_RED_DARK,
            hover_color="#B91C1C",
            text_color=C_WHITE,
            font=ui_font(13, "bold"),
            command=self.destroy
        ).pack(side="right", padx=16, pady=9)
