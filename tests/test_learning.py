"""Behavioral checks using synthetic data only."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


learning = module("learning", ROOT / "skills/evidence-learning-coach/scripts/learning.py")
installer = module("installer", ROOT / "install.py")
packager = module("packager", ROOT / "scripts/package.py")
BASE = datetime(2026, 1, 1, 9, tzinfo=timezone.utc)


def attempt(name, hours=0, assistance="none", unseen=True, variant=None):
    return {
        "id": name, "topic_id": "fractions", "question_id": "addition",
        "variant_id": variant or name,
        "submitted_at": (BASE + timedelta(hours=hours)).isoformat(),
        "response": "An original synthetic answer.", "assistance": assistance,
        "unseen": unseen,
        "exercise_source": {"kind": "generated", "label": "Original practice"},
    }


def assessment(record, score=4, confidence="confirmed"):
    return {
        "id": "g-" + record["id"], "attempt_id": record["id"],
        "assessed_at": (learning.instant(record["submitted_at"]) + timedelta(minutes=5)).isoformat(),
        "rubric": {"id": "addition", "version": "1", "max_points": 4, "pass_points": 4},
        "score": score, "confidence": confidence,
        "feedback": "Synthetic grading criteria and feedback.", "error_types": [],
    }


class LearningTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="learning-coach-test-")
        self.folder = Path(self.temporary.name).resolve()
        self.root = self.folder / "workspace"
        learning.initialize(self.root, "分数", "独立完成加法")

    def tearDown(self):
        self.temporary.cleanup()

    def add(self, record, score=4, confidence="confirmed"):
        learning.add_record(self.root, record, "attempt")
        grade = assessment(record, score, confidence)
        learning.add_record(self.root, grade, "assess")
        return grade

    def state(self, hours=100):
        return learning.review(self.root, BASE + timedelta(hours=hours))["topics"][0]

    def test_empty_workspace_has_no_invented_mastery(self):
        self.assertEqual(learning.review(self.root)["topics"], [])
        self.assertIn("分数", (self.root / "profile.md").read_text())
        self.assertEqual((self.root / ".gitignore").read_text().splitlines()[-1], "*")

    def test_init_does_not_merge_or_overwrite(self):
        original = (self.root / "profile.md").read_bytes()
        with self.assertRaises(learning.InvalidRecord):
            learning.initialize(self.root, "other", "other")
        self.assertEqual((self.root / "profile.md").read_bytes(), original)

    def test_first_answer_is_immutable(self):
        record = attempt("a1")
        learning.add_record(self.root, record, "attempt")
        record["response"] = "A corrected answer"
        with self.assertRaises(FileExistsError):
            learning.add_record(self.root, record, "attempt")
        stored = json.loads((self.root / "state/attempts/a1.json").read_text())
        self.assertEqual(stored["response"], "An original synthetic answer.")

    def test_same_session_success_is_not_delayed(self):
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=2))
        self.assertEqual(self.state()["state"], "initial-pass")

    def test_feedback_repetition_cannot_establish_mastery(self):
        self.add(attempt("a1"), score=0)
        self.add(attempt("a2", hours=1, assistance="feedback"))
        self.assertEqual(self.state()["state"], "needs-practice")
        self.assertEqual(self.state()["qualified_delayed_passes"], 0)

    def test_two_spaced_unseen_successes_establish_stable_evidence(self):
        self.add(attempt("a1"), score=0)
        self.add(attempt("a2", hours=25))
        self.assertEqual(self.state(26)["state"], "delayed-pass")
        self.add(attempt("a3", hours=50))
        self.assertEqual(self.state()["state"], "stable-evidence")

    def test_reference_exposure_resets_delay(self):
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=24, assistance="reference"))
        self.add(attempt("a3", hours=25))
        self.assertEqual(self.state()["qualified_delayed_passes"], 0)

    def test_reused_variant_never_counts_as_new_delayed_evidence(self):
        self.add(attempt("a1", variant="same"))
        self.add(attempt("a2", hours=25, variant="same"))
        self.assertEqual(self.state()["state"], "initial-pass")

    def test_provisional_grading_is_not_mastery(self):
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=25), confidence="provisional")
        self.assertEqual(self.state()["state"], "pending-review")
        self.assertEqual(self.state()["qualified_delayed_passes"], 0)

    def test_independent_failure_rolls_back_stable_state(self):
        for name, hour in (("a1", 0), ("a2", 25), ("a3", 50)):
            self.add(attempt(name, hours=hour))
        self.add(attempt("a4", hours=75), score=0)
        row = self.state()
        self.assertEqual(row["state"], "needs-practice")
        self.assertEqual(row["qualified_delayed_passes"], 0)

    def test_future_attempts_do_not_affect_historical_review(self):
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=25))
        self.assertEqual(self.state(hours=1)["attempt_count"], 1)

    def test_grade_corrections_are_linked_and_preserve_old_records(self):
        previous = self.add(attempt("a1"), score=0)
        correction = deepcopy(previous)
        correction.update(id="corrected", score=4, supersedes=previous["id"],
                          assessed_at=(BASE + timedelta(hours=1)).isoformat())
        learning.add_record(self.root, correction, "assess")
        self.assertEqual(self.state()["state"], "initial-pass")
        self.assertEqual(self.state(hours=0.5)["state"], "needs-practice")
        self.assertTrue((self.root / "state/assessments/g-a1.json").exists())
        correction.update(id="unlinked")
        correction.pop("supersedes")
        with self.assertRaises(learning.InvalidRecord):
            learning.add_record(self.root, correction, "assess")

    def test_invalid_scores_timestamps_ids_and_references_are_refused(self):
        self.add(attempt("a1"))
        for value in (float("nan"), float("inf"), -1, 5, True):
            bad = assessment(attempt("a1"), score=value)
            with self.assertRaises(learning.InvalidRecord):
                learning.validate_assessment(bad, {"a1": attempt("a1")})
        for update in ({"id": "../escape"}, {"submitted_at": "2026-01-01T09:00:00"}):
            bad = attempt("a2")
            bad.update(update)
            with self.assertRaises(learning.InvalidRecord):
                learning.validate_attempt(bad)
        bad = assessment(attempt("missing"))
        with self.assertRaises(learning.InvalidRecord):
            learning.add_record(self.root, bad, "assess")

    def test_symlink_target_does_not_write_outside_workspace(self):
        outside = self.folder / "outside"
        outside.mkdir()
        link = self.root / "state/attempts/linked.json"
        link.symlink_to(outside / "never-written.json")
        with self.assertRaises(learning.InvalidRecord):
            learning.add_record(self.root, attempt("linked"), "attempt")
        self.assertEqual(list(outside.iterdir()), [])

    def test_local_install_is_complete_repeatable_and_non_overwriting(self):
        source = ROOT / "skills/evidence-learning-coach"
        target, state = installer.install(source, self.folder / "skills")
        self.assertEqual(state, "installed")
        _, state = installer.install(source, self.folder / "skills")
        self.assertIn("identical", state)
        learning_file = target / "SKILL.md"
        learning_file.write_text(learning_file.read_text() + "\nUser addition\n")
        with self.assertRaises(FileExistsError):
            installer.install(source, self.folder / "skills")
        self.assertIn("User addition", learning_file.read_text())

    def test_installed_skill_can_initialize_and_validate_using_its_own_assets(self):
        target, _ = installer.install(ROOT / "skills/evidence-learning-coach", self.folder / "installed")
        script = target / "scripts/learning.py"
        root = self.folder / "new-learning"
        initialized = subprocess.run(
            [sys.executable, str(script), "init", "--root", str(root),
             "--subject", "Language", "--goal", "Hold a conversation"],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(initialized.stdout)["archive_policy"], "on_request")
        validated = subprocess.run(
            [sys.executable, str(script), "validate", "--root", str(root)],
            capture_output=True, text=True, check=True,
        )
        self.assertTrue(json.loads(validated.stdout)["valid"])

    def test_missing_grade_is_pending_and_review_does_not_write(self):
        learning.add_record(self.root, attempt("a1"), "attempt")
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.state()["state"], "pending-review")
        after = {p.relative_to(self.root).as_posix(): p.read_bytes()
                 for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_feedback_clock_starts_at_the_assessment(self):
        record = attempt("a1")
        learning.add_record(self.root, record, "attempt")
        grade = assessment(record)
        grade["assessed_at"] = (BASE + timedelta(hours=24)).isoformat()
        learning.add_record(self.root, grade, "assess")
        self.add(attempt("a2", hours=25))
        self.assertEqual(self.state()["qualified_delayed_passes"], 0)

    def test_unseen_flag_false_prevents_delayed_upgrade(self):
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=25, unseen=False))
        self.assertEqual(self.state()["qualified_delayed_passes"], 0)

    def test_user_can_configure_intervals_without_changing_records(self):
        config_path = self.root / "state/config.json"
        config = json.loads(config_path.read_text())
        config["delayed_gap_hours"] = 48
        config_path.write_text(json.dumps(config))
        self.add(attempt("a1"))
        self.add(attempt("a2", hours=25))
        self.assertEqual(self.state()["state"], "initial-pass")

    def test_packaged_skill_is_self_contained_and_archives_are_reproducible(self):
        public = self.folder / "public-repo"
        public.mkdir()
        (public / "README.md").write_text("synthetic public file")
        shutil.copytree(ROOT / "skills", public / "skills")
        project, skill = packager.build(public)
        original = skill.read_bytes()
        packager.build(public)
        self.assertEqual(original, skill.read_bytes())
        with zipfile.ZipFile(skill) as archive:
            names = archive.namelist()
            self.assertIn("evidence-learning-coach/SKILL.md", names)
            self.assertIn("evidence-learning-coach/LICENSE", names)
            self.assertIn("evidence-learning-coach/assets/workspace/.gitignore", names)
            self.assertFalse(any("__pycache__" in name for name in names))
            unpacked = self.folder / "unpacked-release"
            archive.extractall(unpacked)
        installed, _ = installer.install(unpacked / "evidence-learning-coach", self.folder / "from-zip")
        checked = subprocess.run(
            [sys.executable, str(installed / "scripts/learning.py"), "init",
             "--root", str(self.folder / "zip-learning"), "--subject", "Math", "--goal", "Add fractions"],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(json.loads(checked.stdout)["subject"], "Math")
        self.assertTrue(project.is_file())

    def test_release_allowlist_excludes_private_workspace(self):
        private = self.folder / "learning-workspace"
        private.mkdir()
        (private / "profile.md").write_text("private learner")
        (self.folder / "README.md").write_text("public")
        paths = packager.public_files(self.folder)
        self.assertEqual([p.name for p in paths], ["README.md"])


if __name__ == "__main__":
    unittest.main()
