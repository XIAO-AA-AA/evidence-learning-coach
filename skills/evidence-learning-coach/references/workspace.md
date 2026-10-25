# Workspace and CLI

Python 3.10+, standard library only. All example records in this repository are synthetic.

## Initialize and read selectively

```sh
python3 <skill-dir>/scripts/learning.py init --root ./learning-workspace --subject 'Math' --goal 'Solve equations'
```

Initialization accepts a new or empty directory, refuses a nonempty directory, and refuses symbolic-link targets. It does not merge into existing learner data. The generated `.gitignore` ignores everything inside the workspace. Choose an authorized path outside the installed skill.

At conversation start read `profile.md` and `latest-session-notes.md` once. Follow the saved next action and only read the relevant plan, source entries or topic evidence. The helper's review can show a compact derived topic summary without rereading every note through the model.

## Record an attempt

When saving is authorized, create a JSON input file and run:

```sh
python3 <skill-dir>/scripts/learning.py attempt --root ./learning-workspace --input ./attempt.json
```

```json
{
  "id": "a-001",
  "topic_id": "fractions",
  "question_id": "fraction-sum",
  "variant_id": "fraction-sum-v1",
  "submitted_at": "2026-01-01T09:00:00+08:00",
  "response": "My original answer, unchanged.",
  "assistance": "none",
  "unseen": true,
  "exercise_source": {"kind": "generated", "label": "Original practice"},
  "elapsed_seconds": 120
}
```

Required fields are shown except `elapsed_seconds`, which is optional. Assistance: `none`, `hint`, `reference`, `feedback`. Use explicit time offsets. IDs may contain ASCII letters, digits, underscore and hyphen, max 80 characters. Do not store an amended response under the original attempt ID; record a new attempt.

## Record an assessment

```sh
python3 <skill-dir>/scripts/learning.py assess --root ./learning-workspace --input ./assessment.json
```

```json
{
  "id": "g-001",
  "attempt_id": "a-001",
  "assessed_at": "2026-01-01T09:05:00+08:00",
  "rubric": {"id": "fraction-rubric", "version": "1", "max_points": 4, "pass_points": 4},
  "score": 3,
  "confidence": "confirmed",
  "feedback": "Correct model; check the final addition. Criteria: model 1, common denominator 1, arithmetic 1, explanation 1.",
  "error_types": ["calculation"]
}
```

Scores must be finite and between zero and max_points. The pass threshold is positive and no greater than max_points. `confidence` is `confirmed` or `provisional`. An unresolved reference or unclear rubric requires provisional grading. The helper checks structure and references, not the truth of the grading.

To correct a grade, use a new ID and `"supersedes": "g-001"`; keep the same attempt ID, an equal-or-later assessment time and a reason in feedback. Only the latest linked assessment affects the derived queue; all old assessments remain readable. A second grade without `supersedes` is refused.

## Review and validate

```sh
python3 <skill-dir>/scripts/learning.py review --root ./learning-workspace
python3 <skill-dir>/scripts/learning.py validate --root ./learning-workspace
```

Review prints JSON and does not write. It reports evidence labels, last score, qualified delayed passes and the next due time. To evaluate a historical fixture, pass `--now 2026-01-04T10:00:00+08:00`. Future records are not eligible at that time.

Validation checks record shapes, IDs, symlinks, references, assessment history, dates and config. It cannot verify content correctness, whether a learner actually avoided aids, or private reading outside the records.

Default config includes `delayed_gap_hours: 24`, `stable_passes: 2` and intervals in days. Change config deliberately to suit the goal; stable_passes must be at least 2. Markdown summaries are updated by the coach on authorized archive, not overwritten by `review`.

## Save a session

Honor `profile.md` / `config.json` archive policy. The user can request no archival even when a previous default allowed it. Save the original attempt and assessment records, update affected summaries, then write:

- what was completed and the independent vs assisted evidence;
- unresolved or disputed grades;
- exact next exercise/topic and exclusions;
- references to the relevant source and record IDs;
- time budget or deadline, only if known;
- pending exercises, separately from a question the learner could not answer.

Use `sessions/YYYY-MM-DD/` for narrative notes when needed. `latest-session-notes.md` should be a short pointer and continuation instruction, not the entire history. Never claim a write succeeded without checking it.
