"""Tests unitarios para el módulo de Medicina & Stims (core/medical_data.py)."""
import unittest

from core.medical_data import (
    MEDICAL_CATALOG,
    filter_medical_items,
    get_medical_categories,
    get_medical_icon_path,
    get_symptom_filters,
)


class TestMedicalData(unittest.TestCase):
    def test_catalog_and_icons_complete(self):
        self.assertEqual(len(MEDICAL_CATALOG), 43)
        ids = [m["id"] for m in MEDICAL_CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("Todas", get_medical_categories())
        self.assertTrue(any(k == "heavy_bleed" for k, _ in get_symptom_filters()))
        missing_icons = [m["id"] for m in MEDICAL_CATALOG if not get_medical_icon_path(m["id"])]
        self.assertEqual(missing_icons, [])

    def test_filters(self):
        stims = filter_medical_items(category="Estimulantes (Stims)")
        self.assertEqual(len(stims), 22)
        heavy = filter_medical_items(symptom="heavy_bleed")
        self.assertTrue(any(m["id"] == "calok_b_hemostatic_applicator" for m in heavy))
        sj6 = filter_medical_items(query="SJ6")
        self.assertTrue(any(m["id"] == "sj6_tglabs_combat_stimulant_injector" for m in sj6))


if __name__ == "__main__":
    unittest.main()
