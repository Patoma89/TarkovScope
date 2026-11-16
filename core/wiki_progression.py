"""
TarkovScope - Progresión de quests desde la wiki oficial de Escape from Tarkov (Fandom).

La wiki vigente describe el sistema de desbloqueo actual de cada quest en su "Infobox quest":
  * LL requirement : nivel de lealtad del trader necesario para recibirla.
  * LL quests      : cantidad de quests de ese trader y ese nivel que hay que tener completadas
                     (la wiki lo muestra como "LL<N> quests completed").
  * previous       : quests previas; separadas por "or" son alternativas.
y en la sección Rewards la reputación que otorga ("[[Prapor]] Rep +0.1").

Se descarga vía la API de MediaWiki identificándose con un User-Agent propio, y se combina con
los objetivos/mapas de tarkov.dev para armar el bloque "progression" del dataset de rutas.
Lógica pura de negocio: sin dependencias de UI.
"""
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

WIKI_API_URL = "https://escapefromtarkov.fandom.com/api.php"
WIKI_PARALLEL_REQUESTS = 4
WIKI_USER_AGENT = "TarkovScope/1.3.1 (desktop quest planner; https://github.com/Patoma89/TarkovScope)"

_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
_REP_RE = re.compile(r"\[\[([A-Za-z][A-Za-z .]+?)(?:\|[^\]]*)?\]\]\s*Rep\b[^\n]*?([+\-−–])\s*'*\s*([\d]+(?:\.\d+)?)")


def parse_infobox(wikitext: str) -> Dict[str, str]:
    """Campos del {{Infobox quest}} (claves en minúsculas, valores crudos sin espacios extremos)."""
    m = re.search(r"\{\{Infobox quest(.*?)\n\}\}", wikitext or "", re.S | re.I)
    fields: Dict[str, str] = {}
    if not m:
        return fields
    for line in m.group(1).split("\n|"):
        key, sep, value = line.partition("=")
        if sep:
            fields[key.strip().lower()] = value.strip()
    return fields


def parse_links(text: str) -> List[str]:
    return [l.strip() for l in _LINK_RE.findall(text or "") if l.strip()]


def parse_previous(text: str) -> List[List[str]]:
    """'[[A]]<br/>[[B]]' -> [[A], [B]] (ambas); '[[A]]<br/>or<br/>[[B]]' -> [[A, B]] (alguna)."""
    if not text:
        return []
    links = parse_links(text)
    if not links:
        return []
    plain = re.sub(r"<[^>]+>", " ", _LINK_RE.sub(" ", text)).lower()
    if re.search(r"\bor\b", plain):
        return [links]
    return [[l] for l in links]


def parse_int(text: str, default: int = 0) -> int:
    m = re.search(r"\d+", text or "")
    return int(m.group(0)) if m else default


def parse_reputation(wikitext: str) -> Dict[str, float]:
    """Reputación por trader de la sección ==Rewards== (positiva o negativa)."""
    m = re.search(r"==\s*Rewards\s*==(.*?)(?:\n==[^=]|\Z)", wikitext or "", re.S | re.I)
    section = m.group(1) if m else ""
    rep: Dict[str, float] = {}
    for trader, sign, value in _REP_RE.findall(section):
        delta = float(value) * (-1 if sign in "-−–" else 1)
        rep[trader.strip()] = round(rep.get(trader.strip(), 0.0) + delta, 3)
    return rep


def parse_quest_page(title: str, wikitext: str) -> Optional[Dict[str, Any]]:
    """Datos de progresión de una página de quest; None si no es una quest con infobox."""
    box = parse_infobox(wikitext)
    if not box:
        return None
    given = parse_links(box.get("given by", ""))
    return {
        "name": title,
        "trader": given[0] if given else "",
        "ll": parse_int(box.get("ll requirement", ""), 1) or 1,
        "ll_quests": parse_int(box.get("ll quests", ""), 0),
        "previous": parse_previous(box.get("previous", "")),
        "standing": parse_reputation(wikitext),
        "kappa": "yes" in (box.get("reqkappa", "") or "").lower(),
    }


KAPPA_QUEST = "Collector"
LIGHTKEEPER_ENTRY_QUEST = "Keeper's Word"


def parse_collector_requirements(wikitext: str) -> Dict[str, Any]:
    """Requisitos de Collector (contenedor Kappa) desde su sección ==Requirements==."""
    m = re.search(r"==\s*Requirements\s*==(.*?)(?:\n==[^=]|\Z)", wikitext or "", re.S | re.I)
    section = m.group(1) if m else ""
    out: Dict[str, Any] = {"traders": [], "level": 4, "player_level": 0, "quests": [], "notes": []}
    for line in section.split("\n"):
        stripped = line.strip()
        low = stripped.lower()
        if not stripped.startswith("*"):
            continue
        if "loyalty level" in low:
            out["level"] = parse_int(re.search(r"loyalty level\s*(\d+)", low).group(1) if re.search(r"loyalty level\s*(\d+)", low) else "4", 4)
            out["traders"] = parse_links(stripped)
        elif stripped.startswith("**"):
            out["quests"] += parse_links(stripped)
        elif re.search(r"\blevel\s+\d+", low) and "loyalty" not in low:
            out["player_level"] = parse_int(re.search(r"level\s+(\d+)", low).group(1))
        elif "karma" in low:
            plain = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", stripped).lstrip("* ").strip()
            out["notes"].append(plain)
    return out


def fetch_quest_pages(timeout: int = 60) -> Dict[str, str]:
    """Descarga el wikitext de todas las páginas de Category:Quests (título -> wikitext)."""
    import requests  # import diferido: el parser es testeable sin red

    headers = {"User-Agent": WIKI_USER_AGENT}

    def api(params: Dict[str, str]) -> Dict[str, Any]:
        resp = requests.get(WIKI_API_URL, params=params, headers=headers, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"wiki respondió {resp.status_code}")
        return resp.json()

    titles: List[str] = []
    cont: Dict[str, str] = {}
    while True:
        r = api({
            "action": "query", "list": "categorymembers", "cmtitle": "Category:Quests",
            "cmlimit": "500", "cmnamespace": "0", "format": "json", **cont,
        })
        titles += [m["title"] for m in r["query"]["categorymembers"]]
        if "continue" not in r:
            break
        cont = {"cmcontinue": r["continue"]["cmcontinue"]}
    def batch(chunk: List[str]) -> Dict[str, Any]:
        return api({
            "action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main",
            "titles": "|".join(chunk), "format": "json",
        })

    # Los lotes de 50 páginas se piden en paralelo (pocas conexiones, para no saturar la wiki).
    chunks = [titles[i:i + 50] for i in range(0, len(titles), 50)]
    pages: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=WIKI_PARALLEL_REQUESTS) as pool:
        for r in pool.map(batch, chunks):
            for p in r["query"]["pages"].values():
                if "revisions" in p:
                    pages[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
    return pages


def merge_progression(
    tdev_progression: Dict[str, Any],
    wiki_pages: Dict[str, str],
    normalize,
) -> Tuple[Dict[str, Any], Dict[str, int]]:
    """Aplica la progresión de la wiki sobre las quests vigentes de tarkov.dev (cruce por nombre).

    Devuelve (progression, estadísticas). Las quests sin página en la wiki conservan los datos de
    tarkov.dev; los prerrequisitos se guardan como grupos de ids: AND entre grupos, OR dentro.
    """
    tasks = tdev_progression.get("tasks", {})
    ids_by_name: Dict[str, List[str]] = {}
    for tid, t in tasks.items():
        ids_by_name.setdefault(normalize(t["name"]), []).append(tid)
    wiki = {}
    for title, text in wiki_pages.items():
        parsed = parse_quest_page(title, text)
        if parsed:
            wiki[normalize(title)] = parsed

    stats = {"wiki": 0, "tdev_only": 0, "unresolved_previous": 0}
    out_tasks: Dict[str, Any] = {}
    for tid, t in tasks.items():
        entry = dict(t)
        w = wiki.get(normalize(t["name"]))
        if w:
            stats["wiki"] += 1
            if w["trader"]:
                entry["trader"] = w["trader"]
            entry["ll"] = w["ll"]
            entry["ll_quests"] = w["ll_quests"]
            if w["standing"]:
                entry["standing"] = w["standing"]
            groups = []
            for group in w["previous"]:
                ids = [i for name in group for i in ids_by_name.get(normalize(name), [])]
                if ids:
                    groups.append(ids)
                else:
                    stats["unresolved_previous"] += 1
            entry["prev"] = groups
            entry["source"] = "wiki"
        else:
            stats["tdev_only"] += 1
            same_trader = [r["level"] for r in t.get("trader_reqs", []) if r["trader"] == t.get("trader")]
            entry["ll"] = max(same_trader) if same_trader else 1
            entry["ll_quests"] = 0
            entry["prev"] = [[r] for r in t.get("requires", [])]
            entry["source"] = "tarkov.dev"
        entry.pop("requires", None)
        entry.pop("min_level", None)
        out_tasks[tid] = entry
    result = dict(tdev_progression)
    result["tasks"] = out_tasks
    result["source"] = "wiki+tarkov.dev"
    result["goals"] = _special_goals(out_tasks, wiki_pages, ids_by_name, normalize)
    return result, stats


def _special_goals(tasks, wiki_pages, ids_by_name, normalize) -> Dict[str, Any]:
    """Metas compuestas: Kappa (requisitos de Collector) y desbloquear Lightkeeper."""
    goals: Dict[str, Any] = {}
    page = next((t for title, t in wiki_pages.items() if normalize(title) == normalize(KAPPA_QUEST)), "")
    if page:
        req = parse_collector_requirements(page)
        goals["kappa"] = {
            "quest": KAPPA_QUEST,
            "traders": req["traders"],
            "level": req["level"],
            "player_level": req["player_level"],
            "quests": [[i for i in ids_by_name.get(normalize(n), [])] for n in req["quests"]],
            "quest_names": req["quests"],
            "notes": req["notes"],
        }
    entry_ids = ids_by_name.get(normalize(LIGHTKEEPER_ENTRY_QUEST), [])
    if entry_ids:
        groups = tasks[entry_ids[0]].get("prev", [])
        goals["lightkeeper"] = {
            "quest": LIGHTKEEPER_ENTRY_QUEST,
            "quests": groups,
            "quest_names": [tasks[g[0]]["name"] for g in groups if g],
        }
    return goals
