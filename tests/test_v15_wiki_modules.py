"""
Pruebas Unitarias para los módulos Wiki Total Edition (v1.5.0):
  - Prestige & Arena/Ref Sync
  - Achievements Tracker & Persistencia + Perfil Export/Import
  - Tactical Clothing (USEC/BEAR/Ref)
  - Provisions & Health Status Effects
  - AI Factions (Rogues, Raiders, Cultists, Black Division, RUAF, Scavs)
  - Weapon Malfunctions & Durability / Repair Kits
  - Búsqueda Global (Ctrl+K) y Aislamiento de Capa core/
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ai_factions_data import AI_FACTIONS_CATALOG
from core.database import init_db
from core.datastore import DataStore
from core.gear_cache import get_gear_icon_path
from core.hideout_crafts_data import HIDEOUT_CRAFTS_DATA, HIDEOUT_STATION_ICONS
from core.weapons_data import KAPPA_COLLECTOR_ITEMS
from core.pmc_prestige_achievements_data import (
    ACHIEVEMENTS_CATALOG,
    ARENA_REF_SYNC_GUIDE,
    PRESTIGE_LEVELS_DATA,
    PRESTIGE_RESET_MATRIX,
    TACTICAL_CLOTHING_CATALOG,
    filter_achievements,
    filter_tactical_clothing,
)
from core.provisions_health_data import (
    HEALTH_EFFECTS_CATALOG,
    PROVISIONS_CATALOG,
    filter_provisions,
)
from core.user_data import (
    export_user_profile,
    get_prestige_level,
    get_unlocked_achievement_ids,
    import_user_profile,
    set_prestige_level,
    toggle_achievement_unlocked,
)
from core.weapon_malfunctions_data import (
    DURABILITY_AND_REPAIR_GUIDE,
    WEAPON_MALFUNCTIONS_CATALOG,
)


class TestV15CoreIsolation(unittest.TestCase):
    def test_v15_core_modules_never_import_tkinter(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        modules = [
            "core/pmc_prestige_achievements_data.py",
            "core/provisions_health_data.py",
            "core/ai_factions_data.py",
            "core/weapon_malfunctions_data.py",
        ]
        for rel in modules:
            full = os.path.join(repo_root, rel)
            with open(full, "r", encoding="utf-8") as f:
                src = f.read().lower()
            self.assertNotIn("import tkinter", src, f"{rel} importa tkinter")
            self.assertNotIn("import customtkinter", src, f"{rel} importa customtkinter")


class TestV15DataCatalogs(unittest.TestCase):
    def test_prestige_and_arena_integrity(self):
        self.assertEqual(len(PRESTIGE_LEVELS_DATA), 6)
        for p in PRESTIGE_LEVELS_DATA:
            self.assertIn("icon_key", p)
            self.assertIsNotNone(get_gear_icon_path(p["icon_key"]), f"Falta ícono Prestige: {p['icon_key']}")
        self.assertGreaterEqual(len(PRESTIGE_RESET_MATRIX["kept"]), 5)
        self.assertGreaterEqual(len(PRESTIGE_RESET_MATRIX["reset"]), 5)
        self.assertGreaterEqual(len(ARENA_REF_SYNC_GUIDE), 4)

    def test_cached_thumbnails_for_provisions_and_clothing(self):
        for p in PROVISIONS_CATALOG:
            self.assertIn("icon_key", p)
            self.assertIsNotNone(get_gear_icon_path(p["icon_key"]), f"Falta ícono provisión: {p['id']}")
        for c in TACTICAL_CLOTHING_CATALOG:
            self.assertIn("icon_key", c)
            self.assertIsNotNone(get_gear_icon_path(c["icon_key"]), f"Falta ícono ropa: {c['id']}")

    def test_kappa_collector_44_wiki_items_and_icons(self):
        self.assertEqual(len(KAPPA_COLLECTOR_ITEMS), 44)
        names = {it["name"] for it in KAPPA_COLLECTOR_ITEMS}
        for retired in ("Old Firesteel", "Kotton Beanie", "Can of Sprats", "Evasion Armband", "Golden Rooster Figurine"):
            self.assertNotIn(retired, names, f"Ítem discontinuado presente en Collector: {retired}")
        for it in KAPPA_COLLECTOR_ITEMS:
            self.assertIn("icon_key", it)
            self.assertIsNotNone(get_gear_icon_path(it["icon_key"]), f"Falta ícono Kappa: {it['name']}")
        self.assertEqual(len(HIDEOUT_STATION_ICONS), 27)
        for st_name, info in HIDEOUT_STATION_ICONS.items():
            self.assertIsNotNone(get_gear_icon_path(info["icon_key"]), f"Falta ícono Hideout: {st_name}")
        for cr in HIDEOUT_CRAFTS_DATA:
            self.assertIn("icon_key", cr)
            self.assertIsNotNone(get_gear_icon_path(cr["icon_key"]), f"Falta ícono Craft: {cr['output']}")

    def test_achievements_and_clothing_filters(self):
        self.assertGreaterEqual(len(ACHIEVEMENTS_CATALOG), 28)
        boss_achs = filter_achievements(category="Bosses")
        self.assertGreaterEqual(len(boss_achs), 8)
        self.assertTrue(all(a["category"] == "Bosses" for a in boss_achs))

        killa = filter_achievements(query="Stylish One")
        self.assertIn("ach_stylish_one", {a["id"] for a in killa})

        missing = filter_achievements(only_missing=True, unlocked_ids={"ach_stylish_one"})
        self.assertNotIn("ach_stylish_one", {a["id"] for a in missing})

        self.assertGreaterEqual(len(TACTICAL_CLOTHING_CATALOG), 20)
        usec_upper = filter_tactical_clothing(faction="USEC", slot="Superior (Upper)")
        self.assertGreaterEqual(len(usec_upper), 5)
        self.assertTrue(all(c["faction"] == "USEC" and c["slot"] == "Superior (Upper)" for c in usec_upper))

    def test_provisions_and_health_effects(self):
        self.assertEqual(len(PROVISIONS_CATALOG), 45)
        self.assertGreaterEqual(len(HEALTH_EFFECTS_CATALOG), 12)

        names = {p["name"] for p in PROVISIONS_CATALOG}
        for required_name in (
            "Can of GigaBeef meat",
            "Salty Dog beef sausage",
            "Pack of instant noodles",
            "Can of green peas",
            "Bottle of water (0.6L)",
            "Can of Ice Green tea",
            "Pack of Tarker dried meat",
        ):
            self.assertIn(required_name, names, f"Falta provisión oficial: {required_name}")

        drinks = filter_provisions(category="Bebida")
        self.assertGreaterEqual(len(drinks), 6)
        moon = filter_provisions(query="Moonshine")
        moon_item = next((p for p in moon if p["id"] == "prov_moonshine"), None)
        self.assertIsNotNone(moon_item)
        self.assertLess(moon_item["hydration"], 0)

        fir_items = filter_provisions(only_fir=True)
        self.assertGreaterEqual(len(fir_items), 10)

    def test_ai_factions_and_malfunctions(self):
        self.assertEqual(len(AI_FACTIONS_CATALOG), 6)
        ids = {f["id"] for f in AI_FACTIONS_CATALOG}
        self.assertIn("faction_rogues", ids)
        self.assertIn("faction_raiders", ids)
        self.assertIn("faction_cultists", ids)
        self.assertIn("faction_black_division", ids)
        self.assertIn("faction_ruaf_pmc", ids)
        self.assertNotIn("faction_bloodhounds", ids)

        self.assertEqual(len(WEAPON_MALFUNCTIONS_CATALOG), 5)
        self.assertIn("93%", DURABILITY_AND_REPAIR_GUIDE["threshold_93_desc_es"])
        self.assertEqual(len(DURABILITY_AND_REPAIR_GUIDE["overheat_stages"]), 4)
        self.assertGreaterEqual(len(DURABILITY_AND_REPAIR_GUIDE["repair_kits_guide"]), 3)


class TestV15PersistenceAndSearch(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        init_db(self.db_path)

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_achievements_and_prestige_persistence_roundtrip(self):
        self.assertEqual(get_unlocked_achievement_ids(self.db_path), set())
        self.assertTrue(toggle_achievement_unlocked("ach_killer7", self.db_path))
        self.assertIn("ach_killer7", get_unlocked_achievement_ids(self.db_path))
        self.assertFalse(toggle_achievement_unlocked("ach_killer7", self.db_path))
        self.assertNotIn("ach_killer7", get_unlocked_achievement_ids(self.db_path))

        toggle_achievement_unlocked("ach_snowball", self.db_path)
        self.assertEqual(set_prestige_level(6, self.db_path), 6)
        self.assertEqual(set_prestige_level(99, self.db_path), 6)
        self.assertEqual(get_prestige_level(self.db_path), 6)

        backup = export_user_profile(self.db_path)
        self.assertIn("ach_snowball", backup.get("unlocked_achievements", []))
        self.assertEqual(backup.get("prestige_level"), 6)

        # Import into clean DB
        fd2, db2 = tempfile.mkstemp(suffix=".db")
        os.close(fd2)
        try:
            init_db(db2)
            self.assertTrue(import_user_profile(backup, db2))
            self.assertIn("ach_snowball", get_unlocked_achievement_ids(db2))
            self.assertEqual(get_prestige_level(db2), 6)
        finally:
            if os.path.exists(db2):
                os.remove(db2)

    def test_global_search_indexes_v15_modules(self):
        ds = DataStore(self.db_path)
        ds.ensure_loaded()

        self.assertTrue(any(r["target"] == "ACH:Killer7" for r in ds.global_search("Killer7")))
        self.assertTrue(any(r["target"] == "PROV:Moonshine" for r in ds.global_search("Moonshine")))
        self.assertTrue(any(r["target"] == "FACTION:faction_rogues" for r in ds.global_search("Rogues")))
        self.assertTrue(any(r["target"] == "MALFUNCTION:malf_misfire" for r in ds.global_search("Misfire")))
        self.assertTrue(any(r["target"] == "PRESTIGE:" for r in ds.global_search("Prestige")))


class TestModernUIAndTarkovTime(unittest.TestCase):
    def test_tarkov_time_module_is_ui_free_and_12h_offset(self):
        import re
        from core import tarkov_time

        with open(tarkov_time.__file__, encoding="utf-8") as fh:
            src = fh.read()
        self.assertNotIn("tkinter", src)
        self.assertNotIn("customtkinter", src)

        clock_re = re.compile(r"^\d{2}:\d{2}:\d{2}$")
        for sample_ts in (0.0, 1700000000.0, 1730001234.567):
            res = tarkov_time.get_tarkov_raid_times(sample_ts)
            self.assertRegex(res["left_time"], clock_re)
            self.assertRegex(res["right_time"], clock_re)
            self.assertEqual((res["left_hour"] + 12) % 24, res["right_hour"])
            self.assertEqual(res["left_minute"], res["right_minute"])
            self.assertEqual(res["left_second"], res["right_second"])
            expected_left_night = res["left_hour"] >= 22 or res["left_hour"] < 7
            expected_right_night = res["right_hour"] >= 22 or res["right_hour"] < 7
            self.assertEqual(res["left_is_night"], expected_left_night)
            self.assertEqual(res["right_is_night"], expected_right_night)
            self.assertEqual(res["cultists_window_active"], expected_left_night or expected_right_night)

    def test_six_skins_registered_and_unique_hex_palettes(self):
        import re
        from core import config
        from ui import theme

        self.assertEqual(
            set(config.THEME_SKINS.keys()),
            {
                "tarkov_classic",
                "labs_nvg",
                "tactical_slate",
                "modern_obsidian",
                "terragroup_clean",
                "halloween_cultist",
            },
        )
        hex_re = re.compile(r"^#[0-9A-Fa-f]{6}$")
        orig = theme.get_active_skin_id()
        try:
            for skin_id in config.THEME_SKINS:
                theme.apply_ui_skin(skin_id)
                c_names = [n for n in dir(theme) if n.startswith("C_")]
                vals = [getattr(theme, n).upper() for n in c_names]
                for n in c_names:
                    self.assertRegex(getattr(theme, n), hex_re, f"{skin_id}.{n}")
                self.assertEqual(len(vals), len(set(vals)), f"Duplicated C_* hex in {skin_id}")
        finally:
            theme.apply_ui_skin(orig)

    def test_dual_ui_font_and_bind_card_hover(self):
        import customtkinter as ctk
        from ui import theme

        root = ctk.CTk()
        root.withdraw()
        try:
            f_disp = theme.ui_font(18, "bold", display=True)
            f_body = theme.ui_font(12, "normal")
            self.assertEqual(f_disp.cget("family"), theme.TARKOV_FONT_FAMILY)
            self.assertEqual(f_body.cget("family"), "Segoe UI")

            card = ctk.CTkFrame(root, border_width=1, border_color=theme.C_BORDER_SOFT)
            theme.bind_card_hover(
                card,
                normal_border=theme.C_BORDER_SOFT,
                hover_border="#D4B886",
            )
            card.event_generate("<Enter>")
        finally:
            try:
                root.destroy()
            except Exception:
                pass


if __name__ == "__main__":
    unittest.main()
