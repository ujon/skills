# Research Topic Interviews

Use this guide when the interview should produce an experiment or research
direction. Choose only the questions that affect feasibility or usefulness;
this is not a questionnaire to send all at once.

Convert these dimensions into task-specific criteria and subtask dependencies in
`interview.toml`. Evaluate them and generate questions through the fresh-session
workflow in `SKILL.md`; do not choose follow-ups in the coordinator's chat.
Start with everyday language even when the research subject is technical.
Preserve recorded research details and worker outputs under the
[recording-fidelity rule](state-schema.md#storage-and-conversation-language).
Use the user's preferred language for questions.

## Find the Decision Criteria

Clarify the intended outcome first: learning a method, demonstrating a working
system, testing a scientific hypothesis, or improving an existing capability.
Then explore whichever unknown would most change the choice:

- The phenomenon or failure mode the user wants to understand.
- Existing experience, implementations, datasets, and accessible environments.
- Actual compute, time, data-collection capacity, and hardware access.
- Desired evidence: prediction quality, task performance, robustness, cost, or
  another observable improvement.
- Preference for reproducing known work versus exploring a less certain idea.

Separate a hard limit from a flexible preference. When resources are unknown,
design a small pilot to measure feasibility rather than promising a schedule or
training budget. Treat research novelty as unverified until relevant prior work
has been checked with primary sources.

## World Model Example

For an opening such as “I'm looking for an experiment topic about world models,”
a useful first question is:

> What would you like to get out of this experiment? You could learn how a world
> model works, build something that works, or test whether an idea is right.

Choose the next question from the answer. A learning exercise may depend first
on prior experience; a physical-control demo may depend on simulator access;
a research hypothesis may depend on the phenomenon and available observations.
Do not ask all of those questions in the opening turn.

Distinguish relevant technical choices only when they affect the experiment:

- Video generation, state or latent prediction, and action-conditioned planning
  lead to different tasks and evaluations.
- A short prediction horizon and a long rollout test different failure modes.
- Known conditions and held-out dynamics test different kinds of generalization.
- Prediction accuracy alone does not establish better closed-loop control.

Possible directions include adapting to hidden dynamics, comparing predicted
action outcomes, planning with predicted states, anticipating failure, and
maintaining consistency over longer horizons. Treat these as optional prompts
for exploration, not a fixed shortlist or a ranking.

If the user actually chooses a drone experiment, then ask about the relevant
observations, action interface, simulator, or real hardware as needed. Do not
infer drone use, a particular GPU allocation, available flight data, or a
multiweek deadline from an assistant's earlier example.

## Make the Chosen Idea Testable

When the user wants an experiment proposal, organize the result around:

1. **Question and hypothesis:** one claim the experiment could support or weaken.
2. **Data and environment:** what will be observed, how data is obtained, and
   which conditions are held out for evaluation.
3. **Approach and baseline:** the proposed method and a simpler or established
   comparison that tests the claim fairly.
4. **Protocol and metrics:** what changes, what stays fixed, and how results are
   measured. Include an ablation when it is needed to isolate the proposed cause.
5. **Possible outcomes:** what success, failure, or an ambiguous result would
   mean; distinguish hypotheses from measured findings.
6. **Feasibility and next step:** a small pilot, known limits, and any prior-work
   check still needed before claiming novelty.

For example, after the user confirms a simulated dynamics-prediction goal,
compare future-state errors for a learned predictor and an appropriate simpler
baseline under both familiar and held-out conditions. Choose the state variables,
horizons, and resource budget from the interview rather than copying fixed
values from another project.
