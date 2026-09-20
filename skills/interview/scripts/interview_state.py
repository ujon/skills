#!/usr/bin/env python3
"""Read, validate, score, and project interview.toml without modifying it.

Python 3.11+ includes TOML support; Python 3.9/3.10 require tomli.
Recorded provenance is checked, but only the coordinator can attest that a
worker actually ran in a fresh context. This helper cannot prove isolation.
"""

import argparse
import copy
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


SESSION_STATUSES = {
    "interviewing", "ready", "executing", "completed", "paused", "blocked",
    "overridden",
}
TASK_STATUSES = {"pending", "running", "done"}
ATTEMPT_ACTIONS = {"inspect", "experiment", "repair", "pause"}
ATTEMPT_STATUSES = {"proposed", "running", "completed", "failed", "inconclusive", "skipped"}
PROPOSAL_FIELDS = ("question", "method", "stop_condition", "expected_evidence", "informs_decision")
UPGRADE_REQUIRED = (
    "Legacy flat schemas 1/2 and hierarchical schema 3 are read-only. "
    "Explicitly migrate to the current hierarchical schema 1 before readiness "
    "or worker evaluation: record request.root_task_id and the unified tasks hierarchy, preserve "
    "requirements and executable leaf contracts, and replace subtask_ids and "
    "subtask_threshold with task_ids and leaf_threshold where needed."
)
REQUEST_FIELDS = ("text", "goal", "scope", "out_of_scope", "success", "root_task_id")
RECORD_FIELDS = {
    "requirements": ("id", "description", "kind", "evidence_ids"),
    "subtasks": (
        "id", "title", "deliverable", "depends_on", "requirement_ids",
        "inputs", "done_when", "verification",
    ),
    "criteria": (
        "id", "description", "check", "subtask_ids", "weight", "required",
        "evidence_ids", "decision_ids",
    ),
    "decisions": (
        "id", "question", "status", "value", "required", "subtask_ids",
        "evidence_ids",
    ),
    "evidence": ("id", "kind", "text", "source", "accepted", "status"),
    "questions": (
        "id", "revision", "round", "targets", "text", "status", "answer_evidence_ids",
    ),
    "attempts": (
        "id", "revision", "round", "generator_id", "isolated", "action", "targets",
        "why", "status", "result", "evidence_ids",
    ),
    "evaluations": (
        "id", "revision", "criteria_version", "evaluator_id", "isolated",
        "rubric_gaps", "contradictions",
    ),
}


def is_int(value):
    return type(value) is int


def has_task_hierarchy(state):
    """Distinguish current task structure from the older flat schema 1 layout."""
    return isinstance(state, dict) and (
        "request" in state or "tasks" in state or state.get("schema_version") == 3)


def is_current_schema(state):
    return (isinstance(state, dict) and is_int(state.get("schema_version"))
            and state["schema_version"] == 1 and has_task_hierarchy(state))


def _validate_legacy(state):
    """Return shape and reference errors; readiness is a separate decision."""
    errors = []

    def error(path, message):
        errors.append("{}: {}".format(path, message))

    def table(parent, key, path=""):
        label = "{}.{}".format(path, key) if path else key
        value = parent.get(key)
        if not isinstance(value, dict):
            error(label, "must be a table")
            return {}
        return value

    def text_field(obj, key, path, empty=False):
        value = obj.get(key)
        if not isinstance(value, str) or (not empty and not value.strip()):
            error(path + "." + key, "must be a {}string".format(
                "" if empty else "nonempty "))

    def integer(obj, key, path, minimum=1, maximum=None):
        value = obj.get(key)
        if (not is_int(value) or value < minimum
                or (maximum is not None and value > maximum)):
            error(path + "." + key, "must be an integer in {}..{}".format(
                minimum, maximum if maximum is not None else "infinity"))

    def boolean(obj, key, path):
        if type(obj.get(key)) is not bool:
            error(path + "." + key, "must be a boolean")

    def choice(obj, key, path, values):
        if not isinstance(obj.get(key), str) or obj[key] not in values:
            error(path + "." + key, "must be one of " + ", ".join(sorted(values)))

    def strings(obj, key, path, unique=False):
        value = obj.get(key)
        if not isinstance(value, list):
            error(path + "." + key, "must be an array of strings")
            return []
        if any(not isinstance(item, str) or not item.strip() for item in value):
            error(path + "." + key, "must contain only nonempty strings")
            return []
        if unique and len(value) != len(set(value)):
            error(path + "." + key, "must not contain duplicates")
        return value

    def records(obj, key, path="", ids=True):
        label = "{}.{}".format(path, key) if path else key
        value = obj.get(key)
        if not isinstance(value, list):
            error(label, "must be an array of tables")
            return []
        result, seen = [], set()
        for index, item in enumerate(value):
            item_path = "{}[{}]".format(label, index)
            if not isinstance(item, dict):
                error(item_path, "must be a table")
                continue
            if ids:
                text_field(item, "id", item_path)
                record_id = item.get("id")
                if isinstance(record_id, str):
                    if record_id in seen:
                        error(item_path + ".id", "duplicate ID " + record_id)
                    seen.add(record_id)
            result.append((item_path, item))
        return result

    if not isinstance(state, dict):
        return ["state: must be a table"]
    schema_version = state.get("schema_version")
    if not is_int(schema_version) or schema_version not in {1, 2}:
        error("schema_version", "must be integer 1 or 2")
    session = table(state, "session")
    text_field(session, "id", "session")
    for key in ("revision", "criteria_version", "round"):
        integer(session, key, "session", minimum=0 if key == "round" else 1)
    choice(session, "status", "session", SESSION_STATUSES)
    task = table(state, "task")
    for key in ("request", "goal", "success"):
        text_field(task, key, "task", empty=key == "success")
    for key in ("scope", "out_of_scope"):
        strings(task, key, "task")
    gate = table(state, "gate")
    for key in ("overall_threshold", "subtask_threshold"):
        value = gate.get(key)
        if (type(value) not in (int, float) or not 0 < value <= 100
                or not math.isfinite(value)):
            error("gate." + key, "must be a finite number greater than 0 and at most 100")
    user = table(state, "user")
    for key in ("language", "preferred_style"):
        text_field(user, key, "user")
    integer(user, "explanation_level", "user", 1, 3)
    topics = records(user, "topics", "user", ids=False)
    all_records = {
        key: records(state, key)
        for key in ("subtasks", "evidence", "decisions", "criteria", "questions", "evaluations")
    }
    # Older files need no migration or write merely to add an empty history.
    all_records["attempts"] = records(state, "attempts") if "attempts" in state else []
    if schema_version == 2:
        all_records["requirements"] = records(state, "requirements")
        if not all_records["requirements"]:
            error("requirements", "must contain at least one table")
    for key in ("subtasks", "criteria"):
        if not all_records[key]:
            error(key, "must contain at least one table")
    ids = {
        key: {item["id"] for _, item in values if isinstance(item.get("id"), str)}
        for key, values in all_records.items()
    }

    def refs(obj, key, path, target, nonempty=False):
        values = strings(obj, key, path, unique=True)
        if nonempty and not values:
            error(path + "." + key, "must contain at least one ID")
        for value in values:
            if value not in ids[target]:
                error(path + "." + key, "unknown {} ID {}".format(target, value))
        return values

    for path, topic in topics:
        text_field(topic, "name", path)
        choice(topic, "familiarity", path, {"unknown", "beginner", "working", "advanced"})
        choice(topic, "confidence", path, {"low", "medium", "high"})
        refs(topic, "evidence_ids", path, "evidence")
    if schema_version == 2:
        for path, item in all_records["requirements"]:
            text_field(item, "description", path)
            choice(item, "kind", path, {"outcome", "constraint"})
            refs(item, "evidence_ids", path, "evidence")
    graph, covered_requirements = {}, set()
    for path, item in all_records["subtasks"]:
        for key in ("title", "deliverable"):
            text_field(item, key, path)
        choice(item, "status", path, TASK_STATUSES)
        dependencies = refs(item, "depends_on", path, "subtasks")
        if schema_version == 2:
            covered_requirements.update(refs(
                item, "requirement_ids", path, "requirements", nonempty=True))
            strings(item, "inputs", path)
            strings(item, "done_when", path)
            text_field(item, "verification", path, empty=True)
        if isinstance(item.get("id"), str):
            graph[item["id"]] = dependencies
    if schema_version == 2:
        for missing in sorted(ids["requirements"] - covered_requirements):
            error("subtasks", "requirement {} has no subtask".format(missing))
    # Iterative topological reduction avoids recursion depth limits on long DAGs.
    remaining = {key: set(value) & set(graph) for key, value in graph.items()}
    ready = [key for key, value in remaining.items() if not value]
    while ready:
        finished = ready.pop()
        remaining.pop(finished, None)
        for key, dependencies in remaining.items():
            if finished in dependencies:
                dependencies.remove(finished)
                if not dependencies:
                    ready.append(key)
    if remaining:
        error("subtasks", "dependency cycle involving " + ", ".join(sorted(remaining)))
    for path, item in all_records["evidence"]:
        choice(item, "kind", path, {"user", "artifact", "assumption"})
        choice(item, "status", path, {"active", "superseded"})
        boolean(item, "accepted", path)
        for key in ("text", "source"):
            text_field(item, key, path)
    for path, item in all_records["decisions"]:
        text_field(item, "question", path)
        text_field(item, "value", path, empty=True)
        choice(item, "status", path, {"open", "resolved", "deferred"})
        boolean(item, "required", path)
        refs(item, "subtask_ids", path, "subtasks", nonempty=True)
        refs(item, "evidence_ids", path, "evidence")
    covered = set()
    for path, item in all_records["criteria"]:
        for key in ("description", "check"):
            text_field(item, key, path)
        integer(item, "weight", path)
        boolean(item, "required", path)
        covered.update(refs(item, "subtask_ids", path, "subtasks", nonempty=True))
        refs(item, "evidence_ids", path, "evidence")
        refs(item, "decision_ids", path, "decisions")
    for missing in sorted(ids["subtasks"] - covered):
        error("criteria", "subtask {} has no criterion".format(missing))
    for path, item in all_records["questions"]:
        integer(item, "revision", path)
        integer(item, "round", path, 0)
        text_field(item, "generator_id", path, empty=True)
        boolean(item, "isolated", path)
        text_field(item, "text", path)
        choice(item, "status", path, {"pending", "answered", "skipped", "superseded"})
        # Historical questions, like old ratings, can reference retired criteria.
        if item.get("revision") == session.get("revision"):
            refs(item, "targets", path, "criteria", nonempty=True)
        else:
            strings(item, "targets", path, unique=True)
        refs(item, "answer_evidence_ids", path, "evidence")
        if "options" in item:
            strings(item, "options", path)
    for path, item in all_records["attempts"]:
        integer(item, "revision", path)
        integer(item, "round", path, 0)
        # As with questions, retain honest missing/non-isolated provenance.
        # Shape validation cannot attest that a fresh worker actually ran.
        text_field(item, "generator_id", path, empty=True)
        boolean(item, "isolated", path)
        choice(item, "action", path, ATTEMPT_ACTIONS)
        choice(item, "status", path, ATTEMPT_STATUSES)
        text_field(item, "why", path)
        text_field(item, "result", path, empty=item.get("status") in ("proposed", "running"))
        targets = strings(item, "targets", path, unique=True)
        if item.get("action") in ("inspect", "experiment") and not targets:
            error(path + ".targets", "must contain at least one ID")
        # Outcomes remain useful even after the criteria they targeted retire.
        if item.get("revision") == session.get("revision"):
            for target in targets:
                if target not in ids["criteria"]:
                    error(path + ".targets", "unknown criteria ID " + target)
        refs(item, "evidence_ids", path, "evidence")
        if item.get("action") == "inspect" or "inspection" in item:
            text_field(item, "inspection", path, empty=item.get("action") != "inspect")
        if item.get("action") == "experiment" or "proposal" in item:
            proposal = table(item, "proposal", path)
            for key in PROPOSAL_FIELDS:
                text_field(proposal, key, path + ".proposal")
    for path, item in all_records["evaluations"]:
        integer(item, "revision", path)
        integer(item, "criteria_version", path)
        text_field(item, "evaluator_id", path, empty=True)
        boolean(item, "isolated", path)
        strings(item, "rubric_gaps", path)
        strings(item, "contradictions", path)
        current = (item.get("revision") == session.get("revision")
                   and item.get("criteria_version") == session.get("criteria_version"))
        rated = set()
        for rating_path, rating in records(item, "ratings", path, ids=False):
            text_field(rating, "criterion_id", rating_path)
            integer(rating, "score", rating_path, 0, 2)
            text_field(rating, "reason", rating_path)
            refs(rating, "evidence_ids", rating_path, "evidence")
            criterion_id = rating.get("criterion_id")
            if isinstance(criterion_id, str):
                if criterion_id in rated:
                    error(rating_path, "duplicate rating for " + criterion_id)
                rated.add(criterion_id)
                if current and criterion_id not in ids["criteria"]:
                    error(rating_path, "unknown current criterion " + criterion_id)
        if current and rated != ids["criteria"]:
            error(path + ".ratings", "must rate every current criterion exactly once")
    for path, item in records(state, "changes", ids=False):
        integer(item, "revision", path)
        text_field(item, "reason", path)
    return errors


def _task_graph(state):
    """Validate and expand containment and execution edges without recursion."""
    errors, tasks, positions = [], {}, {}

    def error(path, message):
        errors.append("{}: {}".format(path, message))

    def strings(item, key, path, valid_ids=None):
        values = item.get(key)
        if not isinstance(values, list):
            error(path + "." + key, "must be an array of strings")
            return []
        if any(not isinstance(value, str) or not value.strip() for value in values):
            error(path + "." + key, "must contain only nonempty strings")
            return []
        if len(values) != len(set(values)):
            error(path + "." + key, "must not contain duplicates")
        if valid_ids is not None:
            for value in values:
                if value not in valid_ids:
                    error(path + "." + key, "unknown ID " + value)
        return values

    request = state.get("request")
    root = request.get("root_task_id") if isinstance(request, dict) else None
    if not isinstance(root, str) or not root.strip():
        error("request.root_task_id", "must be a nonempty string")
        root = None
    records = state.get("tasks")
    if not isinstance(records, list):
        error("tasks", "must be an array of tables")
        records = []
    if not records:
        error("tasks", "must contain at least one table")
    for index, item in enumerate(records):
        path = "tasks[{}]".format(index)
        if not isinstance(item, dict):
            error(path, "must be a table")
            continue
        task_id = item.get("id")
        if not isinstance(task_id, str) or not task_id.strip():
            error(path + ".id", "must be a nonempty string")
            continue
        if task_id in tasks:
            error(path + ".id", "duplicate ID " + task_id)
            continue
        tasks[task_id], positions[task_id] = item, index
    if root is not None and root not in tasks:
        error("request.root_task_id", "unknown task ID " + root)
    children = {task_id: [] for task_id in tasks}
    parents, dependencies = {}, {}
    requirements = state.get("requirements")
    requirement_ids = {
        item["id"] for item in requirements
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    } if isinstance(requirements, list) else set()
    requirement_links = {}
    for task_id, item in tasks.items():
        path = "tasks[{}]".format(positions[task_id])
        title = item.get("title")
        if not isinstance(title, str) or not title.strip():
            error(path + ".title", "must be a nonempty string")
        dependencies[task_id] = strings(item, "depends_on", path, tasks)
        requirement_links[task_id] = strings(item, "requirement_ids", path, requirement_ids)
        if task_id == root:
            if "parent_id" in item:
                error(path + ".parent_id", "the root task must omit parent_id")
            continue
        parent = item.get("parent_id")
        if not isinstance(parent, str) or not parent.strip():
            error(path + ".parent_id", "nonroot tasks require a nonempty parent ID")
        elif parent not in tasks:
            error(path + ".parent_id", "unknown task ID " + parent)
        else:
            parents[task_id] = parent
            children[parent].append(task_id)
    reached, pending = set(), [root] if root in tasks else []
    while pending:
        task_id = pending.pop()
        if task_id not in reached:
            reached.add(task_id)
            pending.extend(children[task_id])
    if set(tasks) - reached:
        error("tasks", "hierarchy is disconnected from the root: "
              + ", ".join(sorted(set(tasks) - reached)))
    # Bottom-up reduction both detects parent cycles and derives leaf scopes.
    remaining = {task_id: len(values) for task_id, values in children.items()}
    pending = [task_id for task_id, count in remaining.items() if count == 0]
    leaves = list(pending)
    descendants, statuses = {}, {}
    while pending:
        task_id = pending.pop()
        child_ids = children[task_id]
        descendants[task_id] = (set().union(*(descendants[child] for child in child_ids))
                                if child_ids else {task_id})
        if child_ids:
            child_statuses = {statuses[child] for child in child_ids}
            statuses[task_id] = ("done" if child_statuses == {"done"} else
                                 "pending" if child_statuses == {"pending"} else "running")
        else:
            # Invalid values are checked by the shared leaf validator below.
            value = tasks[task_id].get("status")
            statuses[task_id] = value if isinstance(value, str) else "pending"
        remaining.pop(task_id)
        parent = parents.get(task_id)
        if parent in remaining:
            remaining[parent] -= 1
            if remaining[parent] == 0:
                pending.append(parent)
    if remaining:
        error("tasks", "hierarchy cycle involving " + ", ".join(sorted(remaining)))
    for task_id, child_ids in children.items():
        if not child_ids:
            continue
        item, path = tasks[task_id], "tasks[{}]".format(positions[task_id])
        # Current state stores a status on every node. Historical schema 3 may
        # omit group statuses, but any supplied value must still be consistent.
        if state.get("schema_version") == 1 or "status" in item:
            value = item.get("status")
            if not isinstance(value, str) or value not in TASK_STATUSES:
                error(path + ".status", "must be one of: pending, running, done")
            elif task_id in statuses and value != statuses[task_id]:
                error(path + ".status", "must match descendant progress: " + statuses[task_id])
        for key in ("inputs", "done_when"):
            if key in item:
                strings(item, key, path)
        for key in ("deliverable", "verification"):
            if key in item and not isinstance(item[key], str):
                error(path + "." + key, "must be a string when supplied")
    effective = {leaf: set() for leaf in leaves}
    for source, targets in dependencies.items():
        for target in targets:
            source_leaves, target_leaves = descendants.get(source, set()), descendants.get(target, set())
            if source_leaves & target_leaves:
                error("tasks[{}].depends_on".format(positions[source]),
                      "dependency {} -> {} overlaps the same hierarchy branch".format(source, target))
            for leaf in source_leaves:
                effective[leaf].update(target_leaves)
    coverage = {
        requirement_id: sorted(leaf for leaf in leaves
                               if requirement_id in requirement_links[leaf])
        for requirement_id in sorted(requirement_ids)
    }
    dependents = {leaf: set() for leaf in leaves}
    for leaf, prerequisites in effective.items():
        for prerequisite in prerequisites:
            dependents[prerequisite].add(leaf)
    downstream_counts = {}
    for leaf in leaves:
        seen, pending = set(), list(dependents[leaf])
        while pending:
            dependent = pending.pop()
            if dependent not in seen:
                seen.add(dependent)
                pending.extend(dependents[dependent] - seen)
        downstream_counts[leaf] = len(seen - {leaf})
    graph = {
        "root_task_id": root,
        "children": children,
        "leaf_task_ids": leaves,
        "entry_task_ids": [leaf for leaf in leaves if not effective[leaf]],
        "effective_dependencies": {leaf: sorted(values) for leaf, values in effective.items()},
        "requirement_coverage": coverage,
        "covered_requirement_ids": [key for key, value in coverage.items() if value],
        "uncovered_requirement_ids": [key for key, value in coverage.items() if not value],
        "downstream_counts": downstream_counts,
        "task_statuses": statuses,
    }
    return graph, descendants, positions, errors


def _hierarchy_view(state):
    """Project only validated leaf semantics onto the shared v2 shape checks."""
    graph, descendants, positions, errors = _task_graph(state)
    view = copy.deepcopy(state)
    view["schema_version"] = 2
    request = state.get("request")
    if isinstance(request, dict):
        view["task"] = {key: copy.deepcopy(value) for key, value in request.items()}
        view["task"]["request"] = request.get("text")
    else:
        view["task"] = request
    if isinstance(view.get("gate"), dict):
        view["gate"]["subtask_threshold"] = view["gate"].get("leaf_threshold")
    records = state.get("tasks")
    records = records if isinstance(records, list) else []
    view["subtasks"] = []
    for leaf in graph["leaf_task_ids"]:
        item = copy.deepcopy(records[positions[leaf]])
        item["depends_on"] = graph["effective_dependencies"][leaf]
        view["subtasks"].append(item)
    for key in ("criteria", "decisions"):
        values = view.get(key)
        if not isinstance(values, list):
            continue
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                continue
            path = "{}[{}].task_ids".format(key, index)
            targets = item.get("task_ids")
            if not isinstance(targets, list):
                errors.append(path + ": must be an array of strings")
                targets = []
            elif any(not isinstance(target, str) or not target.strip() for target in targets):
                errors.append(path + ": must contain only nonempty strings")
                targets = []
            if not targets:
                errors.append(path + ": must contain at least one ID")
            if len(targets) != len(set(targets)):
                errors.append(path + ": must not contain duplicates")
            expanded = set()
            for target in targets:
                if target not in positions:
                    errors.append(path + ": unknown task ID " + target)
                expanded.update(descendants.get(target, set()))
            item["subtask_ids"] = sorted(expanded)
    return view, graph, descendants, positions, errors


def validate(state):
    """Validate current schema 1 or inspect legacy layouts without migration."""
    if not isinstance(state, dict):
        return ["state: must be a table"]
    version = state.get("schema_version")
    if not is_int(version) or version not in {1, 2, 3}:
        return ["schema_version: current schema must be integer 1 (legacy 2/3 are read-only)"]
    if not has_task_hierarchy(state):
        return _validate_legacy(state)
    if version == 2:
        return ["schema_version: hierarchical layout requires integer 1 (legacy 3 is read-only)"]
    if "task" in state or "subtasks" in state:
        return ["state: must not mix flat task/subtasks and hierarchical request/tasks layouts"]
    view, graph, _, positions, errors = _hierarchy_view(state)
    leaves = graph["leaf_task_ids"]
    for issue in _validate_legacy(view):
        issue = re.sub(r"subtasks\[(\d+)\]", lambda match: "tasks[{}]".format(
            positions[leaves[int(match.group(1))]]), issue)
        issue = issue.replace("task.request:", "request.text:")
        issue = re.sub(r"\btask\.", "request.", issue)
        issue = re.sub(r"^task:", "request:", issue)
        issue = issue.replace("subtask_ids", "task_ids").replace("subtask_threshold", "leaf_threshold")
        issue = issue.replace("subtasks", "tasks").replace("subtask", "leaf task")
        errors.append(issue)
    return list(dict.fromkeys(errors))


def current_evaluation(state):
    """The last recorded result with the exact current input/rubric revision."""
    session = state["session"]
    return next((item for item in reversed(state["evaluations"])
                 if item["revision"] == session["revision"]
                 and item["criteria_version"] == session["criteria_version"]), None)


def graph_diagnostics(state):
    """Describe traceability and unique downstream reach in a validated DAG."""
    if has_task_hierarchy(state):
        return _task_graph(state)[0]
    requirements = state["requirements"] if state["schema_version"] == 2 else []
    requirement_ids = {item["id"] for item in requirements}
    covered = {
        requirement_id for item in state["subtasks"]
        for requirement_id in (item["requirement_ids"] if state["schema_version"] == 2 else [])
    }
    children = {item["id"]: set() for item in state["subtasks"]}
    for item in state["subtasks"]:
        for dependency in item["depends_on"]:
            children[dependency].add(item["id"])
    downstream_counts = {}
    for subtask_id in children:
        seen, pending = set(), list(children[subtask_id])
        while pending:
            descendant = pending.pop()
            if descendant not in seen:
                seen.add(descendant)
                pending.extend(children[descendant] - seen)
        downstream_counts[subtask_id] = len(seen)
    return {
        "covered_requirement_ids": sorted(requirement_ids & covered),
        "uncovered_requirement_ids": sorted(requirement_ids - covered),
        "entry_subtask_ids": [item["id"] for item in state["subtasks"]
                              if not item["depends_on"]],
        "downstream_counts": downstream_counts,
    }


def score(state):
    """Compute readiness from validated state, using exact values for gating."""
    errors = validate(state)
    if errors:
        raise ValueError("Invalid state: " + "; ".join(errors))
    original = state
    hierarchy = has_task_hierarchy(state)
    descendants = {}
    if hierarchy:
        state, _, descendants, _, _ = _hierarchy_view(state)
    blockers = []
    criteria = state["criteria"]
    evaluation = current_evaluation(state)
    result = {
        "overall_score": 0.0,
        "subtask_scores": {item["id"]: 0.0 for item in state["subtasks"]},
        "criterion_scores": {item["id"]: 0 for item in criteria},
        "passed": False,
        "blockers": blockers,
        "graph": graph_diagnostics(original),
    }
    if hierarchy:
        result["leaf_scores"] = result.pop("subtask_scores")
        result["task_scores"] = {item["id"]: 0.0 for item in original["tasks"]}
    if not is_current_schema(original):
        blockers.append(UPGRADE_REQUIRED)
    if not criteria:
        blockers.append("No criteria are defined.")
    if not state["subtasks"]:
        blockers.append("No subtasks are defined.")
    if not state["task"]["success"].strip():
        blockers.append("The task has no observable success check.")
    active = {
        item["id"] for item in state["evidence"]
        if item["status"] == "active"
        and item["text"].strip() and item["source"].strip()
    }
    accepted = {item["id"] for item in state["evidence"]
                if item["accepted"] and item["id"] in active}
    if state["schema_version"] == 2:
        for requirement in state["requirements"]:
            if not accepted.intersection(requirement["evidence_ids"]):
                blockers.append("Requirement {} lacks active accepted evidence.".format(
                    requirement["id"]))
        for subtask in state["subtasks"]:
            label = "Leaf task" if hierarchy else "Subtask"
            if not subtask["done_when"]:
                blockers.append("{} {} has no observable completion conditions.".format(
                    label, subtask["id"]))
            if not subtask["verification"].strip():
                blockers.append("{} {} has no planned verification method.".format(
                    label, subtask["id"]))
    for decision in state["decisions"]:
        if decision["required"] and (
                decision["status"] != "resolved" or not decision["value"].strip()
                or not accepted.intersection(decision["evidence_ids"])):
            blockers.append("Required decision {} lacks a resolved value and active accepted evidence.".format(
                decision["id"]))
    if evaluation is None:
        blockers.append("No evaluation matches the current revision and criteria version.")
        return result
    if not evaluation["isolated"] or not evaluation["evaluator_id"].strip():
        blockers.append("The current evaluation lacks recorded fresh-worker provenance.")
    for key in ("rubric_gaps", "contradictions"):
        for item in evaluation[key]:
            blockers.append("{}: {}".format(key, item))
    ratings = {item["criterion_id"]: item for item in evaluation["ratings"]}
    decisions = {item["id"]: item for item in state["decisions"]}
    effective = result["criterion_scores"]
    for criterion in criteria:
        criterion_id = criterion["id"]
        rating = ratings[criterion_id]
        value = rating["score"]
        if value > 0:
            cited = set(rating["evidence_ids"])
            linked = set(criterion["evidence_ids"])
            for decision_id in criterion["decision_ids"]:
                linked.update(decisions[decision_id]["evidence_ids"])
            issues = []
            if not cited:
                issues.append("no supporting citations")
            for label, invalid in (("inactive citations", cited - active),
                                   ("unlinked citations", cited - linked),
                                   ("unaccepted citations", cited - accepted if value == 2 else set())):
                if invalid:
                    issues.append(label + ": " + ", ".join(sorted(invalid)))
            if issues:
                blockers.append("Criterion {} scored {} with invalid supporting evidence ({}); credited 0.".format(
                    criterion_id, value, "; ".join(issues)))
                value = 0
        effective[criterion_id] = value
        if criterion["required"] and value != 2:
            blockers.append("Required criterion {} must score 2 with evidence.".format(criterion_id))

    def weighted(items):
        total = sum(item["weight"] for item in items)
        return (Fraction(100 * sum(item["weight"] * effective[item["id"]] for item in items),
                         2 * total) if total else Fraction(0))

    overall = weighted(criteria)
    result["overall_score"] = round(float(overall), 6)
    if overall < Fraction(str(state["gate"]["overall_threshold"])):
        blockers.append("Overall score is below the configured threshold.")
    for subtask in state["subtasks"]:
        linked = [item for item in criteria if subtask["id"] in item["subtask_ids"]]
        subtotal = weighted(linked)
        result["leaf_scores" if hierarchy else "subtask_scores"][subtask["id"]] = round(float(subtotal), 6)
        if subtotal < Fraction(str(state["gate"]["subtask_threshold"])):
            blockers.append("{} {} is below the configured threshold.".format(
                "Leaf task" if hierarchy else "Subtask", subtask["id"]))
    if hierarchy:
        for task_id, leaf_ids in descendants.items():
            linked = [item for item in criteria if leaf_ids.intersection(item["subtask_ids"])]
            result["task_scores"][task_id] = round(float(weighted(linked)), 6)
    result["passed"] = not blockers
    return result


def pick(obj, keys):
    return {key: copy.deepcopy(obj[key]) for key in keys}


def packet(state, role):
    """Build an allowlisted input; transporting it to fresh context is external."""
    errors = validate(state)
    if errors:
        raise ValueError("Invalid state: " + "; ".join(errors))
    if role not in {"evaluator", "questioner"}:
        raise ValueError("Unknown worker role: " + role)
    if not is_current_schema(state):
        raise ValueError(UPGRADE_REQUIRED)
    result = {
        "schema_version": state["schema_version"],
        "session": pick(state["session"], ("id", "revision", "criteria_version")),
        "request": pick(state["request"], REQUEST_FIELDS),
    }
    task_fields = (
        "id", "title", "parent_id", "requirement_ids", "depends_on", "inputs",
        "deliverable", "done_when", "verification",
    )
    result["tasks"] = [pick(item, [key for key in task_fields if key in item])
                       for item in state["tasks"]]
    for key in ("requirements", "criteria", "decisions", "evidence"):
        fields = tuple("task_ids" if field == "subtask_ids" else field
                       for field in RECORD_FIELDS[key])
        if role == "evaluator" and key == "criteria":
            fields = tuple(field for field in fields if field != "weight")
        result[key] = [pick(item, fields) for item in state[key]]
    if role == "evaluator":
        profile_ids = {evidence_id for topic in state["user"]["topics"]
                       for evidence_id in topic["evidence_ids"]}
        task_evidence_ids = {evidence_id for key in ("requirements", "criteria", "decisions")
                             for item in state[key] for evidence_id in item["evidence_ids"]}
        profile_only = profile_ids - task_evidence_ids
        result["evidence"] = [item for item in result["evidence"]
                              if item["id"] not in profile_only]
    result["graph"] = graph_diagnostics(state)
    # Completion progress is never evidence of specification readiness.
    result["graph"].pop("task_statuses")
    if role == "questioner":
        evaluation = current_evaluation(state)
        if evaluation is None:
            raise ValueError("A questioner packet requires a current evaluation.")
        if not evaluation["isolated"] or not evaluation["evaluator_id"].strip():
            raise ValueError("A questioner packet requires recorded fresh-worker evaluator provenance.")
        result["gate"] = pick(state["gate"], ("overall_threshold", "leaf_threshold"))
        result["user"] = pick(state["user"], ("language", "explanation_level", "preferred_style"))
        result["user"]["topics"] = [pick(item, ("name", "familiarity", "confidence", "evidence_ids"))
                                    for item in state["user"]["topics"]]
        result["questions"] = [pick(item, RECORD_FIELDS["questions"]) for item in state["questions"]]
        for source, projected in zip(state["questions"], result["questions"]):
            if "options" in source:
                projected["options"] = copy.deepcopy(source["options"])
        result["attempts"] = []
        for source in state.get("attempts", []):
            projected = pick(source, RECORD_FIELDS["attempts"])
            if "inspection" in source:
                projected["inspection"] = copy.deepcopy(source["inspection"])
            if "proposal" in source:
                projected["proposal"] = pick(source["proposal"], PROPOSAL_FIELDS)
            result["attempts"].append(projected)
        result["evaluation"] = pick(evaluation, RECORD_FIELDS["evaluations"])
        result["evaluation"]["ratings"] = [
            pick(item, ("criterion_id", "score", "reason", "evidence_ids"))
            for item in evaluation["ratings"]
        ]
        result["readiness"] = score(state)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("validate", "score", "packet"):
        subparser = commands.add_parser(command)
        subparser.add_argument("path", type=Path, help="Path to interview.toml")
        if command == "packet":
            subparser.add_argument("--role", choices=("evaluator", "questioner"), required=True)
    args = parser.parse_args(argv)
    try:
        if tomllib is None:
            raise ValueError("TOML parsing needs Python 3.11+ or tomli on Python 3.9/3.10.")
        with args.path.open("rb") as stream:
            state = tomllib.load(stream)
        errors = validate(state)
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
            return 1
        if args.command == "validate":
            result = {"valid": True, "errors": []}
        elif args.command == "score":
            result = score(state)
        else:
            result = packet(state, args.role)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
