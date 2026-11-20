"""
TarkovScope - Mixin API WebView2: Combate
Expone Arsenal & Meta Builds, Guías Gunsmith (1-25), Modding Studio Pro (Workbench),
Fallas & Reparación, Balística (203 balas), Duelo STK y Blindajes/Placas/Cascos.
Módulo de lógica pura (sin Tkinter ni pywebview).
"""
import os
from typing import Any, Dict, List

from core.armor_data import get_all_protection_items
from core.ballistics import (
    build_eft_ammo_matrix,
    calculate_leg_meta_shots,
    format_caliber_name,
    simulate_boss_targets,
    simulate_shots_to_kill,
)
from core.config import CACHE_DIR, READONLY_CACHE_DIR
from core.weapon_malfunctions_data import (
    DURABILITY_AND_REPAIR_GUIDE,
    WEAPON_MALFUNCTIONS_CATALOG,
)
from core.weapon_modding_data import (
    ATTACHMENTS_CATALOG,
    MOD_SLOTS,
    MODDABLE_WEAPONS,
    get_attachment_image_key,
    get_available_attachments_for_slot,
)
from core.weapon_modding_engine import (
    auto_optimize_build,
    calculate_build_stats,
    export_build_to_base64,
    export_shopping_list_text,
    import_build_from_base64,
)
from core.weapons_data import GUNSMITH_GUIDES_DATA, WEAPONS_ARSENAL_DATA


class WebAPICombatMixin:
    """Endpoints de Armería, Gunsmith, Modding Studio, Averías, Balística y Blindaje."""

    # --- ARSENAL, GUNSMITH & AVERÍAS ---

    def get_weapons_arsenal(self) -> Dict[str, Any]:
        ds = self._ds()
        arsenal = []
        for wp in WEAPONS_ARSENAL_DATA:
            item = dict(wp)
            item["image_url"] = f"/cache/weapons/{wp['id'].lower()}.png"
            arsenal.append(item)

        gunsmith = []
        for gs in GUNSMITH_GUIDES_DATA:
            g = dict(gs)
            g["is_done"] = ds.get_stash_count(f"gunsmith:{gs['part']}") >= 1
            img_key = gs.get("image_key", f"gs_{gs['part']}")
            g["image_url"] = f"/cache/weapons/{img_key.lower()}.png"
            gunsmith.append(g)

        return {
            "arsenal": arsenal,
            "gunsmith": gunsmith,
            "malfunctions": WEAPON_MALFUNCTIONS_CATALOG,
            "durability_guide": DURABILITY_AND_REPAIR_GUIDE,
        }

    def toggle_gunsmith_done(self, part: int) -> Dict[str, Any]:
        ds = self._ds()
        key = f"gunsmith:{int(part)}"
        new_val = 0 if ds.get_stash_count(key) >= 1 else 1
        ds.set_stash_count(key, new_val)
        return {"ok": True, "part": int(part), "is_done": new_val >= 1}

    # --- MODDING STUDIO PRO (WORKBENCH) ---

    @staticmethod
    def _resolve_weapon_image_url(weapon_id: str) -> str:
        wl = str(weapon_id or "").lower()
        candidates = [f"factory_{wl}.png", f"{wl}.png"]
        for fname in candidates:
            if os.path.isfile(os.path.join(CACHE_DIR, "weapons", fname)) or os.path.isfile(
                os.path.join(READONLY_CACHE_DIR, "weapons", fname)
            ):
                return f"/cache/weapons/{fname}"
        return f"/cache/weapons/factory_{wl}.png"

    def get_modding_catalog(self) -> Dict[str, Any]:
        weapons = []
        for w_id, w_data in MODDABLE_WEAPONS.items():
            w = dict(w_data)
            w["id"] = w_id
            w["image_url"] = self._resolve_weapon_image_url(w_id)
            weapons.append(w)
        slots = [{"key": k, "label": lbl} for k, lbl in MOD_SLOTS]
        return {
            "weapons": weapons,
            "slots": slots,
        }

    def get_weapon_slot_options(self, weapon_id: str, slot_key: str) -> List[Dict[str, Any]]:
        atts = get_available_attachments_for_slot(slot_key, weapon_id)
        out = []
        for a in atts:
            copy = dict(a)
            img_k = get_attachment_image_key(a.get("id", ""))
            copy["image_url"] = f"/cache/weapons/{img_k.lower()}.png" if img_k else ""
            out.append(copy)
        return out

    def calculate_weapon_build(self, weapon_id: str, slots: Dict[str, str]) -> Dict[str, Any]:
        stats = calculate_build_stats(weapon_id, slots or {})
        code = export_build_to_base64(weapon_id, slots or {})
        shopping = export_shopping_list_text(weapon_id, slots or {})
        return {
            "ok": True,
            "stats": stats,
            "base64_code": code,
            "shopping_list": shopping,
        }

    def auto_optimize_weapon(self, weapon_id: str, goal: str = "meta_recoil", max_ll: int = 4) -> Dict[str, Any]:
        slots = auto_optimize_build(weapon_id, goal=goal, max_ll=int(max_ll))
        calc = self.calculate_weapon_build(weapon_id, slots)
        calc["slots"] = slots
        return calc

    def import_weapon_build(self, code: str) -> Dict[str, Any]:
        parsed = import_build_from_base64(str(code or "").strip())
        if not parsed:
            return {"ok": False, "error": "Código TTCBUILD inválido."}
        weapon_id, slots = parsed
        calc = self.calculate_weapon_build(weapon_id, slots)
        calc["weapon_id"] = weapon_id
        calc["slots"] = slots
        return calc

    # --- BALÍSTICA (203 BALAS), DUELO STK & BLINDAJES ---

    def get_ballistics_data(self) -> Dict[str, Any]:
        ds = self._ds()
        raw_calibers = ds.get_calibers()
        calibers = [{"id": c, "label": format_caliber_name(c)} for c in raw_calibers]
        ammo_rows = []
        for a in ds.get_ammo():
            pen = float(a.get("penetration_power", 0) or 0)
            matrix = build_eft_ammo_matrix(pen)
            row = dict(a)
            row["caliber_label"] = format_caliber_name(a.get("caliber", ""))
            row["tiers"] = {str(k): v for k, v in matrix.items()}
            ammo_rows.append(row)
        return {
            "calibers": calibers,
            "ammunition": ammo_rows,
        }

    def simulate_ballistics_duel(
        self,
        damage: int,
        penetration: float,
        armor_damage: int,
        armor_class: int = 4,
        durability: float = 50.0,
        rpm: int = 700,
    ) -> Dict[str, Any]:
        stk = simulate_shots_to_kill(
            damage=int(damage),
            penetration_power=float(penetration),
            armor_damage=int(armor_damage),
            armor_class=int(armor_class),
            max_durability=float(durability),
            rpm=int(rpm),
        )
        leg = calculate_leg_meta_shots(int(damage))
        bosses = simulate_boss_targets(
            damage=int(damage),
            penetration_power=float(penetration),
            armor_damage=int(armor_damage),
        )
        return {
            "ok": True,
            "stk": stk,
            "leg_meta": leg,
            "bosses": bosses,
        }

    def get_armor_catalog(self) -> List[Dict[str, Any]]:
        out = []
        for it in get_all_protection_items():
            copy = dict(it)
            ck = it.get("cache_key", "")
            copy["icon_url"] = f"/cache/gear/{ck}.png" if ck else ""
            out.append(copy)
        return out
