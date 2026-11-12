"""
TarkovScope - Motor de Cálculo Balístico y Exportador de Armería (Gunsmith Studio)
Calcula ergonomía dinámica, retroceso vertical/horizontal, masa total y requisitos de comerciantes.
Permite exportar en formato JSON de EFT/SPT, lista de compra para el portapapeles y código base64 portable.
Lógica pura de negocio (Clean Architecture, sin dependencias de UI).
"""
import json
import base64
import hashlib
from typing import Dict, Any, List, Optional, Tuple

from core.weapon_modding_data import (
    MODDABLE_WEAPONS,
    ATTACHMENTS_CATALOG,
    MOD_SLOTS
)


def calculate_build_stats(weapon_id: str, slots: Dict[str, str]) -> Dict[str, Any]:
    """
    Calcula los atributos dinámicos completos de un arma según los accesorios montados.
    Aplica las fórmulas de Escape from Tarkov:
      - Ergonomía acumulada con límites [1, 100].
      - Factor de reducción de retroceso multiplicativo/porcentual sobre retroceso base.
      - Masa total en kilogramos.
      - Velocidad de boca según longitud y silenciadores.
      - Requisitos de nivel de lealtad (LL) por cada comerciante.
    """
    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])

    base_ergo = float(weapon.get("base_ergo", 50))
    base_recoil_v = float(weapon.get("base_recoil_v", 150))
    base_recoil_h = float(weapon.get("base_recoil_h", 350))
    base_weight = float(weapon.get("base_weight_kg", 3.0))
    base_velocity = float(weapon.get("base_velocity_ms", 850))

    sum_ergo = 0.0
    sum_recoil_pct = 0.0
    sum_weight = 0.0
    sum_vel_pct = 0.0
    total_cost = 0
    traders_needed: Dict[str, int] = {}
    items_breakdown: List[Dict[str, Any]] = []

    for slot_key, slot_name in MOD_SLOTS:
        part_id = slots.get(slot_key, "none")
        part = ATTACHMENTS_CATALOG.get(part_id, ATTACHMENTS_CATALOG["none"])

        if part_id != "none":
            e_delta = float(part.get("ergo_delta", 0.0))
            r_delta = float(part.get("recoil_pct_delta", 0.0))
            w_delta = float(part.get("weight_delta_kg", 0.0))
            v_delta = float(part.get("velocity_delta_pct", 0.0))
            cost = int(part.get("price_rubles", 0))

            sum_ergo += e_delta
            sum_recoil_pct += r_delta
            sum_weight += w_delta
            sum_vel_pct += v_delta
            total_cost += cost

            t_name = part.get("trader", "—")
            t_ll = int(part.get("loyalty_level", 1))
            if t_name and t_name != "—":
                traders_needed[t_name] = max(traders_needed.get(t_name, 1), t_ll)

            items_breakdown.append({
                "slot_key": slot_key,
                "slot_name": slot_name,
                "part_id": part_id,
                "part_name": part.get("name", part_id),
                "ergo_delta": e_delta,
                "recoil_pct_delta": r_delta,
                "weight_delta_kg": w_delta,
                "velocity_delta_pct": v_delta,
                "trader": t_name,
                "loyalty_level": t_ll,
                "price_rubles": cost
            })

    # Fórmulas de EFT
    final_ergo = max(1, min(100, int(round(base_ergo + sum_ergo))))
    recoil_factor = max(0.20, 1.0 + (sum_recoil_pct / 100.0))
    final_recoil_v = max(15, int(round(base_recoil_v * recoil_factor)))
    final_recoil_h = max(30, int(round(base_recoil_h * recoil_factor)))
    final_weight = max(0.6, round(base_weight + sum_weight, 2))
    final_velocity = max(100, int(round(base_velocity * (1.0 + sum_vel_pct / 100.0))))

    return {
        "weapon_id": weapon["id"],
        "weapon_name": weapon["name"],
        "caliber": weapon["caliber"],
        "category": weapon.get("category", "Arma"),
        "fire_rate": weapon.get("fire_rate", 600),
        "effective_dist_m": weapon.get("effective_dist_m", 500),
        "base_ergo": int(base_ergo),
        "final_ergo": final_ergo,
        "ergo_delta_total": int(round(sum_ergo)),
        "base_recoil_v": int(base_recoil_v),
        "final_recoil_v": final_recoil_v,
        "base_recoil_h": int(base_recoil_h),
        "final_recoil_h": final_recoil_h,
        "recoil_reduction_pct": round(sum_recoil_pct, 1),
        "base_weight_kg": base_weight,
        "final_weight_kg": final_weight,
        "base_velocity_ms": int(base_velocity),
        "final_velocity_ms": final_velocity,
        "total_cost_rubles": total_cost,
        "traders_needed": traders_needed,
        "items_breakdown": items_breakdown,
        "slots_equipped": dict(slots)
    }


def export_build_to_json(weapon_id: str, slots: Dict[str, str], build_name: Optional[str] = None) -> str:
    """
    Exporta la configuración al formato JSON estándar utilizado por mods de SPT-AKI y editores de EFT.
    Incluye estructura compatible con presets de 'weaponbuilds'.
    """
    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])
    stats = calculate_build_stats(weapon_id, slots)
    b_name = build_name or f"{weapon['name']} Custom Build"

    root_id = hashlib.md5(f"{weapon_id}_{b_name}".encode("utf-8")).hexdigest()[:24]

    items = [
        {
            "_id": root_id,
            "_tpl": f"tpl_{weapon_id}"
        }
    ]

    for slot_key, slot_name in MOD_SLOTS:
        part_id = slots.get(slot_key, "none")
        if part_id != "none":
            part_hash = hashlib.md5(f"{root_id}_{slot_key}_{part_id}".encode("utf-8")).hexdigest()[:24]
            items.append({
                "_id": part_hash,
                "_tpl": part_id,
                "parentId": root_id,
                "slotId": f"mod_{slot_key}"
            })

    payload = {
        "format": "TarkovScope_EFT_WeaponBuild",
        "version": "1.0",
        "id": root_id,
        "name": b_name,
        "root": root_id,
        "weapon_id": weapon_id,
        "caliber": weapon["caliber"],
        "stats": {
            "ergonomics": stats["final_ergo"],
            "recoil_vertical": stats["final_recoil_v"],
            "recoil_horizontal": stats["final_recoil_h"],
            "weight_kg": stats["final_weight_kg"],
            "muzzle_velocity": stats["final_velocity_ms"]
        },
        "items": items
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_shopping_list_text(weapon_id: str, slots: Dict[str, str], build_name: Optional[str] = None) -> str:
    """
    Genera una lista de compras táctica formateada en texto limpio y listo para el portapapeles.
    Permite al jugador saber exactamente qué piezas comprar, en qué comerciante y con qué nivel de lealtad (LL).
    """
    weapon = MODDABLE_WEAPONS.get(weapon_id, MODDABLE_WEAPONS["m4a1"])
    stats = calculate_build_stats(weapon_id, slots)
    b_name = build_name or f"{weapon['name']} Build Personalizada"

    lines = [
        "════════════════════════════════════════════════════════════════",
        f"🛠️ TARKOVSCOPE — LISTA DE COMPRAS DE ARMERÍA (GUNSMITH STUDIO)",
        f"Arma Base: {weapon['name']}  |  Calibre: {weapon['caliber']}",
        f"Configuración: {b_name}",
        f"Stats Finales: Ergonomía {stats['final_ergo']} | Retroceso V: {stats['final_recoil_v']} / H: {stats['final_recoil_h']} | Peso: {stats['final_weight_kg']} kg",
        "════════════════════════════════════════════════════════════════",
        "PIEZAS Y ACCESORIOS REQUERIDOS:"
    ]

    for item in stats["items_breakdown"]:
        t_info = f"{item['trader']} LL{item['loyalty_level']}" if item['trader'] != "—" else "Flea Market / Loot"
        cost_str = f"{item['price_rubles']:,} ₽".replace(",", ".")
        lines.append(f"  • [{item['slot_name']}]:  {item['part_name']}")
        lines.append(f"      Comerciante: {t_info}  •  Costo aprox: ~{cost_str}")

    lines.append("────────────────────────────────────────────────────────────────")
    cost_total_str = f"{stats['total_cost_rubles']:,} ₽".replace(",", ".")
    lines.append(f"💰 Costo Total Estimado en Piezas: ~{cost_total_str}")

    traders_str = ", ".join(f"{t} (LL{lvl})" for t, lvl in sorted(stats["traders_needed"].items())) or "Sin requisitos altos"
    lines.append(f"🔑 Comerciantes Requeridos: {traders_str}")
    lines.append("════════════════════════════════════════════════════════════════")

    return "\n".join(lines)


def export_build_to_base64(weapon_id: str, slots: Dict[str, str], build_name: Optional[str] = None) -> str:
    """Exporta el preset en una cadena compacta en base64 para compartir fácilmente."""
    data = {
        "w": weapon_id,
        "n": build_name or "Custom Build",
        "s": slots
    }
    raw_json = json.dumps(data, separators=(",", ":"))
    b64 = base64.b64encode(raw_json.encode("utf-8")).decode("utf-8")
    return f"TTCBUILD:{b64}"


def import_build_from_base64(b64_string: str) -> Optional[Dict[str, Any]]:
    """Decodifica una cadena en base64 generada por TarkovScope."""
    try:
        clean = b64_string.strip()
        if clean.startswith("TTCBUILD:"):
            clean = clean[len("TTCBUILD:"):]
        raw = base64.b64decode(clean).decode("utf-8")
        data = json.loads(raw)
        weapon_id = data.get("w")
        if weapon_id in MODDABLE_WEAPONS:
            return {
                "weapon_id": weapon_id,
                "build_name": data.get("n", "Imported Build"),
                "slots": data.get("s", {})
            }
        return None
    except Exception:
        return None


def import_build_from_json(json_string: str) -> Optional[Dict[str, Any]]:
    """Importa una configuración desde un archivo JSON o portapapeles."""
    try:
        data = json.loads(json_string)
        w_id = data.get("weapon_id")
        if not w_id and "root" in data and "items" in data:
            # Reconstruir desde SPT weaponbuilds format
            for item in data.get("items", []):
                tpl = item.get("_tpl", "")
                if tpl.startswith("tpl_"):
                    cand = tpl[4:]
                    if cand in MODDABLE_WEAPONS:
                        w_id = cand
                        break

        if w_id in MODDABLE_WEAPONS:
            slots: Dict[str, str] = {}
            if "items" in data:
                for it in data["items"]:
                    slot_id = it.get("slotId", "")
                    if slot_id.startswith("mod_"):
                        s_name = slot_id[4:]
                        part_tpl = it.get("_tpl", "")
                        if part_tpl in ATTACHMENTS_CATALOG:
                            slots[s_name] = part_tpl
            return {
                "weapon_id": w_id,
                "build_name": data.get("name", "Build Importada"),
                "slots": slots
            }
        return None
    except Exception:
        return None
