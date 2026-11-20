"""
TarkovScope - Mixin API WebView2: Economía, Refugio, Contenedores, Medicina & PMC
Expone Hideout Correlativo (68 niveles), Ítems FiR, Crafteos, Barters, Cultist Circle,
Contenedores/Rigs, Medicina/45 Provisiones/14 Efectos de Salud, PMC Systems (35 Skills,
Scav Karma, BTR/Transits, Prestige 1-6, 32 Logros, 24 Prendas), Lore y Perfil JSON.
Módulo de lógica pura (sin Tkinter ni pywebview).
"""
from typing import Any, Dict, List

from core.barters_data import (
    BARTERS_CATALOG,
    CULTIST_CIRCLE_INFO,
    CULTIST_REPEATABLE_SACRIFICES,
    CULTIST_UNIQUE_SACRIFICES,
)
from core.containers_data import SICC_VS_DOCS_COMPARISON, get_all_storage_items
from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA, HIDEOUT_STATION_ICONS
from core.lore_data import LORE_UNIVERSE_SECTIONS
from core.medical_data import MEDICAL_CATALOG, MEDICAL_CATEGORIES, SYMPTOM_FILTERS
from core.pmc_prestige_achievements_data import (
    ACHIEVEMENTS_CATALOG,
    ARENA_REF_SYNC_GUIDE,
    PRESTIGE_LEVELS_DATA,
    PRESTIGE_RESET_MATRIX,
    TACTICAL_CLOTHING_CATALOG,
)
from core.pmc_systems_data import (
    BTR_SERVICE_DATA,
    PMC_SKILLS_CATALOG,
    SCAV_KARMA_ACTIONS,
    SCAV_KARMA_BRACKETS,
    SKILL_LEVELING_MECHANICS,
    TRANSITS_CATALOG,
)
from core.provisions_health_data import HEALTH_EFFECTS_CATALOG, PROVISIONS_CATALOG
from core.season_pass_docs_data import (
    SEASON_PASS_DOC_TYPES,
    SEASON_PASS_MAP_SUMMARY,
    SEASON_PASS_META,
)
from core.user_data import (
    get_prestige_level,
    get_unlocked_achievement_ids,
    get_user_preference,
    set_prestige_level,
    set_user_preference,
    toggle_achievement_unlocked,
)


class WebAPIEconomyMixin:
    """Endpoints de Hideout, FiR, Barters, Contenedores, Medicina, PMC y Lore."""

    # --- HIDEOUT, FIR, CRAFTEOS, BARTERS & CULTIST ---

    def get_hideout_and_flea_data(self) -> Dict[str, Any]:
        ds = self._ds()
        modules = []
        for mod in ds.get_hideout_modules(progression_mode="ALL"):
            m = dict(mod)
            m["is_unlocked"] = ds.is_hideout_module_unlocked(mod)
            st_info = HIDEOUT_STATION_ICONS.get(mod.get("station", ""), {})
            ik = st_info.get("icon_key", "")
            m["icon_url"] = f"/cache/gear/{ik}.png" if ik else ""
            modules.append(m)

        fir_agg: Dict[str, Dict[str, Any]] = {}
        for row in ds._fir_items:
            name = row.get("item_name", "")
            if not name:
                continue
            entry = fir_agg.setdefault(name, {
                "item_name": name,
                "total_required": 0,
                "collected": ds.get_stash_count(name),
                "quests": [],
            })
            qty = int(row.get("count_required", 1) or 1)
            entry["total_required"] += qty
            entry["quests"].append(f"{qty}x {row.get('quest_title', '')} ({row.get('trader_name', '')})")

        crafts = []
        for c in HIDEOUT_CRAFTS_DATA:
            cc = dict(c)
            ik = c.get("icon_key", "")
            cc["icon_url"] = f"/cache/gear/{ik}.png" if ik else ""
            crafts.append(cc)

        barters = []
        for b in BARTERS_CATALOG:
            bc = dict(b)
            ck = b.get("cache_key", "")
            bc["icon_url"] = f"/cache/gear/{ck}.png" if ck else ""
            barters.append(bc)

        return {
            "hideout": modules,
            "fir_items": sorted(fir_agg.values(), key=lambda x: x["item_name"].lower()),
            "crafts": crafts,
            "barters": barters,
            "cultist": {
                "info": CULTIST_CIRCLE_INFO,
                "unique": CULTIST_UNIQUE_SACRIFICES,
                "repeatable": CULTIST_REPEATABLE_SACRIFICES,
            },
        }

    def toggle_hideout_module(self, module_key: str) -> Dict[str, Any]:
        ds = self._ds()
        new_state = ds.toggle_hideout_module(str(module_key))
        return {
            "ok": True,
            "module_key": str(module_key),
            "is_completed": bool(new_state),
            "command_center": self.get_command_center_data(),
        }

    def set_fir_stash_count(self, item_name: str, count: int) -> Dict[str, Any]:
        ds = self._ds()
        val = ds.set_stash_count(str(item_name), int(count))
        return {"ok": True, "item_name": str(item_name), "count": val}

    # --- CONTENEDORES, RIGS & MOCHILAS ---

    def get_containers_data(self) -> Dict[str, Any]:
        items = []
        for it in get_all_storage_items():
            copy = dict(it)
            ck = it.get("cache_key", "")
            copy["icon_url"] = f"/cache/gear/{ck}.png" if ck else ""
            items.append(copy)
        return {
            "items": items,
            "sicc_vs_docs": SICC_VS_DOCS_COMPARISON,
        }

    # --- MEDICINA, PROVISIONES & EFECTOS DE SALUD ---

    def get_medical_and_provisions_data(self) -> Dict[str, Any]:
        meds = []
        for m in MEDICAL_CATALOG:
            copy = dict(m)
            copy["icon_url"] = f"/cache/medical/{m['id']}.png"
            meds.append(copy)

        provs = []
        for p in PROVISIONS_CATALOG:
            copy = dict(p)
            ik = p.get("icon_key", p["id"])
            copy["icon_url"] = f"/cache/gear/{ik}.png"
            provs.append(copy)

        return {
            "categories": MEDICAL_CATEGORIES,
            "symptoms": SYMPTOM_FILTERS,
            "medical": meds,
            "provisions": provs,
            "health_effects": HEALTH_EFFECTS_CATALOG,
        }

    # --- PMC SYSTEMS (SKILLS, KARMA, BTR, PRESTIGE, LOGROS, ROPA) & LORE ---

    def get_pmc_systems_data(self) -> Dict[str, Any]:
        unlocked = get_unlocked_achievement_ids(db_path=self._db_path)
        prestige_lvl = get_prestige_level(db_path=self._db_path)

        skills = []
        for sk in PMC_SKILLS_CATALOG:
            s = dict(sk)
            ck = sk.get("cache_key", "")
            s["icon_url"] = f"/cache/gear/{ck}.png" if ck else ""
            skills.append(s)

        prestige = []
        for pr in PRESTIGE_LEVELS_DATA:
            p = dict(pr)
            ik = pr.get("icon_key", "")
            p["icon_url"] = f"/cache/gear/{ik}.png" if ik else ""
            prestige.append(p)

        achievements = []
        for a in ACHIEVEMENTS_CATALOG:
            ac = dict(a)
            ac["unlocked"] = a["id"] in unlocked
            achievements.append(ac)

        clothing = []
        for c in TACTICAL_CLOTHING_CATALOG:
            cc = dict(c)
            ik = c.get("icon_key", c["id"])
            cc["icon_url"] = f"/cache/gear/{ik}.png"
            clothing.append(cc)

        return {
            "skills": skills,
            "skill_mechanics": SKILL_LEVELING_MECHANICS,
            "scav_karma_brackets": SCAV_KARMA_BRACKETS,
            "scav_karma_actions": SCAV_KARMA_ACTIONS,
            "btr_service": BTR_SERVICE_DATA,
            "transits": TRANSITS_CATALOG,
            "prestige_level": prestige_lvl,
            "prestige_levels": prestige,
            "prestige_reset_matrix": PRESTIGE_RESET_MATRIX,
            "arena_ref_guide": ARENA_REF_SYNC_GUIDE,
            "achievements": achievements,
            "clothing": clothing,
            "lore": LORE_UNIVERSE_SECTIONS,
        }

    def toggle_achievement(self, ach_id: str) -> Dict[str, Any]:
        new_state = toggle_achievement_unlocked(str(ach_id), db_path=self._db_path)
        return {
            "ok": True,
            "ach_id": str(ach_id),
            "unlocked": bool(new_state),
            "command_center": self.get_command_center_data(),
        }

    def set_prestige_lvl(self, level: int) -> Dict[str, Any]:
        clamped = set_prestige_level(int(level), db_path=self._db_path)
        return {
            "ok": True,
            "prestige_level": clamped,
            "command_center": self.get_command_center_data(),
        }

    # --- DOCS DEL PASE DE TEMPORADA (SEASON 1: KORD BREACH) ---

    def get_season_pass_docs_data(self) -> Dict[str, Any]:
        ds = self._ds()
        mode = get_user_preference("bp_docs_mode", "pvp", db_path=self._db_path) or "pvp"
        if mode not in SEASON_PASS_META["daily_limits"]:
            mode = "pvp"
        daily_found = ds.get_stash_count("bpdoc_daily_today")
        docs = []
        total_collected = 0
        for doc in SEASON_PASS_DOC_TYPES:
            d = dict(doc)
            cnt = ds.get_stash_count(f"bpdoc:{doc['id']}")
            d["collected"] = cnt
            total_collected += cnt
            docs.append(d)
        return {
            "meta": SEASON_PASS_META,
            "mode": mode,
            "daily_found": daily_found,
            "total_collected": total_collected,
            "docs": docs,
            "map_guides": SEASON_PASS_MAP_SUMMARY,
        }

    def set_season_pass_doc_count(self, doc_id: str, count: int) -> Dict[str, Any]:
        ds = self._ds()
        safe_count = max(0, min(999, int(count)))
        ds.set_stash_count(f"bpdoc:{str(doc_id).strip()}", safe_count)
        return {"ok": True, "doc_id": str(doc_id), "count": safe_count}

    def set_season_pass_daily_count(self, count: int) -> Dict[str, Any]:
        ds = self._ds()
        safe_count = max(0, min(99, int(count)))
        ds.set_stash_count("bpdoc_daily_today", safe_count)
        return {"ok": True, "daily_found": safe_count}

    def set_season_pass_mode(self, mode: str) -> Dict[str, Any]:
        clean = str(mode or "pvp").strip().lower()
        if clean not in SEASON_PASS_META["daily_limits"]:
            clean = "pvp"
        set_user_preference("bp_docs_mode", clean, db_path=self._db_path)
        return {"ok": True, "mode": clean}

    # --- EXPORTAR / IMPORTAR PERFIL JSON ---

    def export_profile_json(self) -> Dict[str, Any]:
        return {"ok": True, "profile": self._ds().export_profile()}

    def import_profile_json(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        ok = self._ds().import_profile(profile_data)
        return {
            "ok": bool(ok),
            "command_center": self.get_command_center_data() if ok else None,
        }
