#!/usr/bin/env python3
"""Render interview.toml as a self-contained, offline interactive HTML viewer.

Uses only the standard library (Python 3.11+), or tomli on Python 3.9/3.10.
The input is validated and read without modification. Legacy flat schema 1/2
and hierarchical schema 3 files can be viewed but cannot pass readiness.
"""

import argparse
import copy
import json
import os
import sys
import tempfile
import webbrowser
from pathlib import Path

import interview_state


TEMPLATE_PATH = Path(__file__).resolve().parents[1] / "assets" / "interview-viewer.html"
DATA_PLACEHOLDER = "__INTERVIEW_DATA__"


def _pick(record, fields):
    return {key: copy.deepcopy(record[key]) for key in fields if key in record}


def _leaf_scopes(children):
    """Find each node's descendant leaves without imposing a depth limit."""
    parents = {child: parent for parent, values in children.items() for child in values}
    remaining = {key: len(values) for key, values in children.items()}
    ready = [key for key, count in remaining.items() if count == 0]
    scopes = {}
    while ready:
        node_id = ready.pop()
        scopes[node_id] = (set().union(*(scopes[child] for child in children[node_id]))
                           if children[node_id] else {node_id})
        parent = parents.get(node_id)
        if parent is not None:
            remaining[parent] -= 1
            if remaining[parent] == 0:
                ready.append(parent)
    return scopes


def build_payload(state, source_name="interview.toml", theme="auto"):
    """Return deterministic viewer data without changing the supplied state."""
    if not isinstance(theme, str) or theme not in {"auto", "light", "dark"}:
        raise ValueError("Theme must be auto, light, or dark.")
    errors = interview_state.validate(state)
    if errors:
        raise ValueError("Invalid interview state:\n" + "\n".join(errors))
    readiness = interview_state.score(state)
    evaluation = interview_state.current_evaluation(state)
    has_evaluation = evaluation is not None
    legacy_flat = not interview_state.has_task_hierarchy(state)
    warnings = ([interview_state.UPGRADE_REQUIRED]
                if not interview_state.is_current_schema(state) else [])

    if legacy_flat:
        authored = state["subtasks"]
        used_ids = {item["id"] for item in authored}
        root_id, suffix = "__interview_root__", 0
        while root_id in used_ids:
            suffix += 1
            root_id = "__interview_root_{}__".format(suffix)
        children = {root_id: [item["id"] for item in authored]}
        children.update({item["id"]: [] for item in authored})
        tasks = [{"id": root_id, "title": state["task"]["goal"],
                  "requirement_ids": [], "depends_on": []}]
        for item in authored:
            projected = _pick(item, ("id", "title", "status", "deliverable", "depends_on"))
            if state["schema_version"] == 2:
                projected.update(_pick(item, ("requirement_ids", "inputs", "done_when", "verification")))
            projected["parent_id"] = root_id
            tasks.append(projected)
        leaf_statuses = {item["status"] for item in authored}
        root_status = ("done" if leaf_statuses == {"done"} else
                       "pending" if leaf_statuses == {"pending"} else "running")
        statuses = {item["id"]: item["status"] for item in authored}
        statuses[root_id] = root_status
        node_scores = dict(readiness["subtask_scores"], **{root_id: readiness["overall_score"]})
        request = _pick(state["task"], ("goal", "scope", "out_of_scope", "success"))
        request["text"] = state["task"]["request"]
        target_field = "subtask_ids"
    else:
        tasks = state["tasks"]
        graph = interview_state.graph_diagnostics(state)
        children, statuses = graph["children"], graph["task_statuses"]
        node_scores = readiness["task_scores"]
        request = _pick(state["request"], ("text", "goal", "scope", "out_of_scope", "success"))
        target_field = "task_ids"
    scopes = _leaf_scopes(children)

    ratings = {item["criterion_id"]: item for item in evaluation["ratings"]} if evaluation else {}
    criteria, decisions = [], []
    criterion_scopes, decision_scopes = {}, {}
    for criterion in state["criteria"]:
        item = _pick(criterion, ("id", "description", "check", "weight", "required",
                                 "evidence_ids", "decision_ids"))
        item["task_ids"] = copy.deepcopy(criterion[target_field])
        rating = ratings.get(criterion["id"])
        reported = rating["score"] if rating else None
        credited = readiness["criterion_scores"][criterion["id"]] if rating else None
        item.update({"score": credited, "reported_score": reported,
                     "reason": rating["reason"] if rating else "",
                     "rating_evidence_ids": copy.deepcopy(rating["evidence_ids"]) if rating else []})
        criteria.append(item)
        criterion_scopes[item["id"]] = set().union(*(scopes[key] for key in item["task_ids"]))
    for decision in state["decisions"]:
        item = _pick(decision, ("id", "question", "status", "value", "required", "evidence_ids"))
        item["task_ids"] = copy.deepcopy(decision[target_field])
        decisions.append(item)
        decision_scopes[item["id"]] = set().union(*(scopes[key] for key in item["task_ids"]))

    nodes, edges = [], []
    for task in tasks:
        node_id = task["id"]
        parent_id = task.get("parent_id")
        nodes.append({
            "id": node_id,
            "title": task["title"],
            "parent_id": parent_id,
            "children": list(children[node_id]),
            "kind": "group" if children[node_id] else "leaf",
            "status": statuses[node_id],
            "score": node_scores[node_id] if has_evaluation else None,
            "requirement_ids": copy.deepcopy(task.get("requirement_ids", [])),
            "inputs": copy.deepcopy(task.get("inputs", [])),
            "deliverable": task.get("deliverable", ""),
            "done_when": copy.deepcopy(task.get("done_when", [])),
            "verification": task.get("verification", ""),
            "criteria": [copy.deepcopy(item) for item in criteria
                         if scopes[node_id] & criterion_scopes[item["id"]]],
            "decisions": [copy.deepcopy(item) for item in decisions
                          if scopes[node_id] & decision_scopes[item["id"]]],
        })
        if parent_id is not None:
            edges.append({"source": parent_id, "target": node_id, "type": "hierarchy"})
        for dependency in task["depends_on"]:
            edges.append({"source": dependency, "target": node_id, "type": "dependency"})

    # Embed only a filename, never the machine's directory structure.
    source_name = str(source_name).replace("\\", "/").rsplit("/", 1)[-1] or "interview.toml"
    return {
        "format_version": 1,
        "source_name": source_name,
        "schema_version": state["schema_version"],
        "initial_theme": theme,
        "request": request,
        "session": _pick(state["session"], ("id", "revision", "criteria_version", "round", "status")),
        "summary": {"overall_score": readiness["overall_score"] if has_evaluation else None,
                    "passed": readiness["passed"], "blockers": list(readiness["blockers"]),
                    "has_current_evaluation": has_evaluation},
        "nodes": nodes,
        "edges": edges,
        "requirements": [_pick(item, interview_state.RECORD_FIELDS["requirements"])
                         for item in state["requirements"]]
                         if not legacy_flat or state["schema_version"] == 2 else [],
        "questions": [_pick(item, ("id", "revision", "round", "generator_id", "isolated",
                                    "targets", "text", "status", "answer_evidence_ids", "options", "why"))
                      for item in state["questions"]],
        "attempts": [_pick(item, ("id", "revision", "round", "generator_id", "isolated",
                                  "action", "targets", "why", "status", "result", "evidence_ids",
                                  "inspection", "proposal"))
                     for item in state.get("attempts", [])],
        "user": {**_pick(state["user"], ("language", "explanation_level", "preferred_style")),
                 "topics": [_pick(item, ("name", "familiarity", "confidence", "evidence_ids"))
                            for item in state["user"]["topics"]]},
        "evidence": [_pick(item, interview_state.RECORD_FIELDS["evidence"])
                     for item in state["evidence"]],
        "warnings": warnings,
    }


def render_html(payload):
    """Insert escaped JSON into the offline template's inert data element."""
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    if template.count(DATA_PLACEHOLDER) != 1:
        raise ValueError("Viewer template must contain exactly one data placeholder.")
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
    for character, escaped in (("<", "\\u003c"), (">", "\\u003e"), ("&", "\\u0026"),
                               ("\u2028", "\\u2028"), ("\u2029", "\\u2029")):
        serialized = serialized.replace(character, escaped)
    return template.replace(DATA_PLACEHOLDER, serialized)


def _same_file(source, output):
    if source.resolve() == output.resolve():
        return True
    return output.exists() and os.path.samefile(source, output)


def _write_atomic(output, content):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=output.parent, prefix=".interview-viewer-",
                                         suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=Path("interview.toml"), type=Path,
                        help="Input TOML file (default: interview.toml)")
    parser.add_argument("-o", "--output", type=Path,
                        help="Output HTML file (default: input filename with .html suffix)")
    parser.add_argument("--theme", choices=("auto", "light", "dark"), default="auto")
    parser.add_argument("--open", action="store_true", dest="open_browser",
                        help="Open the finished HTML in the default browser")
    args = parser.parse_args(argv)
    source = args.path.expanduser()
    try:
        output = args.output.expanduser() if args.output is not None else source.with_suffix(".html")
        if interview_state.tomllib is None:
            raise ValueError("TOML parsing needs Python 3.11+ or tomli on Python 3.9/3.10.")
        if _same_file(source, output):
            raise ValueError("Input and output refer to the same file; choose a separate HTML output.")
        with source.open("rb") as stream:
            state = interview_state.tomllib.load(stream)
        payload = build_payload(state, source.name, args.theme)
        rendered = render_html(payload)
        _write_atomic(output, rendered)
    except (OSError, ValueError) as exc:
        print("Cannot create interview viewer: {}".format(exc), file=sys.stderr)
        return 1
    print("Created {}".format(output))
    if args.open_browser:
        try:
            if not webbrowser.open(output.resolve().as_uri()):
                print("The viewer was created, but no browser could be opened.", file=sys.stderr)
        except (OSError, webbrowser.Error) as exc:
            print("The viewer was created, but the browser could not open: {}".format(exc), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
