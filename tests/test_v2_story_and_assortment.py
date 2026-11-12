"""
Tests unitarios para Quests de Historia (Story Quests), Catálogo de Traders LL1-LL4
y Calibración de Spawns de Bosses (Kollontay y Reshala).
"""
import os
import sys
import unittest

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from core.story_quests_data import STORYLINE_QUESTS_DATA
from core.trader_assortment_data import (
    TRADER_LL_REQUIREMENTS,
    TRADER_ASSORTMENT_DATA,
    get_trader_assortment,
    get_trader_requirements
)
from core.bosses_data import BOSSES_DATA
from core.datastore import get_datastore
from core.database import init_db


class TestStoryAndAssortment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def test_story_quests_data_integrity(self):
        """Valida que existan las 72 misiones principales completas con los 10 capítulos oficiales."""
        self.assertEqual(len(STORYLINE_QUESTS_DATA), 72)
        chapters_found = set()
        for q in STORYLINE_QUESTS_DATA:
            self.assertIn("id", q)
            self.assertIn("chapter_id", q)
            self.assertIn("title", q)
            self.assertIn("trader", q)
            self.assertIn("objectives", q)
            chapters_found.add(q["chapter_id"])

        # Verificar presencia de los 10 capítulos
        for ch in range(1, 11):
            self.assertIn(ch, chapters_found, f"Falta misión para el Capítulo {ch}")

    def test_datastore_story_quests_toggle(self):
        """Valida la persistencia en DB del progreso de quests de historia."""
        ds = get_datastore()
        sq_list = ds.get_story_quests()
        self.assertGreaterEqual(len(sq_list), 10)

        first_q = sq_list[0]
        q_id = first_q["id"]
        initial_state = first_q["is_completed"]

        # Alternar estado
        new_state = ds.toggle_story_quest(q_id)
        self.assertNotEqual(initial_state, new_state)

        # Re-alternar para restaurar
        restored = ds.toggle_story_quest(q_id)
        self.assertEqual(initial_state, restored)

    def test_trader_assortment_nine_traders_ll1_to_ll4(self):
        """Valida que los 9 comerciantes tengan inventario y requisitos para LL1 a LL4."""
        expected_traders = [
            "Prapor", "Therapist", "Skier", "Peacekeeper",
            "Mechanic", "Ragman", "Jaeger", "Ref", "Fence"
        ]
        for tr in expected_traders:
            self.assertIn(tr, TRADER_LL_REQUIREMENTS, f"Falta requisitos de LL para {tr}")
            self.assertIn(tr, TRADER_ASSORTMENT_DATA, f"Falta catálogo de ítems para {tr}")

            for ll in (1, 2, 3, 4):
                req = get_trader_requirements(tr, ll)
                self.assertIn("level", req)
                self.assertIn("rep", req)
                self.assertIn("spend", req)

                items = get_trader_assortment(tr, ll)
                self.assertGreater(len(items), 0, f"Comerciante {tr} no tiene ítems en LL{ll}")
                for it in items:
                    self.assertIn("name", it)
                    self.assertIn("category", it)
                    self.assertIn("cost", it)

    def test_trader_stock_grid_images(self):
        """Verifica que las 32 imágenes oficiales de cuadrícula de stock existan en caché."""
        from core.image_cache import get_trader_stock_image_path
        stock_traders = ["Prapor", "Therapist", "Skier", "Peacekeeper", "Mechanic", "Ragman", "Jaeger", "Ref"]
        for tr in stock_traders:
            for ll in (1, 2, 3, 4):
                img_path = get_trader_stock_image_path(tr, ll)
                self.assertTrue(os.path.exists(img_path), f"Falta imagen de stock para {tr} LL{ll}: {img_path}")
                self.assertGreater(os.path.getsize(img_path), 5000, f"Imagen demasiado pequeña o corrupta: {img_path}")

    def test_kollontay_spawn_coordinates(self):
        """Verifica que los spawns de Kollontay en Streets y Ground Zero estén correctamente calibrados."""
        kollontay = next((b for b in BOSSES_DATA if b["id"] == "kollontay"), None)
        self.assertIsNotNone(kollontay)

        streets_spawns = kollontay["map_spawns"].get("Streets of Tarkov", [])
        self.assertEqual(len(streets_spawns), 2)
        # Klimov Mall y MVD Academy en el noreste
        zones = [s["zone"] for s in streets_spawns]
        self.assertTrue(any("Klimov" in z for z in zones))
        self.assertTrue(any("MVD" in z for z in zones))

        for s in streets_spawns:
            self.assertGreater(s["x"], 0.60)
            self.assertLess(s["y"], 0.55)  # Klimov Mall (y=0.324) y MVD Academy (y=0.496)

    def test_wiki_story_chapters_full_database(self):
        """Verifica que los 10 capítulos oficiales de la Wiki tengan guía paso a paso, banners e imágenes."""
        from core.story_quests_data import get_wiki_story_chapters_full
        chapters = get_wiki_story_chapters_full()
        self.assertEqual(len(chapters), 10)
        expected_titles = [
            "Tour", "Batya", "Falling Skies", "Accidental Witness",
            "They Are Already Here", "The Unheard", "Blue Fire",
            "Boreas", "The Ticket", "The Labyrinth"
        ]
        self.assertEqual([c["title"] for c in chapters], expected_titles)
        for ch in chapters:
            self.assertGreater(len(ch.get("objectives", [])), 5)
            self.assertGreater(len(ch.get("guide_steps", [])), 10)
            total_gal = sum(len(s.get("gallery", [])) for s in ch.get("guide_steps", []))
            self.assertGreater(total_gal, 10, f"Capítulo {ch['title']} tiene muy pocas imágenes de galería")

    def test_reshala_spawn_coordinates(self):
        """Verifica que los spawns de Reshala en Customs estén en New Gas y Dorms."""
        reshala = next((b for b in BOSSES_DATA if b["id"] == "reshala"), None)
        self.assertIsNotNone(reshala)

        customs_spawns = reshala["map_spawns"].get("Customs", [])
        self.assertGreaterEqual(len(customs_spawns), 2)
        gas = next((s for s in customs_spawns if "Gas" in s["zone"]), None)
        dorms = next((s for s in customs_spawns if "Dorm" in s["zone"]), None)

        self.assertIsNotNone(gas)
        self.assertIsNotNone(dorms)
        # New Gas Station está en el centro-este
        self.assertGreater(gas["x"], 0.50)

    def test_hideout_crafts_and_cultist_circle(self):
        """Valida la base de datos de Crafteos FiR del Hideout y recetas del Círculo Cultista."""
        from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA
        self.assertGreaterEqual(len(HIDEOUT_CRAFTS_DATA), 25)
        cultist_recipes = [c for c in HIDEOUT_CRAFTS_DATA if "Cultist" in c.get("station", "")]
        self.assertGreaterEqual(len(cultist_recipes), 2)
        fir_quest_crafts = [c for c in HIDEOUT_CRAFTS_DATA if "QUEST" in c.get("category", "")]
        self.assertGreaterEqual(len(fir_quest_crafts), 12)

    def test_map_tactical_pois(self):
        """Valida las capas tácticas de Llaves/Marked y Cajas Fuertes/Loot en los 10 mapas."""
        from core.maps_data import MAPS_TACTICAL_DATA, get_map_tactical_pois
        for m_id, m in MAPS_TACTICAL_DATA.items():
            if m_id == "icebreaker":
                continue
            pois = get_map_tactical_pois(m["name"])
            key_pois = [p for p in pois if p.get("type") == "key"]
            loot_pois = [p for p in pois if p.get("type") == "loot"]
            self.assertGreater(len(key_pois), 0, f"Mapa {m['name']} sin POIs de llaves")
            self.assertGreater(len(loot_pois), 0, f"Mapa {m['name']} sin POIs de loot")

    def test_ballistics_stk_and_boss_simulator(self):
        """Valida el simulador de Disparos para Matar (STK), Leg Meta y Bosses."""
        from core.ballistics import simulate_shots_to_kill, calculate_leg_meta_shots, simulate_boss_targets
        # M61 (70 dmg, 64 pen, 83 armor dmg) vs Clase 5 -> 2 tiros al tórax
        m61_sim = simulate_shots_to_kill(70, 64.0, 83, armor_class=5)
        self.assertLessEqual(m61_sim["stk"], 3)
        self.assertGreaterEqual(m61_sim["first_shot_pen_pct"], 90)
        # 9x19 RIP (102 dmg) Leg Meta -> 5 tiros
        rip_leg = calculate_leg_meta_shots(102)
        self.assertEqual(rip_leg, 5)
        # Boss simulator
        boss_res = simulate_boss_targets(70, 64.0, 83)
        self.assertEqual(len(boss_res), 4)
        self.assertEqual(boss_res[0]["stk"], 1)  # M61 one-taps Killa's visor


if __name__ == "__main__":
    unittest.main()
