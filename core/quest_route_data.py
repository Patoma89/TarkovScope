"""
TarkovScope - Datos geográficos para el Quest Tracker (spawns PMC, extracciones y objetivos).

Fuente: dumps públicos de tarkov.dev (https://json.tarkov.dev/regular/maps y /tasks), que traen
posiciones en metros del juego, y la calibración de mapas 2D del repositorio de tarkov.dev
(src/data/maps.json). Se compactan en un único JSON local para uso 100 % offline.

Lógica pura de negocio: sin dependencias de UI.
"""
import json
import math
import os
import re
import urllib.parse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from core.config import CACHE_DIR, resolve_cache_read_path

TDEV_MAPS_URL = "https://json.tarkov.dev/regular/maps"
TDEV_TASKS_URL = "https://json.tarkov.dev/regular/tasks"
TDEV_MAP_META_URL = "https://raw.githubusercontent.com/the-hideout/tarkov-dev/main/src/data/maps.json"
TDEV_TRADERS_URL = "https://json.tarkov.dev/regular/traders"

ROUTE_DATA_SUBDIR = "route_data"
ROUTE_DATA_FILE = "quest_routes.json"
ROUTE_MAPS_SUBDIR = "route_maps"
DATASET_VERSION = 3

# Traders con niveles de lealtad que se pueden planificar (nombre visible -> normalizedName de tarkov.dev).
PLANNABLE_TRADERS = ["Prapor", "Therapist", "Skier", "Peacekeeper", "Mechanic", "Ragman", "Jaeger", "Ref"]

# Objetivos que se cumplen dentro de una raid; el resto (entregas, gunsmith, niveles...) se hace afuera.
RAID_OBJECTIVE_TYPES = {
    "visit", "mark", "plantItem", "plantQuestItem", "findQuestItem", "shoot", "extract", "useItem",
}

# Mapa canónico de tarkov.dev -> clave interna de TarkovScope (las variantes comparten coordenadas).
TDEV_TO_APP_MAP: Dict[str, str] = {
    "customs": "customs",
    "woods": "woods",
    "shoreline": "shoreline",
    "interchange": "interchange",
    "reserve": "reserve",
    "lighthouse": "lighthouse",
    "streets-of-tarkov": "streetsoftarkov",
    "factory": "factory",
    "night-factory": "factory",
    "ground-zero": "groundzero",
    "ground-zero-21": "groundzero",
    "the-lab": "lab",
}
# Variante de la que se toman spawns/extracciones para cada clave interna.
APP_MAP_PRIMARY_TDEV: Dict[str, str] = {
    "customs": "customs",
    "woods": "woods",
    "shoreline": "shoreline",
    "interchange": "interchange",
    "reserve": "reserve",
    "lighthouse": "lighthouse",
    "streetsoftarkov": "streets-of-tarkov",
    "factory": "factory",
    "groundzero": "ground-zero",
    "lab": "the-lab",
}
APP_MAP_LABELS: Dict[str, str] = {
    "customs": "Customs",
    "woods": "Woods",
    "shoreline": "Shoreline",
    "interchange": "Interchange",
    "reserve": "Reserve",
    "lighthouse": "Lighthouse",
    "streetsoftarkov": "Streets of Tarkov",
    "factory": "Factory",
    "groundzero": "Ground Zero",
    "lab": "The Lab",
}

OBJECTIVE_TYPE_LABELS: Dict[str, str] = {
    "visit": "Visitar zona",
    "mark": "Marcar con MS2000",
    "plantItem": "Colocar ítem",
    "plantQuestItem": "Colocar ítem de quest",
    "findQuestItem": "Recoger ítem de quest",
    "extract": "Extraer",
    "shoot": "Eliminar objetivos",
    "useItem": "Usar ítem",
}

SPAWN_CLUSTER_RADIUS_M = 45.0

# Nombres internos de tarkov.dev -> nombre visible en el juego (solo los inequívocos;
# el resto se embellece automáticamente con prettify_extract_name).
EXTRACT_DISPLAY_NAMES: Dict[str, str] = {
    "ex_customs_pmc_crossroads": "Crossroads",
    "ex_customs_coop_boiler": "Smuggler's Boat",
    "ex_customs_pmc_flare": "Extracción con bengala",
    "ex_customs_pmc_trailerpark": "Trailer Park",
    "ex_customs_pmc_auto": "Dorms V-Ex",
    "ex_customs_pmc_gasstation": "Old Gas Station",
    "un-sec": "Northern UN Roadblock",
    "Lighthouse_pass": "Path to Lighthouse",
    "Road_at_railbridge": "Railway Bridge",
    "Smugglers_Trail_coop": "Smuggler's Path (Co-op)",
    "ex_interchange_pmc_saferoom": "Saferoom Exfil",
    "ex_interchange_pmc_railway": "Railway Exfil",
    "ex_interchange_pmc_emercom": "Emercom Checkpoint",
    "ex_interchange_coop_basement": "Scav Camp (Co-op)",
    "ex_interchange_pmc_auto": "Power Station V-Ex",
    "Hole Exfill": "Hole in the Fence",
    "EXFIL_Train": "Armored Train",
    "EXFIL_vent": "Sewer Manhole",
    "EXFIL_Bunker_D2": "D-2",
    "EXFIL_Bunker": "Bunker Hermetic Door",
    "EXFIL_ScavCooperation": "Scav Lands (Co-op)",
    "Alpinist": "Cliff Descent",
    "Coastal_South_Road": "Southern Road",
    "Nothern_Checkpoint": "Northern Checkpoint",
    "tunnel_shared": "Side Tunnel (Co-op)",
    "Shorl_free": "Path to Shoreline",
    "Nakatani_stairs_free_exit": "Nakatani Basement Stairs",
    "Scav_coop_exit": "Scav Checkpoint (Co-op)",
    "Sandbox_VExit": "Police Cordon V-Ex",
    "lab_Hangar_Gate": "Hangar Gate",
    "lab_Elevator_Med": "Medical Block Elevator",
    "lab_Vent": "Ventilation Shaft",
    "lab_Elevator_Cargo": "Cargo Elevator",
    "lab_Elevator_Main": "Main Elevator",
    "lab_Parking_Gate": "Parking Gate",
    "lab_Under_Storage_Collector": "Sewage Conduit",
}

TRADER_NAMES_BY_ID: Dict[str, str] = {
    "54cb50c76803fa8b248b4571": "Prapor",
    "54cb57776803fa99248b456e": "Therapist",
    "579dc571d53a0658a154fbec": "Fence",
    "58330581ace78e27b8b10cee": "Skier",
    "5935c25fb3acc3127c3d8cd9": "Peacekeeper",
    "5a7c2eca46aef81a7ca2145d": "Mechanic",
    "5ac3b934156ae10c4430e83c": "Ragman",
    "5c0647fdd443bc2504c2d371": "Jaeger",
    "638f541a29ffd1183d187f57": "Lightkeeper",
    "6617beeaa9cfa777ca915b7c": "Ref",
}


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def _pos3(p: Optional[Dict[str, Any]]) -> Optional[List[float]]:
    if not p:
        return None
    try:
        return [round(float(p["x"]), 2), round(float(p.get("y", 0.0)), 2), round(float(p["z"]), 2)]
    except (KeyError, TypeError, ValueError):
        return None


def task_name_from_wiki_link(link: str) -> str:
    """'https://escapefromtarkov.fandom.com/wiki/Saving_the_Mole' -> 'Saving the Mole'."""
    if not link:
        return ""
    slug = link.rstrip("/").rsplit("/", 1)[-1]
    return urllib.parse.unquote(slug).replace("_", " ").strip()


def normalize_quest_name(name: str) -> str:
    """Clave de cruce tolerante a mayúsculas, puntuación y sufijos de facción."""
    clean = (name or "").lower()
    clean = re.sub(r"\[(pvp|pve) zone\]", "", clean)
    clean = re.sub(r"\((bear|usec)\)", "", clean)
    return re.sub(r"[^a-z0-9]+", "", clean)


def prettify_extract_name(raw: str, map_tdev: str) -> str:
    """'ex_customs_pmc_zb1011' -> 'ZB-1011'; los nombres ya legibles se conservan."""
    if not raw:
        return "Extracción"
    if raw in EXTRACT_DISPLAY_NAMES:
        return EXTRACT_DISPLAY_NAMES[raw]
    if not raw.lower().startswith("ex_"):
        text = re.sub(r"^(EXFIL_|lab_)", "", raw.replace("_scav", "")).replace("_", " ").strip()
        return " ".join(w if w.isupper() or "-" in w else w[:1].upper() + w[1:] for w in text.split())
    parts = raw.split("_")[1:]
    stop_words = {map_tdev.replace("-", ""), map_tdev, "pmc", "coop", "scav", "shared"}
    words = [w for w in parts if w.lower() not in stop_words]
    text = " ".join(words) or raw
    text = re.sub(r"\bzb(\d+)", lambda m: f"ZB-{m.group(1)}", text, flags=re.I)
    return " ".join(w if w.isupper() or "-" in w else w.capitalize() for w in text.split())


def _cluster_points(points: List[List[float]], radius: float) -> List[List[int]]:
    """Agrupamiento por enlace simple en el plano XZ (spawns contiguos = un mismo punto de inicio)."""
    n = len(points)
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    r2 = radius * radius
    for i in range(n):
        for j in range(i + 1, n):
            dx = points[i][0] - points[j][0]
            dz = points[i][2] - points[j][2]
            if dx * dx + dz * dz <= r2:
                parent[find(i)] = find(j)
    groups: Dict[int, List[int]] = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return list(groups.values())


def _compass(dx: float, dz: float) -> str:
    """Dirección cardinal aproximada de un vector en coordenadas del mapa ya rotadas a pantalla."""
    ang = math.degrees(math.atan2(-dz, dx)) % 360  # 0 = Este, 90 = Norte (pantalla)
    names = ["Este", "Noreste", "Norte", "Noroeste", "Oeste", "Suroeste", "Sur", "Sureste"]
    return names[int(((ang + 22.5) % 360) // 45)]


# ---------------------------------------------------------------------------
# Proyección mundo -> píxel (réplica de getCRS/applyRotation de tarkov.dev)
# ---------------------------------------------------------------------------

def rotate_world(x: float, z: float, rotation_deg: float) -> Tuple[float, float]:
    """Aplica la rotación de coordenadas de tarkov.dev; devuelve (lng', lat') rotados."""
    if not rotation_deg:
        return x, z
    a = math.radians(rotation_deg)
    c, s = math.cos(a), math.sin(a)
    return x * c - z * s, x * s + z * c


def world_to_crs_pixel(x: float, z: float, map_meta: Dict[str, Any], zoom: float = 0.0) -> Tuple[float, float]:
    """Punto mundo (x, z) -> píxel global de Leaflet (CRS.Simple + Transformation) a un zoom dado."""
    t = map_meta.get("transform") or [1, 0, 1, 0]
    scale_x, margin_x, scale_y, margin_y = t[0], t[1], -t[2], t[3]
    rx, ry = rotate_world(x, z, map_meta.get("coordinateRotation", 0) or 0)
    k = 2.0 ** zoom
    return k * (scale_x * rx + margin_x), k * (scale_y * ry + margin_y)


def world_to_image(x: float, z: float, image_calib: Dict[str, Any]) -> Tuple[float, float]:
    """Punto mundo -> píxel de la imagen pre-renderizada (calibración guardada junto a la imagen)."""
    px, py = world_to_crs_pixel(x, z, image_calib, image_calib.get("zoom", 0.0))
    return px - image_calib["origin_px"][0], py - image_calib["origin_px"][1]


# ---------------------------------------------------------------------------
# Construcción del dataset compacto
# ---------------------------------------------------------------------------

def _extract_map_meta(map_meta_raw: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for group in map_meta_raw or []:
        for m in group.get("maps", []):
            if m.get("projection") != "interactive":
                continue
            out[group.get("normalizedName", m.get("key", ""))] = {
                "transform": m.get("transform"),
                "coordinateRotation": m.get("coordinateRotation", 0),
                "bounds": m.get("bounds"),
                "svgBounds": m.get("svgBounds"),
                "tilePath": m.get("tilePath"),
                "svgPath": m.get("svgPath"),
                "tileSize": m.get("tileSize") or 256,
                "minZoom": m.get("minZoom"),
                "maxZoom": m.get("maxZoom"),
            }
            break
    return out


def _build_map_entry(app_key: str, tdev_map: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
    tdev_name = tdev_map.get("normalizedName", "")
    pmc_points: List[List[float]] = []
    for sp in tdev_map.get("spawns") or []:
        sides = sp.get("sides") or []
        cats = sp.get("categories") or []
        if "player" in cats and ("pmc" in sides or "all" in sides):
            p = _pos3(sp.get("position"))
            if p:
                pmc_points.append(p)

    extracts: List[Dict[str, Any]] = []
    seen_names = set()
    for ex in tdev_map.get("extracts") or []:
        faction = (ex.get("faction") or "").lower()
        raw_name = ex.get("name") or ""
        if faction not in ("pmc", "shared") or "secret" in raw_name.lower():
            continue
        p = _pos3(ex.get("position"))
        if not p:
            continue
        name = prettify_extract_name(raw_name, tdev_name)
        if name in seen_names:
            continue
        seen_names.add(name)
        extracts.append({"name": name, "pos": p, "shared": faction == "shared"})

    groups = []
    for idxs in _cluster_points(pmc_points, SPAWN_CLUSTER_RADIUS_M):
        cx = sum(pmc_points[i][0] for i in idxs) / len(idxs)
        cy = sum(pmc_points[i][1] for i in idxs) / len(idxs)
        cz = sum(pmc_points[i][2] for i in idxs) / len(idxs)
        groups.append({"pos": [round(cx, 2), round(cy, 2), round(cz, 2)], "points": len(idxs)})

    # Etiqueta legible: dirección en pantalla respecto al centro + extracción más cercana.
    if groups:
        rot = meta.get("coordinateRotation", 0) or 0
        rpts = [rotate_world(g["pos"][0], g["pos"][2], rot) for g in groups]
        mx = sum(p[0] for p in rpts) / len(rpts)
        mz = sum(p[1] for p in rpts) / len(rpts)
        # Orden estable: de norte a sur y de oeste a este en pantalla.
        order = sorted(range(len(groups)), key=lambda i: (round(-rpts[i][1] / 40), rpts[i][0]))
        groups = [groups[i] for i in order]
        rpts = [rpts[i] for i in order]
        for n, (g, rp) in enumerate(zip(groups, rpts), start=1):
            near = None
            best = float("inf")
            for ex in extracts:
                d = math.hypot(ex["pos"][0] - g["pos"][0], ex["pos"][2] - g["pos"][2])
                if d < best:
                    best, near = d, ex["name"]
            # El eje Y de pantalla crece hacia abajo; en coordenadas rotadas lat' crece hacia arriba.
            direction = _compass(rp[0] - mx, -(rp[1] - mz))
            label = f"Spawn {n} · {direction}"
            if near is not None and best <= 160:
                label += f" (cerca de {near})"
            g["label"] = label

    return {
        "key": app_key,
        "name": APP_MAP_LABELS.get(app_key, app_key.title()),
        "tdev": tdev_name,
        "meta": meta,
        "spawns": groups,
        "extracts": extracts,
    }


def _build_progression(
    tasks_by_id: Dict[str, Dict[str, Any]],
    id_to_app: Dict[str, str],
    traders_raw: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Grafo de progresión: prerrequisitos, reputación por quest y requisitos de nivel de cada trader."""
    traders_out: Dict[str, Any] = {}
    for tid, tr in ((traders_raw or {}).get("data") or {}).items():
        name = TRADER_NAMES_BY_ID.get(tid)
        if not name:
            continue
        traders_out[name] = {
            "levels": [
                {"level": lv.get("level"), "player_level": lv.get("requiredPlayerLevel") or 0,
                 "reputation": float(lv.get("requiredReputation") or 0.0)}
                for lv in sorted(tr.get("levels") or [], key=lambda x: x.get("level") or 0)
            ]
        }

    tasks_out: Dict[str, Any] = {}
    for task_id, task in tasks_by_id.items():
        name = task_name_from_wiki_link(task.get("wikiLink", ""))
        if not name:
            continue
        requires = []
        for req in task.get("taskRequirements") or []:
            # Solo cuentan los prerrequisitos que exigen completar; "failed"/"active" son ramas alternativas.
            if "complete" in (req.get("status") or []) and req.get("task") in tasks_by_id:
                requires.append(req["task"])
        trader_reqs = []
        for req in task.get("traderRequirements") or []:
            tname = TRADER_NAMES_BY_ID.get(str(req.get("trader") or ""))
            if tname and req.get("requirementType") == "level":
                trader_reqs.append({"trader": tname, "level": int(req.get("value") or 0)})
        standing: Dict[str, float] = {}
        for s in ((task.get("finishRewards") or {}).get("traderStanding")) or []:
            tname = TRADER_NAMES_BY_ID.get(str(s.get("trader") or ""))
            if tname:
                standing[tname] = round(standing.get(tname, 0.0) + float(s.get("standing") or 0.0), 3)
        objectives = []
        for idx, obj in enumerate(task.get("objectives") or []):
            if obj.get("optional"):
                continue
            maps = sorted({id_to_app[m] for m in (obj.get("maps") or []) if m in id_to_app})
            objectives.append({
                "index": idx,
                "type": obj.get("type", ""),
                "maps": maps,
                "raid": obj.get("type", "") in RAID_OBJECTIVE_TYPES,
            })
        tasks_out[task_id] = {
            "id": task_id,
            "name": name,
            "trader": TRADER_NAMES_BY_ID.get(str(task.get("trader") or ""), ""),
            "faction": task.get("factionName") or "Any",
            "min_level": int(task.get("minPlayerLevel") or 0),
            "kappa": bool(task.get("kappaRequired")),
            "requires": requires,
            "trader_reqs": trader_reqs,
            "standing": standing,
            "objectives": objectives,
        }
    return {"traders": traders_out, "tasks": tasks_out}


def build_route_dataset(
    maps_raw: Dict[str, Any],
    tasks_raw: Dict[str, Any],
    map_meta_raw: List[Dict[str, Any]],
    traders_raw: Optional[Dict[str, Any]] = None,
    wiki_pages: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Convierte los dumps crudos de tarkov.dev (y la wiki, si se pasa) en el dataset compacto."""
    maps_by_id: Dict[str, Dict[str, Any]] = (maps_raw.get("data") or {}).get("maps") or {}
    tasks_by_id: Dict[str, Dict[str, Any]] = (tasks_raw.get("data") or {}).get("tasks") or {}
    metas = _extract_map_meta(map_meta_raw)

    id_to_app: Dict[str, str] = {}
    by_tdev_name: Dict[str, Dict[str, Any]] = {}
    for mid, m in maps_by_id.items():
        tname = m.get("normalizedName", "")
        by_tdev_name[tname] = m
        if tname in TDEV_TO_APP_MAP:
            id_to_app[mid] = TDEV_TO_APP_MAP[tname]

    maps_out: Dict[str, Any] = {}
    for app_key, tdev_name in APP_MAP_PRIMARY_TDEV.items():
        tdev_map = by_tdev_name.get(tdev_name)
        meta = metas.get(tdev_name)
        if not tdev_map or not meta:
            continue
        maps_out[app_key] = _build_map_entry(app_key, tdev_map, meta)

    tasks_out: Dict[str, Any] = {}
    for task in tasks_by_id.values():
        name = task_name_from_wiki_link(task.get("wikiLink", ""))
        if not name:
            continue
        objectives = []
        faction = task.get("factionName") or "Any"
        for idx, obj in enumerate(task.get("objectives") or []):
            per_map: Dict[str, List[List[float]]] = {}
            for zone in obj.get("zones") or []:
                app_key = id_to_app.get(zone.get("map", ""))
                p = _pos3(zone.get("position"))
                if app_key and p:
                    per_map.setdefault(app_key, []).append(p)
            for loc in obj.get("possibleLocations") or []:
                app_key = id_to_app.get(loc.get("map", ""))
                for pos in loc.get("positions") or []:
                    p = _pos3(pos)
                    if app_key and p:
                        per_map.setdefault(app_key, []).append(p)
            obj_maps = sorted({id_to_app[m] for m in (obj.get("maps") or []) if m in id_to_app})
            for app_key, cands in per_map.items():
                uniq: List[List[float]] = []
                for c in cands:
                    if all(math.hypot(c[0] - u[0], c[2] - u[2]) > 3.0 for u in uniq):
                        uniq.append(c)
                objectives.append({
                    "index": idx,
                    "type": obj.get("type", ""),
                    "optional": bool(obj.get("optional")),
                    "map": app_key,
                    "candidates": uniq,
                    "faction": faction,
                })
            if not per_map and obj_maps and obj.get("type") in ("shoot", "extract", "findItem", "useItem"):
                for app_key in obj_maps:
                    objectives.append({
                        "index": idx,
                        "type": obj.get("type", ""),
                        "optional": bool(obj.get("optional")),
                        "map": app_key,
                        "candidates": [],
                        "faction": faction,
                    })
        if not objectives:
            continue
        entry = tasks_out.setdefault(name, {
            "name": name,
            "trader": TRADER_NAMES_BY_ID.get(str(task.get("trader") or ""), ""),
            "wiki": task.get("wikiLink", ""),
            "kappa": bool(task.get("kappaRequired")),
            "min_level": task.get("minPlayerLevel") or 0,
            "objectives": [],
        })
        # Variantes con el mismo nombre: se guardan con su facción para filtrarlas al usarlas.
        known = {(o["map"], o["index"], o["type"], o["faction"]) for o in entry["objectives"]}
        for o in objectives:
            if (o["map"], o["index"], o["type"], o["faction"]) not in known:
                entry["objectives"].append(o)

    return {
        "version": DATASET_VERSION,
        "source": "tarkov.dev",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "maps": maps_out,
        "tasks": tasks_out,
        "progression": _with_wiki(_build_progression(tasks_by_id, id_to_app, traders_raw), wiki_pages),
    }


def _with_wiki(progression: Dict[str, Any], wiki_pages: Optional[Dict[str, str]]) -> Dict[str, Any]:
    """Aplica la progresión vigente de la wiki (LL requerido, quests de LL, previas, reputación)."""
    from core.wiki_progression import merge_progression

    merged, stats = merge_progression(progression, wiki_pages or {}, normalize_quest_name)
    merged["wiki_stats"] = stats
    return merged


# ---------------------------------------------------------------------------
# Persistencia y descarga
# ---------------------------------------------------------------------------

def route_data_write_path() -> str:
    return os.path.join(CACHE_DIR, ROUTE_DATA_SUBDIR, ROUTE_DATA_FILE)


def save_route_dataset(dataset: Dict[str, Any], path: Optional[str] = None) -> str:
    dest = path or route_data_write_path()
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    tmp = dest + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(dataset, fh, ensure_ascii=False, separators=(",", ":"))
    os.replace(tmp, dest)
    return dest


_DATASET_CACHE: Dict[str, Any] = {}


def load_route_dataset(path: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
    """Carga el dataset (caché editable > instalación > bundle). Vacío si aún no existe."""
    src = path or resolve_cache_read_path(ROUTE_DATA_SUBDIR, ROUTE_DATA_FILE, min_bytes=64)
    if not force and _DATASET_CACHE.get("path") == src:
        return _DATASET_CACHE["data"]
    data: Dict[str, Any] = {"version": DATASET_VERSION, "maps": {}, "tasks": {}}
    if os.path.exists(src):
        try:
            with open(src, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            pass
    _DATASET_CACHE.update({"path": src, "data": data})
    return data


def download_route_dataset(timeout: int = 60) -> Dict[str, Any]:
    """Descarga los dumps de tarkov.dev y devuelve el dataset compacto (no lo guarda)."""
    import requests  # import diferido: el resto del módulo es testeable sin red

    def get_json(url: str):
        resp = requests.get(url, timeout=timeout)
        if resp.status_code != 200:
            raise RuntimeError(f"{url} respondió {resp.status_code}")
        return resp.json()

    from concurrent.futures import ThreadPoolExecutor

    from core.wiki_progression import fetch_quest_pages

    # Las 4 descargas de tarkov.dev y la de la wiki son independientes: van en paralelo.
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = [pool.submit(get_json, url) for url in
                   (TDEV_MAPS_URL, TDEV_TASKS_URL, TDEV_MAP_META_URL, TDEV_TRADERS_URL)]
        wiki_future = pool.submit(fetch_quest_pages, timeout)
        maps_raw, tasks_raw, meta_raw, traders_raw = (f.result() for f in futures)
        wiki_pages = wiki_future.result()
    return build_route_dataset(maps_raw, tasks_raw, meta_raw, traders_raw, wiki_pages)


def refresh_route_dataset(timeout: int = 60) -> bool:
    """Descarga y guarda el dataset; conserva el anterior si algo falla."""
    try:
        dataset = download_route_dataset(timeout=timeout)
    except Exception:
        return False
    if len(dataset.get("maps", {})) < 5 or len(dataset.get("tasks", {})) < 50:
        return False
    if len(dataset.get("progression", {}).get("traders", {})) < 5:
        return False
    if dataset.get("progression", {}).get("wiki_stats", {}).get("wiki", 0) < 100:
        return False  # la wiki no respondió: mejor conservar el dataset anterior
    save_route_dataset(dataset)
    load_route_dataset(force=True)
    return True


# ---------------------------------------------------------------------------
# Consultas
# ---------------------------------------------------------------------------

def get_route_maps(dataset: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    ds = dataset if dataset is not None else load_route_dataset()
    order = list(APP_MAP_PRIMARY_TDEV.keys())
    maps = list(ds.get("maps", {}).values())
    return sorted(maps, key=lambda m: order.index(m["key"]) if m["key"] in order else 99)


def _objective_faction_ok(obj: Dict[str, Any], faction: Optional[str]) -> bool:
    f = obj.get("faction") or "Any"
    return faction is None or f == "Any" or f.upper() == faction.upper()


def get_tasks_for_map(
    map_key: str, dataset: Optional[Dict[str, Any]] = None, faction: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Quests con al menos un objetivo en el mapa, con sus objetivos filtrados a ese mapa.

    Con `faction` ("BEAR"/"USEC") se descartan los objetivos de la variante de la otra facción.
    """
    ds = dataset if dataset is not None else load_route_dataset()
    out = []
    for task in ds.get("tasks", {}).values():
        objs = [o for o in task.get("objectives", [])
                if o.get("map") == map_key and _objective_faction_ok(o, faction)]
        if objs:
            t = dict(task)
            t["objectives"] = objs
            out.append(t)
    return sorted(out, key=lambda t: t["name"].lower())


def objective_label(obj: Dict[str, Any]) -> str:
    base = OBJECTIVE_TYPE_LABELS.get(obj.get("type", ""), "Objetivo")
    n = len(obj.get("candidates") or [])
    if n > 1:
        base += f" ({n} ubicaciones posibles)"
    if obj.get("optional"):
        base += " · opcional"
    return base
