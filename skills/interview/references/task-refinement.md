# Build and refine the execution graph

Use this coordinator guide to build or revise the task hierarchy. Read the
section for the current operation; routine answers need not reload the whole
file. Storage, field types, and scoring belong to [state-schema.md](state-schema.md);
worker routing belongs to [isolated-rounds.md](isolated-rounds.md).

Treat decomposition as part of the interview: answers sharpen requirements and
reveal task boundaries; gaps in those tasks reveal what to ask next. Keep early
contracts provisional rather than inventing details to finish the tree upfront.

Contents: [Outcomes](#from-request-to-outcomes) · [Decomposition](#decompose-recursively) ·
[Hierarchy edits](#redefine-the-hierarchy) · [Leaves](#define-executable-leaves) ·
[Readiness](#readiness-versus-completion) · [Gap routing](#route-the-gap-before-asking) ·
[Answers](#refine-after-an-answer) · [Example](#example-small-change-then-a-new-boundary)

## From request to outcomes

Keep three discovery results distinct before drafting the tree: the desired
outcome, possible approaches, and necessary conditions. Record observable success
and exclusions; compare ways to achieve it and their unresolved tradeoffs; then
identify inputs, capabilities, prerequisites, and limits. These are lenses on the
same request, not automatic task groups. An approach without user input remains a
method gap for the [web default route](web-defaults.md), not an invented user choice.

Keep the complete request as the coverage reference. Extract independently
meaningful outcomes and constraints into evidence-linked `requirements`; keep
exclusions in `request.out_of_scope`. Do not replace the request with its summary
or turn an illustrative example into a commitment. Preserve unresolved meanings
such as “fast” until they affect the work; do not invent a target number.

For an existing system, inspect the relevant behavior and supplied sources
before asking for available facts. Record actual observations and their sources.
Existing behavior establishes what is present, not what the user wants changed.
Keep familiarity observations separate from task evidence.

## Decompose recursively

Work backward from observable outcomes. Start with the smallest useful tree,
which may be one executable root. Use one `tasks` namespace and `parent_id` at
all depths. Add a group only when it represents a meaningful outcome or shared
responsibility, not a standard phase list.

Split work when outputs, required decisions, input sources, completion checks,
or real prerequisite handoffs can be handled independently. Stop when a leaf
can be performed without an unrecorded material choice; depth and node count
are not quality measures. At each parent, check that its children collectively
fulfill its intended result and constraints. Represent additional integration
or acceptance work as a leaf; completing children does not perform omitted work.

Explicitly map requirements to leaves. Group-only requirement links do not
propagate. Criteria and decisions targeted at a group do apply to every descendant
leaf, so retain a group target only when its scope is truly shared.

`depends_on` records producer-to-consumer prerequisites, independently of the
hierarchy. A group dependency orders every leaf in both branches; prefer precise
leaf handoffs when a whole-branch barrier is unnecessary. Common parents, list
order, and similar subjects do not imply execution order. The helper checks
references and cycles; the coordinator checks whether each edge is needed.

## Redefine the hierarchy

Review the initial or resumed tree and revisit affected boundaries after new
answers, evidence, scope changes, execution blockers, or a worker's structural
finding. A low score alone is not a reason to reorganize. Keeping the tree is a
valid result; do not alternate equivalent structures without new evidence or a
concrete defect.

1. **Locate the effect.** Compare the change with the complete request and accepted
   evidence. Inspect affected parents, siblings, ancestors, and downstream
   consumers for omissions, duplicate work, or newly independent choices.
2. **Choose the smallest justified edit.** Use the operations below. Organizing
   authorized work needs no new permission. If an operation would decide a material
   product tradeoff, keep a valid provisional tree and record the open decision
   for the normal evaluator/questioner loop.

   | Operation | Preserve |
   | --- | --- |
   | Keep | Existing boundaries, IDs, and progress |
   | Split | Original ID as parent intent; new children with explicit contracts |
   | Merge | Combined obligations, external handoffs, and retired-to-current ID mapping |
   | Move or regroup | Same ID/status for unchanged work; updated parent links |
   | Remove a redundant wrapper | Children, retained parent intent, constraints, and effective references |

3. **Compare effective scope.** Before and after the edit, compare descendant leaf
   sets, criterion and decision coverage, explicit requirement mappings, and
   expanded prerequisite edges. Unchanged `task_ids` or `depends_on` can change
   meaning when a child moves. Preserve applicable old-parent obligations without
   inheriting unrelated new-parent constraints. Recheck affected siblings; remove
   merge-internal dependencies while retaining external producers and consumers.
4. **Preserve identity and progress.** Keep IDs whose meaning survives; use a new
   ID for materially different or combined work unless an existing contract still
   fits. Never recycle retired IDs. On split, retain the former contract as parent
   intent and assign leaf execution status based on verified work. Do not copy
   `done` to new children or merged work whose full contract is not satisfied.
   Reparent children before removing wrappers; retain one root and update its ID
   if necessary. An emptied group must not become a fictitious executable leaf.
   Keep `status` on every node and recompute affected groups bottom-up using the
   [status rules](state-schema.md#task-status), including old and new ancestors.
5. **Record one candidate transition.** Apply the answer and resulting graph edits
   together. Advance the input revision once; also advance `criteria_version` when
   criterion meaning, membership, or effective leaf scope changes. Other rubric
   changes follow the [revision rules](state-schema.md#evidence-and-revisions).
   In `changes.reason`, record the trigger, operation, affected IDs, old/new parent
   links, retired ID mappings, former contracts/statuses, and changed scopes or
   handoffs. Preserve evidence, question, attempt, and evaluation history. Remove requested
   work only for an evidenced scope change, never to raise readiness.
6. **Validate, then hand off.** Validate the complete candidate's tree, references,
   leaf coverage, and expanded execution DAG before saving. Return it to the
   common persist/evaluate step; do not start a second evaluation here. Save with
   the assigned revision, retire stale pending questions, and obtain one fresh
   whole-graph evaluation. A review that keeps both graph and inputs unchanged
   adds no revision or evaluation; new task evidence still advances the input
   revision. Profile-only observations and unsuccessful attempts alone do not.

## Define executable leaves

Use the [leaf field contract](state-schema.md#task-hierarchy-and-leaf-coverage).
Each leaf names the result, inputs it consumes, requirements it fulfills, and
observable completion conditions with a way to check them. Name actual upstream
outputs; do not invent file paths just to fill `inputs`. Empty unknown checks are
permitted during clarification and block readiness.

Verification may remain inside a small leaf. Create a separate verification task
only for a useful independent result. An authorized investigation can itself be
a leaf: specify the question, bounded method, stop condition, expected evidence,
and decision it informs. Do not require its unknown result before gathering it.
Execute leaves and persist group status from descendant progress; parent summaries
do not count as additional work.

## Readiness versus completion

A criterion checks whether necessary information and decisions are available;
`done_when` describes the eventual deliverable. Planning a report can require its
source and comparison, but not a finished report. Keep interview logistics such
as worker names and state-file location out of product requirements.

Split independently failing conditions when they need different evidence or
next actions. Keep coherent checks together, preserve their scopes, and revise
weights deliberately. Do not add easy or duplicate criteria to pad scores.
Shared checks cannot replace each leaf's actual input and choice requirements.
The [scoring rules](state-schema.md#criterion-scope-and-scores) define coverage,
weighting, and hard blockers; high scores do not excuse omitted parent intent.

## Route the gap before asking

Use the [coordinator protocol](isolated-rounds.md#coordinator-protocol) for
evaluation of current task inputs, then a different fresh questioner on a failed
gate. Reuse a valid current evaluation when its task inputs are unchanged.
The questioner selects a user question, inspection/web research, bounded experiment,
or structural/rubric repair; invalid-state recovery precedes a valid round.
Do not ask users to repeat supplied facts or settle internal bookkeeping. Workers
propose actions; only the coordinator performs authorized inspection or execution.
Question selection belongs to the isolated questioner, not this graph procedure.

## Refine after an answer

Preserve the actual choice, reason, conditions, exceptions, and exclusions.
“Use email because SMS is out of scope” must not become merely “notifications.”
Resolve only what the answer or inspected evidence supports. A researched method
default can resolve its method decision under the [default policy](web-defaults.md),
without creating a user answer. Supersede corrections without erasing unaffected
constraints or history. Keep material ambiguity open.

Run [hierarchy redefinition](#redefine-the-hierarchy), retaining a tree that still
fits. When task inputs change, use one candidate revision for the answer and
edits, then freshly evaluate the whole tree, including unchanged branches and
parent intent. Profile-only updates or attempts without task changes retain the
valid current evaluation. Never transfer an answer to a merely similar new
requirement. Independent authorized work can continue while a choice is pending.

## Example: small change, then a new boundary

Request: download the visible event rows as CSV, using displayed columns and
current filters, with no scheduled emails. Inspect the existing selection and
export behavior; one leaf with a filtered-sample check may suffice.

If the user adds an all-rows option, keep that leaf when the data is already
available. If unloaded rows need a distinct retrieval capability, preserve the
original ID as an export group and add retrieval and download children with a
real handoff. Retrieval can later split again. Map requirements explicitly;
retain column/filter obligations where applicable and the email exclusion.
Nesting changes neither those obligations nor the need for a whole-task review.
