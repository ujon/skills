# The single state file

Contents: [Language](#storage-and-conversation-language) · [Resume](#schema-version-and-resume) · [Tables](#tables) ·
[Hierarchy](#task-hierarchy-and-leaf-coverage) · [Status](#task-status) · [Dependencies](#execution-dependencies) ·
[Scoring](#criterion-scope-and-scores) · [Evidence](#evidence-and-revisions) · [Attempts](#resolution-attempts) ·
[Example](#evaluation-output-example) · [Helper](#helper) ·
[Visual snapshot](#optional-visual-snapshot)

The coordinator alone writes one `interview.toml`, with no prescribed directory.
Workers return messages; packets and optional HTML snapshots are derived views,
not additional state files. Use [the template](../assets/interview.template.toml)
only for new state, replacing sample facts and assigning a unique session ID.
Resume a matching task. Do not overwrite invalid state or another task without
resolving the issue; obtain confirmation before discarding another task. Preserve
unrecognized fields and history.

## Storage and conversation language

No storage language is prescribed for `interview.toml`, worker packets, or
results. Preserve user requests and answers faithfully, including uncertainty,
conditions, exclusions, and provenance. Do not create duplicate transcripts.
`request.text` must retain the complete original request independently of
requirement extraction, not a shortened requirements summary.

`user.language` records the preferred conversation language as a language code
or name and guides question wording. If translation or localization is needed,
preserve meaning and ambiguity without adding interpretations or commitments;
record translation provenance where relevant. Keep exact identifiers, paths,
URLs, and code unchanged. Persist questions and answers with their source links.

On resume, retain existing prose rather than translating it solely to normalize
language. Apply corrections without losing IDs, facts, history, or provenance.
If stored task inputs change, record the reason, advance `session.revision`, retire
stale pending questions, and reevaluate before reusing readiness. Translation
alone does not change `criteria_version`; semantic corrections follow the normal
versioning rules. Profile-only wording changes follow the exception below.
Do not repeat answered questions merely to translate them.

## Schema version and resume

Set `schema_version` from the integer `interview_schema` setting in
[SKILL.md](../SKILL.md). The current release implements hierarchical schema 1;
changing the setting alone does not implement another schema. Input revisions,
criterion versions, and skill releases are independent counters.

Earlier flat layouts labeled 1/2 (`task` and `subtasks`) and hierarchical layout 3
are read-only: inspection cannot pass readiness or produce worker packets.
Distinguish structure as well as number; the helper never silently migrates.
Only when resuming one of these formats, apply the relevant conversion:

| Earlier layout | Conversion |
| --- | --- |
| Flat 2 | Rename `task` to `request`, its `request` field to `text`, `subtasks` to `tasks`, `subtask_ids` to `task_ids`, and `subtask_threshold` to `leaf_threshold`. Add a unique root and parent links, preserving existing IDs. |
| Flat 1 | Apply the flat-2 conversion; also extract evidenced requirements, map them to leaves, and fill known `inputs`, `done_when`, and `verification`. |
| Hierarchical 3 | Preserve the existing layout and update the schema label. |

Preserve evidence, profile, history, unknown fields, and stable IDs. Repair any
missing contracts in either flat layout from known information; leave unknowns
explicit. Do not invent groups, requirements, or dependency order during migration.
Set the configured schema label, advance input and criterion versions, record the
reason, mark pending questions `superseded`, and return to `interviewing`. Validate
and obtain a fresh evaluation; do not reuse an old pass or ask for answered facts.
For an existing hierarchy that omits group statuses, fill them bottom-up from
recorded leaf progress before validation. This status-only repair does not change
input or criterion versions; never infer execution progress from readiness scores.

## Tables

| Table | Required content |
| --- | --- |
| `session` | `id`, task-input `revision`, `criteria_version`, questioner-selection `round`, `status` |
| `request` | Complete record of the original request in `text`, `goal`, `scope`, `out_of_scope`, observable `success` (empty while unknown), `root_task_id` |
| `requirements[]` | Unique `id`, `description`, `kind` (`outcome`, `constraint`), `evidence_ids` |
| `gate` | `overall_threshold` (default 90), `leaf_threshold` (default 80); both greater than 0 and at most 100 |
| `user` | Conversation-language preference `language`, `explanation_level` (1–3), `preferred_style` |
| `user.topics[]` | `name`, `familiarity` (`unknown`, `beginner`, `working`, `advanced`), `confidence` (`low`, `medium`, `high`), `evidence_ids` |
| `tasks[]` | Unique `id`, `title`, `status`, `requirement_ids`, `depends_on` (task IDs); every task except the root also has `parent_id`; leaf contract fields are described below |
| `evidence[]` | Unique `id`, `kind` (`user`, `artifact`, `assumption`), `text`, `source`, `accepted` (boolean), `status` (`active`, `superseded`) |
| `decisions[]` | Unique `id`, `question`, `status` (`open`, `resolved`, `deferred`), `value`, `required`, `task_ids`, `evidence_ids` |
| `criteria[]` | Unique `id`, `description`, observable `check`, `task_ids`, positive integer `weight`, `required`, `evidence_ids`, `decision_ids` |
| `questions[]` | Unique `id`, input `revision`, `round`, `generator_id`, `isolated`, `targets` (criterion IDs), `text`, `status` (`pending`, `answered`, `skipped`, `superseded`), `answer_evidence_ids` |
| `attempts[]` (optional) | Non-question plans, outcomes, evidence, and worker provenance; see [resolution attempts](#resolution-attempts). Absent means empty. |
| `evaluations[]` | Unique `id`, input `revision`, `criteria_version`, `evaluator_id`, `isolated`, `rubric_gaps`, `contradictions`, `ratings[]` |
| `evaluations[].ratings[]` | `criterion_id`, integer `score` (0–2), `reason`, `evidence_ids` |
| `changes[]` | `revision`, `reason`; record hierarchy, scope, rubric, threshold, and user-requested override changes |

Questions may also store `options` (an array of short strings) and `why` (the
generator's brief reason). Historical question targets and evaluation rating IDs
may reference retired criteria after a scope change; current ones must resolve.
Keep historical evidence records so their references remain valid.

Session statuses are `interviewing`, `ready`, `executing`, `completed`, `paused`,
`blocked`, and `overridden`. `ready` means the information gate passed, not that
the deliverable is complete. `overridden` records a user request to proceed with
known gaps; it must not masquerade as a pass.

## Task hierarchy and leaf coverage

All depths use `[[tasks]]` and one ID namespace. `request.root_task_id` selects
the sole root, which omits `parent_id`; every other node has an existing parent.
Require one connected acyclic tree. Derive children: a node with children is a
group, otherwise a leaf. Do not persist a separate kind or child list. A root
may itself be executable.

Every leaf requires these execution fields:

| Field | Meaning |
| --- | --- |
| `inputs` | Array of materials/upstream outputs; empty when no additional input is needed |
| `deliverable` | Concrete result |
| `done_when` | Array of observable completion conditions |
| `verification` | String describing how those conditions will be checked |

Empty `done_when` or `verification` is valid incomplete state but blocks readiness.
These are planned checks; the deliverable need not exist before planning.
Groups may retain optional contracts as parent intent, which descendants must
fulfill even though those fields have no separate mechanical gate. Additional
integration/acceptance work needs a leaf. Every node stores execution status
under the rules below.

Require nonempty `requirements`, explicit `requirement_ids` on every leaf, and
at least one leaf per requirement. Groups may have no requirement links; their
links do not propagate. Readiness needs active accepted evidence for each
requirement. Broad requirements still need actionable leaf contracts and criteria.
Keep exclusions outside implementation work.

## Task status

Every saved task has a `status`, including the root and intermediate groups.

| Value | Executable leaf | Group |
| --- | --- | --- |
| `pending` | Execution has not started | All descendant leaves are pending |
| `running` | Execution has started but completion checks are not all satisfied | Some work has started or finished, but not every descendant leaf is done |
| `done` | The deliverable satisfies all `done_when` conditions, verified by the specified method | Every descendant leaf is done |

Create new work as `pending`. Move to `running` when execution starts and to
`done` only after verification. Reopen `done` work as `running` if its completion
conditions no longer hold. A pause or blocker does not erase progress; record its
reason and use the session's pause/block mechanism rather than inventing a task
status. Readiness and permission are separate from execution progress.

After any leaf-status or hierarchy change, recompute and persist affected group
statuses bottom-up in the same candidate, including both old and new ancestors
after a move. The helper rejects missing, unknown, or inconsistent statuses;
it does not silently rewrite them. Group completion cannot omit integration work.
Worker task projections deliberately omit progress to avoid biasing evaluation;
the canonical task records always retain it.

## Execution dependencies

`parent_id` means ownership or decomposition. `depends_on` means execution order;
it must not be used merely to draw the hierarchy. Each dependency can reference
a leaf or group. If B depends on A, every descendant leaf of B depends on every
descendant leaf of A, treating a leaf as its own one-element set. Thus a group
dependency is a barrier between whole branches. Use it only when the complete
prerequisite branch must finish first; normally target the specific leaves that
produce and consume the relevant output.

Reject self-dependencies and dependencies between overlapping branches, including
an ancestor and its descendant. After expanding group dependencies, the effective
leaf graph must also be acyclic; an acyclic-looking list of group IDs is not
sufficient. Validate all references before using the graph to order execution.

## Criterion scope and scores

Every leaf needs at least one effective criterion. `criteria[].task_ids` and
`decisions[].task_ids` may target leaves or groups. Targeting a group applies the
criterion or decision to all its descendant leaves. For a child-specific choice
or check, target that child instead. Deduplicate overlapping targets: a criterion
listed for both a parent and child still applies only once to that leaf.

Count each criterion once in the overall weighted score and once in each leaf's
weighted score. In `task_scores`, a group's score uses the union of effective
criteria across its descendant leaves, with each criterion counted once; never
average child scores or count shared criteria once per child. Apply
`leaf_threshold` to every leaf, not to groups. Any failing leaf blocks readiness
even when its parent's score is high. Required criteria and required decisions
remain blockers regardless of weighted averages.

For any covered set, readiness is
`100 * sum(weight * credited_score) / (2 * sum(weight))`.
An empty rubric cannot pass.

Positive ratings require nonempty citations, all active and bound to that
criterion through its `evidence_ids` or its linked decisions' `evidence_ids`.
For score 2, every cited record must also be accepted. A score-0 rating may cite
historical evidence to explain a conflict; that citation earns no credit. The
helper credits a rating that violates these support rules as 0 and reports a
blocker. A valid ID or link still does not establish semantic support: the
evaluator must explain how the cited evidence satisfies the criterion's `check`.
Repair omitted links only when the evidence actually supports that criterion,
advance the input revision, and reevaluate. A bookkeeping defect does not itself
require another user question.

For structural edits, use [hierarchy redefinition](task-refinement.md#redefine-the-hierarchy).
It preserves effective scopes, handoffs, IDs, and verified progress and records
retired contracts in `changes.reason`. Do not leave retired nodes in the live tree
or remove requested work merely to improve its score.

## Evidence and revisions

Record user wording or a faithful extract with its source. Keep artifact findings
with exact paths/URLs. Assistant suggestions remain `kind = "assumption"` and
`accepted = false` until adopted by the user, selected under explicit delegation
or the [web default policy](web-defaults.md), or verified by new artifact evidence.
Record the adoption basis and resulting choice separately from source findings;
an accepted assumption does not become a user answer or an observed fact.
Objective checks need actual inspection/tool results.

Separate profile-only evidence from task facts, even when supplied in one answer.
Link task evidence to requirements, criteria, or decisions; familiarity cannot
resolve them. Corrections supersede affected evidence while retaining its history
and all unaffected conditions. Do not turn translation into a commitment, erase a
conflict, or lower a threshold to force a pass.

| Change | Version update |
| --- | --- |
| Request, requirements, graph, task evidence, decisions, criteria, or gate | Advance `session.revision` once per candidate transition |
| Criterion meaning, membership, effective leaf scope, weight, required status, or thresholds | Also advance `criteria_version` and record why |
| Task evidence links or faithful translation of task inputs | Input revision only |
| Profile preferences/familiarity or exclusively profile-linked evidence, with evaluator inputs unchanged | Neither input nor criterion version |
| Append worker outputs or attempt history, update execution status, or increment selection round, without task-input changes | Neither input nor criterion version |

Answers create sourced evidence linked from their questions. Apply an answer and
its resulting hierarchy edits in one transition, without double-incrementing.
Preserve evaluations but accept only current input/criterion versions. Also compare
the exact role packet before and after a worker runs; matching version numbers
cannot rescue changed inputs. A profile-only update preserves the evaluator
packet and current evaluation but changes the questioner packet. Discard a
questioner response prepared against the old profile or history. Reword a pending
question without changing its meaning when needed; do not re-ask answered facts.
Changes to task inputs supersede stale pending questions and require reevaluation
before a dependent follow-up. Superseded is not user-skipped.

Do not run another evaluator just because an inspection failed or explanation
preferences changed. Reuse its valid current result and send updated history or
profile to a fresh questioner. If a finding also changes task facts or choices,
advance the revision and reevaluate. Profile-only evidence must be linked to the
profile and remain unlinked to requirements, criteria, and decisions to qualify.

Worker IDs and `isolated = true` record coordinator-observed fresh launches, never
a model's assertion. See [the launch protocol](isolated-rounds.md).

## Resolution attempts

Optional `[[attempts]]` preserves non-question actions under schema 1; existing
files need no migration. Each record has a unique `id`, task-input `revision`,
selection `round`, `generator_id`, boolean `isolated`, `action`, criterion-ID
`targets`, `why`, `status`, `result`, and `evidence_ids`.

| Action | Saved plan |
| --- | --- |
| `inspect` | Nonempty `inspection`: named source/check or web query/selection checks |
| `experiment` | `proposal` with nonempty `question`, `method`, `stop_condition`, `expected_evidence`, and `informs_decision` |
| `repair` | Concrete defect and affected IDs in `why` |
| `pause` | Remaining gap and reason in `why` |

Inspection and experiment targets must be nonempty. Current targets must resolve;
historical ones may reference retired criteria. Retain evidence records for all
references. Copy the accepted plan and actual launch provenance before acting;
workers cannot certify their own isolation. Empty worker IDs or false isolation
are permitted only to represent historical provenance honestly, not to authorize
new non-isolated selections.

Start as `proposed`, use `running` while executing, then record `completed`,
`failed`, `inconclusive`, or `skipped`. `result` may be empty only before an
outcome; otherwise summarize what actually happened, including unsuccessful
searches, limitations, or why execution was skipped. A performed pause is
`completed` with its reason and session status `paused`. Update the same record;
retain its selection revision even when findings advance the task revision.
Store actual task findings separately as evidence and link them here. Never
turn the proposal, its completion, or an adopted default into a user answer.

The questioner receives this history, including unproductive and pending plans;
the evaluator receives relevant task evidence, not the action history. An attempt
cannot establish readiness or bypass authorization.

## Evaluation output example

Use the JSON shape in [evaluator.md](evaluator.md); persist its fields under
`[[evaluations]]` and `[[evaluations.ratings]]` after attaching the actual worker
ID and isolation flag. Include every current criterion, not just a sample rating.
No separate report file is needed.

Remove top-level `evaluations = []` before appending `[[evaluations]]`; TOML forbids
defining a key twice. The same applies to `questions`, `attempts`, and `changes`. Use a TOML-aware
editor when available, parse and validate the complete candidate, and replace
atomically when practical. Repair parse failures without resetting saved state.

## Helper

`scripts/interview_state.py` reads the file and prints JSON to standard output.
It never writes state, launches agents, or proves semantic truth or isolation.
Use Python 3.11+ (or Python 3.9+ with `tomli` installed).

```sh
python3 /path/to/interview/scripts/interview_state.py validate interview.toml
python3 /path/to/interview/scripts/interview_state.py score interview.toml
python3 /path/to/interview/scripts/interview_state.py packet interview.toml --role evaluator
python3 /path/to/interview/scripts/interview_state.py packet interview.toml --role questioner
```

`validate` checks structure, not readiness. `score` recomputes `passed` and blockers
from the latest current evaluation; empty `request.success` blocks readiness.
An invalid file exits nonzero; a valid incomplete file yields `passed = false`.
Packet contents and provenance checks are defined in the
[coordinator protocol](isolated-rounds.md#coordinator-protocol).

Score output exposes:

- `criterion_scores`: credited support-checked ratings, also used by the viewer.
- `leaf_scores`: scores subject to `leaf_threshold`; `task_scores`: leaf/group
  criterion-union scores as defined above.
- `graph`: `root_task_id`, `children`, `leaf_task_ids`, prerequisite-free
  `entry_task_ids`, expanded `effective_dependencies`, `requirement_coverage`,
  derived `task_statuses`, and `downstream_counts` of distinct dependent leaves.

Counts describe the graph, not importance or the validity of its authored edges.
Worker task records and direct graph projections omit execution status; the
questioner's readiness result still contains the scoring graph. Evaluators
receive no readiness scores.

## Optional visual snapshot

Use [the viewer](../README.md#inspect-the-graph) on request. It reads TOML without
modifying it and creates an offline HTML snapshot with no AI/network calls.
Regenerate after state changes; it does not watch the file. The HTML is not worker
input or authoritative state. Historical layouts remain viewable with warnings;
visualization does not migrate them or bypass readiness checks.
