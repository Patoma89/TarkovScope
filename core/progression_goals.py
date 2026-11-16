"""
TarkovScope - Metas del Planner de Progresión.

Cada meta se traduce a lo que entiende el motor (core/progression_planner):
  * targets  : [(trader, LL)] -> reputación a alcanzar
  * required : [[ids]]        -> quests a completar (alcanza con una id por grupo)
más avisos que no se pueden planificar con quests (nivel de jugador, karma de Scav...).

Tipos de meta:
  {"type": "trader", "trader": "Prapor", "level": 3}
  {"type": "kappa"}        -> requisitos de Collector según la wiki
  {"type": "lightkeeper"}  -> quests previas a Keeper's Word
  {"type": "quest", "name": "Saving the Mole"}
"""
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence, Tuple

from core.quest_route_data import normalize_quest_name

GOAL_TYPES = [
    ("trader", "Nivel de trader"),
    ("kappa", "Kappa (Collector)"),
    ("lightkeeper", "Desbloquear Lightkeeper"),
    ("quest", "Quest puntual"),
]
GOAL_LABELS = dict(GOAL_TYPES)


@dataclass
class ResolvedGoals:
    targets: List[Tuple[str, int]] = field(default_factory=list)
    required: List[List[str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    player_level: int = 0
    labels: List[str] = field(default_factory=list)  # una línea legible por meta


def _ids_for(progression: Dict[str, Any], name: str) -> List[str]:
    key = normalize_quest_name(name)
    return [tid for tid, t in progression.get("tasks", {}).items() if normalize_quest_name(t["name"]) == key]


def resolve_goals(progression: Dict[str, Any], goals: Sequence[Dict[str, Any]]) -> ResolvedGoals:
    special = progression.get("goals", {})
    out = ResolvedGoals()
    for g in goals:
        kind = g.get("type", "trader")
        if kind == "trader":
            out.targets.append((g.get("trader", "Prapor"), int(g.get("level", 2))))
            out.labels.append(f"{g.get('trader', 'Prapor')} LL{int(g.get('level', 2))}")
        elif kind == "kappa":
            k = special.get("kappa")
            if not k:
                out.notes.append("Kappa: faltan datos de Collector (sincronizá la base de datos).")
                continue
            out.targets += [(tr, int(k.get("level", 4))) for tr in k.get("traders", [])]
            out.required += [grp for grp in k.get("quests", []) if grp]
            out.player_level = max(out.player_level, int(k.get("player_level") or 0))
            out.notes += [f"Kappa: {_translate_note(n)}" for n in k.get("notes", [])]
            out.notes.append("Kappa: después hay que entregarle a Fence los ítems de Collector (FiR).")
            out.labels.append(f"Kappa: {len(k.get('traders', []))} traders en LL{k.get('level', 4)} + "
                              f"{len(k.get('quests', []))} quests")
        elif kind == "lightkeeper":
            lk = special.get("lightkeeper")
            if not lk:
                out.notes.append("Lightkeeper: faltan datos (sincronizá la base de datos).")
                continue
            out.required += [grp for grp in lk.get("quests", []) if grp]
            out.labels.append(f"Lightkeeper: {len(lk.get('quests', []))} quests para habilitar {lk.get('quest')}")
        elif kind == "quest":
            ids = _ids_for(progression, g.get("name", ""))
            if ids:
                out.required.append(ids)
                out.labels.append(f"Quest: {g.get('name')}")
            else:
                out.notes.append(f"No encontré la quest \"{g.get('name', '')}\".")
    # Un mismo trader pedido por varias metas (p. ej. Prapor LL3 + Kappa): queda el nivel más alto.
    best: Dict[str, int] = {}
    for trader, level in out.targets:
        best[trader] = max(best.get(trader, 0), level)
    out.targets = list(best.items())
    return out


def _translate_note(note: str) -> str:
    m = re.search(r"karma[^+\-\d]*([+\-]?\d+)", note, re.I)
    if m:
        return f"karma de Scav de al menos {m.group(1)} (no se sube con quests)"
    return note


def quest_names(progression: Dict[str, Any], faction: str) -> List[str]:
    """Nombres de quests vigentes de la facción, para el buscador de 'Quest puntual'."""
    names = set()
    for t in progression.get("tasks", {}).values():
        f = t.get("faction") or "Any"
        if f == "Any" or f.upper() == (faction or "").upper():
            names.add(t["name"])
    return sorted(names, key=str.lower)


def traders_in_goals(goals: Sequence[Dict[str, Any]], progression: Dict[str, Any]) -> List[str]:
    """Traders cuya reputación conviene pedirle al usuario según las metas cargadas."""
    out: List[str] = []
    for tr, _lvl in resolve_goals(progression, goals).targets:
        if tr not in out:
            out.append(tr)
    return out
