"""
TarkovScope - Motor del Planner de Progresión (niveles de trader, quests obligatorias), sistema de desbloqueo actual.

Una quest está disponible cuando:
  * es de tu facción (o de ambas),
  * tenés el nivel de lealtad (LL) que pide con su trader,
  * completaste al menos `ll_quests` quests de ese trader en ese mismo LL,
  * completaste alguna quest de cada grupo de `prev` (AND entre grupos, OR dentro de cada grupo).

1) select_quests(): elige las quests a completar para alcanzar metas como "Prapor LL3 + Skier LL2"
   con el menor esfuerzo. Cada candidata cuesta ella misma más todo lo que haga falta para
   desbloquearla (previas y quests de "relleno" del mismo LL); se elige la mejor relación
   reputación ganada / quests, se simula y se repite hasta cumplir las metas.
2) build_raid_plan(): ordena esas quests en raids por mapa. En cada paso se elige el mapa donde se
   pueden avanzar más quests desbloqueadas a la vez.

El nivel de jugador que pide cada LL no bloquea el plan (se va subiendo jugando): se avisa.
Lógica pura de negocio sobre el bloque "progression" del dataset de rutas.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

ANYWHERE = "*"  # objetivos de raid sin mapa fijo (p. ej. "eliminá 5 Scavs en cualquier mapa")
MAX_RAIDS = 120
MAX_DEPTH = 10


@dataclass
class PlannerState:
    player_level: int = 1
    faction: str = "BEAR"
    completed: Set[str] = field(default_factory=set)  # ids de quest (tarkov.dev)
    reputation: Dict[str, float] = field(default_factory=dict)


@dataclass
class TargetResult:
    trader: str
    level: int
    required_reputation: float
    required_player_level: int
    current_reputation: float
    planned_gain: float
    reachable: bool
    already_met: bool


@dataclass
class Selection:
    task_ids: List[str]  # en orden válido de desbloqueo
    targets: List[TargetResult]
    level_warnings: List[Tuple[str, int, int]] = field(default_factory=list)  # (trader, LL, nivel jugador)
    required: List[Tuple[str, bool]] = field(default_factory=list)  # (quest obligatoria, alcanzable)


@dataclass
class RaidTask:
    task_id: str
    name: str
    trader: str
    objectives: List[Dict[str, Any]]  # objetivos que se avanzan en esta raid
    finishes: bool  # True si con esta raid quedan cumplidos todos sus objetivos de raid


@dataclass
class RaidStep:
    number: int
    map_key: str  # ANYWHERE = cualquier mapa
    tasks: List[RaidTask]


@dataclass
class RaidPlan:
    raids: List[RaidStep]
    offraid: List[Tuple[str, List[Dict[str, Any]]]]  # (task_id, objetivos fuera de raid)
    blocked: List[str]  # quests que no se pudieron desbloquear en la simulación


# ---------------------------------------------------------------------------
# Niveles y reputación
# ---------------------------------------------------------------------------

def level_requirements(progression: Dict[str, Any], trader: str, level: int) -> Tuple[float, int]:
    """(reputación, nivel de jugador) que pide el LL indicado; (0, 0) si no hay datos."""
    for lv in progression.get("traders", {}).get(trader, {}).get("levels", []):
        if lv.get("level") == level:
            return float(lv.get("reputation") or 0.0), int(lv.get("player_level") or 0)
    return 0.0, 0


def loyalty_level(progression: Dict[str, Any], trader: str, reputation: float, player_level: int = 99) -> int:
    """Nivel de lealtad alcanzado con esa reputación y nivel de jugador."""
    levels = progression.get("traders", {}).get(trader, {}).get("levels", [])
    if not levels:
        return 99  # trader sin escalas de LL (BTR, Lightkeeper...): no limita
    best = 1
    for lv in levels:
        if reputation + 1e-9 >= float(lv.get("reputation") or 0.0) and player_level >= int(lv.get("player_level") or 0):
            best = max(best, int(lv.get("level") or 1))
    return best


def max_level(progression: Dict[str, Any], trader: str) -> int:
    levels = progression.get("traders", {}).get(trader, {}).get("levels", [])
    return max((int(lv.get("level") or 1) for lv in levels), default=1)


def estimate_reputation(progression: Dict[str, Any], completed: Iterable[str]) -> Dict[str, float]:
    """Reputación aproximada por trader sumando las recompensas de las quests completadas."""
    rep: Dict[str, float] = {}
    tasks = progression.get("tasks", {})
    for tid in completed:
        for trader, delta in (tasks.get(tid, {}).get("standing") or {}).items():
            rep[trader] = round(rep.get(trader, 0.0) + float(delta), 3)
    return rep


def _faction_ok(task: Dict[str, Any], faction: str) -> bool:
    f = task.get("faction") or "Any"
    return f == "Any" or f.upper() == (faction or "").upper()


# ---------------------------------------------------------------------------
# Simulación de progreso
# ---------------------------------------------------------------------------

class _Sim:
    """Estado simulado: quests hechas, reputación y conteo de quests por (trader, LL)."""

    def __init__(self, progression: Dict[str, Any], done: Iterable[str], base_rep: Dict[str, float]):
        self.p = progression
        self.tasks = progression.get("tasks", {})
        self.done: Set[str] = set()
        self.rep: Dict[str, float] = dict(base_rep)
        self.count: Dict[Tuple[str, int], int] = {}
        for t in done:
            self._mark(t, add_rep=False)

    def copy(self) -> "_Sim":
        c = _Sim.__new__(_Sim)
        c.p, c.tasks = self.p, self.tasks
        c.done, c.rep, c.count = set(self.done), dict(self.rep), dict(self.count)
        return c

    def _mark(self, tid: str, add_rep: bool = True) -> None:
        if tid in self.done or tid not in self.tasks:
            self.done.add(tid)
            return
        self.done.add(tid)
        t = self.tasks[tid]
        key = (t.get("trader", ""), int(t.get("ll") or 1))
        self.count[key] = self.count.get(key, 0) + 1
        if add_rep:
            for trader, delta in (t.get("standing") or {}).items():
                self.rep[trader] = self.rep.get(trader, 0.0) + float(delta)

    def complete(self, tid: str) -> None:
        self._mark(tid, add_rep=True)

    def ll_ok(self, t: Dict[str, Any]) -> bool:
        return loyalty_level(self.p, t.get("trader", ""), self.rep.get(t.get("trader", ""), 0.0)) >= int(t.get("ll") or 1)

    def tier_count(self, t: Dict[str, Any]) -> int:
        return self.count.get((t.get("trader", ""), int(t.get("ll") or 1)), 0)

    def available(self, tid: str, faction: str) -> bool:
        t = self.tasks[tid]
        if tid in self.done or not _faction_ok(t, faction) or not self.ll_ok(t):
            return False
        if self.tier_count(t) < int(t.get("ll_quests") or 0):
            return False
        return all(any(g in self.done for g in group) for group in t.get("prev", []))


_TIER_CACHE: Dict[int, Dict[Tuple[str, int], List[str]]] = {}


def _tier_index(tasks: Dict[str, Any]) -> Dict[Tuple[str, int], List[str]]:
    """Quests agrupadas por (trader, LL); se cachea por diccionario de quests."""
    key = id(tasks)
    if key not in _TIER_CACHE:
        idx: Dict[Tuple[str, int], List[str]] = {}
        for tid, t in tasks.items():
            idx.setdefault((t.get("trader", ""), int(t.get("ll") or 1)), []).append(tid)
        _TIER_CACHE.clear()
        _TIER_CACHE[key] = idx
    return _TIER_CACHE[key]


def _unlock_chain(
    sim: _Sim, tid: str, faction: str, value, depth: int = 0, stack: Optional[Set[str]] = None
) -> Optional[List[str]]:
    """Quests a completar (en orden) para poder hacer `tid`, incluida ella. None si no se puede.

    `value(task_id)` puntúa quests de relleno: a igual costo se prefieren las que suman a las metas.
    Modifica `sim` aplicando la cadena encontrada.
    """
    if tid in sim.done:
        return []
    tasks = sim.tasks
    stack = set() if stack is None else stack
    if tid not in tasks or tid in stack or depth > MAX_DEPTH:
        return None
    t = tasks[tid]
    if not _faction_ok(t, faction) or not sim.ll_ok(t):
        return None
    stack = stack | {tid}
    order: List[str] = []

    for group in t.get("prev", []):
        if any(g in sim.done for g in group):
            continue
        best: Optional[Tuple[int, List[str], _Sim]] = None
        for alt in group:
            trial = sim.copy()
            chain = _unlock_chain(trial, alt, faction, value, depth + 1, stack)
            if chain is not None and (best is None or len(chain) < best[0]):
                best = (len(chain), chain, trial)
        if best is None:
            return None
        order += best[1]
        sim.done, sim.rep, sim.count = best[2].done, best[2].rep, best[2].count

    need = int(t.get("ll_quests") or 0) - sim.tier_count(t)
    tier = _tier_index(tasks).get((t.get("trader", ""), int(t.get("ll") or 1)), ())
    while need > 0:
        best = None
        # 1) Relleno ya disponible (costo 1): la de más reputación útil.
        for oid in tier:
            if oid not in sim.done and oid not in stack and sim.available(oid, faction):
                cand = (1, -value(oid), oid, None)
                if best is None or cand[:3] < best[:3]:
                    best = cand
        # 2) Si no hay, la cadena de desbloqueo más corta (profundidad acotada).
        if best is None and depth < 3:
            for oid in tier:
                if oid in sim.done or oid in stack:
                    continue
                trial = sim.copy()
                chain = _unlock_chain(trial, oid, faction, value, depth + 1, stack)
                if chain is None:
                    continue
                cand = (len(chain), -value(oid), oid, (chain, trial))
                if best is None or cand[:3] < best[:3]:
                    best = cand
        if best is None:
            return None
        if best[3] is None:
            sim.complete(best[2])
            order.append(best[2])
        else:
            order += best[3][0]
            sim.done, sim.rep, sim.count = best[3][1].done, best[3][1].rep, best[3][1].count
        need = int(t.get("ll_quests") or 0) - sim.tier_count(t)

    if not sim.ll_ok(t):  # el relleno no alcanza para el LL que pide
        return None
    sim.complete(tid)
    order.append(tid)
    return order


# ---------------------------------------------------------------------------
# Selección de quests
# ---------------------------------------------------------------------------

def select_quests(
    progression: Dict[str, Any],
    targets: Sequence[Tuple[str, int]],
    state: PlannerState,
    prefer: Iterable[str] = (),
    required: Iterable[Sequence[str]] = (),
) -> Selection:
    """Elige las quests a completar para alcanzar todas las metas de nivel de trader.

    `prefer`: quests del plan anterior; ante empates se mantienen para que el plan no "salte".
    `required`: grupos de ids de quest que hay que completar (alcanza con una de cada grupo,
    p. ej. las variantes BEAR/USEC de la misma quest).
    """
    prefer_set = set(prefer)
    tasks: Dict[str, Any] = progression.get("tasks", {})
    base_rep = {t: float(state.reputation.get(t, 0.0)) for t in progression.get("traders", {})}
    req_groups = [[g for g in group if g in tasks] for group in required]
    req_groups = [g for g in req_groups if g]
    # Las quests obligatorias pueden exigir cierto LL con otros traders: se suman como metas implícitas.
    all_targets = list(targets)
    for group in req_groups:
        needs = _static_ll_needs(tasks, group, state.faction)
        all_targets += [(tr, lvl) for tr, lvl in needs.items() if lvl > 1 and tr in progression.get("traders", {})]
    needed: Dict[str, float] = {}
    for trader, level in all_targets:
        req_rep, _ = level_requirements(progression, trader, level)
        needed[trader] = max(needed.get(trader, 0.0), req_rep)

    sim = _Sim(progression, state.completed, base_rep)
    selected: List[str] = []

    def missing(trader: str) -> float:
        return max(0.0, needed[trader] - sim.rep.get(trader, 0.0))

    def value(oid: str) -> float:
        st = tasks[oid].get("standing") or {}
        return sum(max(0.0, st.get(tr, 0.0)) for tr in needed if missing(tr) > 1e-9)

    def try_required() -> bool:
        """Agrega las cadenas de quests obligatorias que ya se pueden desbloquear."""
        nonlocal sim
        progressed = False
        for group in req_groups:
            if any(g in sim.done for g in group):
                continue
            best_req = None
            for gid in group:
                trial = sim.copy()
                chain = _unlock_chain(trial, gid, state.faction, value)
                if chain is not None and (best_req is None or len(chain) < len(best_req[0])):
                    best_req = (chain, trial)
            if best_req is not None:
                selected.extend(best_req[0])
                sim = best_req[1]
                progressed = True
        return progressed

    while True:
        progressed = try_required()
        if not any(missing(t) > 1e-9 for t in needed):
            if progressed:
                continue
            break
        best = None
        for tid, t in tasks.items():
            if tid in sim.done or value(tid) <= 0:
                continue
            trial = sim.copy()
            chain = _unlock_chain(trial, tid, state.faction, value)
            if not chain:
                continue
            score = 0.0
            for trader in needed:
                miss = missing(trader)
                if miss > 1e-9:
                    gain = trial.rep.get(trader, 0.0) - sim.rep.get(trader, 0.0)
                    score += min(miss, max(0.0, gain)) / max(needed[trader], 0.01)
            if score <= 0:
                continue
            kept = sum(1 for c in chain if c in prefer_set)
            key = (round(score / len(chain), 9), kept, -len(chain), t["name"])
            if best is None or key > best[0]:
                best = (key, chain, trial)
        if best is None:
            if not progressed:
                break
            continue
        selected += best[1]
        sim = best[2]

    required_results = []
    for group in req_groups:
        required_results.append((tasks[group[0]]["name"], any(g in sim.done for g in group)))

    final_rep = sim.rep
    results = []
    warnings: Set[Tuple[str, int, int]] = set()
    for trader, level in targets:
        req_rep, req_lvl = level_requirements(progression, trader, level)
        cur = base_rep.get(trader, 0.0)
        results.append(TargetResult(
            trader=trader, level=level, required_reputation=req_rep, required_player_level=req_lvl,
            current_reputation=cur, planned_gain=round(final_rep.get(trader, 0.0) - cur, 3),
            reachable=final_rep.get(trader, 0.0) + 1e-9 >= req_rep, already_met=cur + 1e-9 >= req_rep,
        ))
        if req_lvl > state.player_level:
            warnings.add((trader, level, req_lvl))
    for tid in selected:
        t = tasks[tid]
        _, lvl = level_requirements(progression, t.get("trader", ""), int(t.get("ll") or 1))
        if lvl > state.player_level:
            warnings.add((t.get("trader", ""), int(t.get("ll") or 1), lvl))
    return Selection(task_ids=selected, targets=results, level_warnings=sorted(warnings, key=lambda w: (w[2], w[0])),
                     required=required_results)


def _static_ll_needs(tasks: Dict[str, Any], group: List[str], faction: str) -> Dict[str, int]:
    """LL máximo por trader que exige la cadena previa de una quest (eligiendo la alternativa más baja)."""
    memo: Dict[str, Optional[Dict[str, int]]] = {}

    def needs(tid: str, stack: frozenset) -> Optional[Dict[str, int]]:
        if tid in memo:
            return memo[tid]
        t = tasks.get(tid)
        if t is None or tid in stack or not _faction_ok(t, faction):
            return None
        out: Dict[str, int] = {t.get("trader", ""): int(t.get("ll") or 1)}
        for grp in t.get("prev", []):
            options = [n for n in (needs(g, stack | {tid}) for g in grp) if n is not None]
            if not options:
                memo[tid] = None
                return None
            best = min(options, key=lambda d: sum(d.values()))
            for tr, lvl in best.items():
                out[tr] = max(out.get(tr, 0), lvl)
        memo[tid] = out
        return out

    options = [n for n in (needs(g, frozenset()) for g in group) if n is not None]
    return min(options, key=lambda d: sum(d.values())) if options else {}


# ---------------------------------------------------------------------------
# Plan de raids por mapa
# ---------------------------------------------------------------------------

def build_raid_plan(
    progression: Dict[str, Any],
    task_ids: Sequence[str],
    completed: Iterable[str] = (),
    faction: str = "BEAR",
    reputation: Optional[Dict[str, float]] = None,
    done_objectives: Iterable[str] = (),
) -> RaidPlan:
    """Secuencia de raids: en cada una, el mapa que más quests desbloqueadas avanza.

    `done_objectives` son claves "id_quest#indice" de objetivos ya cumplidos en raids anteriores.
    """
    tasks: Dict[str, Any] = progression.get("tasks", {})
    sim = _Sim(progression, completed, reputation or {})
    plan_ids = [t for t in task_ids if t in tasks and t not in sim.done]
    done_obj = set(done_objectives)

    pending: Dict[str, Dict[int, Set[str]]] = {}
    offraid: List[Tuple[str, List[Dict[str, Any]]]] = []
    for tid in plan_ids:
        objs = tasks[tid].get("objectives", [])
        pending[tid] = {o["index"]: set(o.get("maps") or [ANYWHERE]) for o in objs
                        if o.get("raid") and f"{tid}#{o['index']}" not in done_obj}
        rest = [o for o in objs if not o.get("raid")]
        if rest:
            offraid.append((tid, rest))

    started: Set[str] = set()  # quests aceptadas (desbloqueadas) y aún sin terminar

    def unlock_new() -> None:
        progressed = True
        while progressed:
            progressed = False
            for tid in plan_ids:
                if tid in sim.done or tid in started or not sim.available(tid, faction):
                    continue
                if pending[tid]:
                    started.add(tid)
                else:  # solo entregas: se completa al desbloquearse
                    sim.complete(tid)
                    progressed = True

    def obj_by_index(tid: str, idx: int) -> Dict[str, Any]:
        return next(o for o in tasks[tid]["objectives"] if o["index"] == idx)

    raids: List[RaidStep] = []
    while len(raids) < MAX_RAIDS:
        unlock_new()
        open_tasks = [t for t in plan_ids if t in started]
        if not open_tasks:
            break
        score: Dict[str, Tuple[int, int]] = {}
        for tid in open_tasks:
            for m in set().union(*pending[tid].values()) - {ANYWHERE}:
                n_obj = sum(1 for ms in pending[tid].values() if m in ms)
                s = score.get(m, (0, 0))
                score[m] = (s[0] + 1, s[1] + n_obj)
        map_key = max(sorted(score), key=lambda m: score[m]) if score else ANYWHERE

        step_tasks: List[RaidTask] = []
        finished_now: List[str] = []
        for tid in open_tasks:
            idxs = [i for i, ms in pending[tid].items() if map_key in ms or ANYWHERE in ms]
            if not idxs:
                continue
            for i in idxs:
                del pending[tid][i]
            finishes = not pending[tid]
            if finishes:
                finished_now.append(tid)
            step_tasks.append(RaidTask(
                task_id=tid, name=tasks[tid]["name"], trader=tasks[tid].get("trader", ""),
                objectives=[obj_by_index(tid, i) for i in idxs], finishes=finishes,
            ))
        if not step_tasks:
            break
        for tid in finished_now:  # se entregan al volver de la raid
            started.discard(tid)
            sim.complete(tid)
        raids.append(RaidStep(number=len(raids) + 1, map_key=map_key, tasks=step_tasks))

    blocked = [t for t in plan_ids if t not in sim.done]
    return RaidPlan(raids=raids, offraid=offraid, blocked=blocked)
