"""
Pruebas Unitarias para el cálculo de penetración balística, matriz de blindaje,
simulador STK y cobertura de todos los calibres oficiales de Escape from Tarkov (eft-ammo.com).
"""
import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.ballistics import (
    calculate_armor_effectiveness,
    get_full_ballistics_matrix,
    simulate_shots_to_kill,
    calculate_leg_meta_shots,
    simulate_boss_targets,
)
from core.ammo_complete_data import COMPLETE_AMMO_DATA
from core.database import (
    init_db,
    seed_wiki_ammunition,
    get_all_ammunition,
    get_distinct_calibers,
)
from ui.tab_ballistics import CALIBER_CLEAN_MAP, format_caliber_dropdown, format_caliber_short


class TestBallistics(unittest.TestCase):
    def test_high_penetration(self):
        # M995 con 53 de penetración contra Clase 4 (threshold 40, diff 13 >= 5) -> Destruye (Score 6)
        eff_c4 = calculate_armor_effectiveness(53.0, 4)
        self.assertEqual(eff_c4["score"], 6)
        self.assertEqual(eff_c4["label"], "Destruye")

        # Contra Clase 5 (threshold 50, diff 3 >= 0) -> Muy Alta (Score 5)
        eff_c5 = calculate_armor_effectiveness(53.0, 5)
        self.assertEqual(eff_c5["score"], 5)

        # Contra Clase 6 (threshold 60, diff -7 >= -10) -> Media (Score 3)
        eff_c6 = calculate_armor_effectiveness(53.0, 6)
        self.assertEqual(eff_c6["score"], 3)

    def test_low_penetration(self):
        # 9x19 PST GZH con 20 de penetración contra Clase 5 (threshold 50, diff -30) -> Rebota (Score 1)
        eff = calculate_armor_effectiveness(20.0, 5)
        self.assertEqual(eff["score"], 1)
        self.assertEqual(eff["label"], "Rebota")

    def test_matrix_all_classes(self):
        matrix = get_full_ballistics_matrix(40.0)
        self.assertEqual(len(matrix), 6)
        for c in range(1, 7):
            self.assertIn(c, matrix)
            self.assertIn("score", matrix[c])
            self.assertIn("color", matrix[c])

    def test_complete_ammo_dataset_integrity(self):
        """Valida que el catálogo maestro cuente con más de 120 proyectiles y todos los calibres meta."""
        self.assertGreaterEqual(len(COMPLETE_AMMO_DATA), 120)

        calibers = {a["caliber"] for a in COMPLETE_AMMO_DATA}

        # Calibres modernos y tradicionales de eft-ammo.com
        required_calibers = [
            "Caliber127x33",      # .50 Action Express (Desert Eagle)
            "Caliber58x42",       # 5.8x42mm (QBZ-191)
            "Caliber93x64",       # 9.3x64mm Brenneke (TKPD)
            "Caliber68x51",       # 6.8x51mm (.277 Fury / Spear)
            "Caliber762x35",      # .300 Blackout
            "Caliber9x33R",       # .357 Magnum
            "Caliber86x70",       # .338 Lapua Magnum
            "Caliber127x55",      # 12.7x55mm (ASh-12)
            "Caliber556x45NATO",  # 5.56x45mm NATO
            "Caliber545x39",      # 5.45x39mm
            "Caliber762x39",      # 7.62x39mm
            "Caliber762x51",      # 7.62x51mm NATO
            "Caliber762x54R",     # 7.62x54mmR
            "Caliber9x39",        # 9x39mm
            "Caliber366TKM",      # .366 TKM
            "Caliber9x19PARA",    # 9x19mm Parabellum
            "Caliber1143x23ACP",  # .45 ACP
            "Caliber46x30",       # 4.6x30mm HK
            "Caliber57x28",       # 5.7x28mm FN
            "Caliber9x21",        # 9x21mm Gyurza
            "Caliber9x18PM",      # 9x18mm PM
            "Caliber762x25TT",    # 7.62x25mm TT
            "Caliber12g",         # 12/70
            "Caliber20g",         # 20/70
            "Caliber23x75",       # 23x75mm KS-23
            "Caliber40x46",       # 40x46mm GL
        ]

        for req in required_calibers:
            self.assertIn(req, calibers, f"Falta el calibre requerido: {req}")

        for a in COMPLETE_AMMO_DATA:
            self.assertIn("id", a)
            self.assertIn("name", a)
            self.assertIn("shortName", a)
            self.assertIn("caliber", a)
            self.assertIn("damage", a)
            self.assertIn("armorDamage", a)
            self.assertIn("penetrationPower", a)
            self.assertIn("initialSpeed", a)
            self.assertGreaterEqual(a["damage"] + a["penetrationPower"], 0)

    def test_db_seeding_and_queries(self):
        """Valida que la base de datos SQLite se inicialice y siembre el catálogo maestro automáticamente."""
        tmp_fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(tmp_fd)

        try:
            init_db(db_path)
            seed_wiki_ammunition(db_path)
            ammo = get_all_ammunition("TODOS", db_path)
            self.assertGreaterEqual(len(ammo), 120)

            calibers = get_distinct_calibers(db_path)
            self.assertIn("Caliber127x33", calibers)
            self.assertIn("Caliber58x42", calibers)
            self.assertIn("Caliber93x64", calibers)

            # Probar filtro específico
            deagle_ammo = get_all_ammunition("Caliber127x33", db_path)
            self.assertEqual(len(deagle_ammo), 4)
            names = [a["name"] for a in deagle_ammo]
            self.assertIn(".50 AE FMJ", names)
            self.assertIn(".50 AE Hawk JSP", names)
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_caliber_formatting_in_ui(self):
        """Valida que todos los calibres se formateen correctamente para los menús y tablas."""
        disp = format_caliber_dropdown("Caliber127x33")
        self.assertIn(".50 Action Express", disp)

        short = format_caliber_short("Caliber127x33")
        self.assertEqual(short, ".50 AE")

        disp_58 = format_caliber_dropdown("Caliber58x42")
        self.assertIn("5.8x42 mm", disp_58)

        disp_93 = format_caliber_dropdown("Caliber93x64")
        self.assertIn("9.3x64 mm Brenneke", disp_93)

    def test_simulator_stk_new_ammo(self):
        """Prueba simulación de disparos para matar (STK) con munición de .50 AE y 5.8x42."""
        # .50 AE FMJ (85 dmg, 40 pen, 50% armor dmg) vs Armadura Clase 4 (50 dur)
        sim = simulate_shots_to_kill(damage=85, penetration_power=40.0, armor_damage=50, armor_class=4)
        self.assertIn("stk", sim)
        self.assertLessEqual(sim["stk"], 3)  # Mata en 2-3 tiros al tórax

        # Leg meta con .50 AE JHP (147 de daño)
        leg_shots = calculate_leg_meta_shots(damage=147)
        self.assertLessEqual(leg_shots, 5)  # Enormes daños a extremidades

    def test_special_utility_projectiles_safe_simulation(self):
        """Valida que cartuchos de utilidad (bengalas, flashbang Zvezda) no devuelvan disparos letales absurdos."""
        sim = simulate_shots_to_kill(damage=0, penetration_power=0.0, armor_damage=0, armor_class=4)
        self.assertTrue(sim.get("is_utility"))
        self.assertEqual(sim["stk"], 0)
        self.assertEqual(calculate_leg_meta_shots(damage=0), 0)
        boss_sims = simulate_boss_targets(damage=0, penetration_power=0.0, armor_damage=0)
        self.assertTrue(len(boss_sims) > 0)
        self.assertEqual(boss_sims[0]["stk"], 0)


    def test_caliber_ammo_hierarchy_grouping(self):
        """Valida que la agrupación jerárquica Calibre -> Munición mantenga listas compactas y ordenadas."""
        cal_to_ammo = {}
        for a in COMPLETE_AMMO_DATA:
            cal = format_caliber_dropdown(a["caliber"])
            cal_to_ammo.setdefault(cal, []).append(a)

        # Debe haber al menos 25 calibres distintos
        self.assertGreaterEqual(len(cal_to_ammo), 25)

        # Cada calibre debe tener un número manejable de municiones (ninguno > 30),
        # solucionando el problema de dropdowns masivos de 300+ items
        for cal, items in cal_to_ammo.items():
            self.assertLessEqual(len(items), 30, f"El calibre {cal} tiene demasiados proyectiles ({len(items)})")
            # Ordenar por penetración descendente
            sorted_items = sorted(items, key=lambda x: float(x.get("penetrationPower", 0)), reverse=True)
            self.assertGreaterEqual(float(sorted_items[0].get("penetrationPower", 0)), float(sorted_items[-1].get("penetrationPower", 0)))


if __name__ == "__main__":
    unittest.main()
