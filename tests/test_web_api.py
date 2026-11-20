"""
Pruebas unitarias de core/web_api.py (Backend puro para TTC v2.0 Next-Gen WebView2).
Verifica aislamiento de UI, bootstrap, Centro de Mando, toggles persistentes,
cambio de skins, búsqueda global y protección contra path traversal en /cache/.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.web_api as web_api
from core.database import init_db
from core.datastore import DataStore
from core.web_api import TTCWebAPI, resolve_web_asset_path


class TestWebApiLayer(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        init_db(self.db_path)
        self.ds = DataStore(self.db_path)
        self.ds.ensure_loaded()
        self.api = TTCWebAPI(datastore=self.ds, db_path=self.db_path)

    def tearDown(self):
        for suffix in ("", "-wal", "-shm"):
            p = self.db_path + suffix
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass

    def test_web_api_core_module_has_no_ui_imports(self):
        from core import web_api_combat, web_api_economy, web_api_incursion, web_api_progression

        for mod in (web_api, web_api_incursion, web_api_progression, web_api_combat, web_api_economy):
            with open(mod.__file__, "r", encoding="utf-8") as fh:
                src = fh.read().lower()
            self.assertNotIn("import tkinter", src, mod.__name__)
            self.assertNotIn("import customtkinter", src, mod.__name__)
            self.assertNotIn("import webview", src, mod.__name__)

    def test_bootstrap_and_command_center_structure(self):
        boot = self.api.get_bootstrap()
        self.assertIn("version", boot)
        self.assertIn("skins", boot)
        self.assertEqual(len(boot["skins_meta"]), 6)

        cc = boot["command_center"]
        self.assertIn("kpis", cc)
        self.assertIn("next_quests", cc)
        self.assertIn("kappa_items", cc)
        self.assertIn("bosses_radar", cc)
        self.assertIn("hideout_ready_list", cc)
        self.assertIn("missing_quest_keys", cc)
        self.assertIn("campaign_progress", cc)
        self.assertIn("raid_clock", cc)
        self.assertEqual(len(cc["kappa_items"]), 44)
        self.assertGreaterEqual(len(cc["bosses_radar"]), 6)

    def test_toggle_kappa_and_skin_persistence(self):
        first_item = self.api.get_command_center_data()["kappa_items"][0]["name"]
        res_on = self.api.toggle_kappa_item(first_item)
        self.assertTrue(res_on["ok"])
        self.assertTrue(res_on["collected"])
        self.assertEqual(res_on["command_center"]["kpis"]["kappa"]["done"], 1)

        res_off = self.api.toggle_kappa_item(first_item)
        self.assertFalse(res_off["collected"])
        self.assertEqual(res_off["command_center"]["kpis"]["kappa"]["done"], 0)

        skin_res = self.api.set_skin("modern_obsidian")
        self.assertTrue(skin_res["ok"])
        self.assertEqual(self.api.get_bootstrap()["skin_id"], "modern_obsidian")
        self.assertFalse(self.api.set_skin("nonexistent_skin")["ok"])

        lvl_res = self.api.set_pmc_level(42)
        self.assertTrue(lvl_res["ok"])
        self.assertEqual(lvl_res["pmc_level"], 42)
        self.assertEqual(self.api.get_bootstrap()["pmc_level"], 42)

        lang_res = self.api.set_lang("en")
        self.assertTrue(lang_res["ok"])
        self.assertEqual(self.api.get_bootstrap()["lang"], "en")
        self.api.set_lang("es")

        self.assertFalse(self.api.open_external_url("javascript:alert(1)")["ok"])

    def test_global_search_and_patch_notes(self):
        hits = self.api.global_search("M80A1")
        self.assertIsInstance(hits, list)
        notes = self.api.get_patch_notes("es")
        self.assertGreaterEqual(len(notes), 5)
        self.assertEqual(notes[0]["version"], "2.0.0")

    def test_resolve_web_asset_path_blocks_traversal(self):
        self.assertIsNone(resolve_web_asset_path("../TarkovScope.py"))
        self.assertIsNone(resolve_web_asset_path("../../Windows/win.ini"))
        self.assertIsNone(resolve_web_asset_path(""))
        avatar_path = resolve_web_asset_path("avatars/prapor.png")
        self.assertIsNotNone(avatar_path)
        self.assertTrue(os.path.isfile(avatar_path))

    def test_all_domain_endpoints_return_valid_payloads(self):
        maps = self.api.get_maps_catalog()
        self.assertGreaterEqual(len(maps), 10)
        customs_det = self.api.get_map_detail("customs")
        self.assertEqual(customs_det["key"], "customs")
        self.assertTrue(customs_det["calibrated_tarkov_dev"])
        self.assertGreaterEqual(len(customs_det["extractions"]), 6)

        # Docs Pase de Temporada (Season 1: Kord Breach)
        bp = self.api.get_season_pass_docs_data()
        self.assertGreaterEqual(len(bp["docs"]), 8)
        self.assertTrue(self.api.set_season_pass_doc_count("financial_docs", 5)["ok"])
        self.assertEqual(self.api.get_season_pass_docs_data()["total_collected"], 5)
        self.api.set_season_pass_doc_count("financial_docs", 0)

        bosses = self.api.get_bosses_data()
        self.assertGreaterEqual(len(bosses["bosses"]), 12)
        self.assertEqual(len(bosses["factions"]), 6)

        keys_data = self.api.get_keys_data()
        self.assertGreaterEqual(len(keys_data["items"]), 200)
        first_kid = keys_data["items"][0]["id"]
        self.assertTrue(self.api.toggle_key_owned(first_kid)["owned"])
        self.assertFalse(self.api.toggle_key_owned(first_kid)["owned"])

        self.assertGreaterEqual(len(self.api.get_route_maps_list()), 8)
        self.assertEqual(len(self.api.get_story_chapters_data()["chapters"]), 10)

        arsenal = self.api.get_weapons_arsenal()
        self.assertGreaterEqual(len(arsenal["arsenal"]), 5)
        self.assertGreaterEqual(len(arsenal["gunsmith"]), 25)
        mod_cat = self.api.get_modding_catalog()
        self.assertEqual(len(mod_cat["weapons"]), 110)
        ak74n_w = next(w for w in mod_cat["weapons"] if w["id"] == "ak74n")
        self.assertIn("factory_ak74n.png", ak74n_w["image_url"])
        self.assertIsInstance(mod_cat["slots"], list)
        self.assertIn("key", mod_cat["slots"][0])
        barrel_opts = self.api.get_weapon_slot_options("m4a1", "barrel")
        self.assertGreater(len(barrel_opts), 10)
        optic_opts = self.api.get_weapon_slot_options("m4a1", "optic")
        self.assertGreater(len(optic_opts), 50)
        opt = self.api.auto_optimize_weapon(mod_cat["weapons"][0]["id"], "meta_recoil", 4)
        self.assertTrue(opt["ok"])
        self.assertTrue(opt["base64_code"].startswith("TTCBUILD:"))

        # Rutas Óptimas (Custom tasks + cálculo con coordenadas proyectadas)
        rt = self.api.get_route_map_tasks("customs")
        self.assertGreater(len(rt["tasks"]), 20)
        self.assertGreater(len(rt["spawns"]), 5)
        first_task_id = rt["tasks"][0]["id"]
        route_res = self.api.compute_optimal_route("customs", [first_task_id], 0)
        self.assertTrue(route_res["ok"])
        self.assertGreater(len(route_res["ordered_stops"]), 0)
        self.assertIsNotNone(route_res["ordered_stops"][0]["x_pct"])

        # Bosses con coordenadas de spawn válidas y Radar HD calibrado
        reshala = next(b for b in bosses["bosses"] if b["id"] == "reshala")
        self.assertIn("Customs", reshala["map_spawns"])
        self.assertGreater(len(reshala["map_spawns"]["Customs"]), 0)
        self.assertIn("x", reshala["map_spawns"]["Customs"][0])
        radar_res = self.api.get_boss_spawn_map_url("reshala", "Customs")
        self.assertTrue(radar_res["ok"])
        self.assertIn("/cache/boss_maps/", radar_res["url"])

        duel = self.api.simulate_ballistics_duel(55, 45, 55, 4)
        self.assertTrue(duel["ok"])
        self.assertGreaterEqual(len(self.api.get_armor_catalog()), 20)

        flea = self.api.get_hideout_and_flea_data()
        self.assertGreaterEqual(len(flea["hideout"]), 50)
        self.assertGreaterEqual(len(self.api.get_containers_data()["items"]), 10)

        med = self.api.get_medical_and_provisions_data()
        self.assertEqual(len(med["medical"]), 43)
        self.assertEqual(len(med["provisions"]), 45)

        pmc = self.api.get_pmc_systems_data()
        self.assertEqual(len(pmc["skills"]), 35)
        self.assertEqual(self.api.set_prestige_lvl(3)["prestige_level"], 3)
        self.assertTrue(self.api.export_profile_json()["ok"])


if __name__ == "__main__":
    unittest.main()
