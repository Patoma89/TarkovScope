"""Tests del Quest Tracker: dataset de rutas de tarkov.dev, proyección y planificador de rutas."""
import itertools
import os
import tempfile
import unittest

from core.quest_route_data import (
    build_route_dataset,
    get_tasks_for_map,
    load_route_dataset,
    normalize_quest_name,
    objective_label,
    prettify_extract_name,
    save_route_dataset,
    task_name_from_wiki_link,
    world_to_crs_pixel,
    world_to_image,
)
from core.quest_route_planner import Stop, distance, nearest_index, plan_route, rank_spawns


def _pos(x, z, y=0.0):
    return {"x": x, "y": y, "z": z}


def _fake_dumps():
    maps_raw = {"data": {"maps": {
        "m1": {
            "normalizedName": "customs",
            "spawns": [
                {"position": _pos(0, 0), "sides": ["pmc"], "categories": ["player"]},
                {"position": _pos(10, 5), "sides": ["pmc"], "categories": ["player"]},
                {"position": _pos(500, 0), "sides": ["all"], "categories": ["player", "bot"]},
                {"position": _pos(250, 250), "sides": ["scav"], "categories": ["player"]},
                {"position": _pos(300, 300), "sides": ["pmc"], "categories": ["boss"]},
            ],
            "extracts": [
                {"name": "ex_customs_pmc_zb1011", "faction": "pmc", "position": _pos(600, 0)},
                {"name": "ex_customs_scav_admin", "faction": "scav", "position": _pos(0, 600)},
                {"name": "ex_customs_secret_voron_boat", "faction": "pmc", "position": _pos(1, 1)},
                {"name": "ex_customs_coop_boiler", "faction": "shared", "position": _pos(-100, 0)},
            ],
        },
        "m2": {"normalizedName": "night-factory", "spawns": [], "extracts": []},
    }}}
    tasks_raw = {"data": {"tasks": {
        "t1": {
            "wikiLink": "https://escapefromtarkov.fandom.com/wiki/Saving_the_Mole",
            "trader": "54cb50c76803fa8b248b4571",
            "objectives": [
                {"type": "visit", "maps": ["m1"], "zones": [{"map": "m1", "position": _pos(100, 100)}]},
                {"type": "findQuestItem", "maps": ["m1"], "possibleLocations": [
                    {"map": "m1", "positions": [_pos(200, 0), _pos(200, 1), _pos(-300, 0)]},
                ]},
                {"type": "plantItem", "maps": ["m2"], "zones": [{"map": "m2", "position": _pos(5, 5)}]},
            ],
        },
        "t3": {
            "wikiLink": "https://escapefromtarkov.fandom.com/wiki/Saving_the_Mole",
            "factionName": "USEC",
            "objectives": [{"type": "visit", "maps": ["m1"], "zones": [{"map": "m1", "position": _pos(-400, -400)}]}],
        },
        "t2": {"wikiLink": "https://escapefromtarkov.fandom.com/wiki/Gunsmith_-_Part_1",
               "objectives": [{"type": "buildWeapon", "maps": []}]},
    }}}
    meta_raw = [
        {"normalizedName": "customs", "maps": [
            {"projection": "2D"},
            {"projection": "interactive", "transform": [0.239, 168.65, 0.239, 136.35],
             "coordinateRotation": 180, "bounds": [[698, -307], [-372, 237]], "tilePath": "t/{z}/{x}/{y}.png"},
        ]},
    ]
    return maps_raw, tasks_raw, meta_raw


class TestRouteDataset(unittest.TestCase):
    def setUp(self):
        self.ds = build_route_dataset(*_fake_dumps())

    def test_only_pmc_player_spawns_are_kept_and_clustered(self):
        spawns = self.ds["maps"]["customs"]["spawns"]
        # (0,0) y (10,5) forman un grupo; (500,0) "all" es otro; scav y boss quedan fuera.
        self.assertEqual(sorted(s["points"] for s in spawns), [1, 2])
        self.assertTrue(all(s["label"].startswith("Spawn ") for s in spawns))

    def test_extracts_exclude_scav_and_secret(self):
        names = [e["name"] for e in self.ds["maps"]["customs"]["extracts"]]
        self.assertEqual(sorted(names), ["Smuggler's Boat", "ZB-1011"])

    def test_tasks_resolve_name_trader_and_positions(self):
        task = self.ds["tasks"]["Saving the Mole"]
        self.assertEqual(task["trader"], "Prapor")
        customs = [o for o in task["objectives"] if o["map"] == "customs" and o["faction"] == "Any"]
        self.assertEqual(len(customs), 2)
        quest_item = next(o for o in customs if o["type"] == "findQuestItem")
        # Duplicados a < 3 m se fusionan: quedan 2 ubicaciones posibles.
        self.assertEqual(len(quest_item["candidates"]), 2)
        # Objetivo en Night Factory se asigna a la clave interna "factory".
        self.assertTrue(any(o["map"] == "factory" for o in task["objectives"]))

    def test_tasks_without_positions_are_skipped(self):
        self.assertNotIn("Gunsmith - Part 1", self.ds["tasks"])

    def test_faction_variants_are_filtered(self):
        def points(faction):
            task = get_tasks_for_map("customs", self.ds, faction)[0]
            return [c for o in task["objectives"] for c in o["candidates"]]
        usec_only = [-400.0, 0.0, -400.0]
        self.assertIn(usec_only, points("USEC"))
        self.assertNotIn(usec_only, points("BEAR"))

    def test_get_tasks_for_map_filters_objectives(self):
        tasks = get_tasks_for_map("customs", self.ds)
        self.assertEqual([t["name"] for t in tasks], ["Saving the Mole"])
        self.assertTrue(all(o["map"] == "customs" for o in tasks[0]["objectives"]))

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "routes.json")
            save_route_dataset(self.ds, path)
            loaded = load_route_dataset(path, force=True)
            self.assertEqual(set(loaded["tasks"]), set(self.ds["tasks"]))

    def test_helpers(self):
        self.assertEqual(task_name_from_wiki_link("https://x/wiki/Shooting_Cans"), "Shooting Cans")
        self.assertEqual(task_name_from_wiki_link("https://x/wiki/A_Fuel_Matter%3F"), "A Fuel Matter?")
        self.assertEqual(normalize_quest_name("Debut (BEAR)"), normalize_quest_name("debut"))
        self.assertEqual(prettify_extract_name("ex_interchange_pmc_sniper", "interchange"), "Sniper")
        self.assertEqual(prettify_extract_name("EXFIL_Bunker_D2", "reserve"), "D-2")
        self.assertIn("2 ubicaciones", objective_label({"type": "findQuestItem", "candidates": [1, 2]}))


class TestProjection(unittest.TestCase):
    META = {"transform": [0.239, 168.65, 0.239, 136.35], "coordinateRotation": 180}

    def test_matches_tarkov_dev_leaflet_formula(self):
        # rotación 180: (x, z) -> (-x, -z); luego (0.239*-x + 168.65, -0.239*-z + 136.35)
        px, py = world_to_crs_pixel(100.0, 50.0, self.META, 0)
        self.assertAlmostEqual(px, 0.239 * -100 + 168.65, places=6)
        self.assertAlmostEqual(py, 0.239 * 50 + 136.35, places=6)
        px2, py2 = world_to_crs_pixel(100.0, 50.0, self.META, 3)
        self.assertAlmostEqual(px2, px * 8, places=6)
        self.assertAlmostEqual(py2, py * 8, places=6)

    def test_world_to_image_subtracts_origin(self):
        calib = dict(self.META, zoom=2, origin_px=[100.0, 40.0])
        gx, gy = world_to_crs_pixel(10.0, -20.0, self.META, 2)
        ix, iy = world_to_image(10.0, -20.0, calib)
        self.assertAlmostEqual(ix, gx - 100.0)
        self.assertAlmostEqual(iy, gy - 40.0)


class TestPlanner(unittest.TestCase):
    def _brute_force(self, start, stops, extracts):
        best = float("inf")
        for perm in itertools.permutations(stops):
            for choice in itertools.product(*[range(len(s.candidates)) for s in perm]):
                cur, total = start, 0.0
                for s, ci in zip(perm, choice):
                    total += distance(cur, s.candidates[ci])
                    cur = s.candidates[ci]
                if extracts:
                    total += min(distance(cur, p) for _, p in extracts)
                best = min(best, total)
        return best

    def test_line_is_visited_in_order(self):
        stops = [Stop(str(i), f"S{i}", "Q", [(x, 0.0, 0.0)]) for i, x in enumerate([300, 100, 200])]
        plan = plan_route((0.0, 0.0, 0.0), stops, [("Far", (1000.0, 0.0, 0.0)), ("Near", (350.0, 0.0, 0.0))])
        self.assertEqual([leg.point[0] for leg in plan.stop_legs], [100, 200, 300])
        self.assertEqual(plan.extract_name, "Near")
        self.assertAlmostEqual(plan.total_distance, 350.0)

    def test_matches_brute_force_with_alternative_locations(self):
        start = (0.0, 0.0, 0.0)
        stops = [
            Stop("a", "A", "Q1", [(120.0, 0.0, 40.0), (-80.0, 0.0, 10.0)]),
            Stop("b", "B", "Q2", [(60.0, 3.0, -90.0)]),
            Stop("c", "C", "Q3", [(-150.0, 0.0, -60.0), (200.0, 0.0, 200.0)]),
            Stop("d", "D", "Q4", [(30.0, 8.0, 160.0)]),
        ]
        extracts = [("E1", (250.0, 0.0, 0.0)), ("E2", (-250.0, 0.0, 0.0))]
        plan = plan_route(start, stops, extracts)
        self.assertTrue(plan.exact)
        self.assertAlmostEqual(plan.total_distance, self._brute_force(start, stops, extracts), places=6)
        self.assertEqual(len(plan.stop_legs), 4)
        self.assertEqual(plan.legs[-1].stop, None)

    def test_heuristic_used_for_many_stops_and_visits_all(self):
        stops = [Stop(str(i), str(i), "Q", [(float(i * 37 % 500), 0.0, float(i * 91 % 400))]) for i in range(15)]
        plan = plan_route((0.0, 0.0, 0.0), stops, [("E", (0.0, 0.0, 500.0))])
        self.assertFalse(plan.exact)
        self.assertEqual(sorted(leg.stop.key for leg in plan.stop_legs), sorted(s.key for s in stops))

    def test_no_stops_goes_straight_to_extract(self):
        plan = plan_route((0.0, 0.0, 0.0), [], [("E", (30.0, 0.0, 40.0))])
        self.assertAlmostEqual(plan.total_distance, 50.0)
        self.assertEqual(plan.extract_name, "E")

    def test_rank_spawns_prefers_closer_spawn(self):
        stops = [Stop("a", "A", "Q", [(500.0, 0.0, 0.0)])]
        ranking = rank_spawns([("Lejos", (0.0, 0.0, 0.0)), ("Cerca", (450.0, 0.0, 0.0))], stops)
        self.assertEqual(ranking[0][0], "Cerca")

    def test_nearest_index(self):
        pts = [(0.0, 0.0, 0.0), (100.0, 0.0, 100.0)]
        self.assertEqual(nearest_index((90.0, 95.0), pts), 1)
        self.assertEqual(nearest_index((0.0, 0.0), []), -1)


if __name__ == "__main__":
    unittest.main()
