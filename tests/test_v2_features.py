"""
Tests unitarios para las nuevas funcionalidades tácticas de TarkovScope v2.0:
- Alijo / Junkbox Tracker (user_stash_items)
- Reubicación de alfileres (update_map_marker_pos)
- Respaldo de Perfil (export_user_profile / import_user_profile)
- Buscador Global Rápido (global_search)
- Capas de Extracciones y Bosses (get_map_extractions_with_coords)
"""
import os
import tempfile
import unittest
from core.database import (
    init_db,
    insert_ammunition_batch,
    insert_maps_batch,
    insert_quests_and_fir,
    add_map_marker,
    get_map_markers,
    update_map_marker_pos,
    get_all_stash_counts,
    set_stash_item_count,
    export_user_profile,
    import_user_profile,
    toggle_quest_progress,
    toggle_hideout_progress
)
from core.datastore import DataStore
from core.maps_data import get_map_extractions_with_coords
from core.quest_guides_data import get_quest_tactical_guide, extract_required_keys_deep
from core.tactical_map_renderer import render_quest_objective_map
from core.weapon_modding_data import MODDABLE_WEAPONS, ATTACHMENTS_CATALOG
from core.weapon_modding_engine import (
    calculate_build_stats,
    export_build_to_json,
    export_shopping_list_text,
    export_build_to_base64,
    import_build_from_base64,
    import_build_from_json
)
from core.weapon_visual_compositor import render_weapon_workbench_composite


class TestV2Features(unittest.TestCase):
    def setUp(self):
        self.tmp_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(self.tmp_fd)
        init_db(self.db_path)

        # Sembrar datos mínimos para probar
        insert_ammunition_batch([
            {
                "id": "a1",
                "name": "5.56x45 M855A1",
                "shortName": "M855A1",
                "caliber": "Caliber556x45NATO",
                "ballistics": {
                    "damage": 49,
                    "armorDamage": 58,
                    "penetrationPower": 44.0,
                    "initialSpeed": 945
                },
                "tracer": False
            },
            {
                "id": "a2",
                "name": "5.45x39 BT gs",
                "shortName": "BT",
                "caliber": "Caliber545x39",
                "ballistics": {
                    "damage": 42,
                    "armorDamage": 49,
                    "penetrationPower": 42.0,
                    "initialSpeed": 875
                },
                "tracer": True
            }
        ], self.db_path)

        insert_maps_batch({
            "customs": {
                "locale": {"en": "Customs"},
                "wiki": "https://wiki/Customs",
                "description": "Parque industrial",
                "enemies": ["Reshala", "Scavs"],
                "raidDuration": 40
            }
        }, self.db_path)

        insert_quests_and_fir([
            {
                "id": 101,
                "title": "Debut",
                "trader_name": "Prapor",
                "level_req": 1,
                "exp": 3000,
                "wiki_url": "",
                "map_name": "Customs",
                "require": {"level": 1, "quests": []},
                "nokappa": False,
                "objectives": [{"type": "kill", "target": "5 Scavs en Customs", "number": 5, "location": 1, "map_name": "Customs"}]
            }
        ], {}, {}, self.db_path)

        self.ds = DataStore(self.db_path)
        self.ds.refresh()

    def tearDown(self):
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_stash_items_counter(self):
        # Inicialmente vacío
        counts = self.ds.get_stash_items()
        self.assertEqual(counts, {})
        self.assertEqual(self.ds.get_stash_count("Salewa First Aid Kit"), 0)

        # Registrar ítems
        self.ds.set_stash_count("Salewa First Aid Kit", 3)
        self.assertEqual(self.ds.get_stash_count("Salewa First Aid Kit"), 3)

        # Modificar conteo
        self.ds.set_stash_count("Salewa First Aid Kit", 5)
        self.assertEqual(self.ds.get_stash_count("Salewa First Aid Kit"), 5)

        # No permitir conteos negativos
        self.ds.set_stash_count("Salewa First Aid Kit", -2)
        self.assertEqual(self.ds.get_stash_count("Salewa First Aid Kit"), 0)

    def test_update_marker_position(self):
        mid = self.ds.add_marker("customs", 0.25, 0.35, "Alijo Secreto")
        markers = self.ds.get_markers("customs")
        self.assertEqual(len(markers), 1)
        self.assertAlmostEqual(markers[0]["x_pct"], 0.25)
        self.assertAlmostEqual(markers[0]["y_pct"], 0.35)

        # Mover alfiler a nuevas coordenadas
        self.ds.update_marker_pos(mid, 0.75, 0.85)
        markers_after = self.ds.get_markers("customs")
        self.assertEqual(len(markers_after), 1)
        self.assertAlmostEqual(markers_after[0]["x_pct"], 0.75)
        self.assertAlmostEqual(markers_after[0]["y_pct"], 0.85)

    def test_export_and_import_user_profile(self):
        # 1. Crear progreso de prueba
        toggle_quest_progress(101, self.db_path)
        toggle_hideout_progress("workbench_1", self.db_path)
        self.ds.add_marker("customs", 0.50, 0.50, "Nota Alpha", "Peligro", "#EF4444")
        self.ds.set_stash_count("Morphine Injector", 4)

        # 2. Exportar
        profile = self.ds.export_profile()
        self.assertIn("completed_quests", profile)
        self.assertIn(101, profile["completed_quests"])
        self.assertIn("workbench_1", profile["completed_hideout"])
        self.assertEqual(len(profile["map_markers"]), 1)
        self.assertEqual(profile["stash_items"].get("Morphine Injector"), 4)

        # 3. Limpiar base y restaurar en una nueva
        tmp2_fd, db_path2 = tempfile.mkstemp(suffix=".db")
        os.close(tmp2_fd)
        init_db(db_path2)
        ds2 = DataStore(db_path2)
        ds2.refresh()

        ok = ds2.import_profile(profile)
        self.assertTrue(ok)

        # Verificar restauración
        self.assertEqual(ds2.get_stash_count("Morphine Injector"), 4)
        markers2 = ds2.get_markers("customs")
        self.assertEqual(len(markers2), 1)
        self.assertEqual(markers2[0]["title"], "Nota Alpha")

        if os.path.exists(db_path2):
            try:
                os.remove(db_path2)
            except Exception:
                pass

    def test_global_search(self):
        # Búsqueda por proyectil
        res_ammo = self.ds.global_search("M855A1")
        self.assertTrue(any("M855A1" in r["title"] and r["tab"] == "ballistics" for r in res_ammo))

        # Búsqueda por misión
        res_quest = self.ds.global_search("Debut")
        self.assertTrue(any("Debut" in r["title"] and r["tab"] == "quests" for r in res_quest))

        # Búsqueda por mapa
        res_map = self.ds.global_search("Customs")
        self.assertTrue(any("Customs" in r["title"] and r["tab"] == "maps" for r in res_map))

        # Búsqueda por Boss
        res_boss = self.ds.global_search("Reshala")
        self.assertTrue(any("Reshala" in r["title"] and r["tab"] == "bosses" for r in res_boss))

    def test_map_extractions_with_coords(self):
        extracts = get_map_extractions_with_coords("customs")
        self.assertGreater(len(extracts), 0)
        for ex in extracts:
            self.assertIn("name", ex)
            self.assertIn("x", ex)
            self.assertIn("y", ex)
            self.assertGreaterEqual(ex["x"], 0.0)
            self.assertLessEqual(ex["x"], 1.0)
            self.assertGreaterEqual(ex["y"], 0.0)
            self.assertLessEqual(ex["y"], 1.0)

    def test_quest_tactical_guide_curated_and_procedural(self):
        # 1. Curada (Background Check)
        curated_q = {
            "title": "Background Check",
            "trader_name": "Prapor",
            "primary_map": "Customs",
            "objectives_lines": ["Obtain the bronze pocket watch", "Hand over the watch"]
        }
        guide_c = get_quest_tactical_guide(curated_q)
        self.assertEqual(guide_c["title"], "Background Check")
        self.assertTrue(any("Machinery Key" in k["name"] for k in guide_c["keys_required"]))
        self.assertEqual(len(guide_c["phases"]), 4)
        self.assertTrue(len(guide_c["danger_notes"]) > 0)

        # 2. Procedural (Debut)
        procedural_q = {
            "title": "Debut",
            "trader_name": "Prapor",
            "primary_map": "Customs",
            "objectives_lines": ["Eliminate 5 Scavs all over the Customs territory", "Obtain 2 MP-133 shotguns in raid"]
        }
        guide_p = get_quest_tactical_guide(procedural_q)
        self.assertEqual(guide_p["title"], "Debut")
        self.assertEqual(len(guide_p["phases"]), 4)
        self.assertIn("Customs", guide_p["phases"][1]["phase"])

    def test_render_quest_objective_map(self):
        img = render_quest_objective_map(
            map_key="customs",
            pin_coords=(0.42, 0.54),
            quest_title="Background Check",
            objective_poi="Camion Cisterna",
            target_size=(400, 240)
        )
        self.assertIsNotNone(img)
        self.assertGreater(img.size[0], 200)
        self.assertGreater(img.size[1], 150)

    def test_weapon_modding_engine_stats_calculation(self):
        # M4A1 Default
        m4_def = calculate_build_stats("m4a1", MODDABLE_WEAPONS["m4a1"]["default_slots"])
        self.assertEqual(m4_def["weapon_id"], "m4a1")
        self.assertGreater(m4_def["final_ergo"], 0)
        self.assertLessEqual(m4_def["final_ergo"], 100)
        self.assertGreater(m4_def["final_recoil_v"], 0)
        self.assertGreater(m4_def["final_weight_kg"], 1.0)

        # M4A1 Meta Laser Recoil
        m4_meta = calculate_build_stats("m4a1", MODDABLE_WEAPONS["m4a1"]["presets"]["Meta Laser Recoil"])
        # El retroceso del build meta debe ser significativamente menor al de fábrica
        self.assertLess(m4_meta["final_recoil_v"], m4_def["final_recoil_v"])
        self.assertLess(m4_meta["final_recoil_h"], m4_def["final_recoil_h"])
        self.assertLess(m4_meta["recoil_reduction_pct"], 0.0)
        self.assertGreater(m4_meta["total_cost_rubles"], 100000)

    def test_weapon_modding_exporters_and_importers(self):
        w_id = "m4a1"
        slots = MODDABLE_WEAPONS["m4a1"]["presets"]["Meta Laser Recoil"]

        # 1. JSON Export & Import
        json_str = export_build_to_json(w_id, slots, "Meta Laser M4")
        self.assertIn("TarkovScope_EFT_WeaponBuild", json_str)
        self.assertIn("items", json_str)

        imported_json = import_build_from_json(json_str)
        self.assertIsNotNone(imported_json)
        self.assertEqual(imported_json["weapon_id"], "m4a1")
        self.assertEqual(imported_json["slots"]["muzzle"], slots["muzzle"])

        # 2. Text Shopping List
        shop_txt = export_shopping_list_text(w_id, slots, "Meta Laser M4")
        self.assertIn("LISTA DE COMPRAS DE ARMERÍA", shop_txt)
        self.assertIn("Colt M4A1", shop_txt)
        self.assertIn("Costo Total", shop_txt)
        self.assertIn("Comerciantes Requeridos", shop_txt)

        # 3. Base64 Export & Import
        b64_code = export_build_to_base64(w_id, slots, "Meta Laser M4")
        self.assertTrue(b64_code.startswith("TTCBUILD:"))

        imported_b64 = import_build_from_base64(b64_code)
        self.assertIsNotNone(imported_b64)
        self.assertEqual(imported_b64["weapon_id"], "m4a1")
        self.assertEqual(imported_b64["slots"]["barrel"], slots["barrel"])

    def test_weapon_workbench_visual_compositor(self):
        # M4A1 Meta
        img_m4 = render_weapon_workbench_composite("m4a1", MODDABLE_WEAPONS["m4a1"]["presets"]["Meta Laser Recoil"], (680, 260))
        self.assertIsNotNone(img_m4)
        self.assertEqual(img_m4.size, (680, 260))

        # AK-74N Zenit
        img_ak = render_weapon_workbench_composite("ak74n", MODDABLE_WEAPONS["ak74n"]["presets"]["Meta Zenit B-30 / PT-3"], (680, 260))
        self.assertIsNotNone(img_ak)
        self.assertEqual(img_ak.size, (680, 260))


if __name__ == "__main__":
    unittest.main()
