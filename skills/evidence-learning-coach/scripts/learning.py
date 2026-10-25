#!/usr/bin/env python3
"""Local evidence records and conservative review scheduling. Python 3.10+."""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z")
ERROR_TYPES = {
    "recall-gap", "concept", "procedure", "calculation", "terminology",
    "evidence", "omission", "expression", "unknown",
}
DEFAULT_CONFIG = {
    "schema_version": 1,
    "archive_policy": "on_request",
    "delayed_gap_hours": 24,
    "stable_passes": 2,
    "review_days": {
        "needs-practice": 1, "initial-pass": 1, "immediate-repair": 1,
        "delayed-pass": 3, "stable-evidence": 7, "pending-review": 0,
    },
}


class InvalidRecord(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InvalidRecord(message)


def text_field(record, key):
    value = record.get(key)
    require(isinstance(value, str) and bool(value.strip()), f"{key}: expected nonempty text")
    return value


def identifier(value):
    require(isinstance(value, str) and bool(IDENTIFIER.fullmatch(value)), "invalid record identifier")
    return value


def instant(value):
    require(isinstance(value, str), "timestamp must be text")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise InvalidRecord(f"invalid timestamp: {value}") from error
    require(result.tzinfo is not None, "timestamp needs an explicit UTC offset")
    return result.astimezone(timezone.utc)


def number(value, name, minimum=0):
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum,
            f"{name}: expected finite number >= {minimum}")
    return value


def no_symlink(path):
    """Reject links at the target or any existing ancestor before resolving."""
    path = Path(path).expanduser().absolute()
    require(not any(part.is_symlink() for part in (path, *path.parents)),
            f"symbolic-link path is not supported: {path}")
    return path


def read_json(path):
    require(not path.is_symlink(), f"refusing symbolic-link record: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"expected JSON object: {path}")
    return data


def save_new(path, record):
    no_symlink(path)
    # Exclusive creation preserves both original answers and existing grades.
    with path.open("x", encoding="utf-8") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def validate_config(config):
    require(config.get("schema_version") == 1, "unsupported schema version")
    require(config.get("archive_policy") in {"on_request", "automatic"}, "invalid archive policy")
    require(number(config.get("delayed_gap_hours"), "delayed_gap_hours") > 0,
            "delayed_gap_hours must be positive")
    require(type(config.get("stable_passes")) is int and config["stable_passes"] >= 2,
            "stable_passes must be an integer >= 2")
    intervals = config.get("review_days")
    require(isinstance(intervals, dict), "review_days must be an object")
    for state in DEFAULT_CONFIG["review_days"]:
        number(intervals.get(state), f"review_days.{state}")


def validate_attempt(record):
    for field in ("id", "topic_id", "question_id", "variant_id"):
        identifier(record.get(field))
    instant(record.get("submitted_at"))
    text_field(record, "response")
    require(record.get("assistance") in {"none", "hint", "reference", "feedback"},
            "invalid assistance level")
    require(type(record.get("unseen")) is bool, "unseen must be boolean")
    source = record.get("exercise_source")
    require(isinstance(source, dict), "exercise_source must be an object")
    require(source.get("kind") in {"generated", "user-provided", "official", "reference"},
            "invalid exercise source kind")
    text_field(source, "label")
    if "elapsed_seconds" in record:
        number(record["elapsed_seconds"], "elapsed_seconds")


def validate_assessment(record, attempts):
    identifier(record.get("id"))
    attempt_id = identifier(record.get("attempt_id"))
    require(attempt_id in attempts, f"unknown attempt: {attempt_id}")
    timestamp = instant(record.get("assessed_at"))
    require(timestamp >= instant(attempts[attempt_id]["submitted_at"]),
            "assessment predates the attempt")
    rubric = record.get("rubric")
    require(isinstance(rubric, dict), "rubric must be an object")
    identifier(rubric.get("id"))
    text_field(rubric, "version")
    maximum = number(rubric.get("max_points"), "max_points")
    passing = number(rubric.get("pass_points"), "pass_points")
    require(0 < passing <= maximum, "pass_points must be positive and <= max_points")
    require(number(record.get("score"), "score") <= maximum, "score exceeds max_points")
    require(record.get("confidence") in {"confirmed", "provisional"}, "invalid confidence")
    text_field(record, "feedback")
    errors = record.get("error_types")
    require(isinstance(errors, list) and all(isinstance(item, str) and item in ERROR_TYPES for item in errors),
            "invalid error_types")
    if "supersedes" in record:
        identifier(record["supersedes"])


def load_workspace(root):
    root = no_symlink(root)
    require(root.is_dir(), "workspace does not exist")
    for item in root.rglob("*"):
        require(not item.is_symlink(), f"symbolic links are not supported in workspace: {item}")
    config = read_json(root / "state/config.json")
    validate_config(config)
    for name in ("profile.md", "latest-session-notes.md", "plans/current-week.md",
                 "progress/mastery-tracker.md", "mistakes/review-queue.md", "sources/index.md"):
        require((root / name).is_file(), f"missing workspace file: {name}")
    attempts = load_records(root / "state/attempts", validate_attempt)
    assessments = load_records(root / "state/assessments", lambda x: validate_assessment(x, attempts))
    latest = {}
    ordered = sorted(assessments.values(), key=lambda x: (instant(x["assessed_at"]), x["id"]))
    pending = list(ordered)
    while pending:
        progressed = False
        for grade in pending[:]:
            previous = latest.get(grade["attempt_id"])
            old_id = grade.get("supersedes")
            if old_id and old_id not in assessments:
                raise InvalidRecord(f"unknown superseded assessment: {old_id}")
            if old_id and (previous is None or previous["id"] != old_id):
                continue
            if not old_id:
                require(previous is None, "additional grade requires supersedes")
            if previous:
                require(instant(grade["assessed_at"]) >= instant(previous["assessed_at"]),
                        "grade correction predates its predecessor")
            latest[grade["attempt_id"]] = grade
            pending.remove(grade)
            progressed = True
        require(progressed, "invalid, branched or cyclic assessment correction history")
    return root, config, attempts, assessments, latest


def load_records(folder, validate):
    require(folder.is_dir(), f"missing records directory: {folder.name}")
    records = {}
    for file in sorted(folder.glob("*.json")):
        record = read_json(file)
        validate(record)
        require(file.stem == record["id"], f"record ID does not match filename: {file.name}")
        require(record["id"] not in records, "duplicate record ID")
        records[record["id"]] = record
    return records


def initialize(root, subject, goal):
    root = no_symlink(root)
    require(not root.exists() or (root.is_dir() and not any(root.iterdir())),
            "initialization requires a new or empty directory")
    template = Path(__file__).resolve().parents[1] / "assets/workspace"
    require(template.is_dir(), "installed skill is missing workspace templates")
    sources = list(template.rglob("*"))
    require(not any(item.is_symlink() for item in sources), "template contains a symbolic link")
    root.mkdir(parents=True, exist_ok=True)
    for source in sources:
        if source.is_file():
            target = root / source.relative_to(template)
            target.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_text(encoding="utf-8").replace("{{subject}}", subject).replace("{{goal}}", goal)
            with target.open("x", encoding="utf-8") as stream:
                stream.write(content)
    for name in ("attempts", "assessments"):
        (root / "state" / name).mkdir(parents=True)
    (root / "sessions").mkdir()
    save_new(root / "state/config.json", DEFAULT_CONFIG)
    return {"workspace": str(root), "subject": subject, "archive_policy": "on_request"}


def add_record(root, record, kind):
    root, _, attempts, assessments, latest = load_workspace(root)
    if kind == "attempt":
        validate_attempt(record)
        folder = "attempts"
    else:
        validate_assessment(record, attempts)
        previous = latest.get(record["attempt_id"])
        require(record.get("supersedes") == (previous["id"] if previous else None),
                "grade correction must supersede the latest assessment for this attempt")
        if previous:
            require(instant(record["assessed_at"]) >= instant(previous["assessed_at"]),
                    "grade correction predates its predecessor")
        require(record["id"] not in assessments, "assessment ID already exists")
        folder = "assessments"
    save_new(root / "state" / folder / f"{record['id']}.json", record)
    return {"saved": record["id"], "kind": kind}


def review(root, now=None):
    _, config, attempts, assessments, _ = load_workspace(root)
    now = now or datetime.now(timezone.utc)
    # Reconstruct assessment history as of now; future corrections cannot change the past.
    eligible_grades = sorted(
        (g for g in assessments.values() if instant(g["assessed_at"]) <= now),
        key=lambda g: (instant(g["assessed_at"]), g["id"]),
    )
    grades = {}
    remaining = list(eligible_grades)
    while remaining:
        progress = False
        for grade in remaining[:]:
            old = grades.get(grade["attempt_id"])
            if grade.get("supersedes") and (not old or old["id"] != grade["supersedes"]):
                continue
            grades[grade["attempt_id"]] = grade
            remaining.remove(grade)
            progress = True
        require(progress, "assessment history is inconsistent at requested time")
    topics = {}
    for attempt in sorted(attempts.values(), key=lambda a: (instant(a["submitted_at"]), a["id"])):
        timestamp = instant(attempt["submitted_at"])
        if timestamp > now:
            continue
        topics.setdefault(attempt["topic_id"], []).append(attempt)
    rows = []
    gap = timedelta(hours=config["delayed_gap_hours"])
    for topic_id, history in topics.items():
        last_exposure = None
        seen = set()
        delayed = []
        state = "untested"
        unresolved_failure = False
        last_score = None
        for attempt in history:
            timestamp = instant(attempt["submitted_at"])
            grade = grades.get(attempt["id"])
            confirmed = grade and grade["confidence"] == "confirmed"
            passed = confirmed and grade["score"] >= grade["rubric"]["pass_points"]
            independent = attempt["assistance"] == "none"
            qualified = bool(passed and independent and attempt["unseen"]
                             and attempt["variant_id"] not in seen and last_exposure is not None
                             and timestamp - last_exposure >= gap)
            if grade:
                last_score = {"score": grade["score"], "max_points": grade["rubric"]["max_points"],
                              "confidence": grade["confidence"]}
            else:
                last_score = None
            if not confirmed:
                state = "pending-review"
            elif independent and not passed:
                state = "needs-practice"
                unresolved_failure = True
                delayed = []
            elif passed and independent:
                unresolved_failure = False
                if qualified and (not delayed or timestamp - delayed[-1] >= gap):
                    delayed.append(timestamp)
                state = ("stable-evidence" if len(delayed) >= config["stable_passes"] else
                         "delayed-pass" if delayed else "initial-pass")
            elif unresolved_failure:
                state = "needs-practice"
            elif passed:
                state = ("stable-evidence" if len(delayed) >= config["stable_passes"] else
                         "delayed-pass" if delayed else "immediate-repair")
            else:
                state = "needs-practice"
            exposure = max(timestamp, instant(grade["assessed_at"])) if grade else timestamp
            last_exposure = max(last_exposure, exposure) if last_exposure else exposure
            seen.add(attempt["variant_id"])
        due = last_exposure + timedelta(days=config["review_days"][state])
        rows.append({
            "topic_id": topic_id, "state": state,
            "qualified_delayed_passes": len(delayed), "attempt_count": len(history),
            "last_score": last_score, "next_due_at": due.isoformat(), "due": due <= now,
        })
    rows.sort(key=lambda row: (not row["due"], row["next_due_at"], row["topic_id"]))
    return {"as_of": now.isoformat(), "topics": rows}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Create a private learning workspace")
    init.add_argument("--root", required=True, type=Path)
    init.add_argument("--subject", required=True)
    init.add_argument("--goal", required=True)
    for name in ("attempt", "assess"):
        sub = commands.add_parser(name, help="Append a record without overwriting")
        sub.add_argument("--root", required=True, type=Path)
        sub.add_argument("--input", required=True, type=Path)
    queue = commands.add_parser("review", help="Print a derived review queue; no writes")
    queue.add_argument("--root", required=True, type=Path)
    queue.add_argument("--now", type=instant)
    validate = commands.add_parser("validate", help="Check structure, dates and record links")
    validate.add_argument("--root", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            require(bool(args.subject.strip()) and bool(args.goal.strip()), "subject and goal cannot be empty")
            result = initialize(args.root, args.subject, args.goal)
        elif args.command in {"attempt", "assess"}:
            result = add_record(args.root, read_json(args.input), args.command)
        elif args.command == "review":
            result = review(args.root, args.now)
        else:
            _, _, attempts, assessments, _ = load_workspace(args.root)
            result = {"valid": True, "attempts": len(attempts), "assessments": len(assessments)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
