"""
TarkovScope - Mixin API WebView2: Progresión
Expone Quests & Traders, Dossier Wiki Offline, Inventario de Traders (LL1-LL4),
Quest Tracker & Rutas Óptimas, Planner de Progresión y Quests de Historia.
Módulo de lógica pura (sin Tkinter ni pywebview).
"""
import json
import os
from typing import Any, Dict, List, Optional, Tuple

from core.config import CACHE_DIR
from core.maps_data import normalize_map_key
from core.progression_plan_store import sync_quest_completion
from core.quest_guides_data import get_quest_tactical_guide
from core.quest_route_data import (
    ROUTE_MAPS_SUBDIR,
    get_route_maps,
    get_tasks_for_map,
    load_route_dataset,
    objective_label,
    world_to_image,
)
from core.quest_route_planner import Stop, plan_route
from core.trader_assortment_data import get_trader_assortment, get_trader_requirements


WIKI_TRADERS_ORDER = [
    "Prapor", "Therapist", "Fence", "Skier", "Peacekeeper",
    "Mechanic", "Ragman", "Jaeger", "Lightkeeper", "BTR Driver", "Ref",
]

ASSORTMENT_TRADERS = [
    "Prapor", "Therapist", "Skier", "Peacekeeper",
    "Mechanic", "Ragman", "Jaeger", "Ref", "Fence",
]


class WebAPIProgressionMixin:
    """Endpoints de Quests, Dossier Wiki, Traders LL1-LL4, Rutas Óptimas e Historia."""

    # --- QUESTS & TRADERS ---

    def get_quests_data(
        self,
        trader: str = "TODOS",
        map_filter: str = "TODOS",
        mode: str = "CORRELATIVE",
        query: str = "",
        hide_completed: bool = False,
    ) -> Dict[str, Any]:
        ds = self._ds()
        quests = ds.get_quests(
            trader_filter=trader or "TODOS",
            map_filter=map_filter or "TODOS",
            search_query=query or "",
            hide_completed=bool(hide_completed),
            progression_mode=mode or "CORRELATIVE",
        )
        done, total = ds.get_quest_completion_counts()
        traders = [
            {
                "name": t,
                "avatar_url": f"/cache/avatars/{t.lower().replace(' ', '_')}.png",
            }
            for t in WIKI_TRADERS_ORDER
        ]
        items = [
            {
                "id": int(q.get("id", 0)),
                "title": q.get("title", ""),
                "trader_name": q.get("trader_name", ""),
                "trader_avatar": f"/cache/avatars/{str(q.get('trader_name', 'prapor')).lower().replace(' ', '_')}.png",
                "primary_map": q.get("primary_map", "Any Location"),
                "level_req": int(q.get("level_req", 1) or 1),
                "exp": int(q.get("exp", 0) or 0),
                "is_completed": bool(q.get("is_completed")),
                "is_kappa": bool(q.get("is_kappa")),
                "is_lightkeeper": bool(q.get("is_lightkeeper")),
                "objectives_lines": q.get("objectives_lines", [])[:6],
                "rewards_lines": q.get("rewards_lines", [])[:5],
                "wiki_url": q.get("wiki_url", ""),
            }
            for q in quests
        ]
        return {
            "traders": traders,
            "done": done,
            "total": total,
            "count": len(items),
            "items": items,
        }

    def get_quest_guide(self, quest_id: int) -> Dict[str, Any]:
        ds = self._ds()
        quest = ds._quests_by_id.get(int(quest_id))
        if not quest:
            return {"ok": False, "error": "Quest no encontrada"}
        guide = get_quest_tactical_guide(quest)
        map_key = normalize_map_key(guide.get("map_key") or quest.get("primary_map", ""))
        return {
            "ok": True,
            "quest": {
                "id": int(quest.get("id", 0)),
                "title": quest.get("title", ""),
                "trader_name": quest.get("trader_name", ""),
                "primary_map": quest.get("primary_map", "Any Location"),
                "level_req": int(quest.get("level_req", 1) or 1),
                "exp": int(quest.get("exp", 0) or 0),
                "is_completed": bool(quest.get("is_completed")),
                "is_kappa": bool(quest.get("is_kappa")),
                "is_lightkeeper": bool(quest.get("is_lightkeeper")),
                "objectives_lines": quest.get("objectives_lines", []),
                "rewards_lines": quest.get("rewards_lines", []),
                "prereq_titles": quest.get("prereq_titles", []),
                "unlocks_titles": quest.get("unlocks_titles", []),
                "wiki_url": quest.get("wiki_url", ""),
            },
            "guide": guide,
            "map_image_url": f"/cache/maps/{map_key}.png" if map_key else "",
        }

    def toggle_quest_synced(self, quest_id: int) -> Dict[str, Any]:
        ds = self._ds()
        new_state = ds.toggle_quest(int(quest_id))
        quest = ds._quests_by_id.get(int(quest_id))
        if quest:
            try:
                sync_quest_completion(quest.get("title", ""), bool(new_state))
            except Exception:
                pass
        done, total = ds.get_quest_completion_counts()
        return {
            "ok": True,
            "quest_id": int(quest_id),
            "is_completed": bool(new_state),
            "done": done,
            "total": total,
            "command_center": self.get_command_center_data(),
        }

    # --- INVENTARIO DE TRADERS (LL1 - LL4) ---

    def get_trader_assortment_data(self, trader: str = "Prapor", ll: int = 1) -> Dict[str, Any]:
        clean_trader = trader if trader in ASSORTMENT_TRADERS else "Prapor"
        clean_ll = max(1, min(4, int(ll or 1)))
        items = get_trader_assortment(clean_trader, clean_ll)
        reqs = get_trader_requirements(clean_trader, clean_ll)
        stock_file = f"{clean_trader.replace(' ', '').capitalize()}{clean_ll}Stock.png"
        return {
            "traders": [
                {"name": t, "avatar_url": f"/cache/avatars/{t.lower().replace(' ', '_')}.png"}
                for t in ASSORTMENT_TRADERS
            ],
            "trader": clean_trader,
            "ll": clean_ll,
            "requirements": reqs,
            "stock_image_url": f"/cache/trader_stocks/{stock_file}",
            "items": items,
        }

    # --- QUEST TRACKER & RUTAS ÓPTIMAS ---

    @staticmethod
    def _load_route_map_calib(map_key: str) -> Optional[Dict[str, Any]]:
        calib_path = os.path.join(CACHE_DIR, ROUTE_MAPS_SUBDIR, f"{map_key}.json")
        if not os.path.isfile(calib_path):
            return None
        try:
            with open(calib_path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return None

    @staticmethod
    def _project_world_pct(
        pos: Tuple[float, float, float],
        calib: Optional[Dict[str, Any]],
    ) -> Optional[Tuple[float, float]]:
        if not calib:
            return None
        w = float(calib.get("width") or 0)
        h = float(calib.get("height") or 0)
        if w <= 0 or h <= 0:
            return None
        try:
            px, py = world_to_image(float(pos[0]), float(pos[2]), calib)
            return (round((px / w) * 100.0, 2), round((py / h) * 100.0, 2))
        except Exception:
            return None

    def get_route_maps_list(self) -> List[Dict[str, Any]]:
        dataset = load_route_dataset()
        maps = get_route_maps(dataset)
        out = []
        for m in maps:
            calib = self._load_route_map_calib(m["key"])
            img_url = (
                f"/cache/{ROUTE_MAPS_SUBDIR}/{calib['image']}"
                if calib and calib.get("image")
                else f"/cache/maps/{normalize_map_key(m['key'])}.png"
            )
            out.append({
                "key": m["key"],
                "label": m.get("name", m["key"].title()),
                "spawns_count": len(m.get("spawns") or []),
                "extracts_count": len(m.get("extracts") or []),
                "image_url": img_url,
            })
        return out

    def get_route_map_tasks(self, map_key: str) -> Dict[str, Any]:
        dataset = load_route_dataset()
        maps = get_route_maps(dataset)
        map_info = next((m for m in maps if m["key"] == map_key), {})
        calib = self._load_route_map_calib(map_key)
        img_url = (
            f"/cache/{ROUTE_MAPS_SUBDIR}/{calib['image']}"
            if calib and calib.get("image")
            else f"/cache/maps/{normalize_map_key(map_key)}.png"
        )
        raw_tasks = get_tasks_for_map(map_key, dataset)
        tasks_out = []
        for t in raw_tasks:
            t_name = t.get("name", "")
            objs = t.get("objectives") or []
            tasks_out.append({
                "id": t_name,
                "name": t_name,
                "trader": t.get("trader", ""),
                "kappa": bool(t.get("kappa")),
                "min_level": int(t.get("min_level", 0) or 0),
                "objectives_count": len(objs),
                "objectives": [
                    {
                        "index": o.get("index", idx),
                        "label": objective_label(o),
                        "optional": bool(o.get("optional")),
                        "candidates_count": len(o.get("candidates") or []),
                    }
                    for idx, o in enumerate(objs)
                ],
            })

        spawns_out = []
        for idx, sp in enumerate((map_info.get("spawns") or [])[:40]):
            pos = sp.get("pos") or [0.0, 0.0, 0.0]
            pct = self._project_world_pct(
                (float(pos[0]), float(pos[1]), float(pos[2]) if len(pos) > 2 else 0.0),
                calib,
            )
            spawns_out.append({
                "index": idx,
                "label": sp.get("label") or f"Spawn #{idx + 1}",
                "pos": list(pos),
                "x_pct": pct[0] if pct else None,
                "y_pct": pct[1] if pct else None,
            })

        return {
            "map_key": map_key,
            "name": map_info.get("name", map_key.title()),
            "image_url": img_url,
            "calibrated": bool(calib),
            "meta": map_info.get("meta") or {},
            "spawns": spawns_out,
            "extracts": map_info.get("extracts") or [],
            "tasks": tasks_out,
        }

    def compute_optimal_route(
        self,
        map_key: str,
        task_ids: List[str],
        spawn_index: int = 0,
    ) -> Dict[str, Any]:
        dataset = load_route_dataset()
        maps = get_route_maps(dataset)
        map_info = next((m for m in maps if m["key"] == map_key), {})
        calib = self._load_route_map_calib(map_key)
        spawns = map_info.get("spawns") or []
        extracts = map_info.get("extracts") or []
        tasks = get_tasks_for_map(map_key, dataset)
        selected_set = {str(t) for t in (task_ids or [])}

        stops: List[Stop] = []
        for task in tasks:
            t_name = str(task.get("name") or "")
            if t_name not in selected_set:
                continue
            objs = task.get("objectives") or []
            mandatory = [o for o in objs if not o.get("optional") and o.get("candidates")]
            chosen_objs = mandatory if mandatory else [o for o in objs if o.get("candidates")]
            for idx, obj in enumerate(chosen_objs):
                cands = [
                    (float(c[0]), float(c[1]), float(c[2]) if len(c) > 2 else 0.0)
                    for c in (obj.get("candidates") or [])
                    if isinstance(c, (list, tuple)) and len(c) >= 2
                ]
                if not cands:
                    continue
                lbl = objective_label(obj)
                stops.append(Stop(
                    key=f"{t_name}::{obj.get('index', idx)}",
                    label=f"{t_name} — {lbl}",
                    quest=t_name,
                    candidates=cands,
                ))

        if not stops:
            return {"ok": False, "error": "Selecciona al menos una misión con objetivos geolocalizados."}

        start_pos = (0.0, 0.0, 0.0)
        start_label = "Spawn"
        if spawns and 0 <= int(spawn_index) < len(spawns):
            sp = spawns[int(spawn_index)]
            p = sp.get("pos") or [0.0, 0.0, 0.0]
            start_pos = (float(p[0]), float(p[1]), float(p[2]) if len(p) > 2 else 0.0)
            start_label = sp.get("label") or f"Spawn #{int(spawn_index) + 1}"

        ext_tuples = []
        for ex in extracts:
            ep = ex.get("pos")
            if ep and len(ep) >= 2:
                ext_tuples.append((
                    str(ex.get("name") or "Extract"),
                    (float(ep[0]), float(ep[1]), float(ep[2]) if len(ep) > 2 else 0.0),
                ))

        plan = plan_route(start_pos, stops, ext_tuples)
        start_pct = self._project_world_pct(plan.start, calib)
        ext_pct = self._project_world_pct(plan.extract_point, calib) if plan.extract_point else None

        ordered_stops = []
        for leg in plan.legs:
            if leg.stop is None:
                continue
            lpct = self._project_world_pct(leg.point, calib)
            ordered_stops.append({
                "key": leg.stop.key,
                "quest": leg.stop.quest,
                "label": leg.stop.label,
                "distance": round(float(leg.distance), 1),
                "cumulative": round(float(leg.cumulative), 1),
                "pos": list(leg.point),
                "x_pct": lpct[0] if lpct else None,
                "y_pct": lpct[1] if lpct else None,
            })

        return {
            "ok": True,
            "total_distance": round(float(plan.total_distance), 1),
            "exact": bool(plan.exact),
            "start": {
                "label": start_label,
                "pos": list(plan.start),
                "x_pct": start_pct[0] if start_pct else None,
                "y_pct": start_pct[1] if start_pct else None,
            },
            "extract_name": plan.extract_name or "",
            "extract": {
                "name": plan.extract_name or "",
                "pos": list(plan.extract_point) if plan.extract_point else None,
                "x_pct": ext_pct[0] if ext_pct else None,
                "y_pct": ext_pct[1] if ext_pct else None,
            } if plan.extract_point else None,
            "ordered_stops": ordered_stops,
        }

    # --- QUESTS DE HISTORIA (10 CAPÍTULOS) ---

    def get_story_chapters_data(self) -> Dict[str, Any]:
        ds = self._ds()
        chapters = ds.get_wiki_story_chapters()
        completed = ds.get_completed_story_ids()
        out_chapters: List[Dict[str, Any]] = []
        for ch in chapters:
            c = dict(ch)
            if c.get("icon_file"):
                c["icon_url"] = f"/cache/story_chapters/{c['icon_file']}"
            if c.get("banner_file"):
                c["banner_url"] = f"/cache/story_chapters/{c['banner_file']}"
            objectives = []
            for obj in c.get("objectives", []):
                o_copy = dict(obj)
                o_copy["is_completed"] = str(o_copy.get("id", "")) in completed or bool(o_copy.get("is_completed"))
                objectives.append(o_copy)
            c["objectives"] = objectives
            c["completed_count"] = sum(1 for o in objectives if o["is_completed"])
            c["total_count"] = len(objectives)

            guide_steps = []
            for gs in c.get("guide_steps", []):
                g_copy = dict(gs)
                gal = []
                for im in g_copy.get("gallery", []) or []:
                    im_copy = dict(im)
                    if im_copy.get("file"):
                        im_copy["url"] = f"/cache/story_chapters/gallery/{im_copy['file']}"
                    gal.append(im_copy)
                g_copy["gallery"] = gal
                guide_steps.append(g_copy)
            c["guide_steps"] = guide_steps
            out_chapters.append(c)
        return {"chapters": out_chapters}

    def toggle_story_quest(self, quest_id: str) -> Dict[str, Any]:
        ds = self._ds()
        new_state = ds.toggle_story_quest(str(quest_id))
        return {"ok": True, "quest_id": str(quest_id), "is_completed": bool(new_state)}
