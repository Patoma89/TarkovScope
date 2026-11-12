"""
Pruebas Unitarias para el módulo de Bosses, Probabilidades eftboss.com/pve y Coordenadas de Spawns
"""
import unittest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.bosses_data import get_all_bosses, get_boss_by_id, get_boss_map_spawn_chance


class TestBosses(unittest.TestCase):
    def test_all_bosses_present(self):
        bosses = get_all_bosses()
        self.assertEqual(len(bosses), 13)
        boss_ids = [b["id"] for b in bosses]
        for expected in (
            "reshala", "killa", "tagilla", "cultists", "wedge",
            "shturman", "glukhar", "sanitar", "kaban", "kollontay",
            "the_goons", "partisan", "zryachiy"
        ):
            self.assertIn(expected, boss_ids)

    def test_eftboss_pve_spawn_chances(self):
        """Verifica las probabilidades exactas de spawn en PvE según https://eftboss.com/pve."""
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("reshala"), "Customs", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("killa"), "Interchange", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("shturman"), "Woods", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("glukhar"), "Reserve", "pve"), "60%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("sanitar"), "Shoreline", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("kaban"), "Streets of Tarkov", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("kollontay"), "Streets of Tarkov", "pve"), "75%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("zryachiy"), "Lighthouse", "pve"), "100%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("partisan"), "Woods", "pve"), "25%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("the_goons"), "Lighthouse", "pve"), "30%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("the_goons"), "Shoreline", "pve"), "30%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("the_goons"), "Customs", "pve"), "25%")
        self.assertEqual(get_boss_map_spawn_chance(get_boss_by_id("the_goons"), "Woods", "pve"), "25%")

    def test_boss_structure_and_spawn_coordinates(self):
        for b in get_all_bosses():
            self.assertTrue(len(b["maps"]) > 0, f"Boss {b['id']} sin mapas")
            for m_name in b["maps"]:
                spawns = b["map_spawns"].get(m_name, [])
                self.assertTrue(len(spawns) > 0, f"Boss {b['id']} sin spawns en {m_name}")
                for sp in spawns:
                    self.assertIn("x", sp)
                    self.assertIn("y", sp)
                    self.assertTrue(0.0 <= sp["x"] <= 1.0)
                    self.assertTrue(0.0 <= sp["y"] <= 1.0)

        killa = get_boss_by_id("killa")
        self.assertEqual(killa["name"], "Killa")
        self.assertEqual(killa["total_hp"], 890)
        self.assertIn("Interchange", killa["maps"])

    def test_wedge_only_spawns_on_icebreaker(self):
        wedge = get_boss_by_id("wedge")
        self.assertEqual(wedge["maps"], ["Icebreaker"])
        self.assertNotIn("The Lab", wedge["map_spawns"])
        self.assertNotIn("The Lab", wedge["map_spawn_chances"])
        self.assertEqual(get_boss_map_spawn_chance(wedge, "Icebreaker", "pve"), "100%")
        self.assertNotIn("Labs", wedge["spawn_chance"])
        self.assertTrue(wedge["map_spawns"]["Icebreaker"])


if __name__ == "__main__":
    unittest.main()
