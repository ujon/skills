---
name: interview
description: Guide requirements discovery through adaptive, in-depth interviews. Surface implicit assumptions, resolve ambiguity, and establish clear scope and acceptance criteria. Progressively decompose the emerging specification into a coherent hierarchy of tasks and subtasks. Use to develop an initial idea or request into detailed, traceable requirements and a structured task breakdown; not job interview practice.
author: ujon
version: "1.0.0"
interview_schema: "1"
---

# Interview

Develop the user's initial intent into a precise specification through adaptive
requirements discovery. Probe ambiguous language, uncover implicit assumptions,
and establish the desired behavior, scope, constraints, and acceptance criteria.
Refine the requirements and task hierarchy together: each answer sharpens the
specification, while each task boundary reveals the next question worth asking.

The result is a detailed requirements brief and task hierarchy in `interview.toml`.
Evaluation helps locate unresolved ambiguity and decide when the interview is
sufficient; a passing score is not the purpose of the conversation. Continue into
implementation only when the user also requested that work.

## Operating contract

- The coordinator talks to the user, decomposes and revises tasks in the main
  session, and is the only writer of `interview.toml`.
  Keep task details, evidence, decisions, questions, resolution attempts, evaluations, and familiarity
  in that single file, without prescribing its storage directory.
  Set `schema_version` to the integer value of `interview_schema` in the frontmatter
  above. Input revisions and criterion versions advance independently of that
  setting and the skill version.
- Record user requests and answers faithfully. Preserve conditions, uncertainty,
  and provenance without duplicating transcripts. Keep exact identifiers, paths,
  URLs, and code usable.
- Use a **new evaluator** for each evaluation and a **different new questioner**
  for each next-step selection, with no
  inherited conversation. With collaboration tools, set `fork_turns="none"`.
  Never resume a previous worker or simulate isolation by changing roles in chat.
  Give each worker only its role contract and the helper's current packet.
- If fresh contexts are unavailable, record `blocked` and the actual limitation.
  Do not replace either worker with an in-session role or reduced-isolation run.
  Proceeding with known gaps is not an isolation exception or a passing result.
  Worker agreement is not independent evidence.
- Distinguish sourced facts, user choices, and assistant assumptions. Silence,
  elapsed time, or a preselected answer is not a user answer. For an omitted or
  skipped method choice, use the [web default policy](references/web-defaults.md)
  to choose a widely used, compatible approach and record it as a default.

## Load only what this step needs

Do not preload the whole skill directory. Open the relevant section below and
reuse it while valid. Do not paste scripts, the README, examples, or research into
worker prompts. Splitting files saves context only when unused parts stay unloaded.

| Current need | Read |
| --- | --- |
| Create, resume, or edit state | Relevant sections of [state-schema.md](references/state-schema.md); use [the template](assets/interview.template.toml) only for new state |
| Decompose work or revise hierarchy | Relevant section of [task-refinement.md](references/task-refinement.md) |
| Run or recover a worker round | [isolated-rounds.md](references/isolated-rounds.md) |
| Score evidence | Only [evaluator.md](references/evaluator.md) plus the evaluator packet |
| Select the next question or evidence-gathering step | Only [questioner.md](references/questioner.md) plus the questioner packet |
| Choose a method without user input | [web-defaults.md](references/web-defaults.md); coordinator only |
| Research-topic interview | [research-topics.md](references/research-topics.md) |
| Inspect the saved graph | [Viewer instructions](README.md#inspect-the-graph) |
| Maintain, benchmark, or explain the design | [Research and evaluation](references/research-and-evaluation.md); not routine interview context |

Keep the original request, active constraints, exclusions, decisions, and source
links intact when reducing context. Never replace them with an optimistic summary
or silently truncate a packet. Report missing context for coordinator repair;
a partial view cannot support a whole-task pass.

## Interview loop

Follow the [workflow diagram](assets/interview-flow.svg). Discovery has three
distinct lenses; they inform one provisional tree, not three mandatory workstreams.

1. **Establish the request.** Load or create `interview.toml`, reconcile earlier
   answers and corrections, and preserve the complete request in `request.text`.
   Reuse matching state without erasing another task or invalid file. Inspect
   supplied sources before asking for facts already available there.
2. **Define the desired outcome.** Identify who needs what change and how success
   would be observed. Keep competing interpretations and exclusions explicit;
   do not invent a goal to fill a field.
3. **Explore possible approaches.** Identify plausible ways to reach the outcome,
   their material tradeoffs, and unresolved method choices. Reuse compatible
   existing choices. Leave unanswered choices visible for the resolution branch.
4. **Identify necessary conditions.** Record required inputs, capabilities,
   prerequisites, constraints, and limits. Distinguish known conditions from
   assumptions and missing facts; connect them to affected requirements.
5. **Draft and review the task hierarchy.** Map the discovery results to leaves.
   All depths use `tasks`; `parent_id` means ownership, `depends_on` prerequisites.
   Every task, including roots and groups, stores `status` as `pending`, `running`,
   or `done`; follow the [status rules](references/state-schema.md#task-status).
   Give leaves inputs, deliverables, completion conditions, and verification.
   Split recursively where a task still hides an unresolved result or choice;
   keep early contracts provisional and preserve supported work and stable IDs.
6. **Define checks for each task.** Give each criterion a check for score 2,
   task IDs, positive weight, required status, and evidence/decision links. Cover
   material inputs and choices. Separate independently blocking checks without
   duplicating criteria; unknowns remain explicit.
7. **Evaluate the remaining gaps.** Advance the input revision for changed task inputs
   and the criteria version for changed rubric meaning or scope. Validate and
   save the complete candidate, then launch
   a fresh evaluator. Verify its report and provenance and recompute the gate.
   Reuse a valid current evaluation when task inputs are unchanged; profile-only
   changes and attempt history alone do not require another evaluation.
   Invalid state, stale reports, or incomplete packets use technical recovery
   in [isolated-rounds.md](references/isolated-rounds.md), not a fabricated pass.
8. **Apply the readiness gate.** On pass, record `ready` and present requirements,
   task hierarchy, completion checks, decisions, and adopted defaults. The
   interview is complete; implement only if also requested. Otherwise launch a
   different fresh questioner to choose the next gap and its resolution route,
   including substantive hierarchy or rubric repairs found by the evaluator.
9. **Resolve the selected gap.** If user input is needed, record and relay one
   plain question, then wait for its answer. If a method choice has no user input,
   search the web and adopt a widely used compatible method under the
   [default policy](references/web-defaults.md). Other non-user routes inspect
   sources, run an authorized bounded experiment, or repair the structure.
   The coordinator performs these actions; workers only propose them. Persist
   each selected non-question action and its result in `attempts`, including
   failed or inconclusive outcomes, under the [recording rules](references/state-schema.md#resolution-attempts).
10. **Refine requirements and reshape tasks.** Integrate answers or findings with
    their reasons, conditions, sources, and exclusions. Revisit steps 2–4 when
    they change, then [review the hierarchy](references/task-refinement.md#redefine-the-hierarchy):
    keep, split, merge, move, or regroup. Save one candidate transition, retire
    stale questions, and repeat from steps 5–7 using current evidence. Unchanged
    inputs need no repeat evaluation; nondependent authorized work may continue.

There is no minimum question count. The questioner compares plausible answers:
ask only when they change an outcome, constraint, leaf contract, or next action.
An answer that still permits materially different interpretations needs a focused
follow-up, even when the corresponding field is nonempty. Explore examples,
exceptions, or boundaries where they clarify the requirement, not as a checklist.
Prioritize required blockers, then useful distinctions and the user's ability
and effort to answer. Model uncertainty alone is not a reason to question the
user. The questioner's `why` records the concrete difference, not invented
probabilities or a claimed numerical information gain.

## Readiness gate

| Score | Evidence state |
| --- | --- |
| 0 | Missing, conflicting, or unusable |
| 1 | Partly specified, with cited active evidence and an explicit remaining gap |
| 2 | The whole check is supported by active accepted evidence; required linked decisions are resolved |

Positive ratings must cite evidence linked to the criterion or its decisions.
The helper credits unsupported ratings as zero; the evaluator still checks what
the evidence means. The default gate requires overall score >= 90, every leaf
>= 80, every required criterion at 2, all required decisions resolved, valid
coverage and graph structure, no material contradictions or rubric gaps, and a
current isolated evaluation. Shared criteria count once; groups are not averages.
These thresholds are policy settings, not calibrated probabilities. Never lower
them or retry unchanged valid evaluations merely to obtain a pass.

Use [interview_state.py](scripts/interview_state.py) to `validate`, `score`, and
build `packet --role evaluator` or `packet --role questioner`. It is read-only;
it cannot prove semantic truth, translation fidelity, or actual worker isolation.
Readiness is not completed execution. Reopen the loop when execution reveals a
blocker, and check the deliverable against the leaf's completion conditions.

## Conversation and stopping

Start at ELI5 level: short sentences, everyday words, one idea per question.
Use simple examples and neutral comparisons; a brief restatement is useful only
when it can reveal a task-relevant misunderstanding, never as a mandatory test.
This applies the Feynman and Socratic techniques without a fixed question ladder.
Track topic familiarity and explanation preference separately, with evidence and
confidence. Never infer IQ or global ability. Increase detail after repeated
observed comfort or an explicit request; simplify immediately on request.
`user.language` guides conversational wording; no storage language is prescribed.

Default to one question with optional neutral choices, free text, and "I don't
know." Honor explicit batches and budgets. A structured question tool is optional.
If no useful question remains, route to evidence gathering, a smaller scope, or
pause immediately; two rounds without new evidence on one blocker are a backstop,
not a required quota. This never clears a failed gate. Answer side questions
briefly, then resume. On stop, record `paused`; on an explicit request to proceed
with gaps, record `overridden`, preserve the failed result and unresolved gaps,
and do only authorized feasible work. Readiness creates no new permission.
