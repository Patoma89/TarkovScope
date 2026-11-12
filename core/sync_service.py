"""
TarkovScope - Servicio de Sincronización de Datos y Pre-Baking
Descarga los datasets oficiales de Tarkov, actualiza SQLite WAL, refresca el DataStore en RAM
y pre-genera miniaturas de mapas y spawns para operación Zero-Lag.
"""
import requests
import logging
from typing import Callable, Optional
from core.config import TARKOV_DATA_BASE_URL, DATA_FILES, DB_PATH, TARKOV_DEV_GRAPHQL_URL
from core.database import (
    init_db,
    insert_ammunition_batch,
    seed_wiki_ammunition,
    insert_maps_batch,
    insert_quests_and_fir,
    is_db_populated,
    get_db_connection
)
from core.datastore import get_datastore
from core.image_cache import prebake_all_assets

logger = logging.getLogger("TarkovScope.SyncService")


class SyncService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def sync_all(self, progress_callback: Optional[Callable[[int, str], None]] = None) -> bool:
        """
        Sincroniza todos los datos desde los repositorios de la comunidad,
        pre-genera las imágenes tácticas y recarga el DataStore en memoria RAM.
        """
        def update_progress(pct: int, msg: str):
            if progress_callback:
                progress_callback(pct, msg)

        try:
            update_progress(10, "Conectando con la base de datos de Tarkov...")

            # 1. Munición y Balística (Actualizada vía Tarkov.dev GraphQL con fallback a catálogo oficial)
            update_progress(20, "Descargando tablas completas de munición y balística...")
            ammo_synced = False
            try:
                graphql_payload = {
                    "query": """
                    {
                      ammo(lang: en) {
                        item {
                          id
                          name
                          shortName
                        }
                        caliber
                        damage
                        armorDamage
                        penetrationPower
                        initialSpeed
                        tracer
                      }
                    }
                    """
                }
                dev_resp = requests.post(TARKOV_DEV_GRAPHQL_URL, json=graphql_payload, timeout=10)
                if dev_resp.status_code == 200:
                    dev_data = dev_resp.json()
                    raw_ammo = dev_data.get("data", {}).get("ammo", [])
                    if raw_ammo and len(raw_ammo) > 50:
                        with get_db_connection(self.db_path) as conn:
                            conn.execute("DELETE FROM ammunition;")
                            conn.commit()
                        insert_ammunition_batch(raw_ammo, self.db_path)
                        ammo_synced = True
                        logger.info("Sincronizados %d proyectiles desde tarkov.dev GraphQL", len(raw_ammo))
            except Exception as e:
                logger.warning("Fallo al conectar con tarkov.dev GraphQL: %s", e)

            if not ammo_synced:
                # Fallback al catálogo oficial precargado de balística (eft-ammo.com)
                seed_wiki_ammunition(self.db_path)

            # 2. Mapas y Extracciones
            update_progress(40, "Sincronizando mapas tácticos y salidas...")
            maps_url = TARKOV_DATA_BASE_URL + DATA_FILES["maps"]
            maps_resp = requests.get(maps_url, timeout=12)
            if maps_resp.status_code == 200:
                maps_dict = maps_resp.json()
                insert_maps_batch(maps_dict, self.db_path)
            else:
                insert_maps_batch({}, self.db_path)

            # 3. Comerciantes (Traders) e Items para traducción de IDs
            update_progress(60, "Sincronizando Comerciantes y catálogo de Ítems...")
            traders_url = TARKOV_DATA_BASE_URL + DATA_FILES["traders"]
            traders_resp = requests.get(traders_url, timeout=12)
            traders_dict = traders_resp.json() if traders_resp.status_code == 200 else {}

            items_url = TARKOV_DATA_BASE_URL + DATA_FILES["items"]
            items_resp = requests.get(items_url, timeout=15)
            items_dict = items_resp.json() if items_resp.status_code == 200 else {}

            # 4. Quests & Items Found in Raid
            update_progress(78, "Indexando Misiones, Mapas y requerimientos FiR...")
            quests_url = TARKOV_DATA_BASE_URL + DATA_FILES["quests"]
            quests_resp = requests.get(quests_url, timeout=12)
            if quests_resp.status_code == 200:
                quests_list = quests_resp.json()
                insert_quests_and_fir(quests_list, traders_dict, items_dict, self.db_path)

            # 5. Pre-bake de miniaturas y recarga en RAM
            update_progress(90, "Optimizando planos 2D y caché en RAM...")
            prebake_all_assets()
            get_datastore(self.db_path).refresh()

            with get_db_connection(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO metadata (key, value, updated_at)
                    VALUES ('last_sync', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
                """)
                conn.commit()

            update_progress(100, "¡Base de datos táctica lista (Zero-Lag)!")
            return True

        except Exception as e:
            logger.error("Error durante la sincronización: %s", e)
            if is_db_populated(self.db_path):
                get_datastore(self.db_path).refresh()
                update_progress(100, "Modo sin conexión: Usando base de datos táctica local.")
                return True
            update_progress(0, f"Error de conexión: {e}")
            return False
