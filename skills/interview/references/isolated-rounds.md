# Fresh evaluation and question sessions

Read this coordinator protocol when launching workers. Read only the selected
role contract: [evaluator](evaluator.md) or [questioner](questioner.md).
The boundary is no inherited conversation, not statistical independence. Shared
model errors, training, and biased recorded evidence can survive fresh sessions.
More agreeing judges cannot replace missing observations.

## Coordinator protocol

1. Complete any required [hierarchy review](task-refinement.md#redefine-the-hierarchy)
   and [recording-fidelity review](state-schema.md#storage-and-conversation-language).
   Validate the complete state and use `packet --role evaluator`. The helper
   includes the current request, requirements, recursive tree, leaf contracts,
   criteria, decisions, evidence, and graph diagnostics. It excludes thresholds,
   criterion weights, prior scores, completion statuses, user profile, and evidence
   linked exclusively to that profile. Keep profile-only observations separate
   from task evidence when recording them; mixed-purpose evidence remains visible.
2. Reuse a valid current evaluation if its task inputs are unchanged, including
   after profile-only or attempt-history updates; skip to the gate in step 4.
   Otherwise start a **new** worker with only the [evaluator contract](evaluator.md) and that
   packet. Use `spawn_agent(..., fork_turns="none", message=...)` when available;
   verify the runtime's actual schema. Do not pass the coordinator transcript,
   other role instructions, research, README, or earlier worker output.
3. Check the exact packet is unchanged when the result arrives, not only its
   revision fields. Require every current criterion once, valid evidence IDs,
   and brief support/gap reasons. Attach the worker ID and isolation provenance
   from the actual tool result; the worker cannot self-certify. Persist the report
   and recompute the gate with `score`. Use credited `criterion_scores`, not raw
   unsupported ratings. A semantic mismatch or omitted fact needs repair, not
   another identical run hoping for a higher score.
4. Apply the gate to the valid current report. On pass, present the requirements
   and task hierarchy. Otherwise route remaining gaps through a fresh questioner,
   including substantive hierarchy and rubric findings. Keep technical recovery
   for invalid state, incomplete packets, or unusable reports separate: restore
   valid inputs before attempting another round, without asking for supplied facts.
5. For a failed gate, build `packet --role questioner`.
   It includes the current evaluation and credited gate result, question and
   resolution-attempt history, and explanation profile. An evaluation without recorded fresh-worker provenance
   cannot supply this packet. Launch a **different new** worker with only the
   [questioner contract](questioner.md) and packet; never reuse an old worker.
6. Check that the exact questioner packet is still current, including profile
   and history; revision equality alone is insufficient. Validate targets, action,
   and useful execution difference. Increment `session.round` for each accepted
   questioner selection, including non-question actions. Attach the actual worker
   ID and isolation provenance. Persist a question's choices and reason in
   `questions`, or a non-question plan in [attempts](state-schema.md#resolution-attempts)
   before acting. If localization is needed for
   delivery, preserve the question's meaning. For a batch,
   store each question with its own ID and the same round/revision. A pause adds
   an attempt, not a question; record `paused`. Perform the selected user-question or non-user
   resolution route. For a method choice without user input, use
   [web research and default selection](web-defaults.md); a search proposal can
   use `action="inspect"` with the query and selection checks in `inspection`.
   Update the attempt with its actual outcome and evidence, even on failure.
   Record answers or findings, refine requirements, and return to hierarchy
   review. A changed input retires stale pending questions.

Inspection, web-search, and experiment outputs are proposals, not user answers.
The coordinator checks existing authorization, performs permitted work, and saves
actual results, including inconclusive findings. Retain unsuccessful plans so the
next questioner can choose another route instead of repeating them. Experiment proposals need a
method, stopping condition, expected evidence, and the decision they inform.
All resolution routes return to main-session requirements and hierarchy review.
Changed task inputs require fresh evaluation; unchanged inputs retain the current
result. No action's completion clears a failed gate by itself.

## Context and recovery

The full history stays in `interview.toml`; worker inputs are read-only projections.
Prefer concise, atomic evidence records with conditions and provenance over copied
chat passages. Retain active counterevidence and unlinked task facts needed to
catch incomplete requirements. Never remove a constraint merely to fit a budget.
Workers have no tools: a path or summary alone cannot replace needed source facts.
If a packet is incomplete, restore it as coordinator and retry with fresh context.
If complete coverage cannot fit the available context, report `blocked` with the
specific limitation; a silently truncated assessment cannot be a whole-task pass.

Discard stale outputs. Retry malformed results in a new worker with the same
inputs and contract, not its previous chat. After two malformed outputs for one
role, record `blocked` with the actual failure. If the runtime reports a temporary
capacity limit, let unrelated running work finish and retry one fresh launch;
never reuse or interrupt an unrelated worker merely to make room. If isolation
remains unavailable, record `blocked` and the limitation. Never substitute a
non-isolated worker, even when the user elects to proceed with known task gaps.

Workers are internal subtasks, not persistent user-visible chats. Do not launch
external services merely to implement isolation. The coordinator owns source
fidelity, translation, authorization, and state writes; fresh workers do not.

## Evaluator contract

Moved to [evaluator.md](evaluator.md) so unrelated question instructions are not
loaded into an evaluator's context.

## Questioner contract

Moved to [questioner.md](questioner.md). Read it only when selecting a next step;
pass neither this protocol nor the evaluator contract to the questioner.
