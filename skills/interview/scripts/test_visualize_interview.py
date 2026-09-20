"""Checks for the read-only, self-contained interview viewer generator."""

import copy
from html.parser import HTMLParser
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT_DIRECTORY = Path(__file__).resolve().parent
MODULE_PATH = SCRIPT_DIRECTORY / "visualize_interview.py"
TEMPLATE_PATH = SCRIPT_DIRECTORY.parent / "assets" / "interview.template.toml"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


viewer = load_module("visualize_interview", MODULE_PATH)
fixtures = load_module("interview_fixtures", SCRIPT_DIRECTORY / "test_interview_state.py")


def evidence_history_state():
    """Synthetic answers, findings, defaults, and non-question actions."""
    state = fixtures.ready_state()
    state["evidence"].extend([
        {"id": "e-finding", "kind": "artifact", "text": "The sample supports keyboard navigation.",
         "source": "https://example.test/reference?view=keyboard&mode=full", "accepted": True,
         "status": "active"},
        {"id": "e-default", "kind": "assumption", "text": "Use the existing static page method.",
         "source": "Adopted under delegated method choice; see notes/default.txt", "accepted": True,
         "status": "active"},
        {"id": "e-old", "kind": "user", "text": "The earlier answer was phone only.",
         "source": "Earlier user answer", "accepted": True, "status": "superseded"},
        {"id": "e-open", "kind": "assumption", "text": "A form might be useful.",
         "source": "Unreviewed suggestion", "accepted": False, "status": "active"},
    ])
    state["requirements"][0]["evidence_ids"] = ["e1", "e-finding"]
    state["decisions"][0]["evidence_ids"] = ["e-default"]
    state["criteria"][0]["evidence_ids"] = ["e1", "e-finding", "e-open", "e-old"]
    state["evaluations"][0]["ratings"][0]["evidence_ids"] = ["e-finding", "e-default"]
    state["questions"] = [{
        "id": "q-contact", "revision": 2, "round": 1,
        "generator_id": "question-worker", "isolated": True, "targets": ["c1"],
        "text": "Which contact details belong on the page?", "options": ["Phone", "Email"],
        "why": "This changes the page content.", "status": "answered", "answer_evidence_ids": ["e1"],
    }]
    state["attempts"] = [{
        "id": "a-inspect", "revision": 2, "round": 1,
        "generator_id": "inspection-worker", "isolated": True, "targets": ["c1"],
        "action": "inspect", "why": "Check the existing page before choosing a method.",
        "status": "completed", "inspection": "Read the synthetic sample and reference.",
        "result": "The sample has the needed keyboard behavior.", "evidence_ids": ["e-finding"],
    }, {
        "id": "a-experiment", "revision": 2, "round": 1,
        "generator_id": "experiment-worker", "isolated": True, "targets": ["c2"],
        "action": "experiment", "why": "Check the remaining uncertainty with a small sample.",
        "status": "proposed", "result": "", "evidence_ids": [],
        "proposal": {"question": "Does the sample work without scripts?",
                     "method": "Open the synthetic sample with scripts disabled.",
                     "stop_condition": "Stop after checking the two navigation links.",
                     "expected_evidence": "A recorded navigation result.",
                     "informs_decision": "Whether the existing method is sufficient."},
    }]
    return state


class HTMLDocument(HTMLParser):
    def __init__(self, content):
        super().__init__(convert_charrefs=False)
        self.scripts = []
        self.resources = []
        self.active_script = None
        self.feed(content)
        self.close()

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == "script":
            self.active_script = {"attributes": attributes, "text": ""}
            self.scripts.append(self.active_script)
        resource_attributes = {"script": "src", "link": "href", "img": "src",
                               "iframe": "src", "audio": "src", "video": "src"}
        if tag in resource_attributes and resource_attributes[tag] in attributes:
            self.resources.append(attributes[resource_attributes[tag]])

    def handle_endtag(self, tag):
        if tag == "script":
            self.active_script = None

    def handle_data(self, data):
        if self.active_script is not None:
            self.active_script["text"] += data

    def payload(self):
        data_scripts = [script for script in self.scripts
                        if script["attributes"].get("type") == "application/json"]
        if len(data_scripts) != 1:
            raise AssertionError("Expected exactly one embedded JSON payload")
        return json.loads(data_scripts[0]["text"])


class PayloadTests(unittest.TestCase):
    def test_answers_and_linked_evidence_preserve_provenance(self):
        state = evidence_history_state()
        payload = viewer.build_payload(state)
        evidence = {item["id"]: item for item in payload["evidence"]}
        self.assertEqual(payload["questions"], state["questions"])
        self.assertEqual(evidence["e-default"]["kind"], "assumption")
        self.assertTrue(evidence["e-default"]["accepted"])
        self.assertEqual(evidence["e-old"]["status"], "superseded")
        self.assertFalse(evidence["e-open"]["accepted"])
        self.assertEqual(evidence["e-finding"]["source"], state["evidence"][1]["source"])
        root = next(node for node in payload["nodes"] if node["id"] == "t0")
        self.assertEqual(payload["requirements"][0]["evidence_ids"], ["e1", "e-finding"])
        self.assertEqual(root["decisions"][0]["evidence_ids"], ["e-default"])
        self.assertEqual(root["criteria"][0]["rating_evidence_ids"], ["e-finding", "e-default"])

    def test_optional_attempts_preserve_complete_plan_without_becoming_answers(self):
        self.assertEqual(viewer.build_payload(fixtures.ready_state())["attempts"], [])
        state = evidence_history_state()
        original = copy.deepcopy(state)
        payload = viewer.build_payload(state)
        self.assertEqual(payload["attempts"], state["attempts"])
        self.assertEqual(len(payload["questions"]), 1)
        self.assertEqual(payload["questions"][0]["answer_evidence_ids"], ["e1"])
        self.assertEqual(payload, viewer.build_payload(state))
        payload["attempts"][0]["evidence_ids"].clear()
        payload["attempts"][1]["proposal"]["method"] = "Viewer-local change"
        payload["evidence"][1]["source"] = "Viewer-local source"
        self.assertEqual(state, original)

    def test_nested_hierarchy_and_dependencies_remain_distinct(self):
        state = fixtures.ready_state()
        fixtures.add_group(state, "g1", "t0", ["s1"])
        fixtures.add_group(state, "g2", "g1", ["s1"])
        fixtures.leaf(state, "s2")["depends_on"] = ["g1"]
        result = viewer.build_payload(state)
        by_id = {node["id"]: node for node in result["nodes"]}
        self.assertEqual(by_id["g1"]["parent_id"], "t0")
        self.assertEqual(by_id["g1"]["children"], ["g2"])
        self.assertEqual(by_id["s1"]["parent_id"], "g2")
        self.assertEqual(by_id["s1"]["children"], [])
        self.assertEqual(by_id["g1"]["kind"], "group")
        self.assertEqual(by_id["s1"]["kind"], "leaf")
        hierarchy = {(edge["source"], edge["target"]) for edge in result["edges"]
                     if edge["type"] == "hierarchy"}
        dependencies = {(edge["source"], edge["target"]) for edge in result["edges"]
                        if edge["type"] == "dependency"}
        self.assertEqual(hierarchy, {("t0", "g1"), ("g1", "g2"),
                                     ("g2", "s1"), ("t0", "s2")})
        self.assertEqual(dependencies, {("g1", "s2")})

    def test_inherited_criteria_are_unique_and_parent_scores_use_unique_criteria(self):
        state = fixtures.ready_state()
        fixtures.add_group(state, "g1", "t0", ["s1", "s2"])
        state["criteria"][0]["task_ids"] = ["t0", "g1", "s1"]
        state["decisions"][0]["task_ids"] = ["g1"]
        state["evaluations"][0]["ratings"][1]["score"] = 1
        result = viewer.build_payload(state)
        by_id = {node["id"]: node for node in result["nodes"]}
        self.assertEqual([item["id"] for item in by_id["s1"]["criteria"]], ["c1"])
        self.assertEqual({item["id"] for item in by_id["s2"]["criteria"]}, {"c1", "c2"})
        self.assertEqual(len(by_id["g1"]["criteria"]), 2)
        self.assertEqual(by_id["s1"]["score"], 100.0)
        self.assertEqual(by_id["s2"]["score"], 80.0)
        self.assertEqual(by_id["g1"]["score"], 80.0)
        self.assertEqual(by_id["t0"]["score"], 80.0)
        self.assertEqual(result["summary"]["overall_score"], 80.0)
        self.assertEqual([item["id"] for item in by_id["s1"]["decisions"]], ["d1"])

    def test_missing_or_stale_evaluation_has_null_scores(self):
        for stale in (False, True):
            with self.subTest(stale=stale):
                state = fixtures.ready_state()
                if stale:
                    state["session"]["revision"] += 1
                else:
                    state["evaluations"] = []
                result = viewer.build_payload(state)
                self.assertFalse(result["summary"]["has_current_evaluation"])
                self.assertIsNone(result["summary"]["overall_score"])
                self.assertFalse(result["summary"]["passed"])
                self.assertTrue(result["summary"]["blockers"])
                for node in result["nodes"]:
                    self.assertIsNone(node["score"])
                    self.assertTrue(all(item["score"] is None for item in node["criteria"]))

    def test_supported_zero_is_distinct_from_not_evaluated(self):
        state = fixtures.ready_state()
        for rating in state["evaluations"][0]["ratings"]:
            rating["score"] = 0
        result = viewer.build_payload(state)
        self.assertTrue(result["summary"]["has_current_evaluation"])
        self.assertEqual(result["summary"]["overall_score"], 0.0)
        for node in result["nodes"]:
            self.assertEqual(node["score"], 0.0)
            self.assertTrue(all(item["score"] == 0 for item in node["criteria"]))

    def test_unsupported_rating_is_displayed_with_zero_credit(self):
        state = fixtures.ready_state()
        state["evidence"][0]["accepted"] = False
        result = viewer.build_payload(state)
        self.assertEqual(result["summary"]["overall_score"], 0.0)
        for node in result["nodes"]:
            for criterion in node["criteria"]:
                self.assertEqual(criterion["score"], 0)
                self.assertEqual(criterion["reported_score"], 2)
                self.assertEqual(criterion["rating_evidence_ids"], ["e1"])

    def test_viewer_uses_helper_credit_for_all_supported_schema_versions(self):
        cases = (
            ("uncited partial", 1, [], False, "active", True, 0),
            ("unlinked accepted", 2, ["e1", "e2"], False, "active", True, 0),
            ("mixed historical", 2, ["e1", "e2"], True, "superseded", True, 0),
            ("mixed unaccepted", 2, ["e1", "e2"], True, "active", False, 0),
            ("valid partial", 1, ["e2"], True, "active", False, 1),
            ("linked decision", 2, ["e1"], False, "active", True, 2),
        )
        states = (("current1", fixtures.ready_state()),
                  ("flat1", fixtures.legacy_state(1)),
                  ("flat2", fixtures.legacy_state(2)),
                  ("hierarchy3", fixtures.legacy_hierarchy_state()))
        for layout, base in states:
            for name, reported, citations, linked, status, accepted, expected in cases:
                with self.subTest(layout=layout, case=name):
                    state = copy.deepcopy(base)
                    state["evidence"].append(dict(state["evidence"][0], id="e2",
                                                   status=status, accepted=accepted))
                    if linked:
                        state["criteria"][1]["evidence_ids"].append("e2")
                    if name == "linked decision":
                        state["criteria"][1].update(evidence_ids=[], decision_ids=["d1"])
                    state["evaluations"][0]["ratings"][1].update(score=reported, evidence_ids=citations)
                    readiness = fixtures.helper.score(state)
                    payload = viewer.build_payload(state)
                    self.assertEqual(readiness["criterion_scores"]["c2"], expected)
                    self.assertEqual(payload["summary"]["overall_score"], readiness["overall_score"])
                    for node in payload["nodes"]:
                        for criterion in node["criteria"]:
                            self.assertEqual(criterion["score"], readiness["criterion_scores"][criterion["id"]])
                            if criterion["id"] == "c2":
                                self.assertEqual(criterion["reported_score"], reported)

    def test_group_status_comes_from_descendant_progress(self):
        state = fixtures.ready_state()
        fixtures.leaf(state, "s1")["status"] = "done"
        fixtures.leaf(state, "t0")["status"] = "running"
        result = viewer.build_payload(state)
        by_id = {node["id"]: node for node in result["nodes"]}
        self.assertEqual(by_id["t0"]["status"], "running")
        self.assertEqual(by_id["s1"]["status"], "done")
        self.assertEqual(by_id["s2"]["status"], "pending")

    def test_viewer_rejects_missing_or_inconsistent_current_group_status(self):
        for value in (None, "done"):
            with self.subTest(status=value):
                state = fixtures.ready_state()
                if value is None:
                    del fixtures.leaf(state, "t0")["status"]
                else:
                    fixtures.leaf(state, "t0")["status"] = value
                with self.assertRaisesRegex(ValueError, "status"):
                    viewer.build_payload(state)

    def test_output_is_deterministic_and_does_not_alias_source_state(self):
        state = fixtures.ready_state()
        state["questions"] = [{"id": "q1", "revision": 2, "round": 1,
                               "generator_id": "question-worker", "isolated": True,
                               "targets": ["c1"], "text": "What should we show?",
                               "status": "answered", "answer_evidence_ids": ["e1"]}]
        original = copy.deepcopy(state)
        first = viewer.build_payload(state, source_name="other folder/interview-\u2603.toml", theme="dark")
        second = viewer.build_payload(state, source_name="other folder/interview-\u2603.toml", theme="dark")
        self.assertEqual(first, second)
        self.assertEqual(first["format_version"], 1)
        self.assertEqual(first["initial_theme"], "dark")
        self.assertEqual(first["source_name"], "interview-\u2603.toml")
        first["request"]["scope"].clear()
        first["requirements"][0]["evidence_ids"].clear()
        first["nodes"][0]["requirement_ids"].clear()
        first["questions"][0]["answer_evidence_ids"].clear()
        first["user"]["topics"].append({"name": "viewer only"})
        self.assertEqual(state, original)

    def test_legacy_states_are_viewable_without_silent_upgrade(self):
        for version in (1, 2):
            with self.subTest(version=version):
                state = fixtures.legacy_state(version)
                original = copy.deepcopy(state)
                result = viewer.build_payload(state)
                self.assertEqual(result["schema_version"], version)
                self.assertFalse(result["summary"]["passed"])
                self.assertTrue(result["warnings"])
                groups = [node for node in result["nodes"] if node["kind"] == "group"]
                self.assertEqual(len(groups), 1)
                self.assertEqual(set(groups[0]["children"]), {"s1", "s2"})
                self.assertEqual(state, original)

    def test_legacy_hierarchy_preserves_graph_and_blocks_readiness(self):
        state = fixtures.legacy_hierarchy_state()
        original = copy.deepcopy(state)
        result = viewer.build_payload(state)
        current = viewer.build_payload(fixtures.ready_state())
        self.assertEqual(result["schema_version"], 3)
        self.assertFalse(result["summary"]["passed"])
        self.assertTrue(result["warnings"])
        self.assertEqual(result["nodes"], current["nodes"])
        self.assertEqual(result["edges"], current["edges"])
        self.assertEqual(result["requirements"], current["requirements"])
        self.assertEqual(state, original)

    def test_invalid_hierarchy_is_not_rendered_as_a_valid_graph(self):
        state = fixtures.ready_state()
        fixtures.leaf(state, "s1")["parent_id"] = "absent"
        with self.assertRaises(ValueError):
            viewer.build_payload(state)


class HTMLTests(unittest.TestCase):
    def test_embedded_data_round_trips_unicode_and_offline_assets(self):
        state = fixtures.ready_state()
        state["request"]["text"] = "Build a shop website \U0001f3e0 \u2014 opening hours"
        payload = viewer.build_payload(state, source_name="interview-\u2603.toml", theme="light")
        html = viewer.render_html(payload)
        self.assertEqual(html, viewer.render_html(copy.deepcopy(payload)))
        document = HTMLDocument(html)
        self.assertEqual(document.payload(), payload)
        self.assertNotIn("__INTERVIEW_DATA__", html)
        self.assertTrue(all(not script["attributes"].get("src") for script in document.scripts))
        self.assertTrue(all(resource.startswith(("data:", "#")) for resource in document.resources))
        self.assertIn("<style", html)
        self.assertGreater(len(document.scripts), 1)

    def test_script_closing_text_cannot_escape_the_json_container(self):
        attack = '</script><script id="injected">alert("owned")</script><!--&\u2028\u2029'
        state = fixtures.ready_state()
        state["request"]["text"] = attack
        state["tasks"][0]["title"] = attack
        payload = viewer.build_payload(state, source_name=attack)
        baseline = HTMLDocument(viewer.render_html(viewer.build_payload(fixtures.ready_state())))
        html = viewer.render_html(payload)
        document = HTMLDocument(html)
        self.assertEqual(document.payload(), payload)
        self.assertEqual(len(document.scripts), len(baseline.scripts))
        self.assertFalse(any(script["attributes"].get("id") == "injected"
                             for script in document.scripts))
        self.assertNotIn(attack, html)

    def test_source_answer_and_attempt_text_cannot_escape_embedded_data(self):
        attack = '</script><img src=x onerror="window.viewerInjected=true">'
        state = evidence_history_state()
        state["evidence"][0]["text"] = attack
        state["evidence"][1]["source"] = attack
        state["attempts"][0]["result"] = attack
        state["attempts"][1]["proposal"]["method"] = attack
        payload = viewer.build_payload(state)
        document = HTMLDocument(viewer.render_html(payload))
        self.assertEqual(document.payload(), payload)
        self.assertEqual(document.resources, [])
        self.assertEqual(len(document.scripts), 2)


class CLITests(unittest.TestCase):
    def run_cli(self, directory, *arguments):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-B", str(MODULE_PATH), *arguments],
                              cwd=directory, text=True, capture_output=True,
                              check=False, env=environment)

    def copy_template(self, directory, name="interview.toml"):
        target = Path(directory) / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(TEMPLATE_PATH.read_bytes())
        return target

    def test_default_paths_generate_an_offline_html_file_without_state_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.copy_template(directory)
            original = source.read_bytes()
            completed = self.run_cli(directory)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            destination = source.with_suffix(".html")
            self.assertTrue(destination.is_file())
            payload = HTMLDocument(destination.read_text(encoding="utf-8")).payload()
            self.assertEqual(payload["schema_version"], 1)
            self.assertIsNone(payload["summary"]["overall_score"])
            self.assertEqual(source.read_bytes(), original)

    def test_arbitrary_relative_input_and_output_locations(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.copy_template(directory, "notes/interview-\u2603.toml")
            original = source.read_bytes()
            destination = Path(directory) / "exports" / "overview.html"
            destination.parent.mkdir()
            completed = self.run_cli(directory, "notes/interview-\u2603.toml", "-o", "exports/overview.html",
                                     "--theme", "dark")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = HTMLDocument(destination.read_text(encoding="utf-8")).payload()
            self.assertEqual(payload["initial_theme"], "dark")
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse(source.with_suffix(".html").exists())

    def test_malformed_or_missing_state_returns_failure_without_an_output(self):
        for content in (None, "[broken\n", "schema_version = 3\n"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                source = Path(directory) / "interview.toml"
                if content is not None:
                    source.write_text(content, encoding="utf-8")
                completed = self.run_cli(directory)
                self.assertNotEqual(completed.returncode, 0)
                self.assertFalse(source.with_suffix(".html").exists())
                if content is not None:
                    self.assertEqual(source.read_text(encoding="utf-8"), content)

    def test_same_input_and_output_is_rejected_including_file_aliases(self):
        for alias in ("same", "symlink", "hardlink"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                source = self.copy_template(directory)
                original = source.read_bytes()
                if alias == "same":
                    destination = source
                else:
                    destination = Path(directory) / "alias.html"
                    if alias == "symlink":
                        destination.symlink_to(source)
                    else:
                        os.link(source, destination)
                completed = self.run_cli(directory, str(source), "-o", str(destination))
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
