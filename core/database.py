"""
TarkovScope - Módulo de Base de Datos SQLite
Optimizado para lecturas ultra rápidas con WAL mode, transacciones seguras, resolución de IDs,
cadena correlativa de Quests (requisitos previos y desbloqueos), banderas Kappa / Lightkeeper,
y marcadores/notas personalizadas del usuario sobre los mapas (user_map_markers).
"""
import os
import re
import sqlite3
import json
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Set, Iterator
from core.config import DB_PATH, WIKI_QUESTS_JSON_PATH, WIKI_AMMO_JSON_PATH
from core.maps_data import MAPS_TACTICAL_DATA, normalize_map_key
from core.ammo_complete_data import COMPLETE_AMMO_DATA
from core.db_connection import get_db_connection  # noqa: F401 (re-export)
from core.quest_seed_data import (  # noqa: F401 (re-export)
    MAP_ID_TO_NAME, OBJECTIVE_TYPE_LABELS_ES, LIGHTKEEPER_REQUIRED_TITLES, EXTRA_MODERN_QUESTS
)
from core.user_data import (  # noqa: F401 (re-export)
    toggle_quest_progress,
    get_completed_story_quest_ids,
    toggle_story_quest_progress,
    get_completed_hideout_keys,
    toggle_hideout_progress,
    reset_all_hideout_progress,
    get_map_markers,
    add_map_marker,
    delete_map_marker,
    update_map_marker_pos,
    get_all_stash_counts,
    set_stash_item_count,
    export_user_profile,
    import_user_profile,
)

logger = logging.getLogger("TarkovScope.Database")


def init_db(db_path: str = DB_PATH) -> None:
    """Crea las tablas e índices necesarios si no existen."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ammunition (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                short_name TEXT,
                caliber TEXT,
                damage INTEGER,
                armor_damage INTEGER,
                penetration_power REAL,
                initial_speed REAL,
                tracer INTEGER DEFAULT 0,
                raw_json TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ammo_caliber ON ammunition(caliber);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ammo_pen ON ammunition(penetration_power DESC);")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maps (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                wiki_url TEXT,
                description TEXT,
                enemies_json TEXT,
                raid_duration INTEGER,
                raw_json TEXT
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quests (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                trader_id INTEGER,
                trader_name TEXT,
                wiki_url TEXT,
                level_req INTEGER,
                exp INTEGER,
                objectives_json TEXT,
                raw_json TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quests_trader ON quests(trader_name);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_quests_level ON quests(level_req);")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quest_items_fir (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                item_id TEXT,
                quest_id INTEGER,
                quest_title TEXT,
                trader_name TEXT,
                count_required INTEGER,
                FOREIGN KEY (quest_id) REFERENCES quests(id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_fir_item_name ON quest_items_fir(item_name COLLATE NOCASE);")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_quest_progress (
                quest_id INTEGER PRIMARY KEY,
                is_completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_story_quest_progress (
                quest_id TEXT PRIMARY KEY,
                is_completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_hideout_progress (
                module_key TEXT PRIMARY KEY,
                is_completed INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 6. Tabla de Marcadores / Notas personalizadas del usuario en los Mapas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_map_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                map_key TEXT NOT NULL,
                x_pct REAL NOT NULL,
                y_pct REAL NOT NULL,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'Nota Personal',
                color TEXT DEFAULT '#E5732F',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_markers_map ON user_map_markers(map_key);")

        # 7. Tabla de Ítems Guardados en el Alijo (Loot to Keep / Junkbox Tracker)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stash_items (
                item_name TEXT PRIMARY KEY,
                count_collected INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()

        # Auto-sembrado de Munición y purga de duplicados si la base oficial está vacía o tiene residuos antiguos
        if os.path.abspath(db_path) == os.path.abspath(DB_PATH):
            cursor.execute("SELECT COUNT(*) FROM ammunition WHERE length(id) = 24;")
            has_legacy_hex = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM ammunition WHERE caliber = 'Caliber127x33';")
            has_modern = cursor.fetchone()[0]
            if has_legacy_hex > 0 or has_modern == 0:
                seed_wiki_ammunition(db_path)

    logger.info("Base de datos SQLite inicializada correctamente en %s", db_path)


def _resolve_item_token(val: Any, items_map: Dict[str, Any]) -> str:
    """Resuelve un string (posiblemente un Hex ID de 24 caracteres) o lista de strings a nombres reales."""
    if isinstance(val, str):
        clean = val.strip()
        if clean in items_map:
            item_obj = items_map[clean]
            return item_obj.get("name") or item_obj.get("shortName") or clean
        return clean
    elif isinstance(val, list):
        resolved_parts = []
        for sub in val:
            if isinstance(sub, str) and sub in items_map:
                item_obj = items_map[sub]
                name = item_obj.get("name") or item_obj.get("shortName") or sub
                if name not in resolved_parts:
                    resolved_parts.append(name)
            elif isinstance(sub, str):
                resolved_parts.append(sub)
        if len(resolved_parts) > 3:
            return ", ".join(resolved_parts[:3]) + f" (+{len(resolved_parts) - 3} variantes)"
        return " / ".join(resolved_parts)
    return str(val or "")


# --- Operaciones de Inserción y Sincronización ---

def insert_ammunition_batch(ammo_list: List[Dict[str, Any]], db_path: str = DB_PATH) -> None:
    records = []
    for a in ammo_list:
        ballistics = a.get("ballistics") or {}
        dmg = a.get("damage") if a.get("damage") is not None else ballistics.get("damage", 0)
        arm_dmg = a.get("armorDamage") if a.get("armorDamage") is not None else ballistics.get("armorDamage", 0)
        pen = a.get("penetrationPower") if a.get("penetrationPower") is not None else ballistics.get("penetrationPower", 0)
        spd = a.get("initialSpeed") if a.get("initialSpeed") is not None else ballistics.get("initialSpeed", 0)

        a_id = a.get("id") or a.get("item", {}).get("id") or a.get("shortName") or a.get("name")
        name = a.get("name") or a.get("item", {}).get("name") or "Unknown"
        short_name = a.get("shortName") or a.get("item", {}).get("shortName") or ""
        caliber = a.get("caliber") or "Unknown"
        tracer = 1 if a.get("tracer") else 0

        records.append((
            str(a_id),
            name,
            short_name,
            caliber,
            int(dmg or 0),
            int(arm_dmg or 0),
            float(pen or 0),
            float(spd or 0),
            tracer,
            json.dumps(a, ensure_ascii=False)
        ))

    with get_db_connection(db_path) as conn:
        conn.executemany("""
            INSERT OR REPLACE INTO ammunition 
            (id, name, short_name, caliber, damage, armor_damage, penetration_power, initial_speed, tracer, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()


def seed_wiki_ammunition(db_path: str = DB_PATH) -> int:
    """
    Carga el catálogo maestro completo de proyectiles y calibres oficiales (eft-ammo.com / Wiki)
    asegurando cobertura del 100% incluso en modo offline sin conexión a internet.
    """
    ammo_items = []
    if os.path.exists(WIKI_AMMO_JSON_PATH):
        try:
            with open(WIKI_AMMO_JSON_PATH, "r", encoding="utf-8") as f:
                ammo_items = json.load(f)
        except Exception as e:
            logger.warning("Fallo al leer %s, recurriendo a COMPLETE_AMMO_DATA: %s", WIKI_AMMO_JSON_PATH, e)

    if not ammo_items:
        ammo_items = COMPLETE_AMMO_DATA

    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM ammunition;")
        conn.commit()

    insert_ammunition_batch(ammo_items, db_path)
    logger.info("Cargados %d proyectiles oficiales de balística en %s", len(ammo_items), db_path)
    try:
        from core.datastore import get_datastore
        ds = get_datastore(db_path)
        if getattr(ds, "_loaded", False):
            ds.refresh()
    except Exception:
        pass
    return len(ammo_items)


def insert_maps_batch(maps_dict: Dict[str, Any], db_path: str = DB_PATH) -> None:
    with get_db_connection(db_path) as conn:
        records = []
        seen_keys = set()

        for m_id, m_data in maps_dict.items():
            norm_key = normalize_map_key(m_id)
            seen_keys.add(norm_key)
            curated = MAPS_TACTICAL_DATA.get(norm_key, {})

            name = curated.get("name") or m_data.get("locale", {}).get("en") or m_id.capitalize()
            wiki_url = m_data.get("wiki") or f"https://escapefromtarkov.fandom.com/wiki/{name.replace(' ', '_')}"
            desc = curated.get("description") or m_data.get("description") or "Mapa táctico de Escape from Tarkov."
            enemies = curated.get("bosses") or m_data.get("enemies") or []

            raw_dur = m_data.get("raidDuration")
            duration = 35 if norm_key == "groundzero" else 40
            if isinstance(raw_dur, dict):
                duration = int(raw_dur.get("day") or raw_dur.get("night") or duration)
            elif isinstance(raw_dur, (int, float, str)):
                try:
                    duration = int(raw_dur)
                except (ValueError, TypeError):
                    pass

            records.append((
                norm_key,
                name,
                wiki_url,
                desc,
                json.dumps(enemies),
                duration,
                json.dumps(m_data)
            ))

        for m_key, curated in MAPS_TACTICAL_DATA.items():
            if m_key not in seen_keys:
                records.append((
                    m_key,
                    curated["name"],
                    f"https://escapefromtarkov.fandom.com/wiki/{curated['name'].replace(' ', '_')}",
                    curated["description"],
                    json.dumps(curated["bosses"]),
                    35 if m_key == "groundzero" else 40,
                    json.dumps(curated)
                ))

        conn.executemany("""
            INSERT OR REPLACE INTO maps (id, name, wiki_url, description, enemies_json, raid_duration, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, records)
        conn.commit()


def seed_wiki_quests(db_path: str = DB_PATH) -> int:
    """
    Carga las 459 Quests oficiales de la Wiki de Escape from Tarkov (wiki_quests_459.json)
    con sus objetivos, recompensas, orden por Trader, correlatividad y banderas Kappa / Lightkeeper.
    """
    if not os.path.exists(WIKI_QUESTS_JSON_PATH):
        return 0

    with open(WIKI_QUESTS_JSON_PATH, "r", encoding="utf-8") as f:
        wiki_quests = json.load(f)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = OFF;")
        cursor.execute("DELETE FROM quest_items_fir;")
        cursor.execute("DELETE FROM quests;")

        quest_rows = []
        fir_items = []

        for q in wiki_quests:
            q_id = int(q["id"])
            title = q["title"]
            trader_name = q["trader_name"]
            trader_order = int(q.get("trader_order", 99))
            wiki_url = q.get("wiki_url", "")
            level_req = int(q.get("level_req", 1) or 1)
            exp = int(q.get("exp", 0) or 0)
            obj_lines = q.get("objectives_lines", [])
            primary_map = q.get("primary_map", "Cualquier Mapa")

            enriched_objs = [
                {
                    "type": "wiki",
                    "type_es": "Objetivo",
                    "target": line.lstrip("• ").strip(),
                    "number": 1,
                    "map_name": primary_map,
                }
                for line in obj_lines
            ]

            for line in obj_lines:
                clean_line = line.lstrip("• ").strip()
                m_fir = re.search(
                    r"(?:Find and obtain|Obtain|Find|Hand over|Locate and obtain)\s+(?:(\d+)\s+)?(.+?)(?:\s+found in raid|\s+in raid|\s+to\s+|\s+on\s+|$)",
                    clean_line,
                    flags=re.IGNORECASE,
                )
                if m_fir:
                    cnt = int(m_fir.group(1)) if m_fir.group(1) else 1
                    item_txt = m_fir.group(2).strip(" .,")
                    if 2 < len(item_txt) < 85:
                        fir_items.append((item_txt, "", q_id, title, trader_name, cnt))

            quest_rows.append((
                q_id,
                title,
                trader_order,
                trader_name,
                wiki_url,
                level_req,
                exp,
                json.dumps(enriched_objs, ensure_ascii=False),
                json.dumps(q, ensure_ascii=False),
            ))

        cursor.executemany("""
            INSERT OR REPLACE INTO quests (id, title, trader_id, trader_name, wiki_url, level_req, exp, objectives_json, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, quest_rows)

        if fir_items:
            cursor.executemany("""
                INSERT INTO quest_items_fir (item_name, item_id, quest_id, quest_title, trader_name, count_required)
                VALUES (?, ?, ?, ?, ?, ?)
            """, fir_items)

        conn.commit()
    logger.info("Cargadas %d misiones oficiales de la Wiki en %s", len(wiki_quests), db_path)
    return len(wiki_quests)


def insert_quests_and_fir(
    quests_list: List[Dict[str, Any]],
    traders_dict: Dict[str, Any],
    items_dict: Optional[Dict[str, Any]] = None,
    db_path: str = DB_PATH
) -> None:
    if os.path.abspath(db_path) == os.path.abspath(DB_PATH) and os.path.exists(WIKI_QUESTS_JSON_PATH):
        seed_wiki_quests(db_path)
        return

    items_map = items_dict or {}

    trader_names = {}
    for t_key, t_val in traders_dict.items():
        if isinstance(t_val, dict):
            trader_names[t_val.get("id")] = t_val.get("locale", {}).get("en", t_key.capitalize())
            trader_names[t_key] = t_val.get("locale", {}).get("en", t_key.capitalize())

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("DELETE FROM quest_items_fir;")
        cursor.execute("DELETE FROM quests;")

        fir_items = []
        existing_titles = set()

        for q in quests_list:
            q_id = q.get("id")
            giver_id = q.get("giver")
            trader_name = trader_names.get(giver_id) or q.get("trader_name") or f"Trader {giver_id}"
            title = q.get("title") or q.get("locales", {}).get("en", f"Quest #{q_id}")
            existing_titles.add(title.lower())

            require = q.get("require")
            level_req = (require.get("level", 1) or 1) if isinstance(require, dict) else int(q.get("level_req", 1) or 1)
            exp = int(q.get("exp", 0) or 0)
            wiki_url = q.get("wiki") or q.get("wiki_url") or ""
            raw_objectives = q.get("objectives", [])
            if not isinstance(raw_objectives, list):
                raw_objectives = []

            enriched_objectives = []
            for obj in raw_objectives:
                obj_copy = dict(obj)
                obj_type = obj_copy.get("type", "task")
                raw_target = obj_copy.get("target") or obj_copy.get("hint") or ""
                count = int(obj_copy.get("number", 1) or 1)
                loc_id = obj_copy.get("location", -1)

                if isinstance(loc_id, int) and loc_id in MAP_ID_TO_NAME:
                    obj_copy["map_name"] = MAP_ID_TO_NAME[loc_id]
                elif not obj_copy.get("map_name"):
                    obj_copy["map_name"] = "Cualquier Mapa"

                resolved_target = _resolve_item_token(raw_target, items_map)
                obj_copy["target"] = resolved_target
                obj_copy["type_es"] = OBJECTIVE_TYPE_LABELS_ES.get(obj_type, obj_type.capitalize())

                if "with" in obj_copy:
                    obj_copy["with_resolved"] = _resolve_item_token(obj_copy["with"], items_map)

                enriched_objectives.append(obj_copy)

                if obj_type in ("find", "handin", "pickup", "collect", "key", "place", "mark"):
                    if isinstance(raw_target, str) and raw_target:
                        item_hex_id = raw_target if raw_target in items_map else ""
                        item_display_name = resolved_target
                        fir_items.append((item_display_name, item_hex_id, q_id, title, trader_name, count))
                    elif isinstance(raw_target, list):
                        for sub_t in raw_target[:3]:
                            if isinstance(sub_t, str) and sub_t in items_map:
                                sub_name = _resolve_item_token(sub_t, items_map)
                                fir_items.append((sub_name, sub_t, q_id, title, trader_name, count))

            cursor.execute("""
                INSERT OR REPLACE INTO quests (id, title, trader_id, trader_name, wiki_url, level_req, exp, objectives_json, raw_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (q_id, title, giver_id, trader_name, wiki_url, level_req, exp, json.dumps(enriched_objectives), json.dumps(q)))

        for eq in EXTRA_MODERN_QUESTS:
            if eq["title"].lower() not in existing_titles:
                q_id = eq["id"]
                title = eq["title"]
                trader_name = eq["trader_name"]
                level_req = eq["level_req"]
                exp = eq["exp"]
                wiki_url = eq["wiki_url"]
                enriched_objs = []
                for obj in eq["objectives"]:
                    oc = dict(obj)
                    oc["type_es"] = OBJECTIVE_TYPE_LABELS_ES.get(oc.get("type", ""), "Objetivo")
                    enriched_objs.append(oc)
                    if oc.get("type") in ("find", "collect", "pickup", "key"):
                        fir_items.append((oc["target"], "", q_id, title, trader_name, int(oc.get("number", 1))))

                cursor.execute("""
                    INSERT OR REPLACE INTO quests (id, title, trader_id, trader_name, wiki_url, level_req, exp, objectives_json, raw_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (q_id, title, 99, trader_name, wiki_url, level_req, exp, json.dumps(enriched_objs), json.dumps(eq)))

        cursor.executemany("""
            INSERT INTO quest_items_fir (item_name, item_id, quest_id, quest_title, trader_name, count_required)
            VALUES (?, ?, ?, ?, ?, ?)
        """, fir_items)

        conn.commit()


# --- Consultas de Lectura de Alto Rendimiento ---

def get_all_ammunition(caliber: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if caliber and caliber != "TODOS":
            cursor.execute("""
                SELECT id, name, short_name, caliber, damage, armor_damage, penetration_power, initial_speed, tracer
                FROM ammunition
                WHERE caliber = ?
                ORDER BY penetration_power DESC
            """, (caliber,))
        else:
            cursor.execute("""
                SELECT id, name, short_name, caliber, damage, armor_damage, penetration_power, initial_speed, tracer
                FROM ammunition
                ORDER BY caliber ASC, penetration_power DESC
            """)
        return [dict(row) for row in cursor.fetchall()]


def get_distinct_calibers(db_path: str = DB_PATH) -> List[str]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT caliber FROM ammunition WHERE caliber IS NOT NULL AND caliber != '' ORDER BY caliber ASC;")
        return [row[0] for row in cursor.fetchall()]


def get_all_maps(db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, wiki_url, description, enemies_json, raid_duration, raw_json FROM maps ORDER BY name ASC;")
        rows = cursor.fetchall()
        result = []
        seen_keys = set()
        for r in rows:
            d = dict(r)
            norm_key = normalize_map_key(d.get("id") or d.get("name", ""))
            seen_keys.add(norm_key)
            curated = MAPS_TACTICAL_DATA.get(norm_key, {})
            d["key"] = norm_key
            d["name"] = curated.get("name") or d.get("name")
            d["description"] = curated.get("description") or d.get("description")
            d["enemies"] = curated.get("bosses") or json.loads(d.get("enemies_json") or "[]")
            d["raid_duration_str"] = curated.get("raid_duration") or f"{d.get('raid_duration') or 40} min"
            d["players"] = curated.get("players", "10 - 12 PMCs")
            d["level_note"] = curated.get("level_note", "")
            d["extractions"] = curated.get("extractions", [])
            d["transits"] = curated.get("transits", [])
            d["keys"] = curated.get("keys", [])
            d["hotspots"] = curated.get("hotspots", [])
            result.append(d)

        for m_key, curated in MAPS_TACTICAL_DATA.items():
            if m_key not in seen_keys:
                result.append({
                    "id": m_key,
                    "key": m_key,
                    "name": curated["name"],
                    "wiki_url": f"https://escapefromtarkov.fandom.com/wiki/{curated['name'].replace(' ', '_')}",
                    "description": curated["description"],
                    "enemies": curated["bosses"],
                    "raid_duration": 35 if m_key == "groundzero" else 40,
                    "raid_duration_str": curated["raid_duration"],
                    "players": curated["players"],
                    "level_note": curated["level_note"],
                    "extractions": curated["extractions"],
                    "transits": curated["transits"],
                    "keys": curated["keys"],
                    "hotspots": curated["hotspots"],
                })

        result.sort(key=lambda x: x["name"])
        return result


def get_all_quests(trader_filter: Optional[str] = None, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    """Retorna las misiones con su cadena correlativa (requisitos previos), banderas Kappa y Lightkeeper."""
    if os.path.abspath(db_path) == os.path.abspath(DB_PATH) and os.path.exists(WIKI_QUESTS_JSON_PATH):
        with get_db_connection(db_path) as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM quests;")
            cnt = cur.fetchone()[0]
        if cnt != 459:
            seed_wiki_quests(db_path)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        sql = """
            SELECT q.id, q.title, q.trader_id, q.trader_name, q.wiki_url, q.level_req, q.exp,
                   q.objectives_json, q.raw_json,
                   COALESCE(u.is_completed, 0) AS is_completed
            FROM quests q
            LEFT JOIN user_quest_progress u ON q.id = u.quest_id
        """
        params = []
        if trader_filter and trader_filter != "TODOS":
            sql += " WHERE q.trader_name = ?"
            params.append(trader_filter)
        sql += " ORDER BY q.id ASC;"

        cursor.execute(sql, params)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            objs = json.loads(d.get("objectives_json") or "[]")
            raw = json.loads(d.get("raw_json") or "{}")
            d["objectives"] = objs

            # Líneas de objetivos y recompensas estilo Wiki
            if isinstance(raw.get("objectives_lines"), list) and raw["objectives_lines"]:
                d["objectives_lines"] = raw["objectives_lines"]
            else:
                gen_lines = []
                for o in objs:
                    t_es = o.get("type_es") or o.get("type", "Objetivo")
                    tgt = o.get("target", "")
                    num = int(o.get("number", 1) or 1)
                    qty_str = f" (x{num})" if num > 1 else ""
                    gen_lines.append(f"• {t_es}: {tgt}{qty_str}")
                d["objectives_lines"] = gen_lines

            if isinstance(raw.get("rewards_lines"), list) and raw["rewards_lines"]:
                d["rewards_lines"] = raw["rewards_lines"]
            else:
                exp_val = int(d.get("exp") or 0)
                d["rewards_lines"] = [f"• +{exp_val:,} EXP"] if exp_val > 0 else ["• Recompensas de Trader"]

            # Extraer requisitos correlativos de misiones previas
            if isinstance(raw.get("prereq_ids"), list):
                d["prereq_ids"] = raw["prereq_ids"]
            else:
                req_block = raw.get("require", {})
                prereq_quests = req_block.get("quests", []) if isinstance(req_block, dict) else []
                d["prereq_ids"] = prereq_quests if isinstance(prereq_quests, list) else []

            # Determinar banderas Kappa y Lightkeeper
            title_lower = d.get("title", "").strip().lower()
            trader_name = d.get("trader_name", "")
            if "is_kappa" in raw:
                d["is_kappa"] = bool(raw["is_kappa"])
            else:
                nokappa = bool(raw.get("nokappa", False))
                if trader_name in ("Ref", "Lightkeeper", "BTR Driver") or title_lower == "collector":
                    d["is_kappa"] = False
                else:
                    d["is_kappa"] = not nokappa

            if "is_lightkeeper" in raw:
                d["is_lightkeeper"] = bool(raw["is_lightkeeper"])
            else:
                d["is_lightkeeper"] = (
                    trader_name == "Lightkeeper" or title_lower in LIGHTKEEPER_REQUIRED_TITLES
                )

            # Determinar mapa principal de la misión
            if raw.get("primary_map") and isinstance(raw.get("all_maps"), list):
                d["primary_map"] = raw["primary_map"]
                d["all_maps"] = raw["all_maps"]
            else:
                quest_maps = []
                for o in objs:
                    m_name = o.get("map_name")
                    if not m_name:
                        loc = o.get("location", -1)
                        if isinstance(loc, int) and loc in MAP_ID_TO_NAME:
                            m_name = MAP_ID_TO_NAME[loc]
                            o["map_name"] = m_name
                    if m_name and m_name != "Cualquier Mapa" and m_name not in quest_maps:
                        quest_maps.append(m_name)

                d["primary_map"] = quest_maps[0] if quest_maps else "Cualquier Mapa"
                d["all_maps"] = quest_maps
            result.append(d)
        return result


def search_fir_items(query: str, db_path: str = DB_PATH) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT item_name, quest_id, quest_title, trader_name, count_required
            FROM quest_items_fir
            WHERE item_name LIKE ?
            ORDER BY trader_name ASC, count_required DESC;
        """, (f"%{query}%",))
        return [dict(row) for row in cursor.fetchall()]


def is_db_populated(db_path: str = DB_PATH) -> bool:
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ammunition;")
            ammo_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM quests;")
            quests_count = cursor.fetchone()[0]
            return ammo_count > 0 and quests_count > 0
    except Exception:
        return False
