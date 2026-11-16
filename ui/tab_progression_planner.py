"""
TarkovScope - Pestaña Planner de Progresión.

Elegís una o varias metas (nivel de un trader, Kappa, desbloquear Lightkeeper o una quest
puntual); la app calcula qué quests hacer y arma la secuencia de raids por mapa para todas
juntas. Con "Jugar este mapa" se abre el Quest Tracker con ese mapa y esas quests cargadas.
Al volver, marcás la raid como completada y el plan se recalcula.
"""
import logging
import threading
import tkinter as tk
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from core.config import THEME
from core.i18n import t_ui
from core.datastore import get_datastore
from core.progression_goals import GOAL_LABELS, GOAL_TYPES, quest_names, resolve_goals
from core.progression_plan_store import (
    effective_reputation,
    ids_for_names,
    load_config,
    load_progress,
    parse_float,
    push_completion_to_quests_tab,
    drop_task_objectives,
    quests_tab_state,
    reconcile_done,
    save_config,
    save_progress,
    set_manual_reputation,
    sync_quest_completion,
)
from core.quest_route_data import APP_MAP_LABELS, OBJECTIVE_TYPE_LABELS, PLANNABLE_TRADERS, load_route_dataset, normalize_quest_name
from core.progression_planner import ANYWHERE, PlannerState, RaidPlan, Selection, build_raid_plan, select_quests
from ui.theme import C_BG_DARKEST, C_BLUE, C_EMERALD, C_RED, C_TEXT, C_TEXT_DIM, C_TEXT_MUTED, C_WHITE, ui_font

logger = logging.getLogger("TarkovScope.ProgressionPlanner")

RAIDS_PAGE = 8
OFFRAID_LABELS = {
    "giveItem": "Entregar ítems",
    "giveQuestItem": "Entregar ítem de quest",
    "findItem": "Conseguir ítems (FiR)",
    "buildWeapon": "Armar arma (Gunsmith)",
    "traderLevel": "Nivel de trader",
    "taskStatus": "Estado de otra quest",
    "skill": "Nivel de habilidad",
    "sellItem": "Vender ítems",
    "experience": "Experiencia",
    "traderStanding": "Reputación",
}
TYPE_BY_LABEL = {label: key for key, label in GOAL_TYPES}


def map_label(key: str) -> str:
    return "Cualquier mapa" if key == ANYWHERE else APP_MAP_LABELS.get(key, key)


class TabProgressionPlanner(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.progression: Dict[str, Any] = {}
        self.cfg: Dict[str, Any] = load_config()
        self.progress = load_progress()
        self.selection: Optional[Selection] = None
        self.plan: Optional[RaidPlan] = None
        self.show_all_raids = False
        self._token = 0
        self._render_token = 0
        self._debounce_id: Optional[str] = None
        self._last_signature: Optional[tuple] = None
        self.goal_rows: List[Dict[str, Any]] = []
        self.rep_entries: Dict[str, ctk.CTkEntry] = {}
        self._quest_names: List[str] = []

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_main()
        self.reload_data()

    # ------------------------------------------------------------------ layout
    def _build_sidebar(self):
        side = ctk.CTkScrollableFrame(self, width=340, fg_color=THEME["bg_card"], corner_radius=10,
                                      border_width=1, border_color=THEME["border"])
        side.grid(row=0, column=0, padx=(0, 12), sticky="nsew")
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(side, text=t_ui("PLANNER DE PROGRESIÓN", "PROGRESSION PLANNER"), font=ui_font(17, "bold"),
                     text_color=THEME["accent_orange"]).grid(row=0, column=0, padx=12, pady=(12, 2), sticky="w")
        ctk.CTkLabel(side, text=t_ui("Elegí tus metas: arma un solo plan de raids para todas.", "Pick your goals: builds a single raid plan for all."), font=ui_font(12),
                     text_color=C_TEXT_MUTED).grid(row=1, column=0, padx=12, pady=(0, 10), sticky="w")

        row = ctk.CTkFrame(side, fg_color="transparent")
        row.grid(row=2, column=0, padx=10, pady=4, sticky="ew")
        ctk.CTkLabel(row, text=t_ui("Facción", "Faction"), font=ui_font(13, "bold"), text_color=C_TEXT).pack(side="left")
        self.faction_seg = ctk.CTkSegmentedButton(row, values=["BEAR", "USEC"], font=ui_font(12, "bold"),
                                                  selected_color=THEME["accent_orange"],
                                                  command=lambda _v: self._config_changed())
        self.faction_seg.pack(side="right")
        self.faction_seg.set(self.cfg.get("faction", "BEAR"))

        row = ctk.CTkFrame(side, fg_color="transparent")
        row.grid(row=3, column=0, padx=10, pady=4, sticky="ew")
        ctk.CTkLabel(row, text=t_ui("Tu nivel de jugador", "Player level"), font=ui_font(13, "bold"), text_color=C_TEXT).pack(side="left")
        self.level_entry = ctk.CTkEntry(row, width=60, font=ui_font(13), justify="center",
                                        fg_color=THEME["bg_inset"], border_color=THEME["border"])
        self.level_entry.pack(side="right")
        self.level_entry.insert(0, str(self.cfg.get("player_level", 1)))
        self.level_entry.bind("<FocusOut>", lambda _e: self._config_changed())
        self.level_entry.bind("<Return>", lambda _e: self._config_changed())

        ctk.CTkLabel(side, text=t_ui("METAS", "GOALS"), font=ui_font(13, "bold"), text_color=THEME["accent_gold"]
                     ).grid(row=4, column=0, padx=12, pady=(14, 4), sticky="w")
        self.goals_frame = ctk.CTkFrame(side, fg_color="transparent")
        self.goals_frame.grid(row=5, column=0, padx=6, sticky="ew")
        self.goals_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(side, text=t_ui("+ Agregar meta", "+ Add goal"), font=ui_font(13, "bold"), height=32,
                      fg_color=THEME["btn_surface"], hover_color=THEME["btn_hover"],
                      border_width=1, border_color=THEME["border"],
                      command=self._add_goal).grid(row=6, column=0, padx=10, pady=(6, 4), sticky="ew")
        self.calc_btn = ctk.CTkButton(side, text=t_ui("Calcular plan", "Calculate plan"), font=ui_font(14, "bold"), height=36,
                                      fg_color=THEME["accent_orange"], hover_color=THEME["btn_hover"],
                                      text_color=C_WHITE, command=self._config_changed)
        self.calc_btn.grid(row=7, column=0, padx=10, pady=(4, 6), sticky="ew")

        ctk.CTkLabel(side, text=t_ui("TU REPUTACIÓN ACTUAL (opcional)", "CURRENT REPUTATION (optional)"), font=ui_font(13, "bold"),
                     text_color=THEME["accent_gold"]).grid(row=8, column=0, padx=12, pady=(14, 0), sticky="w")
        ctk.CTkLabel(side, text=t_ui("Vacía = se estima con tus quests hechas. Si la copiás del juego,\n"
                                "a partir de ahí se suma lo que completes.",
                                "Empty = estimated from completed quests. If entered from game,\n"
                                "further completions add from there."), font=ui_font(11),
                     text_color=C_TEXT_DIM, justify="left").grid(row=9, column=0, padx=12, pady=(0, 4), sticky="w")
        reps = ctk.CTkFrame(side, fg_color="transparent")
        reps.grid(row=10, column=0, padx=10, sticky="ew")
        for i, trader in enumerate(PLANNABLE_TRADERS):
            cell = ctk.CTkFrame(reps, fg_color="transparent")
            cell.grid(row=i // 2, column=i % 2, padx=2, pady=2, sticky="w")
            ctk.CTkLabel(cell, text=trader, width=82, anchor="w", font=ui_font(12), text_color=C_TEXT_MUTED).pack(side="left")
            e = ctk.CTkEntry(cell, width=64, font=ui_font(12), justify="center", placeholder_text="auto",
                             fg_color=THEME["bg_inset"], border_color=THEME["border"])
            info = self.cfg.get("reps", {}).get(trader)
            if info:
                e.insert(0, f"{float(info['rep']):.2f}")
            e.pack(side="left")
            e.bind("<FocusOut>", lambda _e: self._config_changed())
            e.bind("<Return>", lambda _e: self._config_changed())
            self.rep_entries[trader] = e

        self.sync_lbl = ctk.CTkLabel(side, text="", font=ui_font(11), text_color=C_TEXT_DIM, justify="left",
                                     wraplength=310)
        self.sync_lbl.grid(row=11, column=0, padx=12, pady=(8, 12), sticky="w")

    def _build_main(self):
        self.main = ctk.CTkScrollableFrame(self, fg_color=THEME["bg_card"], corner_radius=10,
                                           border_width=1, border_color=THEME["border"])
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self._content: Optional[ctk.CTkFrame] = None  # contenido visible (se reemplaza entero al redibujar)
        self._target = self.main  # dónde dibujan los helpers de render

    # ------------------------------------------------------------------ metas
    def _render_goals(self):
        for w in self.goals_frame.winfo_children():
            w.destroy()
        self.goal_rows = []
        for i, goal in enumerate(self.cfg.get("goals", [])):
            kind = goal.get("type", "trader")
            box = ctk.CTkFrame(self.goals_frame, fg_color=THEME["bg_row"], corner_radius=8)
            box.grid(row=i, column=0, sticky="ew", pady=3)
            box.grid_columnconfigure(0, weight=1)
            type_menu = ctk.CTkOptionMenu(box, values=[label for _k, label in GOAL_TYPES], font=ui_font(12, "bold"),
                                          fg_color=THEME["btn_surface"], button_color=THEME["accent_orange"],
                                          dropdown_font=ui_font(12),
                                          command=lambda label, idx=i: self._change_type(idx, label))
            type_menu.set(GOAL_LABELS.get(kind, GOAL_LABELS["trader"]))
            type_menu.grid(row=0, column=0, padx=(8, 4), pady=(8, 4), sticky="ew")
            ctk.CTkButton(box, text="✕", width=28, height=28, font=ui_font(12, "bold"), fg_color="transparent",
                          hover_color=THEME["btn_hover"], text_color=C_RED,
                          command=lambda idx=i: self._remove_goal(idx)).grid(row=0, column=1, padx=(2, 6), pady=(8, 4))
            row = {"type": kind, "menu": type_menu}
            body = ctk.CTkFrame(box, fg_color="transparent")
            body.grid(row=1, column=0, columnspan=2, padx=8, pady=(0, 8), sticky="ew")
            if kind == "trader":
                trader_menu = ctk.CTkOptionMenu(body, values=PLANNABLE_TRADERS, width=130, font=ui_font(13, "bold"),
                                                fg_color=THEME["btn_surface"], button_color=THEME["accent_orange"],
                                                dropdown_font=ui_font(12), command=lambda _v: self._config_changed())
                trader_menu.set(goal.get("trader", "Prapor"))
                trader_menu.pack(side="left")
                ll_seg = ctk.CTkSegmentedButton(body, values=["LL2", "LL3", "LL4"], font=ui_font(12, "bold"),
                                                selected_color=C_EMERALD, command=lambda _v: self._config_changed())
                ll_seg.set(f"LL{max(2, min(4, int(goal.get('level', 2))))}")
                ll_seg.pack(side="right")
                row.update(trader=trader_menu, level=ll_seg)
            elif kind == "quest":
                entry = ctk.CTkEntry(body, font=ui_font(12), placeholder_text="Nombre de la quest (Enter)",
                                     fg_color=THEME["bg_inset"], border_color=THEME["border"])
                if goal.get("name"):
                    entry.insert(0, goal["name"])
                entry.pack(fill="x")
                entry.bind("<Return>", lambda _e: self._config_changed())
                entry.bind("<FocusOut>", lambda _e: self._config_changed())
                row["name"] = entry
            else:
                info = self._goal_description(kind)
                ctk.CTkLabel(body, text=info, font=ui_font(11), text_color=C_TEXT_MUTED, justify="left",
                             wraplength=290).pack(anchor="w")
            self.goal_rows.append(row)

    def _goal_description(self, kind: str) -> str:
        special = self.progression.get("goals", {})
        if kind == "kappa" and special.get("kappa"):
            k = special["kappa"]
            return (f"{', '.join(k['traders'])} en LL{k['level']}; quests: {', '.join(k['quest_names'])}; "
                    f"nivel {k['player_level']}.")
        if kind == "lightkeeper" and special.get("lightkeeper"):
            lk = special["lightkeeper"]
            return f"Para habilitar {lk['quest']}: {', '.join(lk['quest_names'])}."
        return "Sin datos: sincronizá la base de datos."

    def _match_quest(self, text: str) -> str:
        key = normalize_quest_name(text)
        if not key:
            return ""
        for n in self._quest_names:
            if normalize_quest_name(n) == key:
                return n
        for n in self._quest_names:
            if normalize_quest_name(n).startswith(key):
                return n
        for n in self._quest_names:
            if key in normalize_quest_name(n):
                return n
        return text.strip()

    def _add_goal(self):
        self._read_form()
        used = {g.get("trader") for g in self.cfg["goals"] if g.get("type") == "trader"}
        trader = next((t for t in PLANNABLE_TRADERS if t not in used), "Prapor")
        self.cfg["goals"].append({"type": "trader", "trader": trader, "level": 2})
        self._render_goals()
        self._config_changed()

    def _remove_goal(self, idx: int):
        self._read_form()
        if 0 <= idx < len(self.cfg["goals"]):
            self.cfg["goals"].pop(idx)
        self._render_goals()
        self._config_changed()

    def _change_type(self, idx: int, label: str):
        self._read_form()
        kind = TYPE_BY_LABEL.get(label, "trader")
        if 0 <= idx < len(self.cfg["goals"]):
            self.cfg["goals"][idx] = {"type": kind, "trader": "Prapor", "level": 2} if kind == "trader" else {"type": kind}
        self._render_goals()
        self._config_changed()

    def _read_form(self):
        self.cfg["faction"] = self.faction_seg.get() or "BEAR"
        try:
            self.cfg["player_level"] = max(1, min(79, int(self.level_entry.get().strip())))
        except ValueError:
            pass
        goals = []
        for row in self.goal_rows:
            kind = row["type"]
            if kind == "trader":
                goals.append({"type": "trader", "trader": row["trader"].get(),
                              "level": int(row["level"].get().replace("LL", "") or 2)})
            elif kind == "quest":
                name = self._match_quest(row["name"].get())
                if name and name != row["name"].get():
                    row["name"].delete(0, "end")
                    row["name"].insert(0, name)
                goals.append({"type": "quest", "name": name})
            else:
                goals.append({"type": kind})
        if self.goal_rows or not self.cfg.get("goals"):
            self.cfg["goals"] = goals
        for trader, entry in self.rep_entries.items():
            set_manual_reputation(self.cfg, trader, parse_float(entry.get()), self.progress["done"])

    def _config_changed(self):
        """Guarda al instante pero recalcula una sola vez cuando se dejan de tocar controles."""
        self._read_form()
        save_config(self.cfg)
        if self._debounce_id is not None:
            self.after_cancel(self._debounce_id)
        self.calc_btn.configure(text="Calculando…")
        self._debounce_id = self.after(220, self._debounced_recalc)

    def _debounced_recalc(self):
        self._debounce_id = None
        self._recalculate()

    # ------------------------------------------------------------------ datos
    def reload_data(self, force: bool = False):
        ds = load_route_dataset(force=force)
        self.progression = ds.get("progression", {})
        self._quest_names = quest_names(self.progression, self.cfg.get("faction", "BEAR"))
        self._render_goals()
        if not self.progression.get("tasks"):
            self._message("No hay datos de progresión. Sincronizá la base de datos con conexión a internet.")
            return
        self._import_quests_tab()
        self._recalculate()

    def on_tab_activated(self):
        if not self.progression.get("tasks"):
            return
        prev_done = set(self.progress["done"])
        prev_obj = set(self.progress["objectives"])
        latest = load_progress()
        self.progress["done"] = latest["done"]
        self.progress["objectives"] = latest["objectives"]
        changed = self._import_quests_tab()
        if changed or self.progress["done"] != prev_done or self.progress["objectives"] != prev_obj or self.plan is None:
            self._recalculate()

    def _import_quests_tab(self) -> bool:
        """Sincroniza con Quests & Traders: lo que se marque o desmarque allí manda."""
        completed, known = quests_tab_state(get_datastore())
        new_done = reconcile_done(self.progression, self.progress["done"], completed, known,
                                  self.cfg.get("faction", "BEAR"))
        changed = new_done != self.progress["done"]
        if changed:
            removed = self.progress["done"] - new_done
            self.progress["done"] = new_done
            self.progress["objectives"] = drop_task_objectives(self.progress["objectives"], removed)
            save_progress(self.progress)
        self.sync_lbl.configure(text=f"{len(self.progress['done'])} quests completadas registradas "
                                     f"(incluye las marcadas en Quests & Traders).")
        return changed

    def _state(self) -> PlannerState:
        rep = effective_reputation(self.progression, self.cfg.get("reps", {}), self.progress["done"])
        return PlannerState(player_level=int(self.cfg.get("player_level", 1)), faction=self.cfg.get("faction", "BEAR"),
                            completed=set(self.progress["done"]), reputation=rep)

    def _recalculate(self):
        if not self.progression.get("tasks"):
            return
        goals = resolve_goals(self.progression, self.cfg.get("goals", []))
        if not goals.targets and not goals.required:
            self._message("Agregá al menos una meta: nivel de trader, Kappa, Lightkeeper o una quest puntual.\n\n"
                          + "\n".join(goals.notes))
            return
        self._token += 1
        token = self._token
        state = self._state()
        done_obj = set(self.progress["objectives"])
        prefer = list(self.selection.task_ids) if self.selection else []
        # El plan anterior queda visible hasta que el nuevo esté listo (sin parpadeo).
        self.calc_btn.configure(text="Calculando…")
        if self._content is None:
            self._message("Calculando plan...")

        def worker():
            try:
                sel = select_quests(self.progression, goals.targets, state, prefer, goals.required)
                plan = build_raid_plan(self.progression, sel.task_ids, state.completed, state.faction,
                                       state.reputation, done_obj)
            except Exception as exc:  # no dejar la UI colgada en "Calculando…"
                logger.exception("Fallo al calcular el plan de progresión")
                err = str(exc) or exc.__class__.__name__
                try:
                    self.after(0, lambda: self._apply_error(token, err))
                except (RuntimeError, tk.TclError):
                    pass
                return
            try:
                self.after(0, lambda: self._apply(token, sel, plan, state, goals))
            except (RuntimeError, tk.TclError):
                pass

        threading.Thread(target=worker, daemon=True).start()

    def _apply_error(self, token: int, err: str):
        if not self.winfo_exists() or token != self._token:
            return
        self._message(f"No se pudo calcular el plan: {err}\n\nProbá sincronizar la base de datos y volver a calcular.")

    def _apply(self, token, sel: Selection, plan: RaidPlan, state: PlannerState, goals):
        if not self.winfo_exists() or token != self._token:
            return
        self.calc_btn.configure(text="Calcular plan")
        self.selection, self.plan = sel, plan
        self._goals = goals
        signature = self._signature(sel, plan, state, goals)
        if signature == self._last_signature and self._content is not None:
            return  # mismo resultado: no hace falta redibujar
        self._last_signature = signature
        self._render_plan(state)

    def _signature(self, sel: Selection, plan: RaidPlan, state: PlannerState, goals) -> tuple:
        return (
            tuple(sel.task_ids),
            tuple((r.map_key, tuple((t.task_id, t.finishes) for t in r.tasks)) for r in plan.raids),
            tuple((t.trader, t.level, round(t.current_reputation, 3), round(t.planned_gain, 3), t.reachable)
                  for t in sel.targets),
            tuple(sel.required), tuple(sel.level_warnings), tuple(goals.notes), goals.player_level,
            state.player_level, frozenset(self.progress["done"]), self.show_all_raids,
        )

    # ------------------------------------------------------------------ acciones
    def _set_done(self, task_ids: List[str], done: bool, objective_keys: List[str] = ()):
        tasks = self.progression.get("tasks", {})
        ds = get_datastore()
        for tid in task_ids:
            if done:
                self.progress["done"].add(tid)
            else:
                self.progress["done"].discard(tid)
                # La quest vuelve al plan entera: sus objetivos de raid tampoco cuentan como hechos.
                self.progress["objectives"] = drop_task_objectives(self.progress["objectives"], [tid])
            if tid in tasks:
                push_completion_to_quests_tab(ds, tasks[tid]["name"], done)
                if done:
                    sync_quest_completion(
                        tasks[tid]["name"],
                        True,
                        datastore=None,
                        progression=self.progression,
                        faction=self.cfg.get("faction", "BEAR"),
                    )
        for key in objective_keys:
            self.progress["objectives"].add(key)
        save_progress(self.progress)
        self.sync_lbl.configure(text=f"{len(self.progress['done'])} quests completadas registradas "
                                     f"(incluye las marcadas en Quests & Traders).")
        self._recalculate()

    def _complete_raid(self, raid):
        finished = [t.task_id for t in raid.tasks if t.finishes]
        keys = [f"{t.task_id}#{o['index']}" for t in raid.tasks for o in t.objectives]
        self._set_done(finished, True, keys)

    def _play_raid(self, raid):
        app = self.winfo_toplevel()
        if not hasattr(app, "switch_tab"):
            return
        app.switch_tab("quest_tracker")
        tracker = getattr(app, "tabs", {}).get("quest_tracker")
        if tracker is not None and hasattr(tracker, "load_plan"):
            names = [t.name for t in raid.tasks]
            tracker.load_plan(raid.map_key, names, f"Planner de Progresión · Raid {raid.number}")

    # ------------------------------------------------------------------ render
    # Rendimiento: el contenido se arma en un frame nuevo que reemplaza al anterior de una sola vez
    # (sin parpadeo), las filas de texto usan tk.Label nativos (mucho más livianos que CTkLabel) y
    # las tarjetas de raids que no entran en la primera vista se dibujan en tandas con after().

    RAIDS_FIRST_PASS = 3
    RAIDS_PER_BATCH = 2

    def _scale(self) -> float:
        return self._get_widget_scaling() if hasattr(self, "_get_widget_scaling") else 1.0

    def _tk_font(self, size: int, weight: str = "normal") -> tuple:
        """Fuente de ui_font (misma familia y peso) escalada como CustomTkinter, para tk.Label nativos.

        tk.Label no aplica el escalado de DPI de CustomTkinter, así que se pasa la tupla ya escalada
        (tamaño negativo = píxeles, el mismo criterio que usa CTk internamente).
        """
        base = ui_font(size, weight)
        return (base.cget("family"), -int(round(size * self._scale())), base.cget("weight"))

    def _text(self, parent, text: str, size: int = 12, weight: str = "normal", color: str = C_TEXT_MUTED,
              bg: str = "", wrap: int = 0) -> tk.Label:
        return tk.Label(parent, text=text, font=self._tk_font(size, weight), fg=color,
                        bg=bg or THEME["bg_card"], justify="left", anchor="w",
                        wraplength=int(wrap * self._scale()) if wrap else 0, bd=0, padx=0, pady=0)

    def _swap_content(self, new: ctk.CTkFrame) -> None:
        new.grid(row=0, column=0, sticky="ew")
        old = self._content
        self._content = new
        if old is not None and old is not new:
            old.grid_forget()
            self.after(30, old.destroy)  # destruir después de mostrar el nuevo

    def _new_content(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        self._target = frame
        return frame

    def _clear(self):
        self._render_token += 1
        self._last_signature = None
        self._swap_content(self._new_content())

    def _message(self, text: str):
        self.calc_btn.configure(text="Calcular plan")
        self._clear()
        self._text(self._target, text, size=14, wrap=760).grid(row=0, column=0, padx=18, pady=18, sticky="w")

    def _summary_box(self, row: int, title: str, status: str, color: str, detail: str):
        bg = THEME["bg_row"]
        box = tk.Frame(self._target, bg=bg)
        box.grid(row=row, column=0, padx=14, pady=(12 if row == 0 else 4, 0), sticky="ew")
        box.grid_columnconfigure(0, weight=1)
        self._text(box, title, 15, "bold", THEME["accent_orange"], bg).grid(row=0, column=0, padx=12, pady=(8, 0), sticky="w")
        self._text(box, status, 13, "bold", color, bg).grid(row=0, column=1, padx=12, pady=(8, 0), sticky="e")
        self._text(box, detail, 12, "normal", C_TEXT_MUTED, bg, wrap=760).grid(
            row=1, column=0, columnspan=2, padx=12, pady=(2, 8), sticky="w")

    def _render_plan(self, state: PlannerState):
        self._render_token += 1
        token = self._render_token
        content = self._new_content()
        sel, plan, goals = self.selection, self.plan, self._goals
        tasks = self.progression.get("tasks", {})
        row = 0

        for tr in sel.targets:
            if tr.already_met:
                status, color = "Ya tenés la reputación", C_EMERALD
            elif tr.reachable:
                status, color = f"+{tr.planned_gain:.2f} de rep con este plan", C_EMERALD
            else:
                status, color = "No alcanza con las quests disponibles", C_RED
            detail = f"Rep: {tr.current_reputation:.2f} → necesitás {tr.required_reputation:.2f}"
            if tr.required_player_level > state.player_level:
                detail += f"   ·   ⚠ el LL{tr.level} también pide nivel {tr.required_player_level} (tenés {state.player_level})"
            self._summary_box(row, f"{tr.trader} LL{tr.level}", status, color, detail)
            row += 1
        if sel.required:
            ok = sum(1 for _n, r in sel.required if r)
            missing = [n for n, r in sel.required if not r]
            status = "Todas en el plan" if not missing else f"Faltan {len(missing)}"
            detail = ", ".join(n for n, _r in sel.required)
            if missing:
                detail += f"\nNo se pudieron desbloquear: {', '.join(missing)}"
            self._summary_box(row, f"Quests obligatorias ({ok}/{len(sel.required)})", status,
                              C_EMERALD if not missing else C_RED, detail)
            row += 1

        notes = list(goals.notes)
        if goals.player_level > state.player_level:
            notes.insert(0, f"Necesitás nivel {goals.player_level} (tenés {state.player_level}).")
        if sel.level_warnings:
            notes.append("Nivel de jugador necesario más adelante: " + ", ".join(
                f"{t} LL{l} → nivel {pl}" for t, l, pl in sel.level_warnings))
        n_quests = len(sel.task_ids)
        self._text(content, f"{n_quests} quests · {len(plan.raids)} raids planificadas", 16, "bold", C_WHITE
                   ).grid(row=row, column=0, padx=16, pady=(14, 2), sticky="w")
        row += 1
        for note in notes:
            self._text(content, f"⚠ {note}", 12, "normal", THEME["accent_yellow"], wrap=780
                       ).grid(row=row, column=0, padx=16, pady=1, sticky="w")
            row += 1

        if not plan.raids and n_quests == 0:
            self._text(content, "No hace falta hacer quests para estas metas.", 13
                       ).grid(row=row, column=0, padx=16, pady=8, sticky="w")
            self._swap_content(content)
            return

        raids = plan.raids if self.show_all_raids else plan.raids[:RAIDS_PAGE]
        first, rest = raids[:self.RAIDS_FIRST_PASS], raids[self.RAIDS_FIRST_PASS:]
        for i, raid in enumerate(first):
            self._raid_card(raid, row, is_next=(i == 0))
            row += 1
        self._swap_content(content)  # ya se ve lo importante; el resto llega en tandas
        tail_row = row + len(rest)

        def render_batch(start: int):
            if token != self._render_token or not content.winfo_exists():
                return
            self._target = content
            for j, raid in enumerate(rest[start:start + self.RAIDS_PER_BATCH]):
                self._raid_card(raid, row + start + j, is_next=False)
            if start + self.RAIDS_PER_BATCH < len(rest):
                self.after(4, lambda: render_batch(start + self.RAIDS_PER_BATCH))
            else:
                self._render_tail(content, tail_row, plan, tasks)

        if rest:
            self.after(4, lambda: render_batch(0))
        else:
            self._render_tail(content, tail_row, plan, tasks)

    def _render_tail(self, content, row: int, plan: RaidPlan, tasks: Dict[str, Any]):
        self._target = content
        if len(plan.raids) > RAIDS_PAGE:
            label = "Mostrar menos" if self.show_all_raids else f"Mostrar las {len(plan.raids)} raids"
            ctk.CTkButton(content, text=label, font=ui_font(12, "bold"), height=30, fg_color=THEME["btn_surface"],
                          hover_color=THEME["btn_hover"], command=self._toggle_all_raids
                          ).grid(row=row, column=0, padx=16, pady=6, sticky="w")
            row += 1
        if plan.offraid:
            self._text(content, "FUERA DE RAID (entregas, gunsmith, ítems)", 13, "bold", THEME["accent_gold"]
                       ).grid(row=row, column=0, padx=16, pady=(14, 2), sticky="w")
            row += 1
            lines = []
            for tid, objs in plan.offraid:
                labels = sorted({OFFRAID_LABELS.get(o["type"], o["type"]) for o in objs})
                lines.append(f"•  {tasks[tid]['name']} ({tasks[tid].get('trader', '')}): {', '.join(labels)}")
            self._text(content, "\n".join(lines), 12).grid(row=row, column=0, padx=22, sticky="w")
            row += 1
        if plan.blocked:
            names = ", ".join(tasks[t]["name"] for t in plan.blocked)
            self._text(content, f"No se pudieron ubicar en raids: {names}", 12, "normal", C_RED, wrap=780
                       ).grid(row=row, column=0, padx=16, pady=(10, 0), sticky="w")
            row += 1
        self._text(content, "Fuentes: requisitos y reputación de la wiki oficial; objetivos y mapas de tarkov.dev.",
                   11, "normal", C_TEXT_DIM).grid(row=row, column=0, padx=16, pady=(12, 14), sticky="w")

    def _toggle_all_raids(self):
        self.show_all_raids = not self.show_all_raids
        self._last_signature = None
        self._render_plan(self._state())

    def _raid_card(self, raid, row: int, is_next: bool):
        bg = THEME["bg_panel_alt"]
        card = ctk.CTkFrame(self._target, fg_color=bg, corner_radius=10, border_width=1,
                            border_color=THEME["accent_orange"] if is_next else THEME["border"])
        card.grid(row=row, column=0, padx=14, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)
        head = tk.Frame(card, bg=bg)
        head.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="ew")
        title = f"{'PRÓXIMA · ' if is_next else ''}Raid {raid.number} · {map_label(raid.map_key)}"
        self._text(head, title, 14, "bold", THEME["accent_orange"] if is_next else C_WHITE, bg).pack(side="left")
        ctk.CTkButton(head, text="Completé esta raid", width=150, height=28, font=ui_font(12, "bold"),
                      fg_color=THEME["btn_surface"], hover_color=THEME["btn_hover"], border_width=1,
                      border_color=C_EMERALD, bg_color=bg,
                      command=lambda r=raid: self._complete_raid(r)).pack(side="right", padx=(6, 0))
        if raid.map_key != ANYWHERE:
            ctk.CTkButton(head, text="Jugar este mapa ▶", width=150, height=28, font=ui_font(12, "bold"),
                          fg_color=C_EMERALD, hover_color=THEME["btn_hover"], text_color=C_BG_DARKEST, bg_color=bg,
                          command=lambda r=raid: self._play_raid(r)).pack(side="right")

        for i, t in enumerate(raid.tasks, start=1):
            line = tk.Frame(card, bg=bg)
            line.grid(row=i, column=0, padx=12, pady=1, sticky="ew")
            var = tk.BooleanVar(value=t.task_id in self.progress["done"])
            tk.Checkbutton(line, variable=var, bg=bg, activebackground=bg, selectcolor=THEME["bg_inset"],
                           fg=C_EMERALD, bd=0, highlightthickness=0, cursor="hand2",
                           command=lambda tid=t.task_id, v=var: self._set_done([tid], v.get())).pack(side="left")
            objs = ", ".join(sorted({OBJECTIVE_TYPE_LABELS.get(o["type"], o["type"]) for o in t.objectives}))
            extra = "" if t.finishes else "  (parcial: sigue en otra raid)"
            self._text(line, t.name, 13, "bold", C_TEXT, bg).pack(side="left", padx=(4, 0))
            self._text(line, f"  {t.trader} · {objs}{extra}", 12, "normal",
                       C_BLUE if not t.finishes else C_TEXT_MUTED, bg).pack(side="left")
        tk.Frame(card, height=6, bg=bg).grid(row=len(raid.tasks) + 1, column=0)
