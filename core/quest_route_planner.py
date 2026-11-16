"""
TarkovScope - Planificador de rutas del Quest Tracker.

Dado un spawn, un conjunto de paradas (objetivos de quests, cada uno con una o varias
ubicaciones posibles) y las extracciones del mapa, encuentra el orden de visita que minimiza
la distancia total en metros: spawn -> paradas -> extracción.

* Hasta MAX_EXACT_STOPS paradas: óptimo exacto (programación dinámica de Held-Karp, eligiendo
  además cuál ubicación de cada objetivo conviene).
* Más paradas: vecino más cercano + mejora 2-opt.

Distancia: línea recta en metros (XZ) más una penalización por desnivel vertical. No contempla
paredes ni obstáculos, así que es una estimación del recorrido real.
Lógica pura de negocio: sin dependencias de UI.
"""
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

Point = Tuple[float, float, float]  # (x, y, z) en metros del juego; y = altura

MAX_EXACT_STOPS = 12
VERTICAL_WEIGHT = 1.5  # subir/bajar pisos cuesta más que caminar en plano


@dataclass
class Stop:
    key: str
    label: str
    quest: str
    candidates: List[Point]


@dataclass
class RouteLeg:
    stop: Optional[Stop]  # None = tramo final hacia la extracción
    point: Point
    distance: float
    cumulative: float
    candidate_index: int = 0


@dataclass
class RoutePlan:
    start: Point
    legs: List[RouteLeg] = field(default_factory=list)
    extract_name: Optional[str] = None
    extract_point: Optional[Point] = None
    total_distance: float = 0.0
    exact: bool = True

    @property
    def stop_legs(self) -> List[RouteLeg]:
        return [leg for leg in self.legs if leg.stop is not None]


def distance(a: Sequence[float], b: Sequence[float]) -> float:
    dx = a[0] - b[0]
    dz = a[2] - b[2]
    return math.hypot(dx, dz) + VERTICAL_WEIGHT * abs(a[1] - b[1])


def _best_extract(point: Point, extracts: Sequence[Tuple[str, Point]]) -> Tuple[Optional[str], Optional[Point], float]:
    best = (None, None, 0.0)
    best_d = float("inf")
    for name, pos in extracts:
        d = distance(point, pos)
        if d < best_d:
            best_d = d
            best = (name, pos, d)
    return best


def _solve_exact(
    start: Point, stops: List[Stop], extracts: Sequence[Tuple[str, Point]]
) -> Tuple[List[Tuple[int, int]], float]:
    """Held-Karp sobre nodos (parada, ubicación). Devuelve [(parada, ubicación)] y costo total."""
    nodes: List[Tuple[int, int, Point]] = [
        (si, ci, c) for si, s in enumerate(stops) for ci, c in enumerate(s.candidates)
    ]
    n_stops = len(stops)
    full = (1 << n_stops) - 1
    INF = float("inf")
    # dp[(mask, node)] = (costo, nodo_previo)
    dp: Dict[Tuple[int, int], Tuple[float, int]] = {}
    for ni, (si, _ci, p) in enumerate(nodes):
        dp[(1 << si, ni)] = (distance(start, p), -1)

    by_mask: Dict[int, List[int]] = {}
    for (mask, ni) in dp:
        by_mask.setdefault(mask, []).append(ni)

    dmat = [[distance(a[2], b[2]) for b in nodes] for a in nodes]
    for size in range(1, n_stops):
        for mask in [m for m in list(by_mask) if bin(m).count("1") == size]:
            for ni in by_mask[mask]:
                cost, _ = dp[(mask, ni)]
                for nj, (sj, _cj, _pj) in enumerate(nodes):
                    if mask & (1 << sj):
                        continue
                    nmask = mask | (1 << sj)
                    ncost = cost + dmat[ni][nj]
                    prev = dp.get((nmask, nj))
                    if prev is None:
                        by_mask.setdefault(nmask, []).append(nj)
                    if prev is None or ncost < prev[0]:
                        dp[(nmask, nj)] = (ncost, ni)

    best_cost, best_end = INF, -1
    for ni in by_mask.get(full, []):
        cost = dp[(full, ni)][0]
        if extracts:
            cost += _best_extract(nodes[ni][2], extracts)[2]
        if cost < best_cost:
            best_cost, best_end = cost, ni

    seq: List[Tuple[int, int]] = []
    mask, ni = full, best_end
    while ni != -1:
        si, ci, _ = nodes[ni]
        seq.append((si, ci))
        _, prev = dp[(mask, ni)]
        mask &= ~(1 << si)
        ni = prev
    seq.reverse()
    return seq, best_cost


def _route_cost(start: Point, pts: List[Point], extracts: Sequence[Tuple[str, Point]]) -> float:
    total, cur = 0.0, start
    for p in pts:
        total += distance(cur, p)
        cur = p
    if extracts:
        total += _best_extract(cur, extracts)[2]
    return total


def _solve_heuristic(
    start: Point, stops: List[Stop], extracts: Sequence[Tuple[str, Point]]
) -> List[Tuple[int, int]]:
    remaining = set(range(len(stops)))
    cur = start
    seq: List[Tuple[int, int]] = []
    while remaining:
        best = None
        for si in remaining:
            for ci, c in enumerate(stops[si].candidates):
                d = distance(cur, c)
                if best is None or d < best[0]:
                    best = (d, si, ci)
        _, si, ci = best
        seq.append((si, ci))
        cur = stops[si].candidates[ci]
        remaining.discard(si)

    improved = True
    while improved:
        improved = False
        pts = [stops[si].candidates[ci] for si, ci in seq]
        base = _route_cost(start, pts, extracts)
        for i in range(len(seq) - 1):
            for j in range(i + 1, len(seq)):
                cand = seq[:i] + seq[i:j + 1][::-1] + seq[j + 1:]
                cpts = [stops[si].candidates[ci] for si, ci in cand]
                if _route_cost(start, cpts, extracts) + 1e-6 < base:
                    seq, improved = cand, True
                    break
            if improved:
                break
    # Reelegir la mejor ubicación de cada parada dado el orden final.
    for k, (si, _ci) in enumerate(seq):
        prev = start if k == 0 else stops[seq[k - 1][0]].candidates[seq[k - 1][1]]
        nxt = stops[seq[k + 1][0]].candidates[seq[k + 1][1]] if k + 1 < len(seq) else None
        best_ci = min(
            range(len(stops[si].candidates)),
            key=lambda ci: distance(prev, stops[si].candidates[ci])
            + (distance(stops[si].candidates[ci], nxt) if nxt else 0.0),
        )
        seq[k] = (si, best_ci)
    return seq


def plan_route(
    start: Point,
    stops: Sequence[Stop],
    extracts: Sequence[Tuple[str, Point]] = (),
) -> RoutePlan:
    """Calcula la ruta más corta desde el spawn por todas las paradas hasta la mejor extracción."""
    usable = [s for s in stops if s.candidates]
    plan = RoutePlan(start=tuple(start))
    if not usable:
        if extracts:
            name, pos, d = _best_extract(start, extracts)
            plan.extract_name, plan.extract_point = name, pos
            plan.legs.append(RouteLeg(None, pos, d, d))
            plan.total_distance = d
        return plan

    if len(usable) <= MAX_EXACT_STOPS:
        seq, _ = _solve_exact(tuple(start), list(usable), extracts)
        plan.exact = True
    else:
        seq = _solve_heuristic(tuple(start), list(usable), extracts)
        plan.exact = False

    cur, total = tuple(start), 0.0
    for si, ci in seq:
        p = usable[si].candidates[ci]
        d = distance(cur, p)
        total += d
        plan.legs.append(RouteLeg(usable[si], p, d, total, ci))
        cur = p
    if extracts:
        name, pos, d = _best_extract(cur, extracts)
        total += d
        plan.extract_name, plan.extract_point = name, pos
        plan.legs.append(RouteLeg(None, pos, d, total))
    plan.total_distance = total
    return plan


def rank_spawns(
    spawns: Sequence[Tuple[str, Point]],
    stops: Sequence[Stop],
    extracts: Sequence[Tuple[str, Point]] = (),
) -> List[Tuple[str, RoutePlan]]:
    """Evalúa la ruta óptima desde cada spawn y los ordena de mejor a peor."""
    results = [(label, plan_route(pos, stops, extracts)) for label, pos in spawns]
    return sorted(results, key=lambda r: r[1].total_distance)


def nearest_index(point_xz: Tuple[float, float], points: Sequence[Sequence[float]]) -> int:
    """Índice del punto (x, y, z) más cercano a un (x, z) dado; -1 si la lista está vacía."""
    best_i, best_d = -1, float("inf")
    for i, p in enumerate(points):
        d = math.hypot(p[0] - point_xz[0], p[2] - point_xz[1])
        if d < best_d:
            best_i, best_d = i, d
    return best_i
