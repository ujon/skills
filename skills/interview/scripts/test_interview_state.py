"""Regression checks for readiness gates and worker-context boundaries."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("interview_state.py")
SPEC = importlib.util.spec_from_file_location("interview_state", MODULE_PATH)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)
TEMPLATE_PATH = MODULE_PATH.parent.parent / "assets" / "interview.template.toml"


def ready_state():
    state = {
        "schema_version": 1,
        "session": {"id": "test", "revision": 2, "criteria_version": 1,
                    "round": 1, "status": "interviewing"},
        "request": {"text": "Build a shop page", "goal": "Help customers find us",
                    "root_task_id": "t0",
                 "scope": ["one page"], "out_of_scope": [],
                 "success": "The page shows the correct address and opening times."},
        "gate": {"overall_threshold": 90, "leaf_threshold": 80},
        "user": {"language": "en", "explanation_level": 1,
                 "preferred_style": "Simple examples", "topics": []},
        "requirements": [
            {"id": "r1", "description": "Visitors can find the shop address and hours",
             "kind": "outcome", "evidence_ids": ["e1"]},
            {"id": "r2", "description": "Use the address and hours supplied by the owner",
             "kind": "constraint", "evidence_ids": ["e1"]},
        ],
        "tasks": [
            {"id": "s1", "parent_id": "t0", "title": "Agree content", "deliverable": "Page content",
             "depends_on": [], "status": "pending", "requirement_ids": ["r1", "r2"],
             "inputs": ["Owner's address and hours"],
             "done_when": ["Page content includes the owner's address and hours"],
             "verification": "Compare the content with the owner's supplied details"},
            {"id": "s2", "parent_id": "t0", "title": "Build page", "deliverable": "Working page",
             "depends_on": ["s1"], "status": "pending", "requirement_ids": ["r1"],
             "inputs": ["Page content from s1"],
             "done_when": ["Visitors can read the address and hours on the page"],
             "verification": "Open the page and compare the displayed content with s1"},
            {"id": "t0", "title": "Deliver shop page", "requirement_ids": ["r1", "r2"],
             "depends_on": [], "status": "pending"},
        ],
        "evidence": [{"id": "e1", "kind": "user", "text": "Show our address and hours",
                      "source": "User answer", "accepted": True, "status": "active"}],
        "decisions": [{"id": "d1", "question": "Which content?", "status": "resolved",
                       "value": "Address and hours", "required": True,
                       "task_ids": ["s1", "s2"], "evidence_ids": ["e1"]}],
        "criteria": [
            {"id": "c1", "description": "Content is clear", "check": "List content",
             "task_ids": ["s1", "s2"], "weight": 3, "required": True,
             "evidence_ids": ["e1"], "decision_ids": ["d1"]},
            {"id": "c2", "description": "Success is clear", "check": "Define a check",
             "task_ids": ["s2"], "weight": 2, "required": False,
             "evidence_ids": ["e1"], "decision_ids": []},
        ],
        "questions": [], "changes": [],
        "evaluations": [{
            "id": "v1", "revision": 2, "criteria_version": 1,
            "evaluator_id": "fresh-worker-1", "isolated": True,
            "rubric_gaps": [], "contradictions": [],
            "ratings": [
                {"criterion_id": "c1", "score": 2, "reason": "Content recorded",
                 "evidence_ids": ["e1"]},
                {"criterion_id": "c2", "score": 2, "reason": "Check recorded",
                 "evidence_ids": ["e1"]},
            ],
        }],
    }
    return state


def legacy_state(version=1):
    """Keep genuine old-schema fixtures for read-only compatibility checks."""
    state = ready_state()
    state["schema_version"] = version
    state["task"] = state.pop("request")
    state["task"]["request"] = state["task"].pop("text")
    del state["task"]["root_task_id"]
    state["subtasks"] = state.pop("tasks")[:2]
    state["gate"]["subtask_threshold"] = state["gate"].pop("leaf_threshold")
    for item in state["subtasks"]:
        del item["parent_id"]
    for item in state["criteria"] + state["decisions"]:
        item["subtask_ids"] = item.pop("task_ids")
    if version == 1:
        del state["requirements"]
        for item in state["subtasks"]:
            for key in ("requirement_ids", "inputs", "done_when", "verification"):
                del item[key]
    return state


def legacy_hierarchy_state():
    state = ready_state()
    state["schema_version"] = 3
    del leaf(state, "t0")["status"]
    return state


def add_group(state, group_id, parent_id, child_ids):
    state["tasks"].append({"id": group_id, "title": group_id,
                           "parent_id": parent_id, "requirement_ids": [],
                           "depends_on": [], "status": "pending"})
    for item in state["tasks"]:
        if item["id"] in child_ids:
            item["parent_id"] = group_id


def leaf(state, task_id):
    return next(item for item in state["tasks"] if item["id"] == task_id)


def attempt_record(action="inspect", **changes):
    attempt = {
        "id": "a1", "revision": 2, "round": 1,
        "generator_id": "fresh-questioner-1", "isolated": True,
        "action": action, "targets": ["c1"],
        "why": "Checking the supplied content can resolve the remaining ambiguity.",
        "status": "proposed", "result": "", "evidence_ids": [],
    }
    if action == "inspect":
        attempt["inspection"] = "Read the owner's supplied opening-hours document."
    elif action == "experiment":
        attempt["proposal"] = {
            "question": "Can the supplied content fit on one accessible page?",
            "method": "Render one local prototype at the agreed mobile width.",
            "stop_condition": "Stop after one render and accessibility check.",
            "expected_evidence": "A screenshot and the accessibility check result.",
            "informs_decision": "Whether the content needs a separate hours section.",
        }
    attempt.update(changes)
    return attempt


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.state = ready_state()

    def test_valid_state(self):
        self.assertEqual(helper.validate(self.state), [])

    def test_cycle_and_dangling_dependency(self):
        self.state["tasks"][0]["depends_on"] = ["s2"]
        self.assertTrue(any("cycle" in error for error in helper.validate(self.state)))
        self.state["tasks"][0]["depends_on"] = ["absent"]
        self.assertTrue(any("depends_on" in error and "absent" in error
                            for error in helper.validate(self.state)))

    def test_uncovered_subtask(self):
        self.state["criteria"][0]["task_ids"] = ["s2"]
        self.assertTrue(any("s1 has no criterion" in error for error in helper.validate(self.state)))

    def test_current_schema_requires_requirements_and_contract_shape(self):
        for field in ("requirements",):
            state = ready_state()
            del state[field]
            self.assertTrue(helper.validate(state))
        for key, invalid in (("requirement_ids", []), ("inputs", "a string"),
                             ("done_when", [""]), ("verification", None)):
            with self.subTest(key=key):
                state = ready_state()
                state["tasks"][0][key] = invalid
                self.assertTrue(helper.validate(state))
        for key, invalid in (("description", " "), ("kind", "implementation"),
                             ("evidence_ids", ["absent"])):
            with self.subTest(key=key):
                state = ready_state()
                state["requirements"][0][key] = invalid
                self.assertTrue(helper.validate(state))
        self.state["requirements"] = []
        self.assertTrue(helper.validate(self.state))

    def test_schema_one_dispatch_rejects_malformed_or_mixed_layouts(self):
        for key in ("request", "tasks"):
            with self.subTest(missing=key):
                state = ready_state()
                del state[key]
                self.assertTrue(helper.validate(state))
        for key in ("task", "subtasks"):
            with self.subTest(legacy_field=key):
                state = ready_state()
                state[key] = legacy_state()[key]
                self.assertTrue(any("must not mix" in error for error in helper.validate(state)))
        state = ready_state()
        state["schema_version"] = 2
        self.assertTrue(helper.validate(state))

    def test_every_requirement_must_be_covered_by_a_subtask(self):
        self.state["tasks"][0]["requirement_ids"] = ["r1"]
        self.assertTrue(any("requirement r2" in error
                            for error in helper.validate(self.state)))
        with self.assertRaisesRegex(ValueError, "requirement r2"):
            helper.score(self.state)

    def test_unknown_requirement_references_are_invalid(self):
        self.state["tasks"][0]["requirement_ids"].append("absent")
        self.assertTrue(any("unknown requirements ID absent" in error
                            for error in helper.validate(self.state)))

    def test_unknown_contract_details_remain_valid_while_interviewing(self):
        self.state["tasks"][0].update(inputs=[], done_when=[], verification="")
        self.state["requirements"][0]["evidence_ids"] = []
        self.assertEqual(helper.validate(self.state), [])
        self.assertFalse(helper.score(self.state)["passed"])

    def test_duplicate_ids_and_current_ratings(self):
        self.state["criteria"][1]["id"] = "c1"
        self.assertTrue(any("duplicate ID" in error for error in helper.validate(self.state)))
        self.state = ready_state()
        self.state["evaluations"][0]["ratings"].append(copy.deepcopy(self.state["evaluations"][0]["ratings"][0]))
        self.assertTrue(any("duplicate rating" in error for error in helper.validate(self.state)))

    def test_missing_and_unknown_current_rating(self):
        self.state["evaluations"][0]["ratings"].pop()
        self.assertTrue(any("every current criterion" in error for error in helper.validate(self.state)))
        self.state["evaluations"][0]["ratings"][0]["criterion_id"] = "retired"
        self.assertTrue(any("unknown current criterion" in error for error in helper.validate(self.state)))

    def test_historical_criteria_are_not_required_in_current_graph(self):
        historic = copy.deepcopy(self.state["evaluations"][0])
        historic.update(id="old", revision=1)
        historic["ratings"][0]["criterion_id"] = "retired"
        self.state["evaluations"].insert(0, historic)
        self.assertEqual(helper.validate(self.state), [])

    def test_dangling_evidence_and_decision_refs(self):
        for key, field in (("criteria", "evidence_ids"), ("criteria", "decision_ids"),
                           ("decisions", "task_ids"), ("decisions", "evidence_ids")):
            with self.subTest(key=key, field=field):
                state = ready_state()
                state[key][0][field] = ["absent"]
                self.assertTrue(helper.validate(state))

    def test_boolean_is_not_integer(self):
        for path in (("schema_version",), ("session", "revision"),
                     ("user", "explanation_level"), ("gate", "overall_threshold"),
                     ("criteria", 0, "weight"), ("evaluations", 0, "ratings", 0, "score")):
            with self.subTest(path=path):
                state = ready_state()
                target = state
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = True
                self.assertTrue(helper.validate(state))

    def test_invalid_numeric_values(self):
        for weight in (0, -1, 0.5, "3"):
            with self.subTest(weight=weight):
                state = ready_state()
                state["criteria"][0]["weight"] = weight
                self.assertTrue(helper.validate(state))
        for threshold in (0, 101, 10 ** 400, float("nan"), float("inf"), "90"):
            with self.subTest(threshold=threshold):
                state = ready_state()
                state["gate"]["overall_threshold"] = threshold
                self.assertTrue(helper.validate(state))
        for rating in (-1, 3, 1.5, "2"):
            with self.subTest(rating=rating):
                state = ready_state()
                state["evaluations"][0]["ratings"][0]["score"] = rating
                self.assertTrue(helper.validate(state))

    def test_empty_or_missing_evidence_is_invalid(self):
        for key in ("text", "source"):
            with self.subTest(key=key):
                state = ready_state()
                state["evidence"][0][key] = "  "
                self.assertTrue(helper.validate(state))
        del self.state["request"]["text"]
        self.assertTrue(helper.validate(self.state))


class AttemptTests(unittest.TestCase):
    def test_absent_and_empty_history_are_backward_compatible_without_writes(self):
        for state in (ready_state(), legacy_state(1), legacy_state(2), legacy_hierarchy_state()):
            with self.subTest(schema=state["schema_version"], hierarchy="tasks" in state):
                original = copy.deepcopy(state)
                self.assertNotIn("attempts", state)
                self.assertEqual(helper.validate(state), [])
                before = helper.score(state)
                if helper.is_current_schema(state):
                    self.assertEqual(helper.packet(state, "questioner")["attempts"], [])
                self.assertEqual(state, original)
                state["attempts"] = []
                self.assertEqual(helper.validate(state), [])
                self.assertEqual(helper.score(state), before)

    def test_failed_and_inconclusive_attempts_preserve_plan_result_and_provenance(self):
        state = ready_state()
        evaluator_before = helper.packet(state, "evaluator")
        readiness_before = helper.score(state)
        failed = attempt_record(status="failed", result="The supplied document could not be opened.")
        experiment = attempt_record(
            "experiment", id="a2", round=2, status="inconclusive",
            result="The prototype rendered, but the supplied hours remain ambiguous.", evidence_ids=["e1"])
        state["attempts"] = [failed, experiment]
        original = copy.deepcopy(state)
        self.assertEqual(helper.validate(state), [])
        questioner = helper.packet(state, "questioner")
        self.assertEqual(questioner["attempts"], [failed, experiment])
        self.assertEqual(helper.packet(state, "evaluator"), evaluator_before)
        self.assertEqual(helper.score(state), readiness_before)
        self.assertNotIn("attempts", evaluator_before)
        self.assertEqual(state, original)
        questioner["attempts"][0]["targets"].clear()
        questioner["attempts"][1]["proposal"]["method"] = "Changed packet only"
        questioner["attempts"][1]["evidence_ids"].clear()
        self.assertEqual(state, original)

    def test_history_keeps_retired_targets_but_current_targets_must_resolve(self):
        state = ready_state()
        state["attempts"] = [attempt_record(
            revision=1, targets=["retired"], status="completed",
            result="The old document supplied the previous content.", evidence_ids=["e1"])]
        self.assertEqual(helper.validate(state), [])
        self.assertEqual(helper.packet(state, "questioner")["attempts"][0], state["attempts"][0])
        state["attempts"][0]["revision"] = state["session"]["revision"]
        self.assertTrue(any("attempts[0].targets: unknown criteria ID retired" in issue
                            for issue in helper.validate(state)))
        with self.assertRaises(ValueError):
            helper.packet(state, "questioner")

    def test_all_actions_and_statuses_support_honest_provenance(self):
        for action in ("inspect", "experiment", "repair", "pause"):
            for status in ("proposed", "running", "completed", "failed", "inconclusive", "skipped"):
                with self.subTest(action=action, status=status):
                    state = ready_state()
                    attempt = attempt_record(
                        action, status=status, generator_id="", isolated=False,
                        targets=["c1"] if action in ("inspect", "experiment") else [],
                        result="" if status in ("proposed", "running") else "Recorded outcome.")
                    state["attempts"] = [attempt]
                    self.assertEqual(helper.validate(state), [])
                    self.assertEqual(helper.packet(state, "questioner")["attempts"], [attempt])

    def test_attempt_provenance_cannot_replace_current_evaluator_provenance(self):
        state = ready_state()
        state["attempts"] = [attempt_record()]
        state["evaluations"][0].update(evaluator_id="", isolated=False)
        self.assertFalse(helper.score(state)["passed"])
        with self.assertRaisesRegex(ValueError, "evaluator provenance"):
            helper.packet(state, "questioner")

    def test_unknown_fields_stay_in_state_but_are_not_projected(self):
        state = ready_state()
        attempt = attempt_record("experiment", coordinator_notes={"private": "retained"})
        attempt["proposal"]["coordinator_notes"] = "retained proposal extension"
        attempt["inspection"] = "Optional source inspection accompanying the plan."
        state["attempts"] = [attempt]
        original = copy.deepcopy(state)
        self.assertEqual(helper.validate(state), [])
        projected = helper.packet(state, "questioner")["attempts"][0]
        self.assertNotIn("coordinator_notes", projected)
        self.assertNotIn("coordinator_notes", projected["proposal"])
        self.assertEqual(projected["inspection"], attempt["inspection"])
        self.assertEqual(set(projected["proposal"]), set(helper.PROPOSAL_FIELDS))
        self.assertEqual(state, original)

    def test_malformed_history_containers_and_duplicate_ids_are_rejected(self):
        for attempts in (None, {}, "history", [None], ["attempt"],
                         [attempt_record(), attempt_record()]):
            with self.subTest(attempts=attempts):
                state = ready_state()
                state["attempts"] = attempts
                self.assertTrue(any("attempts" in issue for issue in helper.validate(state)))
                with self.assertRaises(ValueError):
                    helper.packet(state, "evaluator")

    def test_malformed_attempt_fields_are_rejected_without_crashing(self):
        invalid_fields = {
            "id": (None, " ", 1), "revision": (None, True, 0, "2"),
            "round": (None, True, -1, "1"), "generator_id": (None, False, []),
            "isolated": (None, "true", 1), "action": (None, [], "ask"),
            "targets": (None, "c1", [""], ["c1", "c1"], ["missing"], []),
            "why": (None, " ", []), "status": (None, [], "done"),
            "result": (None, []), "evidence_ids": (None, "e1", [""], ["e1", "e1"], ["missing"]),
            "inspection": (None, " ", []),
        }
        for field, values in invalid_fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    state = ready_state()
                    state["attempts"] = [attempt_record(**{field: value})]
                    self.assertTrue(any("attempts[0]." + field in issue
                                        for issue in helper.validate(state)))
        for field in attempt_record():
            with self.subTest(missing=field):
                state = ready_state()
                state["attempts"] = [attempt_record()]
                del state["attempts"][0][field]
                self.assertTrue(any("attempts[0]." + field in issue
                                    for issue in helper.validate(state)))

    def test_terminal_statuses_require_results_and_historical_actions_require_targets(self):
        for status in ("completed", "failed", "inconclusive", "skipped"):
            for result in ("", " "):
                with self.subTest(status=status, result=result):
                    state = ready_state()
                    state["attempts"] = [attempt_record(status=status, result=result)]
                    self.assertTrue(any("attempts[0].result" in issue for issue in helper.validate(state)))
        for action in ("inspect", "experiment"):
            with self.subTest(action=action):
                state = ready_state()
                state["attempts"] = [attempt_record(action, revision=1, targets=[])]
                self.assertTrue(any("attempts[0].targets" in issue for issue in helper.validate(state)))

    def test_experiment_proposal_must_preserve_every_nonempty_plan_field(self):
        for proposal in (None, [], "plan", {}):
            with self.subTest(proposal=proposal):
                state = ready_state()
                state["attempts"] = [attempt_record("experiment", proposal=proposal)]
                self.assertTrue(any("attempts[0].proposal" in issue for issue in helper.validate(state)))
        state = ready_state()
        state["attempts"] = [attempt_record("experiment")]
        del state["attempts"][0]["proposal"]
        self.assertTrue(any("attempts[0].proposal" in issue for issue in helper.validate(state)))
        for field in helper.PROPOSAL_FIELDS:
            for value in (None, " ", []):
                with self.subTest(field=field, value=value):
                    state = ready_state()
                    attempt = attempt_record("experiment")
                    if value is None:
                        del attempt["proposal"][field]
                    else:
                        attempt["proposal"][field] = value
                    state["attempts"] = [attempt]
                    self.assertTrue(any("attempts[0].proposal." + field in issue
                                        for issue in helper.validate(state)))


class ReadinessTests(unittest.TestCase):
    def test_legacy_state_validates_without_mutation_but_cannot_pass(self):
        for version in (1, 2):
            with self.subTest(version=version):
                state = legacy_state(version)
                original = copy.deepcopy(state)
                self.assertEqual(helper.validate(state), [])
                result = helper.score(state)
                self.assertEqual(result["overall_score"], 100.0)
                self.assertFalse(result["passed"])
                self.assertTrue(any("migrate to the current hierarchical schema 1" in blocker
                                    for blocker in result["blockers"]))
                self.assertEqual(state, original)

    def test_legacy_hierarchy_is_read_only_without_mutation(self):
        state = legacy_hierarchy_state()
        original = copy.deepcopy(state)
        self.assertEqual(helper.validate(state), [])
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 100.0)
        self.assertEqual(result["task_scores"]["t0"], 100.0)
        self.assertFalse(result["passed"])
        self.assertIn(helper.UPGRADE_REQUIRED, result["blockers"])
        self.assertEqual(state, original)

    def test_ready_and_completed_states_pass_without_questions(self):
        state = ready_state()
        self.assertTrue(helper.score(state)["passed"])
        state["session"]["status"] = "completed"
        for subtask in state["tasks"]:
            if "status" in subtask:
                subtask["status"] = "done"
        result = helper.score(state)
        self.assertTrue(result["passed"])
        self.assertEqual(state["questions"], [])

    def test_contracts_define_completion_without_requiring_completed_work(self):
        state = ready_state()
        self.assertTrue(all(item["status"] == "pending" for item in state["tasks"] if "status" in item))
        self.assertTrue(helper.score(state)["passed"])
        for missing, value, message in (("done_when", [], "completion conditions"),
                                        ("verification", " ", "verification method")):
            with self.subTest(missing=missing):
                state = ready_state()
                state["tasks"][1][missing] = value
                self.assertEqual(helper.validate(state), [])
                result = helper.score(state)
                self.assertEqual(result["overall_score"], 100.0)
                self.assertFalse(result["passed"])
                self.assertTrue(any(message in item for item in result["blockers"]))

    def test_requirement_support_cannot_borrow_unlinked_accepted_evidence(self):
        for evidence_ids, change in (([], {}), (["e2"], {"accepted": False}),
                                     (["e2"], {"status": "superseded"})):
            with self.subTest(evidence_ids=evidence_ids, change=change):
                state = ready_state()
                state["evidence"].append(dict(state["evidence"][0], id="e2", **change))
                state["requirements"][0]["evidence_ids"] = evidence_ids
                result = helper.score(state)
                self.assertEqual(result["overall_score"], 100.0)
                self.assertFalse(result["passed"])
                self.assertTrue(any("Requirement r1 lacks" in item for item in result["blockers"]))
        state = ready_state()
        state["evidence"].append(dict(state["evidence"][0], id="e2"))
        state["requirements"][0]["evidence_ids"] = ["e2"]
        self.assertTrue(helper.score(state)["passed"])

    def test_graph_reports_unique_downstream_reach_and_independent_entries(self):
        state = ready_state()
        for subtask_id, dependencies in (("s3", ["s1"]), ("s4", ["s2", "s3"]),
                                          ("s5", [])):
            state["tasks"].append(dict(state["tasks"][1], id=subtask_id,
                                           depends_on=dependencies))
            state["criteria"][0]["task_ids"].append(subtask_id)
        expected = {"covered_requirement_ids": ["r1", "r2"],
                    "uncovered_requirement_ids": [],
                    "entry_task_ids": ["s1", "s5"],
                    "downstream_counts": {"s1": 3, "s2": 1, "s3": 1, "s4": 0, "s5": 0}}
        graph = helper.score(state)["graph"]
        for key, value in expected.items():
            self.assertEqual(graph[key], value)
        state["evaluations"] = []
        result = helper.score(state)
        self.assertFalse(result["passed"])
        for key, value in expected.items():
            self.assertEqual(result["graph"][key], value)

    def test_weighted_score_counts_shared_criterion_once(self):
        state = ready_state()
        state["evaluations"][0]["ratings"][1]["score"] = 1
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 80.0)
        self.assertEqual(result["leaf_scores"], {"s1": 100.0, "s2": 80.0})
        self.assertEqual(result["task_scores"], {"s1": 100.0, "s2": 80.0, "t0": 80.0})
        self.assertFalse(result["passed"])

    def test_each_subtask_must_pass_even_with_high_overall(self):
        state = ready_state()
        state["criteria"][0].update(weight=99, task_ids=["s1"])
        state["criteria"][1].update(weight=1, task_ids=["s2"])
        state["evaluations"][0]["ratings"][1]["score"] = 0
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 99.0)
        self.assertFalse(result["passed"])
        self.assertTrue(any("s2" in item for item in result["blockers"]))

    def test_hard_blockers_despite_perfect_scores(self):
        mutations = [
            lambda s: s["decisions"][0].update(status="open"),
            lambda s: s["decisions"][0].update(value=""),
            lambda s: s["decisions"][0].update(evidence_ids=[]),
            lambda s: s["evaluations"][0].update(isolated=False),
            lambda s: s["evaluations"][0].update(evaluator_id=""),
            lambda s: s["evaluations"][0].update(rubric_gaps=["Missing budget check"]),
            lambda s: s["evaluations"][0].update(contradictions=["Two different addresses"]),
            lambda s: s["request"].update(success=""),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                state = ready_state()
                mutation(state)
                result = helper.score(state)
                self.assertEqual(result["overall_score"], 100.0)
                self.assertFalse(result["passed"])
                self.assertTrue(result["blockers"])

    def test_required_criterion_cannot_hide_in_weighted_average(self):
        state = ready_state()
        state["criteria"][0]["weight"] = 1
        state["criteria"][1]["weight"] = 99
        state["criteria"][1]["task_ids"] = ["s1", "s2"]
        state["evaluations"][0]["ratings"][0]["score"] = 1
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 99.5)
        self.assertFalse(result["passed"])

    def test_stale_revision_or_rubric_cannot_pass(self):
        for key in ("revision", "criteria_version"):
            with self.subTest(key=key):
                state = ready_state()
                state["session"][key] += 1
                result = helper.score(state)
                self.assertFalse(result["passed"])
                self.assertTrue(any("No evaluation matches" in item for item in result["blockers"]))

    def test_latest_matching_evaluation_is_selected(self):
        state = ready_state()
        new = copy.deepcopy(state["evaluations"][0])
        new["id"] = "v2"
        new["ratings"][0]["score"] = 0
        state["evaluations"].append(new)
        self.assertFalse(helper.score(state)["passed"])
        stale = copy.deepcopy(state["evaluations"][0])
        stale.update(id="stale-last", revision=1)
        state["evaluations"].append(stale)
        self.assertEqual(helper.current_evaluation(state)["id"], "v2")

    def test_unsupported_score_two_receives_no_credit(self):
        for evidence_change in ({"accepted": False}, {"status": "superseded"}):
            with self.subTest(change=evidence_change):
                state = ready_state()
                state["evidence"][0].update(evidence_change)
                result = helper.score(state)
                self.assertEqual(result["overall_score"], 0.0)
                self.assertFalse(result["passed"])
        state = ready_state()
        state["evaluations"][0]["ratings"][0]["evidence_ids"] = []
        self.assertEqual(helper.score(state)["overall_score"], 40.0)
        state["evaluations"][0]["ratings"][0]["evidence_ids"] = ["absent"]
        with self.assertRaises(ValueError):
            helper.score(state)

    def test_uncited_partial_rating_cannot_pass_the_default_gate(self):
        state = ready_state()
        state["criteria"][0]["weight"] = 4
        state["criteria"][1]["weight"] = 1
        state["evaluations"][0]["ratings"][1].update(score=1, evidence_ids=[])
        result = helper.score(state)
        self.assertEqual(result["criterion_scores"], {"c1": 2, "c2": 0})
        self.assertEqual(result["overall_score"], 80.0)
        self.assertFalse(result["passed"])
        self.assertTrue(any("no supporting citations" in item for item in result["blockers"]))

    def test_every_positive_citation_must_be_active_and_linked(self):
        for score in (1, 2):
            for problem in ("unlinked", "inactive"):
                for mixed in (False, True):
                    with self.subTest(score=score, problem=problem, mixed=mixed):
                        state = ready_state()
                        state["evidence"].append(dict(state["evidence"][0], id="e2"))
                        if problem == "inactive":
                            state["evidence"][1]["status"] = "superseded"
                            state["criteria"][1]["evidence_ids"].append("e2")
                        state["evaluations"][0]["ratings"][1].update(
                            score=score, evidence_ids=["e1", "e2"] if mixed else ["e2"])
                        result = helper.score(state)
                        self.assertEqual(result["criterion_scores"]["c2"], 0)
                        self.assertFalse(result["passed"])
                        self.assertTrue(any(problem + " citations" in item
                                            for item in result["blockers"]))

    def test_score_two_requires_every_cited_item_to_be_accepted(self):
        state = ready_state()
        state["evidence"].append(dict(state["evidence"][0], id="e2", accepted=False))
        state["criteria"][1]["evidence_ids"].append("e2")
        state["evaluations"][0]["ratings"][1]["evidence_ids"] = ["e1", "e2"]
        result = helper.score(state)
        self.assertEqual(result["criterion_scores"]["c2"], 0)
        self.assertFalse(result["passed"])
        self.assertTrue(any("unaccepted citations: e2" in item for item in result["blockers"]))

    def test_active_unconfirmed_evidence_can_support_a_partial_rating(self):
        state = ready_state()
        state["evidence"].append(dict(state["evidence"][0], id="e2", kind="assumption", accepted=False))
        state["criteria"][0]["weight"] = 4
        state["criteria"][1].update(weight=1, evidence_ids=["e2"])
        state["evaluations"][0]["ratings"][1].update(score=1, evidence_ids=["e2"])
        result = helper.score(state)
        self.assertEqual(result["criterion_scores"], {"c1": 2, "c2": 1})
        self.assertEqual(result["overall_score"], 90.0)
        self.assertTrue(result["passed"])

    def test_linked_decision_evidence_can_support_a_rating(self):
        state = ready_state()
        state["criteria"][0]["evidence_ids"] = []
        self.assertEqual(state["criteria"][0]["decision_ids"], ["d1"])
        self.assertEqual(state["decisions"][0]["evidence_ids"], ["e1"])
        result = helper.score(state)
        self.assertEqual(result["criterion_scores"]["c1"], 2)
        self.assertTrue(result["passed"])

    def test_zero_rating_can_cite_unlinked_historical_conflicts(self):
        state = ready_state()
        state["evidence"].append(dict(state["evidence"][0], id="old", status="superseded"))
        state["evaluations"][0]["ratings"][1].update(score=0, evidence_ids=["old"])
        self.assertEqual(helper.validate(state), [])
        result = helper.score(state)
        self.assertEqual(result["criterion_scores"]["c2"], 0)
        self.assertFalse(any("invalid supporting evidence" in item for item in result["blockers"]))

    def test_empty_graph_never_passes(self):
        state = ready_state()
        for key in ("tasks", "criteria", "decisions"):
            state[key] = []
        state["evaluations"][0]["ratings"] = []
        self.assertTrue(helper.validate(state))
        with self.assertRaises(ValueError):
            helper.score(state)

    def test_gate_uses_fraction_before_display_rounding(self):
        state = ready_state()
        state["criteria"][0].update(weight=900000000 - 1, required=False)
        state["criteria"][1].update(weight=100000000 + 1, required=False)
        state["evaluations"][0]["ratings"][1]["score"] = 0
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 90.0)
        self.assertFalse(result["passed"])
        self.assertTrue(any("Overall score" in item for item in result["blockers"]))


class HierarchyTests(unittest.TestCase):
    def test_arbitrary_depth_keeps_one_root_and_executable_leaves(self):
        state = ready_state()
        parent_id = "t0"
        for index in range(12):
            group_id = f"g{index}"
            add_group(state, group_id, parent_id, ["s1"])
            parent_id = group_id
        self.assertEqual(helper.validate(state), [])
        result = helper.score(state)
        self.assertTrue(result["passed"])
        graph = result["graph"]
        self.assertEqual(graph["root_task_id"], "t0")
        self.assertEqual(graph["leaf_task_ids"], ["s1", "s2"])
        self.assertEqual(set(graph["children"]["t0"]), {"g0", "s2"})
        self.assertEqual(graph["children"]["g11"], ["s1"])
        self.assertEqual(graph["children"]["s1"], [])
        self.assertEqual(graph["entry_task_ids"], ["s1"])
        self.assertEqual(graph["downstream_counts"], {"s1": 1, "s2": 0})

    def test_root_can_be_a_single_executable_task(self):
        state = ready_state()
        state["tasks"] = [state["tasks"][0]]
        del state["tasks"][0]["parent_id"]
        state["request"]["root_task_id"] = "s1"
        for item in state["criteria"] + state["decisions"]:
            item["task_ids"] = ["s1"]
        self.assertEqual(helper.validate(state), [])
        result = helper.score(state)
        self.assertTrue(result["passed"])
        self.assertEqual(result["graph"]["children"], {"s1": []})
        self.assertEqual(result["leaf_scores"], {"s1": 100.0})

    def test_root_identity_and_parent_contract_are_enforced(self):
        mutations = [
            lambda s: s["request"].pop("root_task_id"),
            lambda s: s["request"].update(root_task_id="absent"),
            lambda s: s["request"].update(root_task_id=["t0"]),
            lambda s: leaf(s, "s1").pop("parent_id"),
            lambda s: leaf(s, "s1").update(parent_id="absent"),
            lambda s: leaf(s, "t0").update(parent_id="s1"),
            lambda s: leaf(s, "t0").update(parent_id=""),
            lambda s: s["tasks"].append(copy.deepcopy(leaf(s, "t0"))),
        ]
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                state = ready_state()
                mutation(state)
                self.assertTrue(helper.validate(state))
                with self.assertRaises(ValueError):
                    helper.score(state)

    def test_malformed_parent_types_are_reported_without_crashing(self):
        for parent_id in (None, True, 1, [], {}, ""):
            with self.subTest(parent_id=parent_id):
                state = ready_state()
                leaf(state, "s1")["parent_id"] = parent_id
                self.assertTrue(helper.validate(state))

    def test_disconnected_parent_cycle_is_rejected(self):
        state = ready_state()
        add_group(state, "g1", "g2", ["s1"])
        add_group(state, "g2", "g1", [])
        errors = helper.validate(state)
        self.assertTrue(errors)
        self.assertTrue(any("cycle" in error or "reach" in error for error in errors))
        with self.assertRaises(ValueError):
            helper.packet(state, "evaluator")

    def test_parent_relationship_does_not_create_execution_dependency(self):
        state = ready_state()
        leaf(state, "s2")["depends_on"] = []
        add_group(state, "g1", "t0", ["s1", "s2"])
        result = helper.score(state)
        self.assertEqual(result["graph"]["effective_dependencies"], {"s1": [], "s2": []})
        self.assertEqual(result["graph"]["entry_task_ids"], ["s1", "s2"])
        self.assertEqual(result["graph"]["downstream_counts"], {"s1": 0, "s2": 0})

    def test_dependencies_between_groups_expand_to_every_leaf(self):
        state = ready_state()
        for original, task_id in (("s1", "s1b"), ("s2", "s2b")):
            state["tasks"].append(dict(leaf(state, original), id=task_id, depends_on=[]))
        add_group(state, "g1", "t0", ["s1", "s1b"])
        add_group(state, "g2", "t0", ["s2", "s2b"])
        add_group(state, "g1deep", "g1", ["s1b"])
        leaf(state, "s2")["depends_on"] = []
        leaf(state, "g2")["depends_on"] = ["g1"]
        state["criteria"][0]["task_ids"] = ["t0"]
        graph = helper.score(state)["graph"]
        expected = {"s1": [], "s1b": [], "s2": ["s1", "s1b"], "s2b": ["s1", "s1b"]}
        for task_id, dependencies in expected.items():
            self.assertEqual(set(graph["effective_dependencies"][task_id]), set(dependencies))
        self.assertEqual(set(graph["entry_task_ids"]), {"s1", "s1b"})
        self.assertEqual(graph["downstream_counts"], {"s1": 2, "s1b": 2, "s2": 0, "s2b": 0})

    def test_ancestor_and_descendant_dependency_overlap_is_rejected(self):
        for task_id, prerequisite in (("t0", "s1"), ("s1", "t0"), ("s1", "s1")):
            with self.subTest(task_id=task_id, prerequisite=prerequisite):
                state = ready_state()
                leaf(state, task_id)["depends_on"] = [prerequisite]
                self.assertTrue(helper.validate(state))

    def test_execution_cycle_created_only_by_group_expansion_is_rejected(self):
        state = ready_state()
        leaf(state, "s2")["depends_on"] = []
        add_group(state, "g1", "t0", ["s1"])
        add_group(state, "g2", "t0", ["s2"])
        leaf(state, "g1")["depends_on"] = ["s2"]
        leaf(state, "g2")["depends_on"] = ["s1"]
        # g1 -> s2 and g2 -> s1 alone have no node-level dependency cycle.
        self.assertTrue(any("cycle" in error for error in helper.validate(state)))

    def test_inherited_criteria_and_overlapping_scopes_count_once(self):
        state = ready_state()
        add_group(state, "g1", "t0", ["s1", "s2"])
        state["criteria"][0]["task_ids"] = ["t0", "g1", "s1"]
        state["decisions"][0]["task_ids"] = ["t0"]
        state["evaluations"][0]["ratings"][1]["score"] = 1
        result = helper.score(state)
        self.assertEqual(result["overall_score"], 80.0)
        self.assertEqual(result["leaf_scores"], {"s1": 100.0, "s2": 80.0})
        self.assertEqual(result["task_scores"]["g1"], 80.0)
        self.assertEqual(result["task_scores"]["t0"], 80.0)
        # Parent scores aggregate unique criteria, not the children's mean of 90.
        self.assertNotEqual(result["task_scores"]["g1"], 90.0)

    def test_group_requirement_annotations_cannot_hide_uncovered_requirements(self):
        state = ready_state()
        leaf(state, "s1")["requirement_ids"] = ["r1"]
        self.assertIn("r2", leaf(state, "t0")["requirement_ids"])
        self.assertTrue(helper.validate(state))
        with self.assertRaises(ValueError):
            helper.score(state)
        state = ready_state()
        graph = helper.score(state)["graph"]
        self.assertEqual(graph["requirement_coverage"], {"r1": ["s1", "s2"], "r2": ["s1"]})

    def test_group_status_is_required_and_matches_descendant_progress(self):
        state = ready_state()
        add_group(state, "g1", "t0", ["s1", "s2"])
        for statuses, expected in ((("pending", "pending"), "pending"),
                                   (("running", "pending"), "running"),
                                   (("done", "pending"), "running"),
                                   (("done", "done"), "done")):
            with self.subTest(statuses=statuses):
                leaf(state, "s1")["status"], leaf(state, "s2")["status"] = statuses
                for task_id in ("g1", "t0"):
                    leaf(state, task_id)["status"] = expected
                before = copy.deepcopy(state)
                derived = helper.score(state)["graph"]["task_statuses"]
                self.assertEqual(derived["g1"], expected)
                self.assertEqual(derived["t0"], expected)
                self.assertEqual(state, before)
        leaf(state, "g1")["status"] = "pending"
        self.assertTrue(any("must match descendant progress: done" in error
                            for error in helper.validate(state)))

    def test_every_task_requires_a_valid_status(self):
        for task_id in ("t0", "s1", "s2"):
            for value in (None, "", "ready", "blocked", 1, ["pending"]):
                with self.subTest(task_id=task_id, value=value):
                    state = ready_state()
                    if value is None:
                        del leaf(state, task_id)["status"]
                    else:
                        leaf(state, task_id)["status"] = value
                    before = copy.deepcopy(state)
                    self.assertTrue(any("status" in issue for issue in helper.validate(state)))
                    with self.assertRaises(ValueError):
                        helper.score(state)
                    self.assertEqual(state, before)

    def test_reopening_leaf_requires_updating_every_ancestor(self):
        state = ready_state()
        add_group(state, "g1", "t0", ["s1"])
        for task in state["tasks"]:
            task["status"] = "done"
        self.assertEqual(helper.validate(state), [])
        leaf(state, "s1")["status"] = "running"
        errors = helper.validate(state)
        self.assertEqual(sum("must match descendant progress" in issue for issue in errors), 2)
        for task_id in ("g1", "t0"):
            leaf(state, task_id)["status"] = "running"
        self.assertEqual(helper.validate(state), [])

    def test_splitting_leaf_keeps_dependencies_and_invalidates_old_revision(self):
        state = ready_state()
        original = copy.deepcopy(leaf(state, "s1"))
        group = leaf(state, "s1")
        for key in ("inputs", "deliverable", "done_when", "verification"):
            del group[key]
        for task_id in ("s1a", "s1b"):
            state["tasks"].append(dict(original, id=task_id, parent_id="s1", depends_on=[]))
        state["session"]["revision"] += 1
        self.assertEqual(helper.validate(state), [])
        result = helper.score(state)
        self.assertFalse(result["passed"])
        self.assertTrue(any("No evaluation matches" in item for item in result["blockers"]))
        self.assertEqual(set(result["graph"]["effective_dependencies"]["s2"]), {"s1a", "s1b"})
        self.assertNotIn("s1", result["leaf_scores"])
        with self.assertRaises(ValueError):
            helper.packet(state, "questioner")

    def test_hierarchy_packets_preserve_parent_links_without_mutating_state(self):
        state = ready_state()
        add_group(state, "g1", "t0", ["s1"])
        before = copy.deepcopy(state)
        helper.validate(state)
        helper.score(state)
        for role in ("evaluator", "questioner"):
            result = helper.packet(state, role)
            self.assertEqual(result["request"]["root_task_id"], "t0")
            by_id = {item["id"]: item for item in result["tasks"]}
            self.assertEqual(by_id["s1"]["parent_id"], "g1")
            self.assertEqual(by_id["g1"]["parent_id"], "t0")
            self.assertNotIn("parent_id", by_id["t0"])
            self.assertTrue(all("status" not in item for item in result["tasks"]))
            by_id["s1"]["requirement_ids"].clear()
            by_id["g1"]["depends_on"].append("s2")
        self.assertEqual(state, before)


class PacketTests(unittest.TestCase):
    def test_evaluator_is_blind_to_weights_and_gate_but_questioner_is_not(self):
        state = ready_state()
        evaluator = helper.packet(state, "evaluator")
        self.assertNotIn("gate", evaluator)
        self.assertTrue(all("weight" not in item for item in evaluator["criteria"]))
        questioner = helper.packet(state, "questioner")
        self.assertEqual(questioner["gate"], state["gate"])
        self.assertEqual([item["weight"] for item in questioner["criteria"]], [3, 2])

    def test_evaluator_omits_only_profile_exclusive_evidence(self):
        state = ready_state()
        state["evidence"].extend([
            dict(state["evidence"][0], id="profile", text="I prefer simple explanations."),
            dict(state["evidence"][0], id="unlinked-task", text="The shop also closes on holidays."),
            dict(state["evidence"][0], id="decision-shared", text="Use the owner's content."),
        ])
        state["decisions"][0]["evidence_ids"].append("decision-shared")
        state["user"]["topics"] = [{"name": "Websites", "familiarity": "beginner",
                                     "confidence": "high",
                                     "evidence_ids": ["profile", "e1", "decision-shared"]}]
        original = copy.deepcopy(state)
        evaluator_ids = {item["id"] for item in helper.packet(state, "evaluator")["evidence"]}
        self.assertEqual(evaluator_ids, {"e1", "unlinked-task", "decision-shared"})
        questioner_ids = {item["id"] for item in helper.packet(state, "questioner")["evidence"]}
        self.assertEqual(questioner_ids, {"e1", "profile", "unlinked-task", "decision-shared"})
        self.assertEqual(state, original)

    def test_explanation_preferences_change_only_questioner_input(self):
        for change in ({"language": "ko"}, {"explanation_level": 3},
                       {"preferred_style": "Use technical examples and precise terms."}):
            with self.subTest(change=change):
                state = ready_state()
                evaluator_before = helper.packet(state, "evaluator")
                questioner_before = helper.packet(state, "questioner")
                readiness_before = helper.score(state)
                current_before = copy.deepcopy(helper.current_evaluation(state))
                state["user"].update(change)
                after_edit = copy.deepcopy(state)
                self.assertEqual(helper.packet(state, "evaluator"), evaluator_before)
                self.assertNotEqual(helper.packet(state, "questioner"), questioner_before)
                self.assertEqual(helper.score(state), readiness_before)
                self.assertTrue(readiness_before["passed"])
                self.assertEqual(helper.current_evaluation(state), current_before)
                self.assertEqual(state["session"]["revision"], evaluator_before["session"]["revision"])
                self.assertEqual(state, after_edit)

    def test_profile_only_evidence_updates_preserve_current_readiness_and_evaluator_input(self):
        for change in ("revise", "append", "supersede", "familiarity"):
            with self.subTest(change=change):
                state = ready_state()
                state["evidence"].append(dict(state["evidence"][0], id="profile",
                                              text="I prefer short, concrete examples."))
                topic = {"name": "Websites", "familiarity": "beginner", "confidence": "high",
                         "evidence_ids": ["profile"]}
                state["user"]["topics"] = [topic]
                evaluator_before = helper.packet(state, "evaluator")
                questioner_before = helper.packet(state, "questioner")
                readiness_before = helper.score(state)
                current_before = copy.deepcopy(helper.current_evaluation(state))
                if change == "revise":
                    state["evidence"][1]["text"] = "I now prefer detailed technical explanations."
                elif change == "familiarity":
                    topic.update(familiarity="working", confidence="medium")
                else:
                    state["evidence"].append(dict(state["evidence"][1], id="profile-new",
                                                  text="Use diagrams for explanation."))
                    topic["evidence_ids"].append("profile-new")
                    if change == "supersede":
                        state["evidence"][1]["status"] = "superseded"
                after_edit = copy.deepcopy(state)
                self.assertEqual(helper.packet(state, "evaluator"), evaluator_before)
                self.assertNotEqual(helper.packet(state, "questioner"), questioner_before)
                self.assertEqual(helper.current_evaluation(state), current_before)
                self.assertEqual(helper.score(state), readiness_before)
                self.assertTrue(readiness_before["passed"])
                self.assertEqual(state["session"]["revision"], evaluator_before["session"]["revision"])
                self.assertEqual(state, after_edit)

    def test_task_input_transition_invalidates_readiness_including_profile_shared_evidence(self):
        for change in ("request", "contract", "shared-evidence"):
            with self.subTest(change=change):
                state = ready_state()
                state["user"]["topics"] = [{"name": "Websites", "familiarity": "working",
                                             "confidence": "high", "evidence_ids": ["e1"]}]
                evaluator_before = helper.packet(state, "evaluator")
                self.assertTrue(helper.score(state)["passed"])
                if change == "request":
                    state["request"]["scope"].append("Include holiday closures")
                elif change == "contract":
                    state["tasks"][0]["done_when"].append("Holiday closures are supplied by the owner")
                else:
                    state["evidence"][0]["text"] = "Show our address, hours, and holiday closures."
                # Version changes are coordinator-authored, never inferred or written by the helper.
                state["session"]["revision"] += 1
                after_edit = copy.deepcopy(state)
                self.assertNotEqual(helper.packet(state, "evaluator"), evaluator_before)
                self.assertIsNone(helper.current_evaluation(state))
                readiness = helper.score(state)
                self.assertFalse(readiness["passed"])
                self.assertTrue(any("No evaluation matches" in item for item in readiness["blockers"]))
                with self.assertRaisesRegex(ValueError, "requires a current evaluation"):
                    helper.packet(state, "questioner")
                self.assertEqual(state, after_edit)

    def test_questioner_requires_recorded_evaluator_provenance(self):
        for change in ({"isolated": False}, {"evaluator_id": ""}, {"evaluator_id": "  "}):
            with self.subTest(change=change):
                state = ready_state()
                state["evaluations"][0].update(change)
                self.assertEqual(helper.validate(state), [])
                with self.assertRaisesRegex(ValueError, "provenance"):
                    helper.packet(state, "questioner")

    def test_legacy_packet_requires_explicit_upgrade_without_writing(self):
        for layout, state in (("flat1", legacy_state(1)), ("flat2", legacy_state(2)),
                              ("hierarchy3", legacy_hierarchy_state())):
            original = copy.deepcopy(state)
            for role in ("evaluator", "questioner"):
                with self.subTest(layout=layout, role=role):
                    with self.assertRaisesRegex(ValueError, "migrate to the current hierarchical schema 1"):
                        helper.packet(state, role)
            self.assertEqual(state, original)

    def test_current_schema_one_is_preserved_in_both_packets(self):
        state = ready_state()
        for role in ("evaluator", "questioner"):
            with self.subTest(role=role):
                self.assertEqual(helper.packet(state, role)["schema_version"], 1)

    def test_contract_and_requirement_fields_survive_both_projections(self):
        state = ready_state()
        state["requirements"][0]["coordinator_reasoning"] = "Do not send me"
        state["tasks"][0]["coordinator_reasoning"] = "Do not send me"
        for role in ("evaluator", "questioner"):
            with self.subTest(role=role):
                result = helper.packet(state, role)
                self.assertNotIn("coordinator_reasoning", json.dumps(result))
                self.assertEqual(result["requirements"][0], {
                    "id": "r1", "description": "Visitors can find the shop address and hours",
                    "kind": "outcome", "evidence_ids": ["e1"]})
                for key in ("requirement_ids", "inputs", "done_when", "verification"):
                    self.assertEqual(result["tasks"][0][key], state["tasks"][0][key])
                result["requirements"][0]["evidence_ids"].clear()
                result["tasks"][0]["done_when"].clear()
                self.assertEqual(state["requirements"][0]["evidence_ids"], ["e1"])
                self.assertTrue(state["tasks"][0]["done_when"])

    def test_superseded_question_preserves_retired_criterion_reference(self):
        state = ready_state()
        state["questions"] = [{"id": "q1", "revision": 1, "round": 1,
                               "generator_id": "question-worker", "isolated": True,
                               "targets": ["retired"], "text": "Which address should we use?",
                               "status": "superseded", "answer_evidence_ids": []}]
        self.assertEqual(helper.validate(state), [])
        result = helper.packet(state, "questioner")
        self.assertEqual(result["questions"][0]["status"], "superseded")
        self.assertEqual(result["questions"][0]["targets"], ["retired"])

    def test_evaluator_projection_excludes_profile_old_scores_and_narrative(self):
        state = ready_state()
        state["internal_reasoning"] = "Do not send me"
        state["request"]["coordinator_reasoning"] = "Do not send me"
        state["evidence"][0]["hidden_guess"] = "Do not send me"
        state["user"]["topics"] = [{"name": "Shop pages", "familiarity": "beginner",
                                     "confidence": "low", "evidence_ids": ["e1"]}]
        state["evidence"].append({"id": "e0", "kind": "user", "text": "Old address",
                                   "source": "Old answer", "accepted": True, "status": "superseded"})
        result = helper.packet(state, "evaluator")
        for key in ("user", "questions", "evaluations", "internal_reasoning", "readiness"):
            self.assertNotIn(key, result)
        self.assertNotIn("status", result["session"])
        self.assertNotIn("status", result["tasks"][0])
        self.assertNotIn("task_statuses", result["graph"])
        self.assertNotIn("task_scores", result)
        self.assertNotIn("leaf_scores", result)
        self.assertNotIn("coordinator_reasoning", result["request"])
        self.assertNotIn("hidden_guess", result["evidence"][0])
        self.assertEqual(result["evidence"][1]["status"], "superseded")

    def test_questioner_only_gets_latest_current_evaluation(self):
        state = ready_state()
        old = copy.deepcopy(state["evaluations"][0])
        old.update(id="old", revision=1, secret_reasoning="Do not send me")
        state["evaluations"].insert(0, old)
        state["evaluations"][1]["secret_reasoning"] = "Do not send me"
        state["questions"] = [{"id": "q1", "revision": 1, "round": 1,
                               "generator_id": "question-worker", "isolated": True,
                               "targets": ["c1"], "text": "What should the page show?",
                               "options": ["Address", "Opening hours"],
                               "status": "answered", "answer_evidence_ids": ["e1"],
                               "secret_reasoning": "Do not send me"}]
        result = helper.packet(state, "questioner")
        self.assertNotIn("evaluations", result)
        self.assertEqual(result["evaluation"]["id"], "v1")
        self.assertNotIn("secret_reasoning", json.dumps(result))
        self.assertEqual(result["readiness"], helper.score(state))
        self.assertEqual(result["questions"][0]["answer_evidence_ids"], ["e1"])
        self.assertEqual(result["questions"][0]["round"], 1)
        self.assertEqual(result["questions"][0]["options"], ["Address", "Opening hours"])
        result["criteria"][0]["evidence_ids"].clear()
        self.assertEqual(state["criteria"][0]["evidence_ids"], ["e1"])

    def test_questioner_requires_current_evaluation(self):
        state = ready_state()
        state["session"]["revision"] += 1
        with self.assertRaisesRegex(ValueError, "requires a current evaluation"):
            helper.packet(state, "questioner")


@unittest.skipIf(helper.tomllib is None, "Requires Python 3.11+ or tomli")
class CLITests(unittest.TestCase):
    def run_cli(self, *args):
        completed = subprocess.run([sys.executable, str(MODULE_PATH)] + list(args),
                                   text=True, capture_output=True, check=False)
        return completed.returncode, json.loads(completed.stdout)

    def test_template_parse_validate_score_and_no_writes(self):
        before = TEMPLATE_PATH.read_bytes()
        code, result = self.run_cli("validate", str(TEMPLATE_PATH))
        self.assertEqual(code, 0)
        self.assertTrue(result["valid"])
        code, result = self.run_cli("score", str(TEMPLATE_PATH))
        self.assertEqual(code, 0)
        self.assertFalse(result["passed"])
        code, result = self.run_cli("packet", str(TEMPLATE_PATH), "--role", "evaluator")
        self.assertEqual(code, 0)
        self.assertNotIn("user", result)
        code, result = self.run_cli("packet", str(TEMPLATE_PATH), "--role", "questioner")
        self.assertEqual(code, 1)
        self.assertEqual(TEMPLATE_PATH.read_bytes(), before)

    def test_parse_errors_and_missing_file_are_json_and_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "interview.toml"
            target.write_text("[broken\n", encoding="utf-8")
            code, result = self.run_cli("validate", str(target))
            self.assertEqual(code, 1)
            self.assertFalse(result["valid"])
            code, result = self.run_cli("validate", str(target.with_name("missing.toml")))
            self.assertEqual(code, 1)
            self.assertFalse(result["valid"])


if __name__ == "__main__":
    unittest.main()
