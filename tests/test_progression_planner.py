"""Tests del planner de niveles de trader y del parser de progresión de la wiki."""
import unittest

from core.quest_route_data import normalize_quest_name
from core.progression_planner import (
    ANYWHERE,
    PlannerState,
    build_raid_plan,
    estimate_reputation,
    level_requirements,
    loyalty_level,
    select_quests,
)
from core.wiki_progression import (
    merge_progression,
    parse_infobox,
    parse_previous,
    parse_quest_page,
    parse_reputation,
)

PAGE = """{{Infobox quest
|image           =X.png
|given by        =[[Prapor]]
|location        =[[Customs]]
|LL requirement  =2
|LL quests       =3
|previous        =[[First in Line]]<br/>or<br/>[[Supply Plans]]
|reqkappa        =Yes
}}
==Rewards==
* +3,000 [[EXP]]
* [[Prapor]] Rep <font color="green">'''+0.15'''</font>
* [[Fence]] Rep <font color="red">'''−0.2'''</font>
==Guide==
* [[Skier]] Rep +9 (esto está en la guía y no cuenta)
"""


def _obj(index, maps, raid=True, typ="visit"):
    return {"index": index, "type": typ, "maps": maps, "raid": raid}


def _progression():
    """Prapor: LL2 pide 0.5 de rep. Quest 'gate' (LL2) pide 1 quest de LL2 ya completada."""
    def q(name, ll=1, ll_quests=0, prev=(), rep=0.0, objs=None, faction="Any", trader="Prapor"):
        return {"id": name, "name": name, "trader": trader, "faction": faction, "ll": ll,
                "ll_quests": ll_quests, "prev": [list(g) for g in prev],
                "standing": {trader: rep} if rep else {}, "objectives": objs or [_obj(0, ["customs"])]}

    tasks = [
        q("a", rep=0.1, objs=[_obj(0, ["customs"])]),
        q("b", rep=0.1, objs=[_obj(0, ["woods"])]),
        q("c", rep=0.3, prev=[["a"]], objs=[_obj(0, ["customs"]), _obj(1, [], raid=False, typ="giveItem")]),
        q("d", rep=0.05, objs=[_obj(0, ["customs"])]),
        q("usec_only", rep=5.0, faction="USEC"),
        q("gate", ll=2, ll_quests=1, rep=1.0, objs=[_obj(0, ["woods"]), _obj(1, ["customs"])]),
        q("big_ll2", ll=2, rep=2.0, objs=[_obj(0, [])]),
        q("skier1", rep=0.4, trader="Skier", objs=[_obj(0, ["customs"])]),
    ]
    return {
        "traders": {
            "Prapor": {"levels": [{"level": 1, "player_level": 0, "reputation": 0.0},
                                  {"level": 2, "player_level": 6, "reputation": 0.5},
                                  {"level": 3, "player_level": 20, "reputation": 1.4}]},
            "Skier": {"levels": [{"level": 1, "player_level": 0, "reputation": 0.0},
                                 {"level": 2, "player_level": 7, "reputation": 0.4}]},
        },
        "tasks": {t["id"]: t for t in tasks},
    }


class TestWikiParser(unittest.TestCase):
    def test_infobox_and_page(self):
        box = parse_infobox(PAGE)
        self.assertEqual(box["ll requirement"], "2")
        page = parse_quest_page("Test Quest", PAGE)
        self.assertEqual(page["trader"], "Prapor")
        self.assertEqual((page["ll"], page["ll_quests"]), (2, 3))
        self.assertEqual(page["previous"], [["First in Line", "Supply Plans"]])
        self.assertTrue(page["kappa"])

    def test_reputation_only_from_rewards_section(self):
        self.assertEqual(parse_reputation(PAGE), {"Prapor": 0.15, "Fence": -0.2})

    def test_previous_and_vs_or(self):
        self.assertEqual(parse_previous("[[A]]<br/>[[B]]"), [["A"], ["B"]])
        self.assertEqual(parse_previous("[[A]]<br/>or<br/>[[B|bee]]"), [["A", "B"]])
        self.assertEqual(parse_previous(""), [])

    def test_missing_infobox(self):
        self.assertIsNone(parse_quest_page("Nada", "texto sin infobox"))

    def test_merge_maps_names_to_ids_including_faction_variants(self):
        tdev = {"traders": {}, "tasks": {
            "id1": {"name": "Test Quest", "trader": "Prapor", "requires": [], "trader_reqs": [], "standing": {}},
            "id2": {"name": "First in Line", "trader": "Therapist", "requires": [], "trader_reqs": [], "standing": {}},
            "id3a": {"name": "Supply Plans", "trader": "Therapist", "requires": [], "trader_reqs": [], "standing": {}},
            "id3b": {"name": "Supply Plans", "trader": "Therapist", "requires": [], "trader_reqs": [], "standing": {}},
            "id4": {"name": "Sin Wiki", "trader": "Skier", "requires": ["id2"],
                    "trader_reqs": [{"trader": "Skier", "level": 3}], "standing": {"Skier": 0.2}},
        }}
        merged, stats = merge_progression(tdev, {"Test Quest": PAGE}, normalize_quest_name)
        t1 = merged["tasks"]["id1"]
        self.assertEqual(t1["ll"], 2)
        self.assertEqual(sorted(t1["prev"][0]), ["id2", "id3a", "id3b"])
        self.assertEqual(t1["standing"]["Prapor"], 0.15)
        t4 = merged["tasks"]["id4"]
        self.assertEqual((t4["ll"], t4["prev"], t4["source"]), (3, [["id2"]], "tarkov.dev"))
        self.assertEqual(stats["wiki"], 1)


class TestLevels(unittest.TestCase):
    def test_loyalty_level(self):
        p = _progression()
        self.assertEqual(loyalty_level(p, "Prapor", 0.6, 10), 2)
        self.assertEqual(loyalty_level(p, "Prapor", 0.6, 3), 1)  # falta nivel de jugador
        self.assertEqual(loyalty_level(p, "Prapor", 2.0, 30), 3)
        self.assertEqual(level_requirements(p, "Prapor", 3), (1.4, 20))

    def test_estimate_reputation(self):
        self.assertAlmostEqual(estimate_reputation(_progression(), ["a", "c"])["Prapor"], 0.4)


class TestSelection(unittest.TestCase):
    def test_reaches_ll2_with_fewest_quests(self):
        sel = select_quests(_progression(), [("Prapor", 2)], PlannerState(faction="BEAR"))
        # a + c (0.4) no alcanza; a + c + b = 0.5 con 3 quests; d es peor que b.
        self.assertEqual(sorted(sel.task_ids), ["a", "b", "c"])
        self.assertTrue(sel.targets[0].reachable)
        self.assertNotIn("usec_only", sel.task_ids)

    def test_faction_specific_quest_is_used_by_its_faction(self):
        sel = select_quests(_progression(), [("Prapor", 2)], PlannerState(faction="USEC"))
        self.assertEqual(sel.task_ids, ["usec_only"])

    def test_ll_gate_and_ll_quests_count_unlock_higher_tier(self):
        sel = select_quests(_progression(), [("Prapor", 3)], PlannerState(player_level=30, faction="BEAR"))
        ids = sel.task_ids
        self.assertTrue(sel.targets[0].reachable)
        self.assertIn("big_ll2", ids)
        # Toda quest de LL2 aparece después de llegar a 0.5 de reputación con quests de LL1.
        first_ll2 = min(ids.index(t) for t in ids if t in ("gate", "big_ll2"))
        rep_before = sum(_progression()["tasks"][t]["standing"].get("Prapor", 0) for t in ids[:first_ll2])
        self.assertGreaterEqual(rep_before + 1e-9, 0.5)

    def test_prerequisite_comes_first(self):
        sel = select_quests(_progression(), [("Prapor", 2)], PlannerState(faction="BEAR"))
        self.assertLess(sel.task_ids.index("a"), sel.task_ids.index("c"))

    def test_already_met_and_completed_quests(self):
        state = PlannerState(faction="BEAR", completed={"a", "c"}, reputation={"Prapor": 0.6})
        sel = select_quests(_progression(), [("Prapor", 2)], state)
        self.assertEqual(sel.task_ids, [])
        self.assertTrue(sel.targets[0].already_met)

    def test_prefer_keeps_previous_choice_on_ties(self):
        p = _progression()
        p["tasks"]["d"]["standing"] = {"Prapor": 0.1}  # d empata con b
        default = select_quests(p, [("Prapor", 2)], PlannerState(faction="BEAR"))
        other = "d" if "b" in default.task_ids else "b"
        kept = select_quests(p, [("Prapor", 2)], PlannerState(faction="BEAR"), prefer=["a", "c", other])
        self.assertIn(other, kept.task_ids)

    def test_player_level_warning(self):
        sel = select_quests(_progression(), [("Prapor", 3)], PlannerState(player_level=5, faction="BEAR"))
        self.assertIn(("Prapor", 3, 20), sel.level_warnings)

    def test_multiple_traders_combined(self):
        sel = select_quests(_progression(), [("Prapor", 2), ("Skier", 2)], PlannerState(faction="BEAR"))
        self.assertIn("skier1", sel.task_ids)
        self.assertTrue(all(t.reachable for t in sel.targets))


class TestRaidPlan(unittest.TestCase):
    def test_groups_by_map_and_respects_unlocks(self):
        p = _progression()
        plan = build_raid_plan(p, ["a", "b", "c", "d"], faction="BEAR")
        self.assertEqual(plan.raids[0].map_key, "customs")
        first = {t.task_id for t in plan.raids[0].tasks}
        self.assertEqual(first, {"a", "d"})  # c necesita a terminada antes
        all_tasks = [t.task_id for r in plan.raids for t in r.tasks]
        self.assertEqual(sorted(set(all_tasks)), ["a", "b", "c", "d"])
        self.assertEqual(plan.blocked, [])
        self.assertEqual([tid for tid, _ in plan.offraid], ["c"])

    def test_multi_map_quest_spans_raids(self):
        p = _progression()
        plan = build_raid_plan(p, ["gate"], completed=["a", "b", "big_ll2"], faction="BEAR",
                               reputation={"Prapor": 0.5})
        maps = [r.map_key for r in plan.raids]
        self.assertEqual(sorted(maps), ["customs", "woods"])
        self.assertTrue(plan.raids[-1].tasks[0].finishes)
        self.assertFalse(plan.raids[0].tasks[0].finishes)

    def test_done_objectives_are_skipped(self):
        p = _progression()
        plan = build_raid_plan(p, ["gate"], completed=["a", "b", "big_ll2"], faction="BEAR",
                               reputation={"Prapor": 0.5}, done_objectives={"gate#0"})
        self.assertEqual([r.map_key for r in plan.raids], ["customs"])
        self.assertTrue(plan.raids[0].tasks[0].finishes)

    def test_anywhere_objectives(self):
        p = _progression()
        plan = build_raid_plan(p, ["big_ll2"], faction="BEAR", reputation={"Prapor": 0.5})
        self.assertEqual(plan.raids[0].map_key, ANYWHERE)

    def test_locked_quest_is_reported_blocked(self):
        plan = build_raid_plan(_progression(), ["gate"], faction="BEAR")  # sin rep ni quests de LL2
        self.assertEqual(plan.blocked, ["gate"])
        self.assertEqual(plan.raids, [])


if __name__ == "__main__":
    unittest.main()


class TestRequiredQuestsAndGoals(unittest.TestCase):
    def test_required_quest_pulls_prerequisites(self):
        sel = select_quests(_progression(), [], PlannerState(faction="BEAR"), required=[["c"]])
        self.assertEqual(sel.task_ids, ["a", "c"])
        self.assertEqual(sel.required, [("c", True)])

    def test_required_quest_adds_implicit_reputation_target(self):
        # 'gate' es LL2: el motor tiene que juntar 0.5 de rep con Prapor y hacer 1 quest de LL2 antes.
        sel = select_quests(_progression(), [], PlannerState(faction="BEAR"), required=[["gate"]])
        self.assertEqual(sel.required, [("gate", True)])
        self.assertEqual(sel.task_ids[-1], "gate")
        self.assertIn("big_ll2", sel.task_ids)

    def test_required_group_accepts_any_variant(self):
        sel = select_quests(_progression(), [], PlannerState(faction="USEC"), required=[["usec_only", "a"]])
        self.assertEqual(len(sel.task_ids), 1)

    def test_unreachable_required_is_reported(self):
        sel = select_quests(_progression(), [], PlannerState(faction="BEAR"), required=[["usec_only"]])
        self.assertEqual(sel.required, [("usec_only", False)])

    def test_resolve_goals(self):
        from core.progression_goals import resolve_goals
        p = _progression()
        p["goals"] = {
            "kappa": {"quest": "Collector", "traders": ["Prapor", "Skier"], "level": 2, "player_level": 40,
                      "quests": [["c"]], "quest_names": ["c"], "notes": ["Scav karma +3"]},
            "lightkeeper": {"quest": "Keeper's Word", "quests": [["skier1"]], "quest_names": ["skier1"]},
        }
        r = resolve_goals(p, [{"type": "kappa"}, {"type": "lightkeeper"}, {"type": "quest", "name": "b"},
                              {"type": "trader", "trader": "Prapor", "level": 3}, {"type": "quest", "name": "zzz"}])
        self.assertEqual(r.targets, [("Prapor", 3), ("Skier", 2)])  # Prapor: queda el LL más alto
        self.assertEqual(r.required, [["c"], ["skier1"], ["b"]])
        self.assertEqual(r.player_level, 40)
        self.assertTrue(any("karma de Scav de al menos +3" in n for n in r.notes))
        self.assertTrue(any("zzz" in n for n in r.notes))

    def test_collector_parser(self):
        from core.wiki_progression import parse_collector_requirements
        text = ("==Requirements==\n* Reach Loyalty Level 4 with [[Prapor]] and [[Jaeger]]\n"
                "* [[Scavs#Scav karma|Scav karma]] of at least +3\n* Must be level 40 to start this quest.\n"
                "* Complete the quests:\n** [[Chemical - Part 3]]\n** [[Shooter Born in Heaven]]\n\n==Objectives==\n")
        r = parse_collector_requirements(text)
        self.assertEqual(r["traders"], ["Prapor", "Jaeger"])
        self.assertEqual((r["level"], r["player_level"]), (4, 40))
        self.assertEqual(r["quests"], ["Chemical - Part 3", "Shooter Born in Heaven"])
        self.assertEqual(r["notes"], ["Scav karma of at least +3"])


class TestPlanStore(unittest.TestCase):
    def _prog(self):
        return {"tasks": {
            "deb": {"name": "Debut", "faction": "Any"},
            "adm_b": {"name": "Administrator", "faction": "BEAR"},
            "adm_u": {"name": "Administrator", "faction": "USEC"},
            "new": {"name": "Quest Nueva", "faction": "Any"},
        }}

    def test_drop_task_objectives(self):
        from core.progression_plan_store import drop_task_objectives
        objs = {"a#0", "a#1", "b#0", "ab#0"}
        self.assertEqual(drop_task_objectives(objs, ["a"]), {"b#0", "ab#0"})

    def test_reconcile_done_is_two_way(self):
        from core.progression_plan_store import reconcile_done
        done = {"deb", "new"}
        # 'Debut' se desmarcó en Quests & Traders; 'Administrator' se marcó; 'Quest Nueva' no existe allí.
        result = reconcile_done(self._prog(), done, ["Administrator"], ["Debut", "Administrator"], "USEC")
        self.assertEqual(result, {"adm_u", "new"})

    def test_sync_quest_completion_across_all_three_stores(self):
        import json
        import os
        import tempfile
        from core.database import init_db
        from core.progression_plan_store import (
            PREF_TRACKER_ACTIVE,
            get_completed_quest_keys,
            load_progress,
            sync_quest_completion,
        )
        from core.user_data import get_user_preference, set_user_preference

        class FakeDS:
            def __init__(self):
                self._quests = [
                    {"id": 1, "title": "Debut", "is_completed": 0},
                    {"id": 2, "title": "Administrator", "is_completed": 0},
                ]

            def get_quests(self):
                return list(self._quests)

            def toggle_quest(self, qid):
                for q in self._quests:
                    if q["id"] == qid:
                        q["is_completed"] = 0 if q["is_completed"] else 1
                        return bool(q["is_completed"])
                return False

        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        try:
            init_db(tmp.name)
            ds = FakeDS()
            prog = self._prog()
            set_user_preference(PREF_TRACKER_ACTIVE, json.dumps(["Debut", "Quest Nueva"]), tmp.name)

            # 1) Marcar desde Quest Tracker/Planner sincroniza DataStore, Planner y quita de ruta activa
            sync_quest_completion("Debut", True, datastore=ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertEqual(ds._quests[0]["is_completed"], 1)
            self.assertIn("deb", load_progress(tmp.name)["done"])
            self.assertEqual(json.loads(get_user_preference(PREF_TRACKER_ACTIVE, "[]", tmp.name)), ["Quest Nueva"])
            keys = get_completed_quest_keys(ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertIn("debut", keys)

            # 2) Desmarcar en cualquiera de las 3 limpia en todas
            sync_quest_completion("Debut", False, datastore=ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertEqual(ds._quests[0]["is_completed"], 0)
            self.assertNotIn("deb", load_progress(tmp.name)["done"])
            keys = get_completed_quest_keys(ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertNotIn("debut", keys)

            # 3) Quest solo de tarkov.dev (no existe en DataStore) también sincroniza entre Tracker y Planner
            sync_quest_completion("Quest Nueva", True, datastore=ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertIn("new", load_progress(tmp.name)["done"])
            keys = get_completed_quest_keys(ds, progression=prog, faction="USEC", db_path=tmp.name)
            self.assertIn("questnueva", keys)
        finally:
            for suffix in ("", "-wal", "-shm"):
                try:
                    os.remove(tmp.name + suffix)
                except OSError:
                    pass


class TestWikiFetch(unittest.TestCase):
    def test_fetch_quest_pages_batches_in_parallel(self):
        from unittest import mock
        from core import wiki_progression

        titles = [f"Q{i}" for i in range(120)]

        class Resp:
            status_code = 200

            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_get(url, params=None, headers=None, timeout=None):
            self.assertIn("TarkovScope", headers["User-Agent"])
            if params.get("list") == "categorymembers":
                return Resp({"query": {"categorymembers": [{"title": t} for t in titles]}})
            chunk = params["titles"].split("|")
            self.assertLessEqual(len(chunk), 50)
            return Resp({"query": {"pages": {t: {"title": t, "revisions": [{"slots": {"main": {"*": f"txt {t}"}}}]}
                                             for t in chunk}}})

        with mock.patch("requests.get", side_effect=fake_get):
            pages = wiki_progression.fetch_quest_pages(timeout=5)
        self.assertEqual(len(pages), 120)
        self.assertEqual(pages["Q77"], "txt Q77")
