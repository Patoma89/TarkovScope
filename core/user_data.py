"""TarkovScope - Datos del usuario: progreso de misiones/hideout, marcadores de mapa, alijo y perfil.
Extraido de database.py (responsabilidad unica). database.py re-exporta estas funciones.
"""
import json
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Set, Tuple
from core.config import DB_PATH
from core.maps_data import normalize_map_key
from core.db_connection import get_db_connection

_PREF_CACHE: Dict[Tuple[str, str], str] = {}
_PREF_LOCK = threading.Lock()


def _invalidate_pref_cache(db_path: str) -> None:
    norm = os.path.abspath(db_path)
    with _PREF_LOCK:
        for k in [key for key in _PREF_CACHE if key[0] == norm]:
            _PREF_CACHE.pop(k, None)


def get_user_preference(key: str, default: str = "", db_path: str = DB_PATH) -> str:
    """Lee una preferencia de usuario desde la tabla metadata (con caché O(1) en RAM)."""
    cache_key = (os.path.abspath(db_path), key)
    with _PREF_LOCK:
        if cache_key in _PREF_CACHE:
            return _PREF_CACHE[cache_key]
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?;", (key,))
            row = cursor.fetchone()
            if row and row[0] is not None:
                val = str(row[0])
                with _PREF_LOCK:
                    _PREF_CACHE[cache_key] = val
                return val
            return default
    except Exception:
        return default


def set_user_preference(key: str, value: str, db_path: str = DB_PATH) -> None:
    """Guarda una preferencia de usuario en la tabla metadata y actualiza la caché RAM."""
    str_val = str(value)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP;
            """,
            (key, str_val),
        )
        conn.commit()
    cache_key = (os.path.abspath(db_path), key)
    with _PREF_LOCK:
        _PREF_CACHE[cache_key] = str_val


def toggle_quest_progress(quest_id: int, db_path: str = DB_PATH) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_completed FROM user_quest_progress WHERE quest_id = ?;", (quest_id,))
        row = cursor.fetchone()
        if row is None:
            new_state = 1
            cursor.execute("INSERT INTO user_quest_progress (quest_id, is_completed) VALUES (?, 1);", (quest_id,))
        else:
            new_state = 0 if row["is_completed"] == 1 else 1
            cursor.execute("UPDATE user_quest_progress SET is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE quest_id = ?;", (new_state, quest_id))
        conn.commit()
        return bool(new_state)


def get_owned_key_ids(db_path: str = DB_PATH) -> Set[str]:
    """Devuelve el conjunto de IDs de llaves marcadas como poseídas por el usuario."""
    raw = get_user_preference("owned_keys", "[]", db_path=db_path)
    try:
        data = json.loads(raw) if raw else []
        return {str(k) for k in data} if isinstance(data, list) else set()
    except (TypeError, ValueError):
        return set()


def toggle_owned_key(key_id: str, db_path: str = DB_PATH) -> bool:
    """Alterna el estado de posesión de una llave y retorna el nuevo estado booleano."""
    owned = get_owned_key_ids(db_path=db_path)
    kid = str(key_id)
    if kid in owned:
        owned.remove(kid)
        new_state = False
    else:
        owned.add(kid)
        new_state = True
    set_user_preference("owned_keys", json.dumps(sorted(owned)), db_path=db_path)
    return new_state


def get_unlocked_achievement_ids(db_path: str = DB_PATH) -> Set[str]:
    """Devuelve el conjunto de IDs de Achievements desbloqueados por el usuario."""
    raw = get_user_preference("unlocked_achievements", "[]", db_path=db_path)
    try:
        data = json.loads(raw) if raw else []
        return {str(a) for a in data} if isinstance(data, list) else set()
    except (TypeError, ValueError):
        return set()


def toggle_achievement_unlocked(ach_id: str, db_path: str = DB_PATH) -> bool:
    """Alterna el estado desbloqueado de un Achievement y retorna el nuevo booleano."""
    unlocked = get_unlocked_achievement_ids(db_path=db_path)
    aid = str(ach_id)
    if aid in unlocked:
        unlocked.remove(aid)
        new_state = False
    else:
        unlocked.add(aid)
        new_state = True
    set_user_preference("unlocked_achievements", json.dumps(sorted(unlocked)), db_path=db_path)
    return new_state


def get_prestige_level(db_path: str = DB_PATH) -> int:
    """Lee el nivel actual de Prestige del PMC (0 a 6)."""
    raw = get_user_preference("pmc_prestige_level", "0", db_path=db_path)
    try:
        return max(0, min(6, int(raw)))
    except (TypeError, ValueError):
        return 0


def set_prestige_level(level: int, db_path: str = DB_PATH) -> int:
    """Guarda el nivel de Prestige del PMC acotado entre 0 y 6."""
    clamped = max(0, min(6, int(level)))
    set_user_preference("pmc_prestige_level", str(clamped), db_path=db_path)
    return clamped


def get_completed_story_quest_ids(db_path: str = DB_PATH) -> Set[str]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quest_id FROM user_story_quest_progress WHERE is_completed = 1;")
        return {str(row[0]) for row in cursor.fetchall()}


def toggle_story_quest_progress(quest_id: str, db_path: str = DB_PATH) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_completed FROM user_story_quest_progress WHERE quest_id = ?;", (str(quest_id),))
        row = cursor.fetchone()
        if row is None:
            new_state = 1
            cursor.execute("INSERT INTO user_story_quest_progress (quest_id, is_completed) VALUES (?, 1);", (str(quest_id),))
        else:
            new_state = 0 if row["is_completed"] == 1 else 1
            cursor.execute("UPDATE user_story_quest_progress SET is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE quest_id = ?;", (new_state, str(quest_id)))
        conn.commit()
        return bool(new_state)


def get_completed_hideout_keys(db_path: str = DB_PATH) -> Set[str]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT module_key FROM user_hideout_progress WHERE is_completed = 1;")
        return {row[0] for row in cursor.fetchall()}


def toggle_hideout_progress(module_key: str, db_path: str = DB_PATH) -> bool:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT is_completed FROM user_hideout_progress WHERE module_key = ?;", (module_key,))
        row = cursor.fetchone()
        if row is None:
            new_state = 1
            cursor.execute("INSERT INTO user_hideout_progress (module_key, is_completed) VALUES (?, 1);", (module_key,))
        else:
            new_state = 0 if row["is_completed"] == 1 else 1
            cursor.execute(
                "UPDATE user_hideout_progress SET is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE module_key = ?;",
                (new_state, module_key),
            )
        conn.commit()
        return bool(new_state)


def reset_all_hideout_progress(db_path: str = DB_PATH) -> None:
    """Desmarca todas las zonas del Hideout construidas por el usuario."""
    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM user_hideout_progress;")
        conn.commit()


# --- Marcadores y Notas Personalizadas del Usuario en Mapas ---

def get_map_markers(map_key: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    norm = normalize_map_key(map_key)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, map_key, x_pct, y_pct, title, category, color, created_at
            FROM user_map_markers
            WHERE map_key = ?
            ORDER BY id ASC;
        """, (norm,))
        return [dict(r) for r in cursor.fetchall()]


def add_map_marker(
    map_key: str,
    x_pct: float,
    y_pct: float,
    title: str,
    category: str = "Nota Personal",
    color: str = "#E5732F",
    db_path: str = DB_PATH
) -> int:
    norm = normalize_map_key(map_key)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_map_markers (map_key, x_pct, y_pct, title, category, color)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (norm, float(x_pct), float(y_pct), title.strip(), category, color))
        conn.commit()
        return int(cursor.lastrowid or 0)


def delete_map_marker(marker_id: int, db_path: str = DB_PATH) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM user_map_markers WHERE id = ?;", (marker_id,))
        conn.commit()


def update_map_marker_pos(marker_id: int, x_pct: float, y_pct: float, db_path: str = DB_PATH) -> bool:
    """Actualiza la posición (x_pct, y_pct) de un alfiler existente (Drag & Drop / Reubicación)."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_map_markers
            SET x_pct = ?, y_pct = ?
            WHERE id = ?;
        """, (max(0.01, min(0.99, float(x_pct))), max(0.01, min(0.99, float(y_pct))), marker_id))
        conn.commit()
        return cursor.rowcount > 0


# --- Gestión de Ítems en el Alijo (Loot to Keep / Junkbox Tracker) ---

def get_all_stash_counts(db_path: str = DB_PATH) -> Dict[str, int]:
    """Retorna un diccionario {nombre_item: cantidad_en_alijo}."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT item_name, count_collected FROM user_stash_items;")
        return {row[0]: int(row[1]) for row in cursor.fetchall()}


def set_stash_item_count(item_name: str, count: int, db_path: str = DB_PATH) -> int:
    """Guarda la cantidad recolectada de un ítem FiR en el alijo (mínimo 0)."""
    val = max(0, int(count))
    clean_name = item_name.strip()
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if val == 0:
            cursor.execute("DELETE FROM user_stash_items WHERE item_name = ?;", (clean_name,))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO user_stash_items (item_name, count_collected, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP);
            """, (clean_name, val))
        conn.commit()
        return val


# --- Respaldo, Exportación e Importación de Perfil de Usuario ---

def export_user_profile(db_path: str = DB_PATH) -> Dict[str, Any]:
    """Exporta todo el progreso del usuario (Quests, Hideout, Alfileres, Alijo) a un diccionario JSON."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Quests completadas
        cursor.execute("SELECT quest_id FROM user_quest_progress WHERE is_completed = 1;")
        completed_quests = [r[0] for r in cursor.fetchall()]

        # Quests de historia completadas
        cursor.execute("SELECT quest_id FROM user_story_quest_progress WHERE is_completed = 1;")
        completed_story_quests = [r[0] for r in cursor.fetchall()]

        # Módulos del Hideout completados
        cursor.execute("SELECT module_key FROM user_hideout_progress WHERE is_completed = 1;")
        completed_hideout = [r[0] for r in cursor.fetchall()]

        # Alfileres en mapas
        cursor.execute("SELECT map_key, x_pct, y_pct, title, category, color FROM user_map_markers ORDER BY id ASC;")
        markers = [
            {
                "map_key": r[0],
                "x_pct": float(r[1]),
                "y_pct": float(r[2]),
                "title": r[3],
                "category": r[4],
                "color": r[5]
            }
            for r in cursor.fetchall()
        ]

        # Ítems en el alijo
        cursor.execute("SELECT item_name, count_collected FROM user_stash_items WHERE count_collected > 0;")
        stash_items = {r[0]: int(r[1]) for r in cursor.fetchall()}

    return {
        "version": "2.0",
        "app": "TarkovScope",
        "exported_at": datetime.now().isoformat(timespec="seconds"),
        "completed_quests": completed_quests,
        "completed_story_quests": completed_story_quests,
        "completed_hideout": completed_hideout,
        "map_markers": markers,
        "stash_items": stash_items,
        "unlocked_achievements": sorted(get_unlocked_achievement_ids(db_path)),
        "prestige_level": get_prestige_level(db_path),
    }


def import_user_profile(profile_data: Dict[str, Any], db_path: str = DB_PATH) -> bool:
    """Restaura el progreso del usuario desde un diccionario de respaldo."""
    if not isinstance(profile_data, dict):
        return False

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Restaurar Quests
        if "completed_quests" in profile_data:
            cursor.execute("DELETE FROM user_quest_progress;")
            for q_id in profile_data["completed_quests"]:
                if isinstance(q_id, int):
                    cursor.execute("INSERT OR REPLACE INTO user_quest_progress (quest_id, is_completed) VALUES (?, 1);", (q_id,))

        # Restaurar Story Quests
        if "completed_story_quests" in profile_data:
            cursor.execute("DELETE FROM user_story_quest_progress;")
            for sq_id in profile_data["completed_story_quests"]:
                if isinstance(sq_id, str):
                    cursor.execute("INSERT OR REPLACE INTO user_story_quest_progress (quest_id, is_completed) VALUES (?, 1);", (sq_id,))

        # Restaurar Hideout
        if "completed_hideout" in profile_data:
            cursor.execute("DELETE FROM user_hideout_progress;")
            for m_key in profile_data["completed_hideout"]:
                if isinstance(m_key, str):
                    cursor.execute("INSERT OR REPLACE INTO user_hideout_progress (module_key, is_completed) VALUES (?, 1);", (m_key,))

        # Restaurar Alfileres
        if "map_markers" in profile_data:
            cursor.execute("DELETE FROM user_map_markers;")
            for m in profile_data["map_markers"]:
                if isinstance(m, dict):
                    cursor.execute("""
                        INSERT INTO user_map_markers (map_key, x_pct, y_pct, title, category, color)
                        VALUES (?, ?, ?, ?, ?, ?);
                    """, (
                        normalize_map_key(m.get("map_key", "")),
                        float(m.get("x_pct", 0.5)),
                        float(m.get("y_pct", 0.5)),
                        m.get("title", "Nota").strip(),
                        m.get("category", "Nota Personal"),
                        m.get("color", "#EF4444")
                    ))

        # Restaurar Ítems en Alijo
        if "stash_items" in profile_data:
            cursor.execute("DELETE FROM user_stash_items;")
            for item_name, count in profile_data["stash_items"].items():
                if isinstance(item_name, str) and int(count) > 0:
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_stash_items (item_name, count_collected)
                        VALUES (?, ?);
                    """, (item_name.strip(), int(count)))

        conn.commit()

    _invalidate_pref_cache(db_path)

    if "unlocked_achievements" in profile_data and isinstance(profile_data["unlocked_achievements"], list):
        clean_achs = sorted({str(a) for a in profile_data["unlocked_achievements"] if a})
        set_user_preference("unlocked_achievements", json.dumps(clean_achs), db_path=db_path)

    if "prestige_level" in profile_data:
        try:
            set_prestige_level(int(profile_data["prestige_level"]), db_path=db_path)
        except (TypeError, ValueError):
            pass

    return True


DEFAULT_PRERAID_CHECKLIST: List[Dict[str, Any]] = [
    {"id": "keys", "label_es": "Llaves del mapa / SICC / Docs", "label_en": "Map Keys / SICC / Docs", "checked": False, "custom": False},
    {"id": "meds", "label_es": "Médicos, CMS / Surv12 & Painkillers", "label_en": "Meds, CMS / Surv12 & Painkillers", "checked": False, "custom": False},
    {"id": "food", "label_es": "Comida y Agua (Energía / Hidratación)", "label_en": "Food & Water (Energy / Hydration)", "checked": False, "custom": False},
    {"id": "ammo", "label_es": "Munición, Cargadores & Balas extra", "label_en": "Ammo, Mags & Spare Stack", "checked": False, "custom": False},
    {"id": "nades", "label_es": "Granadas, Stims & Contenedor Seguro", "label_en": "Grenades, Stims & Secure Container", "checked": False, "custom": False},
    {"id": "insure", "label_es": "Seguro de equipo & Modo de disparo", "label_en": "Gear Insurance & Fire Mode", "checked": False, "custom": False},
]


def _normalize_preraid_item(item: Dict[str, Any]) -> Dict[str, Any]:
    label_es = str(item.get("label_es") or item.get("label_en") or "").strip()
    label_en = str(item.get("label_en") or label_es).strip()
    return {
        "id": str(item.get("id", "")).strip(),
        "label_es": label_es,
        "label_en": label_en,
        "checked": bool(item.get("checked", False)),
        "custom": bool(item.get("custom", False)),
    }


def get_preraid_checklist(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Devuelve el checklist rápido Pre-Raid persistido (o los 6 ítems base por defecto)."""
    raw = get_user_preference("preraid_checklist", "", db_path=db_path)
    if raw:
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and parsed:
                cleaned = [
                    _normalize_preraid_item(it)
                    for it in parsed
                    if isinstance(it, dict) and str(it.get("id", "")).strip() and (it.get("label_es") or it.get("label_en"))
                ]
                if cleaned:
                    return cleaned
        except (TypeError, ValueError):
            pass
    return [dict(item) for item in DEFAULT_PRERAID_CHECKLIST]


def _save_preraid_checklist(items: List[Dict[str, Any]], db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    set_user_preference("preraid_checklist", json.dumps(items, ensure_ascii=False), db_path=db_path)
    return items


def toggle_preraid_item(item_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Alterna el estado marcado de un ítem del checklist Pre-Raid."""
    target = str(item_id or "").strip()
    items = get_preraid_checklist(db_path=db_path)
    for item in items:
        if item["id"] == target:
            item["checked"] = not item["checked"]
            break
    return _save_preraid_checklist(items, db_path=db_path)


def add_preraid_item(label: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Agrega un ítem personalizado al checklist Pre-Raid (máximo 20 ítems)."""
    clean_label = str(label or "").strip()[:80]
    items = get_preraid_checklist(db_path=db_path)
    if not clean_label or len(items) >= 20:
        return items
    new_id = f"custom_{int(datetime.now().timestamp() * 1000)}_{len(items)}"
    items.append({
        "id": new_id,
        "label_es": clean_label,
        "label_en": clean_label,
        "checked": False,
        "custom": True,
    })
    return _save_preraid_checklist(items, db_path=db_path)


def remove_preraid_item(item_id: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Elimina un ítem personalizado del checklist Pre-Raid (protege los ítems base)."""
    target = str(item_id or "").strip()
    items = get_preraid_checklist(db_path=db_path)
    filtered = [it for it in items if not (it["id"] == target and it.get("custom"))]
    if len(filtered) == len(items):
        return items
    return _save_preraid_checklist(filtered, db_path=db_path)


def reset_preraid_checklist(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Desmarca todos los ítems del checklist Pre-Raid manteniendo los ítems personalizados."""
    items = get_preraid_checklist(db_path=db_path)
    for item in items:
        item["checked"] = False
    return _save_preraid_checklist(items, db_path=db_path)
