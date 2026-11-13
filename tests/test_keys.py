"""Tests unitarios para el módulo de Llaves & Intel (core/keys_data.py y core/user_data.py)."""
import os
import tempfile
import unittest

from core.database import init_db
from core.keys_data import (
    KEYS_CATALOG,
    filter_keys,
    get_key_stats,
    get_keys_categories,
    get_keys_maps,
)
from core.user_data import get_owned_key_ids, toggle_owned_key


class TestKeysDataAndPersistence(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self._tmp.close()
        self.db_path = self._tmp.name
        init_db(db_path=self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_catalog_integrity(self):
        self.assertGreaterEqual(len(KEYS_CATALOG), 35)
        ids = [k["id"] for k in KEYS_CATALOG]
        self.assertEqual(len(ids), len(set(ids)), "Los IDs de llaves deben ser únicos")
        self.assertIn("Todos", get_keys_maps())
        self.assertIn("Todas", get_keys_categories())

    def test_filter_by_map_category_and_query(self):
        labs_cards = filter_keys(map_filter="The Lab", category_filter="Keycard")
        self.assertGreaterEqual(len(labs_cards), 6)
        self.assertTrue(all(k["map"] == "The Lab" and k["category"] == "Keycard" for k in labs_cards))

        dorm_314 = filter_keys(query="314")
        self.assertTrue(any(k["id"] == "customs_dorm_314_marked" for k in dorm_314))

    def test_owned_keys_toggle_and_missing_quest_filter(self):
        self.assertEqual(get_owned_key_ids(db_path=self.db_path), set())
        new_state = toggle_owned_key("customs_machinery", db_path=self.db_path)
        self.assertTrue(new_state)
        owned = get_owned_key_ids(db_path=self.db_path)
        self.assertIn("customs_machinery", owned)

        missing_q = filter_keys(owned_ids=owned, only_missing_quest=True)
        self.assertFalse(any(k["id"] == "customs_machinery" for k in missing_q))
        self.assertTrue(all(bool(k.get("quests")) for k in missing_q))

        st = get_key_stats(owned)
        self.assertEqual(st["owned"], 1)
        self.assertEqual(st["total"], len(KEYS_CATALOG))


if __name__ == "__main__":
    unittest.main()
