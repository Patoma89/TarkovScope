"""
Pruebas unitarias para los módulos v1.3 de TTC (Tactical Tarkov Companion):
- Blindaje, Placas, Cascos, Auriculares & Simulación dual Plate + Soft Aramid
- Contenedores, Mochilas & Rigs Tácticos
- Barters, Cultist Circle & Semáforo FiR (¿Vender o Guardar?)
- PMC Skills, Scav Karma, BTR Driver & Transits
- Caché de iconos de gear (mocked HTTP) & DataStore.global_search v1.3
"""
import io
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.armor_data as armor_data
import core.barters_data as barters_data
import core.containers_data as containers_data
import core.gear_cache as gear_cache
import core.pmc_systems_data as pmc_systems_data
from core.ballistics import simulate_plate_and_aramid
from core.database import init_db, seed_wiki_ammunition
from core.datastore import DataStore


class TestArmorAndPlateBallistics(unittest.TestCase):
    def test_catalog_counts_and_min_class_filter(self):
        all_prot = armor_data.get_all_protection_items()
        self.assertGreaterEqual(len(armor_data.ARMOR_PLATES_CATALOG), 30)
        self.assertGreaterEqual(len(armor_data.ARMOR_VESTS_CATALOG), 40)
        self.assertGreaterEqual(len(armor_data.ARMORED_RIGS_CATALOG), 50)
        self.assertGreaterEqual(len(armor_data.HELMETS_CATALOG), 70)
        self.assertGreaterEqual(len(armor_data.HEADSETS_CATALOG), 20)
        self.assertGreater(len(all_prot), 220)

        cls5_plus = armor_data.filter_protection_items(min_class=5)
        self.assertTrue(cls5_plus)
        self.assertTrue(all(int(x.get("armor_class", 0)) >= 5 for x in cls5_plus))

    def test_helmet_headset_compatibility_filter(self):
        compat_helmets = armor_data.filter_protection_items(
            category="Cascos Blindados",
            headset_only_compat=True,
        )
        self.assertTrue(compat_helmets)
        for item in compat_helmets:
            self.assertNotEqual(item.get("headset_compat"), "Bloquea Auriculares")

    def test_dual_layer_plate_and_aramid_simulation(self):
        low_pen = simulate_plate_and_aramid(
            damage=65,
            penetration_power=22,
            armor_damage=40,
            plate_class=5,
            plate_effective_durability=55.0,
            aramid_class=3,
        )
        high_pen = simulate_plate_and_aramid(
            damage=54,
            penetration_power=58,
            armor_damage=62,
            plate_class=5,
            plate_effective_durability=55.0,
            aramid_class=3,
        )
        self.assertGreater(low_pen["stk"], high_pen["stk"])
        self.assertGreaterEqual(high_pen["stk"], 2)
        self.assertGreater(low_pen["ttk_ms"], high_pen["ttk_ms"])
        self.assertGreater(high_pen["first_shot_pen_pct"], low_pen["first_shot_pen_pct"])


class TestContainersData(unittest.TestCase):
    def test_storage_filters(self):
        all_items = containers_data.get_all_storage_items()
        self.assertGreater(len(all_items), 120)

        rigs_2x2 = containers_data.filter_storage_items(
            category="Rig Táctico",
            only_2x2_rigs=True,
        )
        self.assertTrue(rigs_2x2)
        self.assertTrue(all(r.get("has_2x2") for r in rigs_2x2))

        secure_fits = containers_data.filter_storage_items(only_in_secure=True)
        self.assertTrue(secure_fits)
        self.assertTrue(all(it.get("in_secure") == "Sí" for it in secure_fits))
        self.assertGreaterEqual(len(containers_data.SICC_VS_DOCS_COMPARISON), 4)


class TestBartersAndKeepSell(unittest.TestCase):
    def test_barter_filters(self):
        essentials = barters_data.filter_barters(only_essential=True)
        self.assertGreaterEqual(len(essentials), 40)
        self.assertTrue(all(b.get("is_essential") for b in essentials))

        low_ll = barters_data.filter_barters(max_ll=2)
        self.assertTrue(low_ll)
        self.assertTrue(all(int(b.get("ll", 1)) <= 2 for b in low_ll))

    def test_keep_or_sell_traffic_light(self):
        short_res = barters_data.check_item_keep_status("a", [], [], [])
        self.assertEqual(short_res["level"], "INFO")

        fir_mock = [{"item_name": "Graphics card", "amount": 3, "quest_title": "Farming - Part 4", "trader_name": "Mechanic", "found_in_raid": 1}]
        hideout_mock = [{"station_name": "Bitcoin Farm", "level": 1, "requirements_lines": ["5x Graphics card"], "is_completed": 0}]
        res_fir = barters_data.check_item_keep_status("Graphics card", fir_mock, hideout_mock, ["Old firesteel"])
        self.assertEqual(res_fir["level"], "KEEP_FIR")

        res_hideout = barters_data.check_item_keep_status("Thermite", [], [{"station": "Workbench", "level": 2, "requirements_lines": ["2x Thermite"], "is_completed": 0}], [])
        self.assertEqual(res_hideout["level"], "KEEP_HIDEOUT")

        sample_input = barters_data.BARTERS_CATALOG[0]["inputs"][0]["name"]
        res_barter = barters_data.check_item_keep_status(sample_input, [], [], [])
        self.assertIn(res_barter["level"], ("BARTER", "KEEP_FIR", "KEEP_HIDEOUT"))

        res_sell = barters_data.check_item_keep_status("xyznonexistentloot999", [], [], [])
        self.assertEqual(res_sell["level"], "SELL")


class TestPMCSystemsData(unittest.TestCase):
    def test_skills_and_transits_filters(self):
        phys = pmc_systems_data.filter_skills(category="Física")
        self.assertGreaterEqual(len(phys), 5)
        self.assertTrue(all(s["category"] == "Física" for s in phys))

        str_hits = pmc_systems_data.filter_skills(query="Strength")
        self.assertTrue(any("Strength" in s["name"] for s in str_hits))

        shoreline_tr = pmc_systems_data.filter_transits(from_map="Shoreline")
        destinations = {t["to_map"] for t in shoreline_tr}
        self.assertIn("Lighthouse", destinations)
        self.assertIn("Terminal", destinations)

        self.assertGreaterEqual(len(pmc_systems_data.SCAV_KARMA_BRACKETS), 5)
        self.assertGreaterEqual(len(pmc_systems_data.SCAV_KARMA_ACTIONS), 8)
        self.assertIn("Woods", pmc_systems_data.BTR_SERVICE_DATA["maps"])


class TestGearCache(unittest.TestCase):
    def test_download_and_resolve_with_mock_http(self):
        buf = io.BytesIO()
        Image.new("RGBA", (32, 32), (212, 184, 134, 255)).save(buf, format="PNG")
        png_bytes = buf.getvalue()

        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.content = png_bytes
        fake_session = MagicMock()
        fake_session.get.return_value = fake_resp

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(gear_cache, "GEAR_CACHE_DIR", tmpdir), \
                 patch.object(gear_cache, "BUNDLED_GEAR_CACHE_DIR", os.path.join(tmpdir, "bundled")), \
                 patch.object(gear_cache, "_get_session", return_value=fake_session):
                self.assertIsNone(gear_cache.get_gear_icon_path("unit_test_missing"))
                saved = gear_cache.download_gear_icon("unit_test_plate", "https://example.com/plate.png")
                self.assertIsNotNone(saved)
                self.assertTrue(os.path.exists(saved))
                self.assertEqual(gear_cache.get_gear_icon_path("unit_test_plate"), saved)


class TestV13GlobalSearch(unittest.TestCase):
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

    def test_global_search_indexes_all_new_v13_tabs(self):
        armor_hits = self.ds.global_search("ComTac")
        self.assertTrue(
            any(h["tab"] == "ballistics" and str(h["target"]).startswith("ARMOR:") for h in armor_hits)
        )

        cont_hits = self.ds.global_search("Junk")
        self.assertTrue(any(h["tab"] == "containers" for h in cont_hits))

        cultist_hits = self.ds.global_search("Cultist Circle")
        self.assertTrue(
            any(h["tab"] == "flea" and h["target"] == "CULTIST:" for h in cultist_hits)
        )

        skill_hits = self.ds.global_search("Strength")
        self.assertTrue(
            any(h["tab"] == "pmc_systems" and str(h["target"]).startswith("SKILL:") for h in skill_hits)
        )

        btr_hits = self.ds.global_search("BTR")
        self.assertTrue(
            any(h["tab"] == "pmc_systems" and h["target"] == "BTR:" for h in btr_hits)
        )

        key_hits = self.ds.global_search("Dorm")
        self.assertTrue(any(h["tab"] == "keys" for h in key_hits))

        med_hits = self.ds.global_search("Propital")
        self.assertTrue(any(h["tab"] == "medical" for h in med_hits))


class TestCoreLayerIsolation(unittest.TestCase):
    def test_v13_core_modules_never_import_tkinter(self):
        for mod in (armor_data, barters_data, containers_data, gear_cache, pmc_systems_data):
            with open(mod.__file__, encoding="utf-8") as fh:
                src = fh.read()
            self.assertNotIn("customtkinter", src, mod.__name__)
            self.assertNotIn("tkinter", src, mod.__name__)


if __name__ == "__main__":
    unittest.main()
