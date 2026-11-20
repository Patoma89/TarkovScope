"""
TarkovScope - Mixin API WebView2: Incursión & Mapas
Expone Mapas 2D interactivos (extracciones, POIs, pines de usuario),
Bosses & Spawns (PvE/PvP + sync eftboss.com + Facciones IA) y Llaves & Intel.
Módulo de lógica pura (sin Tkinter ni pywebview).
"""
import json
import os
from typing import Any, Dict, List

from core.ai_factions_data import AI_FACTIONS_CATALOG
from core.bosses_data import get_all_bosses, sync_live_boss_spawns_from_eftboss
from core.config import BASE_DIR, BUNDLE_DIR, CACHE_DIR, READONLY_CACHE_DIR
from core.image_cache import get_boss_spawn_map_paths
from core.keys_data import (
    KEYS_CATALOG,
    get_key_stats,
    get_keys_categories,
    get_keys_maps,
)
from core.maps_data import (
    get_map_extractions_with_coords,
    get_map_tactical_pois,
    normalize_map_key,
)
from core.quest_route_data import (
    ROUTE_MAPS_SUBDIR,
    get_route_maps,
    load_route_dataset,
    prettify_extract_name,
    world_to_image,
)
from core.tactical_map_renderer import load_boss_spawn_map_image
from core.user_data import get_owned_key_ids, toggle_owned_key


class WebAPIIncursionMixin:
    """Endpoints de Mapas 2D, Bosses/Facciones IA y Llaves & Intel."""

    # --- MAPAS 2D INTERACTIVOS ---

    def get_maps_catalog(self) -> List[Dict[str, Any]]:
        ds = self._ds()
        out: List[Dict[str, Any]] = []
        for m in ds.get_maps():
            key = m.get("key") or normalize_map_key(m.get("name", ""))
            out.append({
                "key": key,
                "name": m.get("name", key.title()),
                "raid_duration": m.get("raid_duration_str") or f"{m.get('raid_duration', 40)} min",
                "players": m.get("players_str") or m.get("players", "8-14 PMCs"),
                "description": m.get("description", ""),
                "enemies": m.get("enemies", []),
                "image_url": f"/cache/maps/{key}.png",
            })
        return out

    _TDEV_LAYERS_CACHE: Dict[str, Any] = {}

    @classmethod
    def _load_tarkov_dev_layers(cls) -> Dict[str, Any]:
        if cls._TDEV_LAYERS_CACHE:
            return cls._TDEV_LAYERS_CACHE
        for base in (BASE_DIR, BUNDLE_DIR):
            cand = os.path.join(base, "data", "tarkov_dev_map_layers.json")
            if os.path.isfile(cand):
                try:
                    with open(cand, "r", encoding="utf-8") as fh:
                        cls._TDEV_LAYERS_CACHE = json.load(fh)
                        return cls._TDEV_LAYERS_CACHE
                except Exception:
                    pass
        return {}

    def get_map_detail(self, map_key: str) -> Dict[str, Any]:
        ds = self._ds()
        norm = normalize_map_key(map_key)
        m = ds.get_map_by_key_or_name(norm)
        key = m.get("key") or norm
        tdev_all = self._load_tarkov_dev_layers()
        tdev = tdev_all.get(key) or {}
        markers = ds.get_markers(key)

        if tdev:
            image_url = tdev["image_url"]
            extractions = tdev.get("extracts") or []
            pois_on_map = tdev.get("locks") or []
            boss_by_name: Dict[str, List[Dict[str, Any]]] = {}
            for bp in tdev.get("boss_pins") or []:
                boss_by_name.setdefault(bp["boss"], []).append(bp)
            bosses_here: List[Dict[str, Any]] = []
            for b in get_all_bosses():
                short_n = b["name"].split(" (")[0]
                matched = boss_by_name.get(short_n) or boss_by_name.get(b["name"])
                if not matched:
                    # Chequear si el boss aparece en este mapa aunque no tenga polígono en tdev
                    if any(normalize_map_key(mn) == key for mn in (b.get("maps") or [])):
                        matched = []
                    else:
                        continue
                bosses_here.append({
                    "id": b["id"],
                    "name": b["name"],
                    "avatar_url": f"/cache/avatars/{b['id']}.png",
                    "pve_chance": b.get("pve_chance", ""),
                    "pvp_chance": b.get("pvp_chance", ""),
                    "spawns": matched,
                })
            return {
                "key": key,
                "name": m.get("name", key.title()),
                "raid_duration": m.get("raid_duration_str") or f"{m.get('raid_duration', 40)} min",
                "players": m.get("players_str") or m.get("players", "8-14 PMCs"),
                "description": m.get("description", ""),
                "image_url": image_url,
                "calibrated_tarkov_dev": True,
                "extractions": extractions,
                "pois": pois_on_map,
                "pois_on_map": pois_on_map,
                "bosses": bosses_here,
                "markers": markers,
            }

        # Fallback para mapas sin calibración tarkov.dev (ej. Icebreaker)
        image_url = f"/cache/maps/{key}.png"
        extractions = get_map_extractions_with_coords(key)
        pois = get_map_tactical_pois(key)
        bosses_here = []
        for b in get_all_bosses():
            spawns = []
            for mk, sv in (b.get("map_spawns") or {}).items():
                if normalize_map_key(mk) == key:
                    spawns = sv
                    break
            if spawns:
                bosses_here.append({
                    "id": b["id"],
                    "name": b["name"],
                    "avatar_url": f"/cache/avatars/{b['id']}.png",
                    "pve_chance": b.get("pve_chance", ""),
                    "pvp_chance": b.get("pvp_chance", ""),
                    "spawns": spawns,
                })

        return {
            "key": key,
            "name": m.get("name", key.title()),
            "raid_duration": m.get("raid_duration_str") or f"{m.get('raid_duration', 40)} min",
            "players": m.get("players_str") or m.get("players", "8-14 PMCs"),
            "description": m.get("description", ""),
            "image_url": image_url,
            "calibrated_tarkov_dev": False,
            "extractions": extractions,
            "pois": pois,
            "pois_on_map": pois,
            "bosses": bosses_here,
            "markers": markers,
        }

    def add_map_marker(
        self,
        map_key: str,
        x_pct: float,
        y_pct: float,
        title: str,
        category: str = "Nota Personal",
        color: str = "#E5732F",
    ) -> Dict[str, Any]:
        ds = self._ds()
        norm = normalize_map_key(map_key)
        mid = ds.add_marker(norm, float(x_pct), float(y_pct), str(title or "Pin").strip(), str(category), str(color))
        return {"ok": True, "id": mid, "markers": ds.get_markers(norm)}

    def delete_map_marker(self, map_key: str, marker_id: int) -> Dict[str, Any]:
        ds = self._ds()
        norm = normalize_map_key(map_key)
        ds.delete_marker(int(marker_id))
        return {"ok": True, "markers": ds.get_markers(norm)}

    # --- BOSSES & FACCIONES IA ---

    def get_bosses_data(self) -> Dict[str, Any]:
        bosses: List[Dict[str, Any]] = []
        for b in get_all_bosses():
            b_copy = dict(b)
            b_copy["avatar_url"] = f"/cache/avatars/{b['id']}.png"
            b_copy["map_keys"] = [normalize_map_key(mn) for mn in b.get("maps", [])]
            spawn_urls: Dict[str, str] = {}
            for mn in b.get("maps", []):
                _, hd_path = get_boss_spawn_map_paths(b["id"], mn)
                if os.path.isfile(hd_path):
                    spawn_urls[mn] = f"/cache/boss_maps/{os.path.basename(hd_path)}"
            b_copy["map_spawn_urls"] = spawn_urls
            bosses.append(b_copy)
        return {
            "bosses": bosses,
            "factions": AI_FACTIONS_CATALOG,
        }

    def get_boss_spawn_map_url(self, boss_id: str, map_name: str) -> Dict[str, Any]:
        boss = next((b for b in get_all_bosses() if b["id"] == boss_id), None)
        if not boss:
            return {"ok": False, "url": f"/cache/maps/{normalize_map_key(map_name)}.png"}
        _, hd_path = get_boss_spawn_map_paths(boss_id, map_name)
        if not os.path.isfile(hd_path):
            try:
                load_boss_spawn_map_image(boss, map_name, high_res=True)
            except Exception:
                pass
        if os.path.isfile(hd_path):
            return {"ok": True, "url": f"/cache/boss_maps/{os.path.basename(hd_path)}"}
        return {"ok": False, "url": f"/cache/maps/{normalize_map_key(map_name)}.png"}

    def sync_boss_spawns_live(self) -> Dict[str, Any]:
        ok, msg = sync_live_boss_spawns_from_eftboss()
        return {
            "ok": bool(ok),
            "message": str(msg),
            "data": self.get_bosses_data(),
        }

    # --- LLAVES & INTEL ---

    def get_keys_data(self) -> Dict[str, Any]:
        owned = get_owned_key_ids(db_path=self._db_path)
        items: List[Dict[str, Any]] = []
        for k in KEYS_CATALOG:
            item = dict(k)
            item["owned"] = k["id"] in owned
            item["icon_url"] = f"/cache/keys/{k['id']}.png"
            items.append(item)
        return {
            "maps": get_keys_maps(),
            "categories": get_keys_categories(),
            "stats": get_key_stats(owned),
            "items": items,
        }

    def toggle_key_owned(self, key_id: str) -> Dict[str, Any]:
        new_state = toggle_owned_key(str(key_id), db_path=self._db_path)
        owned = get_owned_key_ids(db_path=self._db_path)
        return {
            "ok": True,
            "key_id": str(key_id),
            "owned": bool(new_state),
            "stats": get_key_stats(owned),
        }
