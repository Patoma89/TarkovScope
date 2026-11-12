"""
Pruebas unitarias del DataStore en RAM, la configuración global y la paleta centralizada.
"""
import os
import re
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import config
from core.database import init_db, seed_wiki_ammunition
from core.datastore import DataStore

HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


class TestConfig(unittest.TestCase):
    def test_theme_keys_are_valid_hex(self):
        required = {
            "bg_dark", "bg_card", "bg_card_hover", "border", "text_main", "text_muted",
            "accent_gold", "accent_orange", "accent_olive", "accent_blue", "accent_red",
            "accent_yellow", "accent_green",
        }
        self.assertTrue(required.issubset(config.THEME))
        for key, value in config.THEME.items():
            self.assertRegex(value, HEX, key)

    def test_paths_live_under_base_dir(self):
        for path in (config.DATA_DIR, config.CACHE_DIR, config.DB_PATH):
            self.assertTrue(os.path.abspath(path).startswith(os.path.abspath(config.BASE_DIR)))
        self.assertTrue(os.path.isdir(config.DATA_DIR))

    def test_data_files_cover_sync_endpoints(self):
        for key in ("quests", "hideout", "items", "maps", "traders", "ammo"):
            self.assertIn(key, config.DATA_FILES)

    def test_config_has_no_duplicate_except_blocks(self):
        with open(config.__file__, encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotRegex(src, r"except Exception:\s*\n\s*pass\s*\n\s*except Exception:")


class TestPalette(unittest.TestCase):
    def test_palette_constants_are_valid_and_unique(self):
        from ui import theme

        names = [n for n in dir(theme) if n.startswith("C_")]
        self.assertGreater(len(names), 10)
        values = [getattr(theme, n).upper() for n in names]
        for n in names:
            self.assertRegex(getattr(theme, n), HEX, n)
        self.assertEqual(len(values), len(set(values)), "colores duplicados bajo distinto nombre")


class TestDataStore(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.db = tmp.name
        init_db(self.db)
        seed_wiki_ammunition(self.db)
        self.ds = DataStore(self.db)

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.db + suffix)
            except OSError:
                pass

    def test_lazy_load_and_ammo_queries(self):
        self.assertFalse(self.ds._loaded)
        calibers = self.ds.get_calibers()
        self.assertTrue(self.ds._loaded)
        self.assertGreater(len(calibers), 5)

        all_ammo = self.ds.get_ammo(caliber="TODOS")
        self.assertGreater(len(all_ammo), 50)
        one = calibers[0]
        filtered = self.ds.get_ammo(caliber=one)
        self.assertTrue(filtered)
        self.assertTrue(all(a["caliber"] == one for a in filtered))

    def test_ammo_sorted_descending_by_penetration(self):
        ammo = self.ds.get_ammo(caliber="TODOS", sort_by="penetration_power", descending=True)
        values = [a.get("penetration_power") or 0 for a in ammo]
        self.assertEqual(values, sorted(values, reverse=True))

    def test_stash_count_is_clamped_and_cached(self):
        self.assertEqual(self.ds.set_stash_count("  GPU  ", 4), 4)
        self.assertEqual(self.ds.get_stash_count("GPU"), 4)
        self.assertEqual(self.ds.set_stash_count("GPU", -9), 0)
        self.assertEqual(self.ds.get_stash_count("GPU"), 0)

    def test_markers_roundtrip_through_store(self):
        marker_id = self.ds.add_marker("customs", 0.5, 0.5, "Spawn")
        self.assertEqual(len(self.ds.get_markers("customs")), 1)
        self.ds.update_marker_pos(marker_id, 0.25, 0.75)
        m = self.ds.get_markers("customs")[0]
        self.assertAlmostEqual(m["x_pct"], 0.25)
        self.ds.delete_marker(marker_id)
        self.assertEqual(self.ds.get_markers("customs"), [])

    def test_profile_export_import_refreshes(self):
        self.ds.set_stash_count("Bitcoin", 2)
        profile = self.ds.export_profile()
        self.assertEqual(profile["stash_items"].get("Bitcoin"), 2)
        profile["stash_items"] = {"Bitcoin": 9}
        self.assertTrue(self.ds.import_profile(profile))
        self.assertEqual(self.ds.get_stash_count("Bitcoin"), 9)
        self.assertFalse(self.ds.import_profile("invalido"))  # type: ignore[arg-type]

    def test_global_search_short_query_is_safe(self):
        self.assertIsInstance(self.ds.global_search(""), list)
        self.assertIsInstance(self.ds.global_search("m"), list)


if __name__ == "__main__":
    unittest.main()
