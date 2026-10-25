# Evidence Learning Coach

A local-first learning skill that preserves first attempts, scores against explicit criteria, schedules delayed retrieval and resumes from saved evidence.

Use it for languages, math, programming, exam preparation or practical skills. The learning goal determines the rubric and the evidence required. A polished rewrite after feedback is not independent mastery.

## Install with one sentence

Ask a Codex agent with `skill-installer`:

> Use skill-installer to install https://github.com/XIAO-AA-AA/evidence-learning-coach/tree/main/skills/evidence-learning-coach

Then ask in the next turn:

> Use evidence-learning-coach to help me learn linear algebra for 30 minutes a day. Assess my current level first and store my learning workspace in ./learning-workspace.

See [INSTALL.md](INSTALL.md) for local and ZIP installation, or [download the release](https://github.com/XIAO-AA-AA/evidence-learning-coach/releases/latest). Codex discovery metadata is included. Other agents can read the Markdown protocol, but their automatic installation and discovery are not yet verified. Persistent continuation requires local file access.

## What is included

- A portable coaching protocol and Codex Skill entry point.
- Rubrics for recall, conceptual understanding, calculations, programming and open-ended work.
- A Python 3.10+ standard-library CLI to initialize a private workspace, preserve attempts, record assessments, derive a review queue and validate records.
- A synthetic example, behavior tests and release packaging.

```sh
python3 skills/evidence-learning-coach/scripts/learning.py init \
  --root ./learning-workspace --subject 'Linear algebra' --goal 'Solve linear systems independently'
python3 skills/evidence-learning-coach/scripts/learning.py review --root ./learning-workspace
python3 -m unittest discover -s tests -v
```

The skill preserves the original response separately from assessments. A corrected assessment is an additional record that names the previous assessment it supersedes. Delayed evidence requires a new, independent variant after the configured gap since the latest topic exposure. Correcting or rereading an answer resets that clock. Provisional grading cannot establish mastery.

Default delays are configurable workflow heuristics, not scientifically validated learning intervals. This project has no controlled outcome study and makes no pass-rate promises.

Study records are private by default. Recording is opt-in per session or enabled in the learner profile. No third-party textbooks, paid question banks or real learner records are included. MIT licensed.
