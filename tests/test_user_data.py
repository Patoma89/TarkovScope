"""
Pruebas unitarias de core/user_data.py: progreso, marcadores, alijo y respaldo de perfil.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import init_db
from core.user_data import (
    add_map_marker,
    delete_map_marker,
    export_user_profile,
    get_all_stash_counts,
    get_completed_hideout_keys,
    get_completed_story_quest_ids,
    get_map_markers,
    import_user_profile,
    reset_all_hideout_progress,
    set_stash_item_count,
    toggle_hideout_progress,
    toggle_quest_progress,
    toggle_story_quest_progress,
    update_map_marker_pos,
)


class TestUserData(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        self.db = tmp.name
        init_db(self.db)

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(self.db + suffix)
            except OSError:
                pass

    def test_toggle_quest_is_idempotent_pair(self):
        self.assertTrue(toggle_quest_progress(1, self.db))
        self.assertFalse(toggle_quest_progress(1, self.db))
        self.assertTrue(toggle_quest_progress(1, self.db))

    def test_story_quest_progress(self):
        self.assertTrue(toggle_story_quest_progress("ch1_a", self.db))
        self.assertIn("ch1_a", get_completed_story_quest_ids(self.db))
        self.assertFalse(toggle_story_quest_progress("ch1_a", self.db))
        self.assertNotIn("ch1_a", get_completed_story_quest_ids(self.db))

    def test_hideout_progress_and_reset(self):
        toggle_hideout_progress("generator_1", self.db)
        toggle_hideout_progress("vents_1", self.db)
        self.assertEqual(get_completed_hideout_keys(self.db), {"generator_1", "vents_1"})
        reset_all_hideout_progress(self.db)
        self.assertEqual(get_completed_hideout_keys(self.db), set())

    def test_marker_lifecycle_and_position_clamp(self):
        marker_id = add_map_marker("customs", 0.4, 0.6, "  Stash  ", db_path=self.db)
        self.assertGreater(marker_id, 0)
        markers = get_map_markers("customs", self.db)
        self.assertEqual(len(markers), 1)
        self.assertEqual(markers[0]["title"], "Stash")

        self.assertTrue(update_map_marker_pos(marker_id, 5.0, -3.0, self.db))
        moved = get_map_markers("customs", self.db)[0]
        self.assertAlmostEqual(moved["x_pct"], 0.99)
        self.assertAlmostEqual(moved["y_pct"], 0.01)

        self.assertFalse(update_map_marker_pos(99999, 0.5, 0.5, self.db))
        delete_map_marker(marker_id, self.db)
        self.assertEqual(get_map_markers("customs", self.db), [])

    def test_stash_counts_clamp_and_delete_on_zero(self):
        self.assertEqual(set_stash_item_count(" Salewa ", 3, self.db), 3)
        self.assertEqual(get_all_stash_counts(self.db), {"Salewa": 3})
        self.assertEqual(set_stash_item_count("Salewa", -5, self.db), 0)
        self.assertEqual(get_all_stash_counts(self.db), {})

    def test_export_has_timestamp_and_roundtrip(self):
        toggle_quest_progress(7, self.db)
        toggle_story_quest_progress("ch2_x", self.db)
        toggle_hideout_progress("stash_1", self.db)
        add_map_marker("woods", 0.2, 0.3, "Punto", db_path=self.db)
        set_stash_item_count("GPhone", 2, self.db)

        profile = export_user_profile(self.db)
        self.assertTrue(profile["exported_at"], "exported_at no debe estar vacío")
        self.assertEqual(profile["completed_quests"], [7])
        self.assertEqual(profile["stash_items"], {"GPhone": 2})

        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        other = tmp.name
        try:
            init_db(other)
            self.assertTrue(import_user_profile(profile, other))
            again = export_user_profile(other)
            for key in ("completed_quests", "completed_story_quests", "completed_hideout", "map_markers", "stash_items"):
                self.assertEqual(again[key], profile[key], key)
        finally:
            for suffix in ("", "-wal", "-shm"):
                try:
                    os.remove(other + suffix)
                except OSError:
                    pass

    def test_import_rejects_invalid_payload(self):
        self.assertFalse(import_user_profile([], self.db))
        self.assertFalse(import_user_profile("nope", self.db))  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
