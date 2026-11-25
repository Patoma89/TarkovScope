"""
TarkovScope - API Backend Pura para Interfaz WebView2 GPU (TTC v2.0 Next-Gen)
Expone DataStore, UserData, Reloj Tarkov, Búsqueda Global, Skins y Patch Notes
mediante tipos JSON-serializables puros (sin Tkinter ni pywebview).
"""
import os
import webbrowser
from typing import Any, Callable, Dict, List, Optional

from core.bosses_data import get_all_bosses
from core.config import (
    APP_NAME,
    APP_VERSION,
    BUNDLE_DIR,
    CACHE_DIR,
    DB_PATH,
    READONLY_CACHE_DIR,
    THEME_SKIN_META,
    THEME_SKINS,
    resolve_cache_read_path,
)
from core.datastore import DataStore, get_datastore
from core.i18n import SUPPORTED_LANGS, get_active_lang, set_active_lang
from core.keys_data import KEYS_CATALOG
from core.patch_notes_data import get_patch_notes
from core.pmc_prestige_achievements_data import ACHIEVEMENTS_CATALOG
from core.sync_service import SyncService
from core.tarkov_time import get_tarkov_raid_times
from core.updater import check_github_release, download_installer, launch_installer
from core.user_data import (
    add_preraid_item,
    get_owned_key_ids,
    get_preraid_checklist,
    get_prestige_level,
    get_unlocked_achievement_ids,
    get_user_preference,
    remove_preraid_item,
    reset_preraid_checklist,
    set_user_preference,
    toggle_preraid_item,
)
from core.weapons_data import GUNSMITH_GUIDES_DATA, KAPPA_COLLECTOR_ITEMS
from core.web_api_combat import WebAPICombatMixin
from core.web_api_economy import WebAPIEconomyMixin
from core.web_api_incursion import WebAPIIncursionMixin
from core.web_api_progression import WebAPIProgressionMixin


def resolve_web_asset_path(rel_path: str) -> Optional[str]:
    """Resuelve de forma segura una ruta relativa bajo /cache/ bloqueando path traversal."""
    cleaned = (rel_path or "").replace("\\", "/").lstrip("/")
    if not cleaned or ".." in cleaned.split("/"):
        return None
    parts = [p for p in cleaned.split("/") if p and p != "."]
    if not parts:
        return None

    candidate = resolve_cache_read_path(*parts, min_bytes=1)
    if candidate and os.path.isfile(candidate):
        # Verificar que el archivo real permanezca dentro de alguna raíz de caché permitida
        real_cand = os.path.realpath(candidate)
        allowed_roots = [os.path.realpath(CACHE_DIR)]
        if READONLY_CACHE_DIR:
            allowed_roots.append(os.path.realpath(READONLY_CACHE_DIR))
        allowed_roots.append(os.path.realpath(os.path.join(BUNDLE_DIR, "cache")))
        for root in allowed_roots:
            try:
                if os.path.commonpath([real_cand, root]) == root:
                    return real_cand
            except ValueError:
                continue
    return None


def _trader_avatar_url(trader_name: str) -> str:
    clean = (trader_name or "prapor").strip().lower().replace(" ", "_")
    return f"/cache/avatars/{clean}.png"


class TTCWebAPI(
    WebAPIIncursionMixin,
    WebAPIProgressionMixin,
    WebAPICombatMixin,
    WebAPIEconomyMixin,
):
    """Puente de datos JSON-serializable entre `core/` y la interfaz GPU `web_ui/`."""

    def __init__(
        self,
        datastore: Optional[DataStore] = None,
        db_path: Optional[str] = None,
        on_toggle_topmost: Optional[Callable[[bool], None]] = None,
    ) -> None:
        self._datastore = datastore
        self._db_path = db_path or (datastore.db_path if datastore is not None else DB_PATH)
        self._on_toggle_topmost = on_toggle_topmost
        self._always_on_top = False

    def _ds(self) -> DataStore:
        ds = self._datastore if self._datastore is not None else get_datastore()
        ds.ensure_loaded()
        return ds

    def get_bootstrap(self) -> Dict[str, Any]:
        """Devuelve la configuración inicial completa y los datos del Centro de Mando."""
        skin_id = get_user_preference("ui_skin", "tarkov_classic", db_path=self._db_path)
        if skin_id not in THEME_SKINS:
            skin_id = "tarkov_classic"
        saved_lang = get_user_preference("ui_lang", "", db_path=self._db_path)
        if saved_lang in SUPPORTED_LANGS:
            set_active_lang(saved_lang, db_path=self._db_path)
        lang = get_active_lang()
        collapsed = get_user_preference("sidebar_collapsed", "0", db_path=self._db_path) == "1"
        try:
            pmc_level = max(1, min(79, int(get_user_preference("pmc_level", "1", db_path=self._db_path) or 1)))
        except (TypeError, ValueError):
            pmc_level = 1

        skins_meta = [
            {
                "id": sid,
                "label": THEME_SKIN_META.get(sid, {}).get("label", sid),
                "accent": THEME_SKINS[sid].get("accent_gold", "#D4B886"),
                "bg": THEME_SKINS[sid].get("bg_dark", "#0B0B09"),
            }
            for sid in THEME_SKINS
        ]

        return {
            "app_name": APP_NAME,
            "version": APP_VERSION,
            "skin_id": skin_id,
            "skins": THEME_SKINS,
            "skins_meta": skins_meta,
            "lang": lang,
            "supported_langs": dict(SUPPORTED_LANGS),
            "sidebar_collapsed": collapsed,
            "pmc_level": pmc_level,
            "always_on_top": self._always_on_top,
            "global_hotkey": "Ctrl+Alt+T",
            "command_center": self.get_command_center_data(),
        }

    def get_command_center_data(self) -> Dict[str, Any]:
        """Construye el payload completo del Centro de Mando desde RAM (<1 ms)."""
        ds = self._ds()
        q_done, q_total = ds.get_quest_completion_counts()
        q_pct = int(round((q_done / q_total) * 100)) if q_total else 0

        correlative = ds.get_quests(progression_mode="CORRELATIVE", hide_completed=True)
        unlocked_count = len(correlative)

        next_quests: List[Dict[str, Any]] = []
        for q in correlative[:20]:
            trader = q.get("trader_name", "Prapor")
            next_quests.append({
                "id": int(q.get("id", 0)),
                "title": q.get("title", ""),
                "trader_name": trader,
                "trader_avatar": _trader_avatar_url(trader),
                "primary_map": q.get("primary_map", "Any Location"),
                "level_req": int(q.get("level_req", 1) or 1),
                "exp": int(q.get("exp", 0) or 0),
                "is_kappa": bool(q.get("is_kappa")),
                "is_lightkeeper": bool(q.get("is_lightkeeper")),
            })

        kappa_items: List[Dict[str, Any]] = []
        k_done = 0
        for it in KAPPA_COLLECTOR_ITEMS:
            count = ds.get_stash_count(f"kappa:{it['name']}")
            collected = count >= 1
            if collected:
                k_done += 1
            icon_key = it.get("icon_key", "")
            kappa_items.append({
                "name": it["name"],
                "boss_or_spot": it.get("boss_or_spot", ""),
                "icon_url": f"/cache/gear/{icon_key}.png" if icon_key else "",
                "count": count,
                "collected": collected,
            })
        k_total = len(KAPPA_COLLECTOR_ITEMS)
        k_pct = int(round((k_done / k_total) * 100)) if k_total else 0

        all_hideout = ds.get_hideout_modules(progression_mode="ALL")
        h_total = len(all_hideout)
        h_done = sum(1 for m in all_hideout if m.get("is_completed"))
        h_pct = int(round((h_done / h_total) * 100)) if h_total else 0
        h_ready_mods = ds.get_hideout_modules(progression_mode="CORRELATIVE", hide_completed=True)
        h_ready = len(h_ready_mods)
        hideout_ready_list = [
            {
                "id": int(m.get("id", 0)),
                "station": m.get("station_name") or m.get("station", ""),
                "level": int(m.get("level", 1) or 1),
                "reqs_count": len(m.get("requirements_list") or []),
            }
            for m in h_ready_mods[:6]
        ]

        a_total = len(ACHIEVEMENTS_CATALOG)
        a_done = len(get_unlocked_achievement_ids(db_path=self._db_path))
        a_pct = int(round((a_done / a_total) * 100)) if a_total else 0
        prestige_lvl = get_prestige_level(db_path=self._db_path)

        # Radar de Bosses (top 6 icónicos con tasas PvE/PvP)
        bosses_radar = [
            {
                "id": b["id"],
                "name": b["name"].split(" (")[0],
                "avatar_url": f"/cache/avatars/{b['id']}.png",
                "maps": ", ".join((b.get("maps") or [])[:2]),
                "pve_chance": b.get("pve_chance", ""),
                "pvp_chance": b.get("pvp_chance", ""),
            }
            for b in get_all_bosses()[:6]
        ]

        # Llaves de Quest faltantes
        owned_keys = get_owned_key_ids(db_path=self._db_path)
        quest_keys = [k for k in KEYS_CATALOG if k.get("quests")]
        missing_q_keys = [k for k in quest_keys if k["id"] not in owned_keys]
        missing_quest_keys = {
            "owned": len(owned_keys),
            "total": len(KEYS_CATALOG),
            "missing_quest_count": len(missing_q_keys),
            "items": [
                {
                    "id": k["id"],
                    "name": k["name"],
                    "map": k.get("map", ""),
                    "quest": (k.get("quests") or [""])[0],
                }
                for k in missing_q_keys[:6]
            ],
        }

        # Progreso Historia (10 Capítulos) & Gunsmith (25 Partes)
        story_chapters = ds.get_wiki_story_chapters()
        story_done_ids = ds.get_completed_story_ids()
        st_total = sum(len(ch.get("objectives") or []) for ch in story_chapters)
        st_done = sum(
            1
            for ch in story_chapters
            for obj in (ch.get("objectives") or [])
            if obj.get("id") in story_done_ids
        )
        st_pct = int(round((st_done / st_total) * 100)) if st_total else 0
        next_ch = next(
            (
                f"Cap. {ch.get('chapter_number', 1)}: {ch.get('title', '')}"
                for ch in story_chapters
                if any(o.get("id") not in story_done_ids for o in (ch.get("objectives") or []))
            ),
            "¡Historia Completa!",
        )

        gs_total = len(GUNSMITH_GUIDES_DATA)
        gs_done = sum(1 for g in GUNSMITH_GUIDES_DATA if ds.get_stash_count(f"gunsmith:{g['part']}") >= 1)
        gs_pct = int(round((gs_done / gs_total) * 100)) if gs_total else 0
        next_gs = next(
            (
                f"Parte {g['part']}: {g.get('weapon', '')}"
                for g in GUNSMITH_GUIDES_DATA
                if ds.get_stash_count(f"gunsmith:{g['part']}") < 1
            ),
            "¡Gunsmith 25/25 Completo!",
        )

        return {
            "kpis": {
                "quests": {
                    "done": q_done,
                    "total": q_total,
                    "pct": q_pct,
                    "unlocked": unlocked_count,
                },
                "kappa": {
                    "done": k_done,
                    "total": k_total,
                    "pct": k_pct,
                    "missing": max(0, k_total - k_done),
                },
                "hideout": {
                    "done": h_done,
                    "total": h_total,
                    "pct": h_pct,
                    "ready": h_ready,
                },
                "achievements": {
                    "done": a_done,
                    "total": a_total,
                    "pct": a_pct,
                    "prestige": prestige_lvl,
                },
            },
            "next_quests": next_quests,
            "kappa_items": kappa_items,
            "bosses_radar": bosses_radar,
            "hideout_ready_list": hideout_ready_list,
            "missing_quest_keys": missing_quest_keys,
            "campaign_progress": {
                "story": {"done": st_done, "total": st_total, "pct": st_pct, "next": next_ch},
                "gunsmith": {"done": gs_done, "total": gs_total, "pct": gs_pct, "next": next_gs},
            },
            "raid_clock": get_tarkov_raid_times(),
            "preraid_checklist": get_preraid_checklist(db_path=self._db_path),
        }

    def toggle_quest(self, quest_id: int) -> Dict[str, Any]:
        """Marca o desmarca una misión y retorna el estado actualizado del Centro de Mando."""
        ds = self._ds()
        new_state = ds.toggle_quest(int(quest_id))
        return {
            "ok": True,
            "quest_id": int(quest_id),
            "is_completed": bool(new_state),
            "command_center": self.get_command_center_data(),
        }

    def toggle_kappa_item(self, item_name: str) -> Dict[str, Any]:
        """Alterna un ítem Collector (Kappa) en el alijo (0 <-> 1) y actualiza métricas."""
        ds = self._ds()
        key = f"kappa:{str(item_name).strip()}"
        current = ds.get_stash_count(key)
        new_count = 0 if current >= 1 else 1
        ds.set_stash_count(key, new_count)
        return {
            "ok": True,
            "item_name": item_name,
            "count": new_count,
            "collected": new_count >= 1,
            "command_center": self.get_command_center_data(),
        }

    def set_skin(self, skin_id: str) -> Dict[str, Any]:
        """Persiste la skin seleccionada en SQLite y devuelve su paleta."""
        if skin_id not in THEME_SKINS:
            return {"ok": False, "error": f"Unknown skin: {skin_id}"}
        set_user_preference("ui_skin", skin_id, db_path=self._db_path)
        return {
            "ok": True,
            "skin_id": skin_id,
            "palette": THEME_SKINS[skin_id],
        }

    def set_lang(self, lang: str) -> Dict[str, Any]:
        """Cambia el idioma activo (es/en)."""
        clean = (lang or "es").strip().lower()
        if clean not in SUPPORTED_LANGS:
            return {"ok": False, "error": f"Unsupported lang: {lang}"}
        set_active_lang(clean, db_path=self._db_path)
        return {"ok": True, "lang": clean}

    def set_pmc_level(self, level: int) -> Dict[str, Any]:
        """Persiste el nivel actual del PMC (1-79) en SQLite."""
        try:
            clean = max(1, min(79, int(level)))
        except (TypeError, ValueError):
            clean = 1
        set_user_preference("pmc_level", str(clean), db_path=self._db_path)
        return {"ok": True, "pmc_level": clean}

    def check_github_update(self) -> Dict[str, Any]:
        """Verifica si existe una versión más nueva publicada en GitHub Releases."""
        return check_github_release()

    def download_and_launch_update(self, installer_url: str, installer_name: str = "TTC_Setup.exe") -> Dict[str, Any]:
        """Descarga el instalador desde GitHub Releases y lo ejecuta con entorno limpio."""
        url = str(installer_url or "").strip()
        if not url.startswith("https://"):
            return {"ok": False, "error": "URL de instalador inválida."}
        try:
            exe_path = download_installer(url, filename=str(installer_name or "TTC_Setup.exe"))
            launch_installer(exe_path)
            return {"ok": True, "path": exe_path}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def open_external_url(self, url: str) -> Dict[str, Any]:
        """Abre un enlace seguro (https:// o http://) en el navegador predeterminado del sistema."""
        clean = str(url or "").strip()
        if not clean.startswith(("https://", "http://")):
            return {"ok": False, "error": "URL no permitida."}
        try:
            webbrowser.open(clean)
            return {"ok": True, "url": clean}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def set_sidebar_collapsed(self, collapsed: bool) -> Dict[str, Any]:
        """Persiste el estado colapsado de la barra lateral."""
        val = "1" if collapsed else "0"
        set_user_preference("sidebar_collapsed", val, db_path=self._db_path)
        return {"ok": True, "collapsed": bool(collapsed)}

    def toggle_always_on_top(self) -> Dict[str, Any]:
        """Alterna el estado Always-on-Top en la ventana contenedora."""
        self._always_on_top = not self._always_on_top
        if callable(self._on_toggle_topmost):
            try:
                self._on_toggle_topmost(self._always_on_top)
            except Exception:
                pass
        return {"ok": True, "always_on_top": self._always_on_top}

    def global_search(self, query: str) -> List[Dict[str, Any]]:
        """Ejecuta la búsqueda global táctica (Ctrl+K) sobre todo el DataStore."""
        ds = self._ds()
        return ds.global_search(str(query or ""))[:30]

    def get_raid_clock(self) -> Dict[str, Any]:
        """Retorna el horario dual oficial In-Raid de Tarkov (ciclo 7x)."""
        return get_tarkov_raid_times()

    def get_patch_notes(self, lang: str = "") -> List[Dict[str, Any]]:
        """Devuelve el historial de notas de versión en el idioma solicitado."""
        use_lang = (lang or get_active_lang() or "es").strip().lower()
        return get_patch_notes(use_lang)

    def sync_data(self) -> Dict[str, Any]:
        """Sincroniza la base de datos y refresca el DataStore en RAM."""
        service = SyncService()
        ok = service.sync_all()
        if ok:
            self._ds().refresh()
        return {
            "ok": bool(ok),
            "command_center": self.get_command_center_data(),
        }

    def toggle_preraid_item(self, item_id: str) -> Dict[str, Any]:
        """Alterna un ítem del checklist Pre-Raid y devuelve la lista actualizada."""
        items = toggle_preraid_item(str(item_id or ""), db_path=self._db_path)
        return {"ok": True, "preraid_checklist": items}

    def add_preraid_item(self, label: str) -> Dict[str, Any]:
        """Agrega un ítem personalizado al checklist Pre-Raid."""
        clean = str(label or "").strip()
        if not clean:
            return {"ok": False, "error": "Etiqueta vacía"}
        items = add_preraid_item(clean, db_path=self._db_path)
        return {"ok": True, "preraid_checklist": items}

    def remove_preraid_item(self, item_id: str) -> Dict[str, Any]:
        """Elimina un ítem personalizado del checklist Pre-Raid."""
        items = remove_preraid_item(str(item_id or ""), db_path=self._db_path)
        return {"ok": True, "preraid_checklist": items}

    def reset_preraid_checklist(self) -> Dict[str, Any]:
        """Reinicia (desmarca) todos los ítems del checklist Pre-Raid."""
        items = reset_preraid_checklist(db_path=self._db_path)
        return {"ok": True, "preraid_checklist": items}
