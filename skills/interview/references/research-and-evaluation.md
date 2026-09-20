# Research basis and evaluation

Evidence reviewed through **2026-09-20**. This is a maintenance reference, not
routine interview context. These studies motivate design choices; they do not
establish the effectiveness of this particular skill. Publication status and
limits matter more than recency alone.

## Findings translated into design choices

| Primary source and status | Finding and limit | Application here |
| --- | --- | --- |
| [Structured Uncertainty guided Clarification for LLM Agents](https://aclanthology.org/2026.findings-acl.2028.pdf), Findings ACL, July 2026 | Distinguishes missing user specifications from model uncertainty and penalizes repetitive clarification. Tool-domain and simulated-user experiments do not establish general interview behavior. | Route inspectable facts away from user questions; require an answer-to-action distinction and account for repetition. |
| [Value of Information: A Framework for Human–Agent Communication](https://aclanthology.org/2026.acl-long.1987/), ACL, July 2026 | Balances expected decision benefit against user effort in four studied domains. Its utilities and answer modeling are not available for arbitrary task graphs. | Compare useful execution differences with answerability and effort. Do not invent probabilities or call a heuristic score measured information gain. |
| [From Rubrics to Reliable Scores](https://arxiv.org/html/2601.08654v3), September 9, 2026 revision; [record](https://arxiv.org/abs/2601.08654) reports EMNLP 2026 acceptance | Combines locked criteria, traceable evidence, and human-score calibration on text benchmarks. Calibration needs labeled examples; citations alone do not prove entailment or truth. | Freeze criteria, bind positive ratings to eligible evidence, and require a short condition-to-evidence reason. Keep policy thresholds distinct from calibrated confidence. |
| [Correlated Errors in Large Language Models](https://proceedings.mlr.press/v267/kim25e.html), ICML, July 2025 | Finds correlated errors across models; its judge case study does not directly test fresh-session isolation. | Fresh workers control shared history; agreement across workers/models is not independent evidence. Do not add routine voting. |
| [Judging LLM-as-a-Judge: Concerning Rubric Artifacts](https://arxiv.org/html/2609.02942v1), August 31, 2026 preprint; [record](https://arxiv.org/abs/2609.02942) reports EMNLP 2026 acceptance | Reports sensitivity to rubric artifacts and failures to update judgments after counterfactual changes. The counterfactual experiment uses a small judge; one reported rate is inconsistent between prose and table. | Test changed evidence, irrelevant citations, and equivalent wording. Do not extrapolate a numerical error rate to this skill. |
| [Context Length Alone Hurts LLM Performance Despite Perfect Retrieval](https://aclanthology.org/2025.findings-emnlp.1264/), Findings EMNLP, November 2025 | In studied models/tasks, correct retrieval does not remove degradation from longer input. It does not determine a safe skill-file size. | Reduce the active context, not just improve headings or retrieval. Preserve enough evidence for actual reasoning. |
| [How Many Instructions Can LLMs Follow at Once?](https://arxiv.org/abs/2507.11538), IFScale preprint, July 15, 2025 | Instruction adherence declines as simultaneous constraints increase in an artificial keyword-inclusion task. This is not a direct test of Markdown skills. | Keep a short operating contract, eliminate repeated rules, and load one role's instructions at a time. |
| [Context Rot](https://www.trychroma.com/research/context-rot), Chroma technical report, July 14, 2025 | Reports effects of length and distractors, including stronger performance with focused conversation evidence. Focused evidence selection used labels/manual work; automatic filtering may drop necessary information. | Prefer exact relevant projections over whole transcripts, retain sources and counterevidence, and test omission failures. This is a technical report, not a verified peer-reviewed result. |
| [LLMs Get Lost In Multi-Turn Conversation](https://arxiv.org/html/2505.06120v1), May 9, 2025 preprint | Controlled simulated conversations expose early assumptions and unreliable recovery. Simulations do not measure real user behavior, and recaps do not fully restore performance. | Reconcile corrections into canonical state and rebuild worker packets from it; do not treat an earlier answer attempt as the specification. |
| [Evaluating AGENTS.md](https://arxiv.org/html/2602.11988v2), June 23, 2026 revision, preprint | Coding context files add cost without consistent success gains; the length analysis finds no clear size–success relationship. Python repository results do not establish an optimal interview-skill length. | Remove redundant process requirements while retaining necessary constraints. Test behavior and induced work, not word count alone. |
| [ContextPilot](https://arxiv.org/html/2608.28476v1), August 28, 2026; [record](https://arxiv.org/abs/2608.28476) reports EMNLP 2026 acceptance | Combines context-management tools with training and reports gains in long-context QA/deep search. It does not test shortening Markdown or demonstrate that untrained pruning is safe. | Keep canonical evidence recoverable while selecting active context. Do not import its RL machinery, token gains, or lossy pruning into this skill. |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), September 29, 2025, vendor engineering guidance | Recommends concise but sufficient instructions, selective retrieval, and representative examples. This is engineering experience, not a controlled skill-length study. | Give each coordinator reference one responsibility and retain a small example where it clarifies a decision boundary. |

The readiness defaults **90/80**, the two-stalled-round backstop, and the default
one-question interaction are engineering choices. None of these papers validates
their exact values, proves that isolated workers are unbiased, or supports
estimating general intelligence from user dialogue.

## Keeping Markdown and worker context manageable

The relevant quantity is what is loaded together, not the number or extension of
files on disk. A larger context window is capacity, not a guarantee of faithful
use. There is no research-backed universal line or token ceiling for this skill.

- Keep `SKILL.md` as the operating contract and conditional reading map. Detailed
  schema, graph procedures, role contracts, examples, and research stay separate.
- Read the needed reference section, not every linked file. Load the research
  reference only for maintenance or an explicit explanation request.
- Give coordinator rules one authoritative home: graph decisions in
  `task-refinement.md`, data invariants in `state-schema.md`, and launch/recovery
  in `isolated-rounds.md`. Link to another section when needed; do not follow
  every link recursively. Removing repetition must not remove the rule itself.
- Keep isolated worker contracts self-contained. Repeated essentials across
  evaluator/questioner contracts are intentional because each receives only its
  own contract. A link cannot replace a rule inside a tools-disabled worker.
- Pass a worker only its role contract and its current structured packet. An
  evaluator does not receive question-writing instructions, prior scores, weights,
  thresholds, or profile-only evidence. A questioner needs the current gate result
  and explanation profile. Separate files do not help if all are pasted together.
- Use concise atomic evidence in the single TOML, retaining conditions, negation,
  exclusions, source identity, and uncertainty. A shortened paraphrase must not
  strengthen a claim. A translation must not silently decide an ambiguity.
- Preserve canonical evidence and history in the TOML. A navigation summary or
  source path cannot replace facts needed by a worker that has no retrieval tools.
  Do not arbitrarily clip large packets or drop unlinked facts that could reveal
  an omitted requirement. Restore missing context before accepting a report.
- Record loaded document sections, packet size, model/runtime, and context-related
  failures when evaluating a change. Measure tokens with the actual tokenizer
  when available; otherwise label byte/word counts as such. Optimize only after
  checking constraint retention and false passes, not length alone.

This is selective loading and evidence preservation, not automatic proof that a
shorter prompt is better. The complete global task still needs a coverage check;
separately checking selected leaves cannot establish a whole-task pass.

## Behavioral checks for maintainers

Use the same fixtures and expected outcomes before and after changing contracts.
Keep expectations hidden from the worker under test. Start a fresh context for
each independent case, using only its role contract and packet. Script tests
check structure, arithmetic, and projection; they do not measure model behavior.

| Case or controlled change | Expected observable behavior |
| --- | --- |
| Fully specified simple request | Summarize requirements and task breakdown without unnecessary questions; execute only if also requested. |
| Populated but ambiguous requirement | Ask a focused follow-up that distinguishes materially different meanings; do not pass it merely because text exists. |
| One consequential user-owned goal or scope choice | A plain question whose answers lead to different concrete actions. |
| Cosmetic alternatives with equivalent authorized work | No question solely to fill an optional field; do not invent a material preference or bypass a failed gate. |
| Fact already present in a supplied source | Inspect or repair a missing packet fact; do not ask the user to repeat it. |
| Omitted method choice or "I don't know" about a method | Propose web research, adopt a compatible well-supported common method, preserve sources and adoption basis, and reevaluate; no fabricated user answer. |
| Popular method conflicts with a stated constraint | Reject the incompatible default; prevalence does not override the request. |
| Missing private fact, unavailable web evidence, or merely pending answer | Keep the unsupported gap explicit; no invented fact, source, or user response. |
| Repeated unproductive questions about intent | Easier comparison, bounded evidence gathering, scope choice, or pause; no fabricated answer. |
| Remove decisive evidence or substitute unrelated accepted evidence | The affected positive rating loses support; a previous pass cannot survive unsupported credit. |
| Add conflicting or late corrective evidence | Preserve unaffected constraints, identify the conflict/correction, and reevaluate current inputs. |
| Paraphrase a criterion without changing meaning | Equivalent support requirements; no reward for polished wording alone. |
| Small request with no independent outputs | One executable leaf can suffice; no mandatory phase tree or extra verification task. |
| Split completed work after adding a new capability | Keep the original ID as parent intent; preserve verified progress without marking new work done. |
| Reparent a task inheriting a constraint or dependency | Compare effective scopes; preserve obligations and recheck global coverage. |
| Profile-only change with unchanged evaluator inputs | Retain current evaluation/readiness; update questioner wording and reject responses based on an outdated packet. |
| Failed or inconclusive inspection/experiment | Retain plan, provenance, and outcome in attempts; select a different route or pause instead of repeating unchanged work. |
| Fresh sessions unavailable | Block the interview loop; a known-gap override cannot bypass worker isolation. |
| Translate qualified user input when needed | Preserve quantities, negation, conditions, and uncertainty; no extra commitments. |
| Omit a needed fact from a compact packet | Report missing context and repair the packet; never infer the fact from its filename. |

Report false-ready cases, supported-condition coverage, retention of late
constraints, repeated/unanswerable questions, useful decision changes per turn,
and actual task checks. Include failures and exact sample counts. Do not report
simulated user satisfaction as a human study or a few passing cases as a measured
improvement rate. For tuning thresholds or claiming confidence calibration, use
human-labeled examples and a separate held-out set; retest when models or domains
change. Independent user feedback is needed to assess real effort and usefulness.

For a reference edit, compare the old and new loaded sections on the same cases,
including a no-change case, a new boundary, and a cross-branch move. Check both
constraint preservation and unnecessary restructuring. Record which obligations
were removed, moved, or retained and why. A lower word count is a measured size
change, not a measured gain in task success. Keep model, inputs, and tool access
constant for a behavioral comparison; isolated spot checks are not a calibrated
benchmark.
