"""
TarkovScope - Persistencia del Planner de Progresión (configuración, progreso y sincronización).

* Configuración: facción, nivel de jugador, metas y reputación real cargada por trader.
* Progreso: quests completadas (ids de tarkov.dev) y objetivos de raid ya cumplidos.
* Sincronización con la pestaña "Quests & Traders": las quests marcadas allí cuentan como hechas y
  las que se completan en el planner se marcan allí también (cruce por nombre).
"""
import json
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from core.config import DB_PATH
from core.quest_route_data import load_route_dataset, normalize_quest_name
from core.progression_planner import estimate_reputation
from core.user_data import get_user_preference, set_user_preference

PREF_CONFIG = "progression_plan_config"
PREF_PROGRESS = "progression_plan_progress"
PREF_TRACKER_ACTIVE = "quest_tracker_active"

DEFAULT_CONFIG: Dict[str, Any] = {
    "faction": "BEAR",
    "player_level": 1,
    "goals": [{"type": "trader", "trader": "Prapor", "level": 2}],
    "reps": {},  # trader -> {"rep": float, "base_done": [ids completadas al cargarla]}
}


def _load_json(key: str, default: Any, db_path: str) -> Any:
    try:
        raw = get_user_preference(key, "", db_path)
        return json.loads(raw) if raw else default
    except (ValueError, TypeError):
        return default


def load_config(db_path: str = DB_PATH) -> Dict[str, Any]:
    cfg = _load_json(PREF_CONFIG, None, db_path)
    if not isinstance(cfg, dict):
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    cfg.setdefault("faction", "BEAR")
    cfg.setdefault("player_level", 1)
    cfg.setdefault("goals", [])
    cfg.setdefault("reps", {})
    return cfg


def save_config(cfg: Dict[str, Any], db_path: str = DB_PATH) -> None:
    set_user_preference(PREF_CONFIG, json.dumps(cfg), db_path)


def load_progress(db_path: str = DB_PATH) -> Dict[str, Set[str]]:
    data = _load_json(PREF_PROGRESS, {}, db_path)
    return {"done": set(data.get("done", [])), "objectives": set(data.get("objectives", []))}


def save_progress(progress: Dict[str, Set[str]], db_path: str = DB_PATH) -> None:
    set_user_preference(PREF_PROGRESS, json.dumps({
        "done": sorted(progress["done"]), "objectives": sorted(progress["objectives"]),
    }), db_path)


def ids_for_names(progression: Dict[str, Any], names: Iterable[str], faction: str) -> Set[str]:
    """Ids de quest que corresponden a esos nombres (solo variantes de la facción del jugador)."""
    wanted = {normalize_quest_name(n) for n in names}
    out = set()
    for tid, t in progression.get("tasks", {}).items():
        f = t.get("faction") or "Any"
        if normalize_quest_name(t["name"]) in wanted and (f == "Any" or f.upper() == faction.upper()):
            out.add(tid)
    return out


def quests_tab_state(datastore) -> Tuple[List[str], List[str]]:
    """(títulos completados, todos los títulos) de la pestaña Quests & Traders."""
    try:
        quests = datastore.get_quests()
    except Exception:
        return [], []
    titles = [q.get("title", "") for q in quests]
    return [q.get("title", "") for q in quests if q.get("is_completed")], titles


def drop_task_objectives(objectives: Set[str], task_ids: Iterable[str]) -> Set[str]:
    """Saca los objetivos 'id#indice' de esas quests (cuando se desmarcan vuelven al plan enteras)."""
    removed = set(task_ids)
    return {k for k in objectives if k.split("#", 1)[0] not in removed}


def reconcile_done(
    progression: Dict[str, Any], done: Set[str], completed_names: Iterable[str],
    known_names: Iterable[str], faction: str,
) -> Set[str]:
    """Quests hechas tras sincronizar con Quests & Traders, en las dos direcciones.

    Para las quests que existen en esa pestaña, manda su check: marcada = hecha, desmarcada = no.
    Las que no existen allí (quests nuevas que la pestaña no lista) conservan lo marcado en el planner.
    """
    known_ids = ids_for_names(progression, known_names, faction)
    completed_ids = ids_for_names(progression, completed_names, faction)
    return (set(done) - known_ids) | completed_ids


def push_completion_to_quests_tab(datastore, quest_name: str, done: bool) -> bool:
    """Marca/desmarca la quest homónima en la pestaña Quests & Traders. True si cambió algo."""
    key = normalize_quest_name(quest_name)
    changed = False
    try:
        for q in datastore.get_quests():
            if normalize_quest_name(q.get("title", "")) == key and bool(q.get("is_completed")) != done:
                datastore.toggle_quest(q["id"])
                changed = True
    except Exception:
        pass
    return changed


def _prune_tracker_active_by_keys(completed_keys: Set[str], db_path: str = DB_PATH) -> None:
    """Saca de la ruta activa del Quest Tracker cualquier quest recién completada."""
    if not completed_keys:
        return
    try:
        raw = get_user_preference(PREF_TRACKER_ACTIVE, "[]", db_path)
        active = json.loads(raw) if raw else []
        if not isinstance(active, list):
            return
        filtered = [n for n in active if normalize_quest_name(n) not in completed_keys]
        if len(filtered) != len(active):
            set_user_preference(PREF_TRACKER_ACTIVE, json.dumps(sorted(set(filtered))), db_path)
    except (ValueError, TypeError):
        pass


def sync_quest_completion(
    quest_name: str,
    done: bool,
    datastore=None,
    progression: Optional[Dict[str, Any]] = None,
    faction: Optional[str] = None,
    db_path: str = DB_PATH,
) -> Set[str]:
    """Sincroniza el estado completado de una quest entre Quests & Traders, Quest Tracker y Planner."""
    if datastore is not None:
        push_completion_to_quests_tab(datastore, quest_name, done)

    prog = progression if progression is not None else load_route_dataset().get("progression", {})
    fac = faction or load_config(db_path).get("faction", "BEAR")
    progress = load_progress(db_path)
    tids = ids_for_names(prog, [quest_name], fac) if prog.get("tasks") else set()

    changed = False
    if tids:
        if done:
            before = len(progress["done"])
            progress["done"].update(tids)
            changed = len(progress["done"]) != before
        else:
            removed = progress["done"] & tids
            if removed:
                progress["done"] -= removed
                progress["objectives"] = drop_task_objectives(progress["objectives"], removed)
                changed = True
    if changed:
        save_progress(progress, db_path)

    if done:
        _prune_tracker_active_by_keys({normalize_quest_name(quest_name)}, db_path)

    return progress["done"]


def get_completed_quest_keys(
    datastore=None,
    progression: Optional[Dict[str, Any]] = None,
    faction: Optional[str] = None,
    db_path: str = DB_PATH,
) -> Set[str]:
    """Retorna nombres normalizados de todas las quests completadas en Quests & Traders + Planner."""
    completed_names, known_names = quests_tab_state(datastore) if datastore is not None else ([], [])
    prog = progression if progression is not None else load_route_dataset().get("progression", {})
    fac = faction or load_config(db_path).get("faction", "BEAR")
    progress = load_progress(db_path)

    done_ids = (
        reconcile_done(prog, progress["done"], completed_names, known_names, fac)
        if prog.get("tasks")
        else progress["done"]
    )
    keys = {normalize_quest_name(n) for n in completed_names if n}
    tasks = prog.get("tasks", {})
    for tid in done_ids:
        t = tasks.get(tid)
        if t and t.get("name"):
            keys.add(normalize_quest_name(t["name"]))
    return keys


def set_manual_reputation(cfg: Dict[str, Any], trader: str, rep: Optional[float], done: Set[str]) -> None:
    """Guarda la reputación real de un trader como foto del momento (o la borra con None)."""
    reps = cfg.setdefault("reps", {})
    if rep is None:
        reps.pop(trader, None)
        return
    old = reps.get(trader)
    if old and abs(float(old.get("rep", 0.0)) - rep) < 1e-6:
        return
    reps[trader] = {"rep": rep, "base_done": sorted(done)}


def effective_reputation(progression: Dict[str, Any], reps: Dict[str, Any], done: Set[str]) -> Dict[str, float]:
    """Reputación a usar por trader.

    Si el usuario cargó su reputación real, se le suman solo las quests completadas después de
    cargarla. Si no, se estima con las recompensas de las quests completadas.
    """
    rep = dict(estimate_reputation(progression, done))
    tasks = progression.get("tasks", {})
    for trader, info in (reps or {}).items():
        base_done = set(info.get("base_done") or [])
        after = sum(float((tasks.get(t, {}).get("standing") or {}).get(trader, 0.0))
                    for t in done if t not in base_done)
        rep[trader] = round(float(info.get("rep", 0.0)) + after, 3)
    return rep


def parse_float(text: str) -> Optional[float]:
    try:
        return float((text or "").strip().replace(",", "."))
    except ValueError:
        return None
