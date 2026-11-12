"""
Pruebas Unitarias para la capa de Base de Datos SQLite, Mapas Tácticos y DataStore en RAM de TarkovScope v2.0
"""
import unittest
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import (
    init_db,
    insert_ammunition_batch,
    get_all_ammunition,
    get_distinct_calibers,
    insert_maps_batch,
    get_all_maps,
    insert_quests_and_fir,
    get_all_quests,
    toggle_quest_progress,
    search_fir_items
)
from core.datastore import DataStore
from core.maps_data import MAPS_TACTICAL_DATA


class TestDatabaseAndDataStore(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except OSError:
                pass

    def test_ammunition_crud(self):
        dummy_ammo = [
            {
                "id": "ammo_1",
                "name": "5.56x45mm M995",
                "shortName": "M995",
                "caliber": "Caliber556x45NATO",
                "ballistics": {
                    "damage": 40,
                    "armorDamage": 58,
                    "penetrationPower": 53.0,
                    "initialSpeed": 1013.0
                },
                "tracer": False
            },
            {
                "id": "ammo_2",
                "name": "5.56x45mm M855",
                "shortName": "M855",
                "caliber": "Caliber556x45NATO",
                "ballistics": {
                    "damage": 50,
                    "armorDamage": 37,
                    "penetrationPower": 28.0,
                    "initialSpeed": 922.0
                },
                "tracer": False
            }
        ]
        insert_ammunition_batch(dummy_ammo, self.db_path)

        all_ammo = get_all_ammunition(db_path=self.db_path)
        self.assertEqual(len(all_ammo), 2)
        self.assertEqual(all_ammo[0]["short_name"], "M995")
        self.assertEqual(all_ammo[1]["short_name"], "M855")

        calibers = get_distinct_calibers(self.db_path)
        self.assertIn("Caliber556x45NATO", calibers)

    def test_maps_crud_and_ground_zero_complete(self):
        dummy_maps = {
            "customs": {
                "locale": {"en": "Customs"},
                "wiki": "https://wiki/Customs",
                "description": "Industrial zone",
                "enemies": ["Reshala", "Scavs"],
                "raidDuration": 40
            },
            "groundzero": {
                "locale": {"en": "Ground Zero"},
                "description": "",
                "enemies": [],
                "raidDuration": None
            }
        }
        insert_maps_batch(dummy_maps, self.db_path)
        maps = get_all_maps(self.db_path)
        # Deben estar los 10 mapas tácticos completos
        self.assertEqual(len(maps), len(MAPS_TACTICAL_DATA))

        gz = next(m for m in maps if m["key"] == "groundzero")
        self.assertEqual(gz["name"], "Ground Zero")
        self.assertIn("TerraGroup", gz["description"])
        self.assertGreaterEqual(len(gz["extractions"]), 5)
        self.assertGreaterEqual(len(gz["keys"]), 2)

    def test_quests_hex_resolution_and_datastore(self):
        dummy_traders = {
            "prapor": {"id": 0, "locale": {"en": "Prapor"}},
            "therapist": {"id": 1, "locale": {"en": "Therapist"}}
        }
        dummy_items = {
            "54491c4f4bdc2db1078b4568": {"name": "MP-133 12ga pump-action shotgun", "shortName": "MP-133"}
        }
        dummy_quests = [
            {
                "id": 101,
                "title": "Debut",
                "giver": 0,
                "wiki": "https://wiki/debut",
                "require": {"level": 1},
                "exp": 1500,
                "objectives": [
                    {"type": "kill", "target": "Scavs", "number": 5, "location": 1},
                    {"type": "collect", "target": "54491c4f4bdc2db1078b4568", "number": 2, "location": 1}
                ]
            },
            {
                "id": 102,
                "title": "Broadcast",
                "giver": 1,
                "wiki": "https://wiki/shortage",
                "require": {"level": 2, "quests": [101]},
                "exp": 2000,
                "objectives": [
                    {"type": "find", "target": "Salewa first aid kit", "number": 3, "location": -1}
                ]
            }
        ]
        insert_quests_and_fir(dummy_quests, dummy_traders, dummy_items, db_path=self.db_path)

        ds = DataStore(self.db_path)
        ds.ensure_loaded()

        # Verificar que el Hex ID fue traducido dentro de objectives
        debut = next(q for q in ds.get_quests() if q["id"] == 101)
        self.assertEqual(debut["primary_map"], "Customs")
        self.assertTrue(debut["is_kappa"])
        self.assertIn("Broadcast", debut["unlocks_titles"])
        targets = [o["target"] for o in debut["objectives"]]
        self.assertIn("MP-133 12ga pump-action shotgun", targets)

        # Verificar bloqueo correlativo inicial: Broadcast (102) requiere Debut (101)
        correlative_before = [q["id"] for q in ds.get_quests(progression_mode="CORRELATIVE")]
        self.assertIn(101, correlative_before)
        self.assertNotIn(102, correlative_before)

        # Al completar Debut (101), Broadcast (102) se desbloquea automáticamente
        new_state = ds.toggle_quest(101)
        self.assertTrue(new_state)
        correlative_after = [q["id"] for q in ds.get_quests(progression_mode="CORRELATIVE")]
        self.assertIn(102, correlative_after)

        # Verificar bandera Lightkeeper en Broadcast
        bcast = next(q for q in ds.get_quests() if q["id"] == 102)
        self.assertTrue(bcast["is_lightkeeper"])

        # Verificar CRUD de marcadores personalizados de mapa
        mk_id = ds.add_marker("Customs", 0.45, 0.65, "Mochila oculta en arbusto", "💎 Loot", "#10B981")
        self.assertGreater(mk_id, 0)
        customs_markers = ds.get_markers("customs")
        self.assertEqual(len(customs_markers), 1)
        self.assertEqual(customs_markers[0]["title"], "Mochila oculta en arbusto")
        ds.delete_marker(mk_id)
        self.assertEqual(len(ds.get_markers("customs")), 0)

        # Buscar items FiR
        fir_salewa = search_fir_items("Salewa", self.db_path)
        self.assertGreaterEqual(len(fir_salewa), 1)

        # Hideout stations & Progresión Correlativa de Hideout
        stations = ds.get_hideout_stations("Workbench")
        self.assertEqual(len(stations), 1)

        corr_mods = [m["key"] for m in ds.get_hideout_modules(progression_mode="CORRELATIVE")]
        self.assertIn("security_lv1", corr_mods)
        self.assertNotIn("generator_lv1", corr_mods)
        self.assertNotIn("hall_of_fame_lv3", corr_mods)

        # Al construir Security Nv. 1, se desbloquea Generator Nv. 1
        ds.toggle_hideout_module("security_lv1")
        corr_after = [m["key"] for m in ds.get_hideout_modules(progression_mode="CORRELATIVE")]
        self.assertIn("generator_lv1", corr_after)
        self.assertNotIn("hall_of_fame_lv3", corr_after)

        # Al limpiar/desmarcar zonas del Hideout, vuelve a las 9 estaciones iniciales
        ds.reset_hideout_progress()
        corr_reset = [m["key"] for m in ds.get_hideout_modules(progression_mode="CORRELATIVE")]
        self.assertNotIn("generator_lv1", corr_reset)


if __name__ == "__main__":
    unittest.main()
