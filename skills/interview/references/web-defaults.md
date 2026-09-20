# Choose a method without user input

Read this coordinator-only procedure for the workflow's no-user-input branch.
An omitted, skipped, unknown, or delegated method choice triggers web research
instead of repeated requests for a preference. This skill authorizes selecting a
widely used method within the stated outcome and constraints. A user's explicit
choice or restriction takes precedence. A pending question stays pending until
answered, skipped, or superseded; elapsed time is not an answer.

## Research and select

1. Name the missing method choice and the constraints it must satisfy. Search the
   web using the actual domain, environment, and intended result. Do not send
   private request text or sensitive project details in search queries.
2. Read current primary sources: official documentation, relevant standards,
   maintainer guidance, or published adoption data. Prefer methods with broad
   support in the relevant setting. A search rank, a single tutorial, or repeated
   marketing claims do not establish that something is the most widely used.
3. Compare plausible compatible methods on adoption evidence, support,
   complexity, and fit. Choose the best-supported common approach; when adoption
   is unclear, prefer a simple, well-supported convention and disclose that the
   evidence does not establish a universal winner. Popularity cannot override
   an explicit constraint or make an unsuitable method acceptable.
4. Record the chosen default, the alternatives that mattered, why it fits,
   source URLs and access date, and uncertainty. Explain the choice briefly to
   the user and continue without requiring a separate preference confirmation.
   Reopen the choice if later answers or evidence contradict it.

This resolves a method choice, not missing intent or private facts. A common
page layout can be selected; a shop's opening hours cannot be inferred from
other shops. Missing outcomes, incompatible constraints, and facts only the user
can supply remain gaps for the interview. External research does not expand
permission for purchases, publication, or other actions beyond the current task.

If web access fails or no compatible method is supported, record the search
limitation and remaining gap. Use available verified evidence or route to one
useful question, a bounded check, smaller scope, or pause. Do not invent sources
or silently treat memory as a completed search.

## Keep evidence and adoption separate

Use schema 1 evidence and the optional [attempt history](state-schema.md#resolution-attempts):

- Persist the questioner's search plan before execution. Update its attempt with
  the actual result and evidence links, including failed or inconclusive searches;
  do not record a failed search as a user answer or resolved choice.
- Store inspected source findings as `kind = "artifact"` evidence, with URLs,
  access date, applicability, and limitations. A source describes public facts,
  not the user's preferences or proof that this project already works.
- Store the selected approach as `kind = "assumption"`. Set `accepted = true`
  only when adoption follows this default policy or an explicit user delegation;
  name that basis and link the source evidence in its text/source. Acceptance
  means adopted for planning, not user-confirmed or experimentally verified.
- Resolve only the method decision, linking both source findings and the adopted
  default through `evidence_ids`. Preserve open factual or intent decisions.
  Never create a user answer for a researched choice. A superseded question keeps
  its history and is not relabeled as answered.
- Record the change in `changes.reason`, update affected task contracts and
  criteria, then obtain a fresh evaluation when task inputs changed. With no task
  change, keep the current evaluation and send the failed attempt to the next
  fresh questioner. Objective feasibility or completion
  checks still require their own evidence; research does not grant readiness.
