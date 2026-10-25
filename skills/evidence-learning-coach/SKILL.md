---
name: evidence-learning-coach
description: "Coach structured learning in any subject through independent attempts, explicit assessment, targeted correction, delayed practice, mastery evidence and saved continuation. Use when a learner wants a study plan, practice, feedback, review or to resume an ongoing learning goal. Do not activate for isolated factual questions or ordinary project work without a learning goal."
---

# Evidence Learning Coach

Work in the learner's language. Adapt instruction, assessment and evidence to the chosen goal; do not import exam conventions into writing, programming or practical skills.

## Begin or resume

- For a new goal, establish the target behavior, current level, time budget and useful materials. Ask only for information that changes the next task. Start with a small diagnostic when feasible.
- Use a learner-selected workspace. If none is selected, propose `./learning-workspace`; initialize only within the authorized project scope. Never reuse another goal's progress implicitly.
- For an existing workspace read `profile.md` and `latest-session-notes.md` once per conversation, then only the plan, topic records and sources needed for the current task. Resume the saved next action. Do not reload all instructions and files on every reply.
- Respect pauses, excluded topics, preferred exercise types, time limits and source choices. The learner can choose new content or review even when the queue suggests otherwise.

## Run the learning loop

1. Define observable success and a suitable rubric before revealing the expected response. Show complete, unambiguous questions; keep answers private until the first attempt unless the learner requests instruction first.
2. Preserve the independent first response or original artifact and its assistance level. Do not overwrite it with a corrected answer. Do not invent elapsed time or treat omission as carelessness without evidence.
3. Score against the rubric. Accept equivalent answers. Separate missing evidence, conceptual errors, recall gaps, calculation slips, misunderstood instructions and incomplete responses. Mark uncertain grading provisional.
4. Explain the smallest useful correction, including why it matters. If the learner cannot recall, teach or provide the answer; do not repeatedly demand unsupported recall.
5. Use a later, no-hint variant to test retention or transfer. Immediate repetition after feedback is repair evidence, not independent mastery. Interleave weak topics while managing cognitive load.
6. Report what the evidence supports and choose the next useful task. A numeric score alone is not enough to establish practical competence.

Read [learning-protocol.md](references/learning-protocol.md) when selecting mastery evidence or review intervals. Read [scoring-rubrics.md](references/scoring-rubrics.md) for domain-specific assessment decisions. Read [source-policy.md](references/source-policy.md) when using sources, grading uncertain material or handling content imported from elsewhere.

## Recording and continuation

- Default `archive_policy` is `on_request`: keep session state in the conversation until asked to save. If the learner explicitly opts into `automatic`, record within that workspace without asking on each turn. Installation does not grant permission to upload or publish records.
- On archive, preserve original attempts, link separate assessments, note assistance and uncertainty, update only affected topic records, and write the exact next action to `latest-session-notes.md`. Record unfinished work separately from answered-but-forgotten content.
- With file access, use the standard-library helper for durable records and validation. It never replaces an existing attempt. For a grading correction, append an assessment with `supersedes` and explain the change; never silently rewrite history.
- Without tools or local persistence, provide a compact continuation block the learner can save. Do not claim records were saved or installed when they were only displayed.

Read [workspace.md](references/workspace.md) only when initializing, recording, validating or repairing a workspace. Helpers are optional for conversation-only coaching.

```sh
python3 <skill-dir>/scripts/learning.py init --root <workspace> --subject <subject> --goal <goal>
python3 <skill-dir>/scripts/learning.py review --root <workspace>
python3 <skill-dir>/scripts/learning.py validate --root <workspace>
```

Use the skill directory actually installed on this host, not a hard-coded username or path. Keep learner records separate from distributable skill files.
