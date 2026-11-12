"""TarkovScope - Datos del usuario: progreso de misiones/hideout, marcadores de mapa, alijo y perfil.
Extraido de database.py (responsabilidad unica). database.py re-exporta estas funciones.
"""
from datetime import datetime
from typing import Any, Dict, List, Set
from core.config import DB_PATH
from core.maps_data import normalize_map_key
from core.db_connection import get_db_connection


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
        "stash_items": stash_items
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
    return True
