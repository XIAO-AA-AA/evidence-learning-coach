# Learning protocol and evidence

## Goal-relative competence

Before practice, state what the learner wants to be able to do and what would demonstrate it. Knowing a label, explaining a concept, solving a new problem and performing a physical action require different evidence. Do not claim universal expertise from text recall.

Use task types as needed: recall, concept explanation, problem solving, procedure, debugging, creation, real-world practice. Adapt difficulty to observed errors. A small amount of new material plus interleaved retrieval often fits the workflow, but respect a learner's request to focus exclusively on one mode.

## Evidence labels

| Label | Evidence |
| --- | --- |
| untested | No recorded attempt for the topic |
| needs-practice | An independent confirmed attempt did not meet the rubric |
| initial-pass | Independent confirmed success; delayed evidence is not yet sufficient |
| immediate-repair | A correct response used a hint, reference or feedback |
| delayed-pass | Confirmed independent success on a previously unseen variant after the delay |
| stable-evidence | At least two qualified delayed successes separated by the configured gap |
| pending-review | Current assessment is missing or provisional |

Labels are not a mandatory sequence. They describe the latest evidence. A fresh independent failure rolls back a prior success. A provisional assessment is not counted as a confirmed failure or success. Subsequent assisted practice preserves earlier success evidence but resets the topic exposure clock. A prior failure remains unresolved until a new confirmed independent success.

For automatic delayed qualification all must hold:

- assistance is `none`;
- assessment is `confirmed` and meets the rubric's stated pass threshold;
- learner reports the variant as `unseen: true`, and no earlier attempt uses the same `variant_id` for that topic;
- at least `delayed_gap_hours` elapsed since the last exposure to the topic, including attempts and assessment feedback;
- the earlier exposure exists. A first-ever attempt cannot be a delayed retest.

The helper cannot detect unreported rereading or answer leakage. Record such exposure as an assisted attempt, or manually delay the next task and document why. Do not create fake answer records to simulate evidence.

## Scheduling defaults

Default gap: 24 hours. Default next reviews: needs-practice/immediate-repair/initial-pass after 1 day, delayed-pass after 3 days, stable-evidence after 7 days. Pending grading is due immediately. These are transparent, configurable planning defaults; no claim is made that these intervals are optimal for every learner or subject.

Same-session, cross-question retrieval can improve confidence and diagnose recall but is not labeled a 24-hour delayed pass. A deadline can justify shorter practice intervals without changing what the evidence label means. Explain when there is not enough time to collect delayed evidence.

To reach stable-evidence, accumulate two delayed successes since the most recent confirmed independent failure; they must be separated by the gap. This prevents a history of repeated errors from being hidden by one correction.

## Use the evidence in conversation

Report a short result, complete error inventory and the next action. Do not repeatedly reteach mastered basics. If a learner forgot a whole list, mark a recall gap; do not insist it was a checking failure. A blank subquestion may be either omission or lack of knowledge, so ask only when the distinction affects the plan.

When time is short, prioritize likely useful skills, recurring errors and deadline requirements. Separate current performance, predicted readiness and uncertainty. Do not promise an outcome from a small sample.
