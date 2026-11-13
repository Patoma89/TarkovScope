"""
TarkovScope - In-Memory DataStore (Zero-Lag RAM Cache)
Carga todas las tablas de SQLite en memoria RAM al iniciar (<15 ms), construye el grafo
correlativo de Quests (requisitos previos y desbloqueos en cadena), banderas Kappa/Lightkeeper
y gestiona los marcadores personalizados del usuario sobre cada mapa.
"""
import os
import json
import time
import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from core.config import DB_PATH, WIKI_HIDEOUT_JSON_PATH
from core.database import (
    init_db,
    seed_wiki_ammunition,
    get_all_ammunition,
    get_distinct_calibers,
    get_all_maps,
    get_all_quests,
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
    get_db_connection
)
from core.maps_data import normalize_map_key

logger = logging.getLogger("TarkovScope.DataStore")

HIDEOUT_STATIONS_DATA: List[Dict[str, Any]] = [
    {
        "id": "workbench",
        "name": "Workbench (Mesa de Trabajo)",
        "max_level": 3,
        "bonus": "Habilita la modificación avanzada de armas (Presets) y el crafteo de munición Meta.",
        "key_items": [
            "Screw Nuts & Bolts (Tuercas y Tornillos)",
            "Leatherman Multitool",
            "Electric Drill (Taladro eléctrico)",
            "Weapon Parts (Piezas de armas)",
            "Pliers Elite & Set of Files 'Master'"
        ],
        "top_crafts": [
            "Nv. 1: 7.62x39 PS / 9x19 Pst gzh / Piezas de armas",
            "Nv. 2: 5.45x39 PP / .45 ACP AP / 9x19 AP 6.3 / Placas balísticas",
            "Nv. 3: 7.62x39 BP / 5.56x45 M856A1 & M995 / 7.62x51 M61 / 9x39 BP"
        ]
    },
    {
        "id": "medstation",
        "name": "Medstation (Estación Médica)",
        "max_level": 3,
        "bonus": "+Regeneración de salud fuera de raid y fabricación de Salewas, IFAKs y estimulantes.",
        "key_items": [
            "Disposable Syringe & Pile of Meds",
            "Aseptic Bandage & Bottle of Saline Solution",
            "Medical Bloodset & Esmarch Tourniquet",
            "Ophthalmoscope (Oftalmoscopio)",
            "LEDX Skin Transilluminator (Para Nivel 3)"
        ],
        "top_crafts": [
            "Nv. 1: Salewa First Aid Kit (¡Sirve como FiR para la quest 'Shortage' de Therapist!)",
            "Nv. 2: IFAK / AFAK / Morphine Injector FiR (Para 'Health Care Privacy')",
            "Nv. 3: Propital / SJ6 TGLabs / M.U.L.E. Stimulant / Grizzly First Aid Kit"
        ]
    },
    {
        "id": "lavatory",
        "name": "Lavatory (Lavabo / Sastrería)",
        "max_level": 3,
        "bonus": "Fabricación rentable de mochilas, chalecos tácticos, vendas, cargadores y cajas de granadas.",
        "key_items": [
            "Toilet Paper, Toothpaste & Soap",
            "Awl (Punzón — importante en Nv. 1)",
            "KEKTAPE Duct Tape & Corrugated Hose (Mangueras)",
            "Sewing Kit (Kit de costura) & Electric Drill",
            "Pressure Gauge (Manómetro)"
        ],
        "top_crafts": [
            "Nv. 1: Vendajes / Mochilas Sling / Gas Mask Air Filter",
            "Nv. 2: Cargadores 60 tiros 5.45x39 AK-74 (¡Para 'Ice Cream Cones' de Prapor!) / Cordura / BlackRock",
            "Nv. 3: Magazine Case / Grenade Case / Mochila Raid 6Sh118 / Chalecos CPC"
        ]
    },
    {
        "id": "intel_center",
        "name": "Intelligence Center (Centro de Inteligencia)",
        "max_level": 3,
        "bonus": "-Tiempo de enfriamiento de Scav, +Reputación en Quests, -Comisión del Flea Market.",
        "key_items": [
            "Intelligence Folder (Carpeta de Inteligencia)",
            "Secure Flash Drive (Pendrive — 3x para Nv. 2)",
            "Power Cord, Damaged Hard Drive & Printed Circuit Board",
            "Military COFDM Wireless Signal Transmitter (2x para Nv. 3)",
            "VPX Flash Storage Module & Far-forward GPS Signal Amplifier (GPSA)"
        ],
        "top_crafts": [
            "Nv. 1: Secure Flash Drive FiR (¡Para Skier y Jaeger!)",
            "Nv. 2: Intelligence Folder / UHF RFID Reader / Virtex Programmable Processor FiR",
            "Nv. 3: TerraGroup Labs Access Keycard / Military COFDM / Microcontroller Board"
        ]
    },
    {
        "id": "bitcoin_farm",
        "name": "Bitcoin Farm (Granja de Bitcoins)",
        "max_level": 3,
        "bonus": "Generación pasiva continua de Bitcoins físicos (0.2 BTC) según la cantidad de GPUs instaladas (10 / 25 / 50 GPUs).",
        "key_items": [
            "Graphics Card (Tarjeta Gráfica GPU — hasta 50 unidades)",
            "CPU Fan (Ventiladores de CPU — 15x Nv. 1, 15x Nv. 2, 25x Nv. 3)",
            "Power Supply Unit (PSU — Fuentes de alimentación)",
            "Powerfilter (Filtro de energía militar)",
            "Solar Power (Requerido para subir a Nivel 3)"
        ],
        "top_crafts": [
            "Nv. 1 (Máx. 10 GPUs): ~1 Bitcoin cada 28 a 38 horas",
            "Nv. 2 (Máx. 25 GPUs): ~1 Bitcoin cada 20 horas",
            "Nv. 3 (Máx. 50 GPUs): ~1 Bitcoin cada 13 horas"
        ]
    },
    {
        "id": "scav_case",
        "name": "Scav Case (Caja de Scavs)",
        "max_level": 1,
        "bonus": "Envía Scavs a buscar botín aleatorio de alto valor (Keycards, Llaves Marcadas, Armas raras, Stims y objetos de Kappa).",
        "key_items": [
            "Lucky Scav Junk Box (Caja de chatarra Scav)",
            "Fierce Hatchling Moonshine (3x)",
            "Golden Rooster, Roler Submariner Watch & Golden Skull Ring",
            "Bronze Lion (León de bronce — 2x)"
        ],
        "top_crafts": [
            "Pago con 95,000 ₽: Llaves raras, armas y electrónica",
            "Pago con Moonshine: Objetos de streamer (Kappa), estimulantes para 'Samples' y armaduras",
            "Pago con Intelligence Folder: Llaves marcadas, Keycards de Labs y armas militares"
        ]
    },
    {
        "id": "water_booze",
        "name": "Water Collector & Booze Generator (Agua y Destilería)",
        "max_level": 3,
        "bonus": "Hidratación pasiva y producción de Agua Purificada y Fierce Hatchling Moonshine.",
        "key_items": [
            "Corrugated Hose (Mangueras corrugadas) & Duct Tape",
            "Electric Motor (Motor eléctrico — 2x)",
            "Pressure Gauge (Manómetro) & Plumber's Ratchet Wrench (Llave crique)",
            "Silicone Tube (Tubos de silicona) & Analog Thermometer"
        ],
        "top_crafts": [
            "Water Collector Nv. 3: Superwater (Purified Water) usando Water Filter (100/100)",
            "Booze Generator: Fierce Hatchling Moonshine usando 2x Sugar + 1x Superwater"
        ]
    }
]


class DataStore:
    """Almacén en memoria RAM para acceso instantáneo O(1) sin lecturas de disco repetitivas."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)
        self._ammo_all: List[Dict[str, Any]] = []
        self._calibers: List[str] = []
        self._maps: List[Dict[str, Any]] = []
        self._maps_by_key: Dict[str, Dict[str, Any]] = {}
        self._quests: List[Dict[str, Any]] = []
        self._quests_by_id: Dict[int, Dict[str, Any]] = {}
        self._fir_items: List[Dict[str, Any]] = []
        self._hideout_modules: List[Dict[str, Any]] = []
        self._hideout_by_key: Dict[str, Dict[str, Any]] = {}
        self._hideout_by_station_level: Dict[Tuple[str, int], Dict[str, Any]] = {}
        self._stash_items: Dict[str, int] = {}
        self._loaded = False

    def ensure_loaded(self) -> None:
        if not self._loaded:
            self.refresh()

    def _load_hideout_modules_into_ram(self) -> None:
        self._hideout_modules = []
        self._hideout_by_key = {}
        self._hideout_by_station_level = {}

        if not os.path.exists(WIKI_HIDEOUT_JSON_PATH):
            return

        with open(WIKI_HIDEOUT_JSON_PATH, "r", encoding="utf-8") as f:
            raw_mods = json.load(f)

        completed_keys = get_completed_hideout_keys(self.db_path)

        for m in raw_mods:
            mod = dict(m)
            key = mod["key"]
            st_lower = mod["station"].strip().lower()
            lvl = int(mod["level"])
            mod["is_completed"] = 1 if key in completed_keys else 0
            mod["unlocks_modules"] = []
            self._hideout_modules.append(mod)
            self._hideout_by_key[key] = mod
            self._hideout_by_station_level[(st_lower, lvl)] = mod

        for mod in self._hideout_modules:
            label_this = f"{mod['station']} Nv. {mod['level']}"
            for req in mod.get("prereq_modules", []):
                req_st = req.get("station", "").strip().lower()
                req_lvl = int(req.get("level", 1))
                parent_mod = self._hideout_by_station_level.get((req_st, req_lvl))
                if parent_mod and label_this not in parent_mod["unlocks_modules"]:
                    parent_mod["unlocks_modules"].append(label_this)

    def refresh(self) -> None:
        """Recarga todas las tablas de SQLite en estructuras en memoria RAM y arma el grafo de Quests y Hideout."""
        t0 = time.perf_counter()
        try:
            if os.path.abspath(self.db_path) == os.path.abspath(DB_PATH):
                with get_db_connection(self.db_path) as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT COUNT(*) FROM ammunition WHERE length(id) = 24;")
                    has_legacy_hex = cur.fetchone()[0]
                    cur.execute("SELECT COUNT(*) FROM ammunition WHERE caliber = 'Caliber127x33';")
                    has_modern = cur.fetchone()[0]
                    if has_legacy_hex > 0 or has_modern == 0:
                        seed_wiki_ammunition(self.db_path)

            self._ammo_all = get_all_ammunition("TODOS", self.db_path)
            self._calibers = get_distinct_calibers(self.db_path)
            self._maps = get_all_maps(self.db_path)
            self._maps_by_key = {m["key"]: m for m in self._maps}
            self._quests = get_all_quests("TODOS", self.db_path)
            self._quests_by_id = {q["id"]: q for q in self._quests}

            # Construir grafo correlativo de misiones (prereq_titles y unlocks_titles)
            for q in self._quests:
                q["prereq_titles"] = []
                q["unlocks_titles"] = []

            for q in self._quests:
                for req_item in q.get("prereq_ids", []):
                    if isinstance(req_item, int) and req_item in self._quests_by_id:
                        parent_q = self._quests_by_id[req_item]
                        q["prereq_titles"].append(parent_q["title"])
                        if q["title"] not in parent_q["unlocks_titles"]:
                            parent_q["unlocks_titles"].append(q["title"])
                    elif isinstance(req_item, list):
                        or_names = []
                        for sub_id in req_item:
                            if isinstance(sub_id, int) and sub_id in self._quests_by_id:
                                parent_q = self._quests_by_id[sub_id]
                                or_names.append(parent_q["title"])
                                if q["title"] not in parent_q["unlocks_titles"]:
                                    parent_q["unlocks_titles"].append(q["title"])
                        if or_names:
                            q["prereq_titles"].append(" o ".join(or_names))

            with get_db_connection(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT item_name, item_id, quest_id, quest_title, trader_name, count_required
                    FROM quest_items_fir
                    ORDER BY item_name ASC, count_required DESC;
                """)
                self._fir_items = [dict(r) for r in cursor.fetchall()]

            self._load_hideout_modules_into_ram()
            self._stash_items = get_all_stash_counts(self.db_path)
            self._completed_story_ids: Set[str] = get_completed_story_quest_ids(self.db_path)

            self._loaded = True
            elapsed_ms = (time.perf_counter() - t0) * 1000
            logger.info(
                "DataStore cargado en %.1f ms (%d municiones, %d mapas, %d quests, %d ítems FiR, %d zonas hideout)",
                elapsed_ms, len(self._ammo_all), len(self._maps), len(self._quests), len(self._fir_items), len(self._hideout_modules)
            )
        except Exception as e:
            logger.error("Error cargando DataStore en RAM: %s", e)

    # --- Lógica Correlativa de Quests ---

    def is_quest_unlocked(self, quest: Dict[str, Any]) -> bool:
        """
        Determina si una misión está desbloqueada según las misiones previas completadas.
        Si no tiene requisitos previos (prereq_ids vacío), está disponible desde el inicio.
        """
        prereqs = quest.get("prereq_ids", [])
        if not prereqs:
            return True

        for req_item in prereqs:
            if isinstance(req_item, int):
                parent_q = self._quests_by_id.get(req_item)
                if parent_q and not parent_q.get("is_completed"):
                    return False
            elif isinstance(req_item, list):
                valid_parents = [self._quests_by_id[sid] for sid in req_item if isinstance(sid, int) and sid in self._quests_by_id]
                if valid_parents and not any(p.get("is_completed") for p in valid_parents):
                    return False
        return True

    # --- Consultas Instantáneas en RAM (< 1 ms) ---

    def get_calibers(self) -> List[str]:
        self.ensure_loaded()
        return list(self._calibers)

    def get_ammo(
        self,
        caliber: str = "TODOS",
        search_query: str = "",
        sort_by: str = "penetration_power",
        descending: bool = True,
        sort_desc: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        self.ensure_loaded()
        if sort_desc is not None:
            descending = sort_desc

        q = search_query.strip().lower()
        res = []
        seen_names = set()
        for a in self._ammo_all:
            if caliber and caliber != "TODOS" and a.get("caliber") != caliber:
                continue
            name = a.get("name", "")
            if name in seen_names:
                continue
            if q and q not in name.lower() and q not in a.get("caliber", "").lower():
                continue
            seen_names.add(name)
            res.append(a)

        def _sort_key(item: Dict[str, Any]):
            val = item.get(sort_by)
            if val is None:
                return (1, 0)
            if isinstance(val, (int, float)):
                return (0, float(val))
            return (0, str(val).lower())

        res.sort(key=_sort_key, reverse=descending)
        return res

    def get_maps(self) -> List[Dict[str, Any]]:
        self.ensure_loaded()
        return list(self._maps)

    def get_map_by_key_or_name(self, name_or_key: str) -> Dict[str, Any]:
        self.ensure_loaded()
        norm = normalize_map_key(name_or_key)
        if norm in self._maps_by_key:
            return self._maps_by_key[norm]
        return self._maps[0] if self._maps else {}

    def get_quests(
        self,
        trader_filter: str = "TODOS",
        map_filter: str = "TODOS",
        search_query: str = "",
        hide_completed: bool = False,
        progression_mode: str = "ALL"  # "CORRELATIVE", "ALL", "KAPPA", "LIGHTKEEPER"
    ) -> List[Dict[str, Any]]:
        self.ensure_loaded()
        q = search_query.strip().lower()
        norm_map_filter = normalize_map_key(map_filter) if (map_filter and map_filter != "TODOS") else ""

        res = []
        for quest in self._quests:
            if trader_filter and trader_filter != "TODOS" and quest.get("trader_name") != trader_filter:
                continue
            if hide_completed and quest.get("is_completed"):
                continue

            if progression_mode == "CORRELATIVE":
                # Si el usuario no está buscando por texto específico, mostrar solo las desbloqueadas o completadas
                if not q and not (self.is_quest_unlocked(quest) or quest.get("is_completed")):
                    continue
            elif progression_mode == "KAPPA":
                if not quest.get("is_kappa"):
                    continue
            elif progression_mode == "LIGHTKEEPER":
                if not quest.get("is_lightkeeper"):
                    continue

            if norm_map_filter:
                quest_maps_norm = [normalize_map_key(m) for m in quest.get("all_maps", [])]
                if norm_map_filter not in quest_maps_norm:
                    continue
            if q:
                in_title = q in quest.get("title", "").lower()
                in_map = q in quest.get("primary_map", "").lower()
                in_objs = any(q in str(o.get("target", "")).lower() for o in quest.get("objectives", []))
                in_lines = any(q in line.lower() for line in quest.get("objectives_lines", []))
                if not (in_title or in_map or in_objs or in_lines):
                    continue
            res.append(quest)
        return res

    def toggle_quest(self, quest_id: int) -> bool:
        self.ensure_loaded()
        new_state = toggle_quest_progress(quest_id, self.db_path)
        if quest_id in self._quests_by_id:
            self._quests_by_id[quest_id]["is_completed"] = 1 if new_state else 0
        return new_state

    # --- Lógica Correlativa de Hideout ---

    def is_hideout_module_unlocked(self, mod: Dict[str, Any]) -> bool:
        """
        Determina si una estación/nivel del Hideout está desbloqueada según sus requisitos previos.
        Por ejemplo, Hall of Fame Nv. 3 requiere Hall of Fame Nv. 2 + Workbench Nv. 3 + Illumination Nv. 3.
        """
        self.ensure_loaded()
        prereqs = mod.get("prereq_modules", [])
        if not prereqs:
            return True

        for req in prereqs:
            st_lower = req.get("station", "").strip().lower()
            lvl = int(req.get("level", 1))
            parent = self._hideout_by_station_level.get((st_lower, lvl))
            if parent and not parent.get("is_completed"):
                return False
        return True

    def get_hideout_modules(
        self,
        query: str = "",
        progression_mode: str = "CORRELATIVE",  # "CORRELATIVE" o "ALL"
        hide_completed: bool = False
    ) -> List[Dict[str, Any]]:
        self.ensure_loaded()
        q = query.strip().lower()
        res = []
        for mod in self._hideout_modules:
            if hide_completed and mod.get("is_completed"):
                continue
            if progression_mode == "CORRELATIVE":
                if not q and not (self.is_hideout_module_unlocked(mod) or mod.get("is_completed")):
                    continue
            if q:
                in_st = q in mod.get("station", "").lower()
                in_req = any(q in r.lower() for r in mod.get("requirements_lines", []))
                in_fn = any(q in f.lower() for f in mod.get("function_lines", []))
                if not (in_st or in_req or in_fn):
                    continue
            res.append(mod)
        return res

    def toggle_hideout_module(self, module_key: str) -> bool:
        self.ensure_loaded()
        new_state = toggle_hideout_progress(module_key, self.db_path)
        if module_key in self._hideout_by_key:
            self._hideout_by_key[module_key]["is_completed"] = 1 if new_state else 0
        return new_state

    def reset_hideout_progress(self) -> None:
        """Desmarca todas las zonas del Hideout en SQLite y en RAM."""
        self.ensure_loaded()
        reset_all_hideout_progress(self.db_path)
        for mod in self._hideout_modules:
            mod["is_completed"] = 0

    # --- Marcadores y Notas Personalizadas en Mapas ---

    def get_markers(self, map_key: str) -> List[Dict[str, Any]]:
        return get_map_markers(map_key, self.db_path)

    def add_marker(
        self,
        map_key: str,
        x_pct: float,
        y_pct: float,
        title: str,
        category: str = "Nota Personal",
        color: str = "#E5732F"
    ) -> int:
        return add_map_marker(map_key, x_pct, y_pct, title, category, color, self.db_path)

    def delete_marker(self, marker_id: int) -> None:
        delete_map_marker(marker_id, self.db_path)

    def update_marker_pos(self, marker_id: int, x_pct: float, y_pct: float) -> None:
        """Actualiza la posición (x, y) de un alfiler existente en el mapa."""
        update_map_marker_pos(marker_id, x_pct, y_pct, self.db_path)

    # --- Alijo / Junkbox Tracker (Loot to Keep) ---

    def get_stash_items(self) -> Dict[str, int]:
        self.ensure_loaded()
        return dict(self._stash_items)

    def get_stash_count(self, item_name: str) -> int:
        self.ensure_loaded()
        return self._stash_items.get(item_name.strip(), 0)

    def set_stash_count(self, item_name: str, count: int) -> int:
        self.ensure_loaded()
        clean_name = item_name.strip()
        val = max(0, int(count))
        set_stash_item_count(clean_name, val, self.db_path)
        self._stash_items[clean_name] = val
        return val

    # --- Respaldo de Perfil (Exportar / Importar) ---

    def export_profile(self) -> Dict[str, Any]:
        self.ensure_loaded()
        return export_user_profile(self.db_path)

    def import_profile(self, profile_data: Dict[str, Any]) -> bool:
        ok = import_user_profile(profile_data, self.db_path)
        if ok:
            self.refresh()
        return ok

    # --- Buscador Global Rápido (Ctrl + K / Command Palette) ---

    def global_search(self, query: str) -> List[Dict[str, Any]]:
        self.ensure_loaded()
        q = query.strip().lower()
        if not q or len(q) < 2:
            return []

        results: List[Dict[str, Any]] = []

        # 1. Quests
        for quest in self._quests:
            title = quest.get("title", "")
            trader = quest.get("trader_name", "")
            primary_map = quest.get("primary_map", "")
            in_title = q in title.lower()
            in_trader = q in trader.lower()
            in_obj = any(q in obj.lower() for obj in quest.get("objectives_lines", []))
            if in_title or in_trader or in_obj:
                score = 110 if title.lower().startswith(q) else (85 if in_title else 50)
                results.append({
                    "score": score,
                    "category": "Misión / Quest",
                    "badge_color": "#D4B886",
                    "title": title,
                    "subtitle": f"Trader: {trader}  •  Mapa: {primary_map or 'Cualquier Mapa'}",
                    "tab": "quests",
                    "target": title
                })

        # 2. Bosses
        from core.bosses_data import BOSSES_DATA
        for b in BOSSES_DATA:
            b_name = b.get("name", "")
            maps_str = ", ".join(b.get("maps", []))
            in_name = q in b_name.lower()
            in_maps = q in maps_str.lower()
            if in_name or in_maps:
                score = 115 if b_name.lower().startswith(q) else (90 if in_name else 45)
                results.append({
                    "score": score,
                    "category": "Boss / Jefe",
                    "badge_color": "#EF4444",
                    "title": b_name,
                    "subtitle": f"Mapas: {maps_str}  •  Spawn: {b.get('spawn_chance', '')}",
                    "tab": "bosses",
                    "target": b.get("id", "")
                })

        # 3. Mapas Tácticos
        from core.maps_data import MAPS_TACTICAL_DATA
        for m_key, m_info in MAPS_TACTICAL_DATA.items():
            m_name = m_info.get("name", "")
            aliases = m_info.get("aliases", [])
            in_name = q in m_name.lower() or any(q in a.lower() for a in aliases)
            in_desc = q in m_info.get("description", "").lower()
            if in_name or in_desc:
                score = 105 if m_name.lower().startswith(q) else (85 if in_name else 40)
                results.append({
                    "score": score,
                    "category": "Mapa Táctico",
                    "badge_color": "#3B82F6",
                    "title": m_name,
                    "subtitle": f"Jugadores: {m_info.get('players', '')}  •  Duración: {m_info.get('raid_duration', '')}",
                    "tab": "maps",
                    "target": m_key
                })

        # 4. Balística & Munición
        for ammo in self._ammo_all:
            a_name = ammo.get("name", "")
            a_cal = ammo.get("caliber", "")
            in_name = q in a_name.lower()
            in_cal = q in a_cal.lower()
            if in_name or in_cal:
                score = 100 if a_name.lower().startswith(q) else (80 if in_name else 40)
                results.append({
                    "score": score,
                    "category": "Balística",
                    "badge_color": "#10B981",
                    "title": a_name,
                    "subtitle": f"Daño: {ammo.get('damage', 0)}  •  Pen: {ammo.get('penetration_power', 0)}  •  Calibre: {a_cal}",
                    "tab": "ballistics",
                    "target": a_name
                })

        # 5. Ítems Found in Raid (FiR)
        seen_items = set()
        for item in self._fir_items:
            i_name = item.get("item_name", "")
            if i_name in seen_items:
                continue
            if q in i_name.lower():
                seen_items.add(i_name)
                score = 95 if i_name.lower().startswith(q) else 70
                results.append({
                    "score": score,
                    "category": "Ítem FiR",
                    "badge_color": "#F59E0B",
                    "title": i_name,
                    "subtitle": f"Requerido: {item.get('count_required', 1)}x para '{item.get('quest_title', '')}' ({item.get('trader_name', '')})",
                    "tab": "flea",
                    "target": i_name
                })

        # 6. Hideout / Estaciones
        for mod in self._hideout_modules:
            st_label = f"{mod.get('station', '')} Nv. {mod.get('level', 1)}"
            if q in st_label.lower() or any(q in req.lower() for req in mod.get("requirements_lines", [])):
                score = 90 if q in st_label.lower() else 50
                results.append({
                    "score": score,
                    "category": "Hideout",
                    "badge_color": "#8B5CF6",
                    "title": st_label,
                    "subtitle": f"Requisitos: {', '.join(mod.get('requirements_lines', [])[:2])}",
                    "tab": "flea",
                    "target": mod.get("station", "")
                })

        # 7. Llaves & Keycards
        from core.keys_data import KEYS_CATALOG
        for ky in KEYS_CATALOG:
            k_name = ky.get("name", "")
            k_map = ky.get("map", "")
            if q in k_name.lower() or q in k_map.lower() or q in ky.get("opens", "").lower():
                score = 102 if k_name.lower().startswith(q) else (84 if q in k_name.lower() else 45)
                results.append({
                    "score": score,
                    "category": f"Llave ({k_map})",
                    "badge_color": "#0284C7",
                    "title": k_name,
                    "subtitle": f"{ky.get('category', 'Llave')}  •  {ky.get('verdict', '')}",
                    "tab": "keys",
                    "target": k_name,
                })

        # 8. Medicina & Stims
        from core.medical_data import MEDICAL_CATALOG
        for med in MEDICAL_CATALOG:
            m_name = med.get("name", "")
            if q in m_name.lower() or q in med.get("cures_label", "").lower():
                score = 104 if m_name.lower().startswith(q) else (82 if q in m_name.lower() else 45)
                results.append({
                    "score": score,
                    "category": med.get("category", "Medicina"),
                    "badge_color": "#DC2626",
                    "title": m_name,
                    "subtitle": f"{med.get('uses', '')}  •  {med.get('cures_label', '')[:70]}",
                    "tab": "medical",
                    "target": m_name,
                })

        # 9. Blindaje, Placas, Cascos & Auriculares
        from core.armor_data import get_all_protection_items
        for prot in get_all_protection_items():
            p_name = prot.get("name", "")
            if q in p_name.lower() or q in prot.get("material", "").lower():
                score = 98 if p_name.lower().startswith(q) else (76 if q in p_name.lower() else 42)
                cls_lbl = f"Clase {prot.get('armor_class', 0)}" if prot.get("armor_class") else f"{prot.get('hearing_distance_m', '')}m"
                results.append({
                    "score": score,
                    "category": prot.get("category", "Protección"),
                    "badge_color": "#0D9488",
                    "title": p_name,
                    "subtitle": f"{cls_lbl}  •  {prot.get('areas', prot.get('audio_profile', ''))[:65]}",
                    "tab": "ballistics",
                    "target": f"ARMOR:{p_name}",
                })

        # 10. Contenedores, Mochilas & Rigs
        from core.containers_data import get_all_storage_items
        for stg in get_all_storage_items():
            s_name = stg.get("name", "")
            if q in s_name.lower() or q in stg.get("holds", "").lower():
                score = 96 if s_name.lower().startswith(q) else (74 if q in s_name.lower() else 40)
                results.append({
                    "score": score,
                    "category": stg.get("category", "Almacenamiento"),
                    "badge_color": "#6366F1",
                    "title": s_name,
                    "subtitle": f"{stg.get('slots', 0)} slots  •  {stg.get('holds', '')[:65]}",
                    "tab": "containers",
                    "target": s_name,
                })

        # 11. Trueques Clave (Barters) & Cultist Circle
        from core.barters_data import BARTERS_CATALOG, CULTIST_UNIQUE_SACRIFICES, CULTIST_REPEATABLE_SACRIFICES
        for bar in BARTERS_CATALOG:
            rew = bar.get("reward", "")
            inps = bar.get("inputs_text", "")
            if q in rew.lower() or q in inps.lower():
                bonus = 10 if bar.get("is_essential") else 0
                score = (92 if q in rew.lower() else 65) + bonus
                results.append({
                    "score": score,
                    "category": f"Trueque ({bar.get('trader', '')} LL{bar.get('ll', 1)})",
                    "badge_color": "#EA580C",
                    "title": rew,
                    "subtitle": f"Pide: {inps[:70]}",
                    "tab": "flea",
                    "target": f"BARTER:{rew}",
                })
        if "cultist" in q or "circle" in q or "amulet" in q:
            results.append({
                "score": 105,
                "category": "Cultist Circle",
                "badge_color": "#9333EA",
                "title": "Cultist Circle — Umbrales & Recetas",
                "subtitle": "350k+ (14h) · 400k+ (25% 6h FiR) · Sacrificios Únicos y Repetibles",
                "tab": "flea",
                "target": "CULTIST:",
            })
        for sac in CULTIST_UNIQUE_SACRIFICES + CULTIST_REPEATABLE_SACRIFICES:
            if q in sac.get("input", "").lower() or q in sac.get("outcome", "").lower():
                results.append({
                    "score": 88,
                    "category": "Cultist Circle",
                    "badge_color": "#9333EA",
                    "title": f"{sac['input']} -> {sac['outcome']}",
                    "subtitle": f"Duración: {sac['duration']}",
                    "tab": "flea",
                    "target": "CULTIST:",
                })

        # 12. PMC Skills, BTR, Karma & Transits
        from core.pmc_systems_data import PMC_SKILLS_CATALOG, TRANSITS_CATALOG
        for sk in PMC_SKILLS_CATALOG:
            sk_name = sk.get("name", "")
            if q in sk_name.lower() or q in sk.get("requirements", "").lower():
                results.append({
                    "score": 94 if q in sk_name.lower() else 70,
                    "category": f"Skill ({sk.get('category', '')})",
                    "badge_color": "#16A34A",
                    "title": sk_name,
                    "subtitle": f"Req: {sk.get('requirements', '')[:70]}",
                    "tab": "pmc_systems",
                    "target": f"SKILL:{sk_name}",
                })
        if any(w in q for w in ("btr", "karma", "fence", "transit")):
            results.append({
                "score": 100,
                "category": "Sistemas PMC / Raid",
                "badge_color": "#0EA5E9",
                "title": "Scav Karma, Servicio BTR & Red de Transits",
                "subtitle": "Tarifas BTR, tramos Fence LL2 (+6.0) y viajes entre mapas",
                "tab": "pmc_systems",
                "target": "BTR:" if "btr" in q or "transit" in q else "KARMA:",
            })
        for tr in TRANSITS_CATALOG:
            if q in tr.get("to_map", "").lower() or q in tr.get("from_map", "").lower():
                results.append({
                    "score": 68,
                    "category": f"Transit ({tr.get('from_map', '')})",
                    "badge_color": "#0EA5E9",
                    "title": f"{tr['from_map']} -> {tr['to_map']}",
                    "subtitle": tr.get("notes", "")[:72],
                    "tab": "pmc_systems",
                    "target": f"TRANSIT:{tr['from_map']}",
                })

        # Ordenar por score decreciente y limitar a los 45 mejores resultados
        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:45]

    def search_fir_items(self, query: str = "", trader_filter: str = "TODOS") -> List[Dict[str, Any]]:
        self.ensure_loaded()
        q = query.strip().lower()
        res = []
        for item in self._fir_items:
            if trader_filter and trader_filter != "TODOS" and item.get("trader_name") != trader_filter:
                continue
            if q and q not in item.get("item_name", "").lower() and q not in item.get("quest_title", "").lower():
                continue
            res.append(item)
        return res

    def get_hideout_stations(self, query: str = "") -> List[Dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return HIDEOUT_STATIONS_DATA
        res = []
        for st in HIDEOUT_STATIONS_DATA:
            in_name = q in st["name"].lower()
            in_items = any(q in it.lower() for it in st["key_items"])
            in_crafts = any(q in cr.lower() for cr in st["top_crafts"])
            if in_name or in_items or in_crafts:
                res.append(st)
        return res

    def get_story_quests(self, chapter_filter: int = 0, search_query: str = "") -> List[Dict[str, Any]]:
        """Retorna las misiones principales de la historia con su estado de completitud desde RAM (<0.1 ms)."""
        self.ensure_loaded()
        from core.story_quests_data import get_all_storyline_quests
        all_sq = get_all_storyline_quests()

        completed_set = getattr(self, "_completed_story_ids", set())

        res = []
        q_lower = search_query.strip().lower()
        for sq in all_sq:
            sq_copy = dict(sq)
            sq_copy["is_completed"] = 1 if sq["id"] in completed_set else 0

            if chapter_filter > 0 and sq.get("chapter_id") != chapter_filter:
                continue
            if q_lower:
                match = (
                    q_lower in sq["title"].lower()
                    or q_lower in sq.get("trader", "").lower()
                    or q_lower in sq.get("map", "").lower()
                    or q_lower in sq.get("briefing", "").lower()
                )
                if not match:
                    continue
            res.append(sq_copy)
        return res

    def toggle_story_quest(self, sq_id: str) -> bool:
        """Alterna el estado completado/pendiente de una misión u objetivo de la historia y actualiza RAM."""
        self.ensure_loaded()
        new_state = toggle_story_quest_progress(sq_id, self.db_path)
        if not hasattr(self, "_completed_story_ids"):
            self._completed_story_ids = set()
        if new_state:
            self._completed_story_ids.add(str(sq_id))
        else:
            self._completed_story_ids.discard(str(sq_id))
        return new_state

    def get_completed_story_ids(self) -> Set[str]:
        """Retorna el conjunto de IDs de misiones/objetivos de historia completados desde RAM."""
        self.ensure_loaded()
        return set(getattr(self, "_completed_story_ids", set()))

    def get_wiki_story_chapters(self) -> List[Dict[str, Any]]:
        """Retorna los 10 Capítulos de la Historia de la Wiki Oficial con estado de progreso en vivo desde RAM (<0.1 ms)."""
        self.ensure_loaded()
        from core.story_quests_data import get_wiki_story_chapters_full
        chapters = get_wiki_story_chapters_full()
        done_ids = getattr(self, "_completed_story_ids", set())
        for ch in chapters:
            objs = ch.get("objectives", [])
            checkable = [o for o in objs if o.get("type") == "objective"]
            done_cnt = 0
            for o in objs:
                if o.get("type") == "objective":
                    is_done = o["id"] in done_ids
                    o["is_completed"] = 1 if is_done else 0
                    if is_done:
                        done_cnt += 1
            ch["total_objectives"] = len(checkable)
            ch["completed_objectives"] = done_cnt
        return chapters



_GLOBAL_DATASTORE: Optional[DataStore] = None


def get_datastore(db_path: str = DB_PATH) -> DataStore:
    """Retorna la instancia singleton del DataStore en memoria."""
    global _GLOBAL_DATASTORE
    if _GLOBAL_DATASTORE is None or _GLOBAL_DATASTORE.db_path != db_path:
        _GLOBAL_DATASTORE = DataStore(db_path)
    return _GLOBAL_DATASTORE
