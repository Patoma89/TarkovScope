"""
TarkovScope - Pestaña Quest Tracker: ruta óptima por mapa según el spawn.

Flujo: elegís el mapa, marcás las quests activas, elegís tu spawn (lista o clic en el mapa)
o dejás que la app busque el mejor, y se calcula el orden de objetivos más corto hasta la
mejor extracción. Datos de posiciones: tarkov.dev (core/quest_route_data.py).
"""
import json
import logging
import threading
from typing import Any, Dict, List, Optional, Set, Tuple

import customtkinter as ctk

from core.config import THEME
from core.progression_plan_store import load_config as load_progression_config
from core.quest_route_data import get_route_maps, get_tasks_for_map, load_route_dataset, objective_label
from core.quest_route_planner import RoutePlan, Stop, plan_route, rank_spawns
from core.route_map_renderer import render_route_map, world_to_view
from core.user_data import get_user_preference, set_user_preference
from ui.theme import (C_BG_DARKEST, C_BLUE, C_EMERALD, C_GREEN_LIGHT, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED,
                      C_WHITE, ui_font)

PREF_ACTIVE = "quest_tracker_active"
PREF_MAP = "quest_tracker_map"
AUTO_SPAWN_LABEL = "★ Elegir el mejor spawn"
MAP_VIEW_SIZE = (900, 600)
QUEST_ROWS_PER_BATCH = 15
logger = logging.getLogger("TarkovScope.QuestTracker")
TIP_TEXT = "Tip: hacé clic en el mapa sobre tu punto de aparición para elegir ese spawn."


class TabQuestTracker(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.dataset: Dict[str, Any] = {}
        self.maps: List[Dict[str, Any]] = []
        self.map_key: str = ""
        self.active: Set[str] = self._load_active()
        self.spawn_index: int = -1  # -1 = automático
        self.only_active = ctk.BooleanVar(value=False)
        self.zoom_route = ctk.BooleanVar(value=True)
        self._render_token = 0
        self._view: Optional[Dict[str, Any]] = None
        self._ctk_img: Optional[ctk.CTkImage] = None
        self._quest_rows: List[ctk.CTkFrame] = []
        self._list_token = 0
        self._search_after: Optional[str] = None
        self.faction: str = "BEAR"

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self.reload_data()

    # ------------------------------------------------------------------ persistencia
    def _load_active(self) -> Set[str]:
        try:
            return set(json.loads(get_user_preference(PREF_ACTIVE, "[]") or "[]"))
        except (ValueError, TypeError):
            return set()

    def _save_active(self) -> None:
        set_user_preference(PREF_ACTIVE, json.dumps(sorted(self.active)))

    # ------------------------------------------------------------------ layout
    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=330, fg_color=THEME["bg_card"], corner_radius=10,
                            border_width=1, border_color=THEME["border"])
        side.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)
        side.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(side, text="QUEST TRACKER", font=ui_font(17, "bold"),
                     text_color=THEME["accent_orange"]).grid(row=0, column=0, padx=16, pady=(16, 2), sticky="w")
        ctk.CTkLabel(side, text="Marcá tus quests activas y calculá la ruta.",
                     font=ui_font(12), text_color=C_TEXT_MUTED).grid(row=1, column=0, padx=16, pady=(0, 10), sticky="w")

        self.map_menu = ctk.CTkOptionMenu(
            side, values=["—"], command=self._on_map_menu, font=ui_font(13, "bold"),
            fg_color=THEME["btn_surface"], button_color=THEME["accent_orange"],
            button_hover_color=THEME["btn_hover"], dropdown_font=ui_font(13), height=32)
        self.map_menu.grid(row=2, column=0, padx=14, pady=(0, 8), sticky="ew")

        # Sin textvariable: CustomTkinter oculta el placeholder si la entrada tiene variable.
        self.search_entry = ctk.CTkEntry(side, placeholder_text="Buscar quest...",
                                         font=ui_font(13), height=32, fg_color=THEME["bg_inset"],
                                         border_color=THEME["border"])
        self.search_entry.grid(row=3, column=0, padx=14, pady=(0, 6), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _e: self._on_search_key())

        opts = ctk.CTkFrame(side, fg_color="transparent")
        opts.grid(row=4, column=0, padx=14, pady=(0, 6), sticky="ew")
        ctk.CTkCheckBox(opts, text="Solo activas", variable=self.only_active, command=self._populate_quests,
                        font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=THEME["accent_orange"],
                        height=22, width=24).pack(side="left")
        self.count_lbl = ctk.CTkLabel(opts, text="", font=ui_font(12), text_color=C_TEXT_DIM)
        self.count_lbl.pack(side="right")

        self.quest_scroll = ctk.CTkScrollableFrame(side, fg_color="transparent")
        self.quest_scroll.grid(row=5, column=0, padx=6, pady=(0, 10), sticky="nsew")
        self.quest_scroll.grid_columnconfigure(0, weight=1)

    def _build_main(self):
        main = ctk.CTkScrollableFrame(self, fg_color=THEME["bg_card"], corner_radius=10,
                                      border_width=1, border_color=THEME["border"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        self.main = main

        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="ew")
        ctk.CTkLabel(bar, text="Spawn:", font=ui_font(13, "bold"), text_color=C_TEXT).pack(side="left", padx=(0, 6))
        self.spawn_menu = ctk.CTkOptionMenu(
            bar, values=[AUTO_SPAWN_LABEL], command=self._on_spawn_menu, width=330, font=ui_font(13),
            fg_color=THEME["btn_surface"], button_color=C_EMERALD, button_hover_color=THEME["btn_hover"],
            dropdown_font=ui_font(12), height=32)
        self.spawn_menu.pack(side="left")
        ctk.CTkCheckBox(bar, text="Zoom a la ruta", variable=self.zoom_route, command=self._recalculate,
                        font=ui_font(12, "bold"), text_color=C_TEXT, fg_color=THEME["accent_orange"],
                        height=22, width=24).pack(side="left", padx=12)
        self.status_lbl = ctk.CTkLabel(bar, text="", font=ui_font(12), text_color=C_TEXT_DIM)
        self.status_lbl.pack(side="right")

        self.tip_lbl = ctk.CTkLabel(main, text=TIP_TEXT, font=ui_font(12), text_color=C_TEXT_DIM)
        self.tip_lbl.grid(row=1, column=0, padx=16, sticky="w")

        self.map_lbl = ctk.CTkLabel(main, text="", fg_color=THEME["bg_inset"], corner_radius=8,
                                    width=MAP_VIEW_SIZE[0], height=MAP_VIEW_SIZE[1], cursor="crosshair")
        self.map_lbl.grid(row=2, column=0, padx=14, pady=8)
        self.map_lbl.bind("<Button-1>", self._on_map_click)

        self.steps_frame = ctk.CTkFrame(main, fg_color="transparent")
        self.steps_frame.grid(row=3, column=0, padx=14, pady=(4, 16), sticky="ew")
        self.steps_frame.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------ datos
    def _load_faction(self) -> str:
        try:
            return load_progression_config().get("faction", "BEAR") or "BEAR"
        except Exception:
            return "BEAR"

    def _tasks_here(self, map_key: Optional[str] = None) -> List[Dict[str, Any]]:
        return get_tasks_for_map(map_key or self.map_key, self.dataset, self.faction)

    def reload_data(self):
        self.dataset = load_route_dataset(force=True)
        self.faction = self._load_faction()
        self.maps = get_route_maps(self.dataset)
        if not self.maps:
            self.map_menu.configure(values=["Sin datos"])
            self.map_menu.set("Sin datos")
            self._show_message("No hay datos de rutas. Sincronizá la base de datos con conexión a internet.")
            return
        names = [m["name"] for m in self.maps]
        self.map_menu.configure(values=names)
        saved = get_user_preference(PREF_MAP, "")
        initial = next((m for m in self.maps if m["key"] == saved), None)
        if initial is None:
            # Por defecto, el mapa con más quests activas.
            initial = max(self.maps, key=lambda m: sum(
                1 for t in self._tasks_here(m["key"]) if t["name"] in self.active))
        self._select_map(initial["key"])

    def _current_map(self) -> Dict[str, Any]:
        return self.dataset.get("maps", {}).get(self.map_key, {})

    def _on_map_menu(self, name: str):
        m = next((m for m in self.maps if m["name"] == name), None)
        if m:
            self._select_map(m["key"])

    def _select_map(self, key: str):
        self.map_key = key
        set_user_preference(PREF_MAP, key)
        m = self._current_map()
        self.map_menu.set(m.get("name", key))
        self.spawn_index = -1
        labels = [AUTO_SPAWN_LABEL] + [s["label"] for s in m.get("spawns", [])]
        self.spawn_menu.configure(values=labels)
        self.spawn_menu.set(AUTO_SPAWN_LABEL)
        self._populate_quests()
        self._recalculate()

    def load_plan(self, map_key: str, quest_names: List[str], caption: str = "") -> None:
        """Lo usa el Planner de Progresión: carga el mapa y deja activas solo las quests de esa raid."""
        self.active = set(quest_names)
        self._save_active()
        self.only_active.set(True)
        self.faction = self._load_faction()
        if caption:
            self.tip_lbl.configure(text=f"{caption}  ·  {TIP_TEXT}", text_color=THEME["accent_gold"])
        if map_key in self.dataset.get("maps", {}):
            self._select_map(map_key)
        else:
            self._populate_quests()
            self._recalculate()

    def _on_search_key(self):
        """Debounce del buscador: redibuja cuando se deja de tipear."""
        if self._search_after is not None:
            self.after_cancel(self._search_after)
        self._search_after = self.after(150, self._populate_quests)

    def _populate_quests(self):
        self._search_after = None
        self._list_token += 1
        token = self._list_token
        for w in self.quest_scroll.winfo_children():
            w.destroy()
        if not self.map_key:
            return
        query = self.search_entry.get().strip().lower()
        tasks = self._tasks_here()
        n_active = sum(1 for t in tasks if t["name"] in self.active)
        self.count_lbl.configure(text=f"{n_active} activas · {len(tasks)} en el mapa")
        tasks.sort(key=lambda t: (t["name"] not in self.active, t["name"].lower()))
        visible = [t for t in tasks
                   if (not self.only_active.get() or t["name"] in self.active)
                   and (not query or query in t["name"].lower())]
        if not visible:
            ctk.CTkLabel(self.quest_scroll, text="Ninguna quest coincide.", font=ui_font(12),
                         text_color=C_TEXT_DIM).grid(row=0, column=0, pady=12)
            return

        def render_batch(start: int):
            if token != self._list_token or not self.winfo_exists():
                return
            for row, t in enumerate(visible[start:start + QUEST_ROWS_PER_BATCH], start=start):
                self._quest_row(row, t)
            if start + QUEST_ROWS_PER_BATCH < len(visible):
                self.after(4, lambda: render_batch(start + QUEST_ROWS_PER_BATCH))

        render_batch(0)

    def _quest_row(self, row: int, t: Dict[str, Any]):
        is_active = t["name"] in self.active
        var = ctk.BooleanVar(value=is_active)
        n_pos = sum(1 for o in t["objectives"] if o.get("candidates"))
        sub = f"{t['trader'] or 'Trader'} · {n_pos} punto(s) en el mapa"
        cell = ctk.CTkFrame(self.quest_scroll, fg_color=THEME["bg_row"] if is_active else "transparent",
                            corner_radius=6)
        cell.grid(row=row, column=0, sticky="ew", pady=1)
        cell.grid_columnconfigure(0, weight=1)
        ctk.CTkCheckBox(cell, text=t["name"], variable=var, font=ui_font(13, "bold"),
                        text_color=C_WHITE if is_active else C_TEXT_MUTED,
                        fg_color=THEME["accent_orange"], height=22,
                        command=lambda name=t["name"], v=var: self._toggle_quest(name, v.get())
                        ).grid(row=0, column=0, padx=8, pady=(5, 0), sticky="w")
        ctk.CTkLabel(cell, text=sub, font=ui_font(11), text_color=C_TEXT_DIM
                     ).grid(row=1, column=0, padx=38, pady=(0, 4), sticky="w")

    def _toggle_quest(self, name: str, on: bool):
        if on:
            self.active.add(name)
        else:
            self.active.discard(name)
        self._save_active()
        self._populate_quests()
        self._recalculate()

    def _on_spawn_menu(self, label: str):
        spawns = self._current_map().get("spawns", [])
        self.spawn_index = next((i for i, s in enumerate(spawns) if s["label"] == label), -1)
        self._recalculate()

    def _on_map_click(self, event):
        if not self._view:
            return
        spawns = self._current_map().get("spawns", [])
        if not spawns:
            return
        # El CTkLabel centra la imagen: convertir el clic a coordenadas de la imagen.
        img_w, img_h = self._ctk_img.cget("size") if self._ctk_img else MAP_VIEW_SIZE
        lbl_w, lbl_h = self.map_lbl.winfo_width(), self.map_lbl.winfo_height()
        scaling = self.map_lbl._get_widget_scaling() if hasattr(self.map_lbl, "_get_widget_scaling") else 1.0
        ix = event.x / scaling - (lbl_w / scaling - img_w) / 2
        iy = event.y / scaling - (lbl_h / scaling - img_h) / 2
        best, best_d = -1, float("inf")
        for i, s in enumerate(spawns):
            sx, sy = world_to_view(s["pos"], self._view)
            d = (sx - ix) ** 2 + (sy - iy) ** 2
            if d < best_d:
                best, best_d = i, d
        if best >= 0 and best_d <= 60 ** 2:
            self.spawn_index = best
            self.spawn_menu.set(spawns[best]["label"])
            self._recalculate()

    # ------------------------------------------------------------------ cálculo
    def _active_stops(self) -> Tuple[List[Stop], List[Tuple[str, str]], List[Tuple[float, float, float]]]:
        """Paradas con posición, objetivos sin posición (durante la raid) y ubicaciones alternativas."""
        stops: List[Stop] = []
        loose: List[Tuple[str, str]] = []
        for t in self._tasks_here():
            if t["name"] not in self.active:
                continue
            for o in t["objectives"]:
                if o.get("optional"):
                    continue
                cands = [tuple(c) for c in o.get("candidates") or []]
                if cands:
                    stops.append(Stop(f"{t['name']}#{o['index']}", objective_label(o), t["name"], cands))
                else:
                    loose.append((t["name"], objective_label(o)))
        return stops, loose, []

    def _recalculate(self):
        if not self.map_key:
            return
        self._render_token += 1
        token = self._render_token
        m = self._current_map()
        stops, loose, _ = self._active_stops()
        spawns = m.get("spawns", [])
        extracts = [(e["name"], tuple(e["pos"])) for e in m.get("extracts", [])]
        spawn_index = self.spawn_index
        zoom = self.zoom_route.get()
        self.status_lbl.configure(text="Calculando ruta...")

        def worker():
            try:
                ranking: List[Tuple[str, RoutePlan]] = []
                plan: Optional[RoutePlan] = None
                chosen = spawn_index
                if stops and spawns:
                    if chosen < 0:
                        ranking = rank_spawns([(s["label"], tuple(s["pos"])) for s in spawns], stops, extracts)
                        best_label = ranking[0][0]
                        chosen = next(i for i, s in enumerate(spawns) if s["label"] == best_label)
                        plan = ranking[0][1]
                    else:
                        plan = plan_route(tuple(spawns[chosen]["pos"]), stops, extracts)
                alts = []
                if plan:
                    for leg in plan.stop_legs:
                        alts += [c for i, c in enumerate(leg.stop.candidates) if i != leg.candidate_index]
                img, view = render_route_map(self.map_key, plan, spawns, chosen, m.get("extracts", []),
                                             alts, crop_to_route=zoom and plan is not None,
                                             target_size=MAP_VIEW_SIZE)
            except Exception as exc:
                logger.exception("Fallo al calcular la ruta del Quest Tracker")
                err = str(exc) or exc.__class__.__name__
                self.after(0, lambda: self._apply_error(token, err))
                return
            self.after(0, lambda: self._apply_result(token, img, view, plan, ranking, chosen, loose, len(stops)))

        threading.Thread(target=worker, daemon=True).start()

    def _apply_error(self, token: int, err: str):
        if not self.winfo_exists() or token != self._render_token:
            return
        self.status_lbl.configure(text="Error al calcular la ruta")
        self._show_message(f"No se pudo calcular la ruta: {err}\n\n"
                           "Probá sincronizar la base de datos o regenerar los mapas.")

    def _apply_result(self, token, img, view, plan, ranking, chosen, loose, n_stops):
        if not self.winfo_exists() or token != self._render_token:
            return
        self._view = view
        self._ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
        self.map_lbl.configure(image=self._ctk_img, text="")
        if self.spawn_index < 0 and 0 <= chosen < len(self._current_map().get("spawns", [])):
            self.status_lbl.configure(text="Spawn elegido automáticamente")
        else:
            self.status_lbl.configure(text="")
        self._render_steps(plan, ranking, chosen, loose, n_stops)

    # ------------------------------------------------------------------ texto de la ruta
    def _show_message(self, text: str):
        for w in self.steps_frame.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.steps_frame, text=text, font=ui_font(13), text_color=C_TEXT_MUTED,
                     wraplength=820, justify="left").grid(row=0, column=0, sticky="w")

    def _step_row(self, row: int, badge: str, color: str, title: str, detail: str):
        f = ctk.CTkFrame(self.steps_frame, fg_color=THEME["bg_row"], corner_radius=6)
        f.grid(row=row, column=0, sticky="ew", pady=2)
        f.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(f, text=badge, width=34, height=28, corner_radius=14, fg_color=color,
                     text_color=C_BG_DARKEST, font=ui_font(13, "bold")).grid(row=0, column=0, rowspan=2, padx=8, pady=6)
        ctk.CTkLabel(f, text=title, font=ui_font(13, "bold"), text_color=C_WHITE, anchor="w"
                     ).grid(row=0, column=1, sticky="w", pady=(5, 0))
        ctk.CTkLabel(f, text=detail, font=ui_font(12), text_color=C_TEXT_MUTED, anchor="w"
                     ).grid(row=1, column=1, sticky="w", pady=(0, 5))

    def _render_steps(self, plan: Optional[RoutePlan], ranking, chosen: int, loose, n_stops: int):
        for w in self.steps_frame.winfo_children():
            w.destroy()
        spawns = self._current_map().get("spawns", [])
        if n_stops == 0:
            msg = "Marcá al menos una quest activa con objetivos en este mapa para calcular la ruta."
            if loose:
                msg = "Las quests activas no tienen puntos fijos en este mapa (por ejemplo, eliminar enemigos)."
            self._show_message(msg)
            self._render_loose(loose, 1)
            return
        if not plan:
            self._show_message("Este mapa no tiene spawns PMC en los datos de tarkov.dev.")
            return

        row = 0
        spawn_label = spawns[chosen]["label"] if 0 <= chosen < len(spawns) else "Spawn"
        ctk.CTkLabel(self.steps_frame, text=f"RUTA SUGERIDA · {round(plan.total_distance)} m aprox.",
                     font=ui_font(16, "bold"), text_color=THEME["accent_orange"]
                     ).grid(row=row, column=0, sticky="w", pady=(0, 6))
        row += 1
        self._step_row(row, "S", C_GREEN_LIGHT, f"Arrancás en {spawn_label}", "Punto de aparición")
        row += 1
        n = 0
        for leg in plan.legs:
            if leg.stop is None:
                self._step_row(row, "E", C_BLUE, f"Extraé por {plan.extract_name}",
                               f"{round(leg.distance)} m desde el último objetivo")
            else:
                n += 1
                verb = "Arrancá por" if n == 1 else "Seguí con"
                extra = ""
                if len(leg.stop.candidates) > 1:
                    extra = " · se eligió la ubicación más cercana (los círculos vacíos son las demás)"
                self._step_row(row, str(n), THEME["accent_yellow"], f"{verb} {leg.stop.quest}",
                               f"{leg.stop.label} · {round(leg.distance)} m{extra}")
            row += 1

        if ranking and len(ranking) > 1:
            best = ranking[0][1].total_distance
            others = ", ".join(f"{lbl.split(' (')[0]} (+{round(p.total_distance - best)} m)"
                               for lbl, p in ranking[1:4])
            ctk.CTkLabel(self.steps_frame, text=f"Spawns alternativos: {others}", font=ui_font(12),
                         text_color=C_TEXT_DIM, wraplength=820, justify="left"
                         ).grid(row=row, column=0, sticky="w", pady=(8, 0))
            row += 1
        note = ("Distancias en línea recta entre puntos (no cuentan paredes ni desvíos). "
                + ("Orden óptimo exacto." if plan.exact else "Muchas paradas: orden aproximado."))
        ctk.CTkLabel(self.steps_frame, text=note, font=ui_font(11), text_color=C_TEXT_DIM,
                     wraplength=820, justify="left").grid(row=row, column=0, sticky="w", pady=(6, 0))
        row += 1
        self._render_loose(loose, row)

    def _render_loose(self, loose, row: int):
        if not loose:
            return
        ctk.CTkLabel(self.steps_frame, text="Durante la raid (sin punto fijo):", font=ui_font(13, "bold"),
                     text_color=C_TEXT).grid(row=row, column=0, sticky="w", pady=(10, 2))
        for i, (quest, label) in enumerate(loose, start=1):
            ctk.CTkLabel(self.steps_frame, text=f"•  {quest}: {label}", font=ui_font(12),
                         text_color=C_TEXT_MUTED).grid(row=row + i, column=0, sticky="w")
